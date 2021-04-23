
import json
from datetime import datetime
import uuid
import random
import string
import sys
from jsonschema import validate
import logging
from collections import OrderedDict
from translator.source_code import translator_shared_library


# Translator


def wzdx_creator(messages, info=None, unsupported_message_callback=None):
    if not messages or not messages.get('incidents', {}).get('incident'):
        return None
   # verify info obj
    if not info:
        info = translator_shared_library.initialize_info()
    if not translator_shared_library.validate_info(info):
        return None

    wzd = translator_shared_library.initialize_wzdx_object(info)

    for incident in messages['incidents']['incident']:
        # Parse Incident to WZDx Feature
        feature = parse_incident(
            incident, callback_function=unsupported_message_callback)
        if feature:
            wzd['features'].append(feature)
    if not wzd['features']:
        return None
    wzd = translator_shared_library.add_ids(wzd)
    return wzd


#################### Sample Incident ####################
#   <incident id="U13631714_202012161717">
#     <creationtime>2020-12-16T17:17:00Z</creationtime>
#     <updatetime>2020-12-16T17:47:00Z</updatetime>
#     <type>CONSTRUCTION</type>
#     <description>Roadwork - Lane Closed, MERGE LEFT [iCone]</description>
#     <location>
#       <direction>ONE_DIRECTION</direction>
#       <polyline>[28.8060608,-96.9916512,28.8060608,-96.9916512]</polyline>
#     </location>
#     <starttime>2020-12-16T17:17:00Z</starttime>
#   </incident>


# function to calculate vehicle impact
def get_vehicle_impact(description):
    vehicle_impact = 'all-lanes-open'
    if 'lane closed' in description.lower():
        vehicle_impact = 'some-lanes-closed'
    return vehicle_impact


# function to parse polyline to geometry line string
def parse_polyline(polylinestring):
    if not polylinestring or type(polylinestring) != str:
        return None
    # polyline rightnow is a list which has an empty string in it.
    polyline = polylinestring.split(',')
    coordinates = []
    for i in range(0, len(polyline)-1, 2):
        try:
            coordinates.append([float(polyline[i + 1]), float(polyline[i])])
        except ValueError as e:
            logging.warning('failed to parse polyline!')
            return []
    return coordinates


# function to get road direction by using geometry coordinates
def get_road_direction(coordinates):
    if not coordinates:
        return None
    try:
        long_dif = coordinates[-1][0] - coordinates[0][0]
        lat_dif = coordinates[-1][1] - coordinates[0][1]
    except ValueError as e:
        raise RuntimeError('Failed to get road direction.') from e

    if abs(long_dif) > abs(lat_dif):
        if long_dif > 0:
            direction = 'eastbound'
        else:
            direction = 'westbound'
    elif lat_dif > 0:
        direction = 'northbound'
    else:
        direction = 'southbound'

    if lat_dif == 0 and long_dif == 0:
        direction = None

    return direction

# function to parse direction from street name


def parse_direction_from_street_name(street):
    if not street or type(street) != str:
        return None
    street_char = street[-1]
    street_chars = street[-2:]
    if street_char == 'N' or street_chars == 'NB':
        direction = 'northbound'
    elif street_char == 'S' or street_chars == 'SB':
        direction = 'southbound'
    elif street_char == 'W' or street_chars == 'WB':
        direction = 'westbound'
    elif street_char == 'E' or street_chars == 'EB':
        direction = 'eastbound'
    else:
        direction = None

    return direction


# function to get event status
def get_event_status(start_time_string, end_time_string):
    start_time = datetime.strptime(start_time_string, "%Y-%m-%dT%H:%M:%SZ")

    event_status = "active"
    if datetime.now() < start_time:
        event_status = "planned"  # if < 2 to 3 weeks make it pending instead of planned
    elif end_time_string:
        end_time = datetime.strptime(end_time_string, "%Y-%m-%dT%H:%M:%SZ")

        if end_time < datetime.now():
            event_status = "completed"
    return event_status

# function to get description


def create_description(incident):
    description = incident['description']

    if incident.get('sensor'):
        description += '\n sensors: '
        for sensor in incident['sensor']:
            if not isinstance(sensor, str):
                if sensor['@type'] == 'iCone':
                    description += '\n' + \
                        json.dumps(parse_icone_sensor(sensor), indent=2)
            else:
                sensor = incident['sensor']
                if sensor['@type'] == 'iCone':
                    description += '\n' + \
                        json.dumps(parse_icone_sensor(sensor), indent=2)

    if incident.get('display'):
        description += '\n displays: '
        for display in incident['display']:
            if not isinstance(display, str):
                if display['@type'] == 'PCMS':
                    description += '\n' + json.dumps(parse_pcms_sensor(display),
                                                     indent=2)  # add baton,ab,truck beacon,ipin,signal
            else:
                display = incident['display']
                if display['@type'] == 'PCMS':
                    description += '\n' + json.dumps(parse_pcms_sensor(display),
                                                     indent=2)  # add baton,ab,truck beacon,ipin,signal

    return description


def parse_icone_sensor(sensor):
    icone = {}
    icone['type'] = sensor['@type']
    icone['id'] = sensor['@id']
    icone['location'] = [float(sensor['@latitude']),
                         float(sensor['@longitude'])]

    if sensor.get('radar', None):
        avg_speed = 0
        std_dev_speed = 0
        num_reads = 0
        for radar in sensor['radar']:
            timestamp = ''
            if not isinstance(radar, str):
                curr_reads = int(radar['@numReads'])
                if curr_reads == 0:
                    continue
                curr_avg_speed = float(radar['@avgSpeed'])
                curr_dev_speed = float(radar['@stDevSpeed'])
                total_num_reads = num_reads + curr_reads
                avg_speed = (avg_speed * num_reads +
                             curr_avg_speed * curr_reads) / total_num_reads
                std_dev_speed = (std_dev_speed * num_reads +
                                 curr_dev_speed * curr_reads) / total_num_reads
                num_reads = total_num_reads
                timestamp = radar['@intervalEnd']
            else:
                radar = sensor['radar']
                avg_speed = float(radar['@avgSpeed'])
                std_dev_speed = float(radar['@stDevSpeed'])
                timestamp = radar['@intervalEnd']

        radar = {}

        radar['average_speed'] = round(avg_speed, 2)
        radar['std_dev_speed'] = round(std_dev_speed, 2)
        radar['timestamp'] = timestamp
        icone['radar'] = radar
    return icone


def parse_pcms_sensor(sensor):
    pcms = {}
    pcms['type'] = sensor['@type']
    pcms['id'] = sensor['@id']
    pcms['timestamp'] = sensor['@id']
    pcms['location'] = [float(sensor['@latitude']),
                        float(sensor['@longitude'])]
    if sensor.get('message', None):
        pcms['messages'] = []
        for message in sensor['message']:
            if not isinstance(message, str):
                pcms['timestamp'] = message['@verified']
                if message['@text'] not in pcms['messages']:
                    pcms['messages'].append(message['@text'])
            else:
                message = sensor['message']
                pcms['timestamp'] = message['@verified']
                if message['@text'] not in pcms['messages']:
                    pcms['messages'].append(message['@text'])
    return pcms


# Parse Icone Incident to WZDx
def parse_incident(incident, callback_function=None):
    if not validate_incident(incident):
        if callback_function:  # Note :a call back fucnction , which will trigger every time the invalid data is given
            callback_function(incident)
        return None
    geometry = {}
    geometry['type'] = "LineString"
    geometry['coordinates'] = parse_polyline(incident['location']['polyline'])
    properties = {}

    # I included a skeleton of the message, fill out all required fields and as many optional fields as you can. Below is a link to the spec page for a road event
    # https://github.com/usdot-jpo-ode/jpo-wzdx/blob/master/spec-content/objects/RoadEvent.md

    # road_event_id
    # Leave this empty, it will be populated by add_ids
    properties['road_event_id'] = ''

    # Event Type ['work-zone', 'detour']
    properties['event_type'] = 'work-zone'

    # data_source_id
    # Leave this empty, it will be populated by add_ids
    properties['data_source_id'] = ''

    # start_date
    properties['start_date'] = incident['starttime']

    # end_date
    properties['end_date'] = incident.get('endtime', '')

    # start_date_accuracy
    properties['start_date_accuracy'] = "estimated"

    # end_date_accuracy
    properties['end_date_accuracy'] = "estimated"

    # beginning_accuracy
    properties['beginning_accuracy'] = "estimated"

    # ending_accuracy
    properties['ending_accuracy'] = "estimated"

    # road_name
    road_name = incident['location']['street']
    properties['road_name'] = road_name

    # direction
    direction = parse_direction_from_street_name(road_name)

    if not direction:
        direction = get_road_direction(geometry['coordinates'])
    properties['direction'] = direction

    # vehicle impact

    properties['vehicle_impact'] = get_vehicle_impact(incident['description'])

    # Relationship
    properties['relationship'] = {}

    # lanes
    properties['lanes'] = []

    # road_name
    properties['road_number'] = ""

    # beginning_cross_street
    properties['beginning_cross_street'] = ""

    # beginning_cross_street
    properties['ending_cross_street'] = ""

    # event status
    properties['event_status'] = get_event_status(
        incident['starttime'], incident.get('endtime'))

    # type_of_work
    # maintenance, minor-road-defect-repair, roadside-work, overhead-work, below-road-work, barrier-work, surface-work, painting, roadway-relocation, roadway-creation
    properties['types_of_work'] = []

    # reduced speed limit
    properties['reduced_speed_limit'] = 25

    # workers present
    properties['workers_present'] = False

    # restrictions
    properties['restrictions'] = []

    # description
    properties['description'] = create_description(incident)

    # creation_date
    properties['creation_date'] = incident['creationtime']

    # update_date
    properties['update_date'] = incident['updatetime']

    feature = {}
    feature['type'] = "Feature"
    feature['properties'] = properties
    feature['geometry'] = geometry

    return feature

# function to validate the incident


def validate_incident(incident):

    if not incident or (type(incident) != dict and type(incident) != OrderedDict):
        logging.warning('incident is empty or has invalid type')
        return False

    location = incident.get('location')
    if not location:
        logging.warning(
            f'Invalid incident with id = {incident.get("@id")}. Location object not present')
        return False

    polyline = location.get('polyline')
    coords = parse_polyline(polyline)
    street = location.get('street', '')

    starttime = incident.get('starttime')
    description = incident.get('description')
    creationtime = incident.get('creationtime')
    updatetime = incident.get('updatetime')
    direction = parse_direction_from_street_name(street)
    if not direction:
        direction = get_road_direction(coords)
        if not direction:
            logging.warning(
                f'Invalid incident with id = {incident.get("@id")}.unable to parse direction from street name or polyline')
            return False
    required_fields = [location, polyline, coords, street,
                       starttime, description, creationtime, updatetime, direction]
    for field in required_fields:
        if not field:
            logging.warning(
                f'Invalid incident with id = {incident.get("@id")}. Not all required fields are present')
            return False

    try:
        datetime.strptime(incident['starttime'], "%Y-%m-%dT%H:%M:%SZ")
        if incident.get('endtime'):
            datetime.strptime(incident['endtime'], "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        logging.warning(
            f'Invalid incident with id = {incident.get("@id")}. Invalid date time format')
        return False

    return True


inputfile, outputfile = translator_shared_library.parse_arguments(
    sys.argv[1:], default_output_file_name='icone_wzdx_translated_output_message.geojson')


def validate_write(wzdx_obj, outputfile, location_schema):
    wzdx_schema = json.loads(open(location_schema).read())
    if not translator_shared_library.validate_wzdx(wzdx_obj, wzdx_schema):
        return False
    with open(outputfile, 'w') as fwzdx:
        fwzdx.write(json.dumps(wzdx_obj, indent=2))
    return True


if inputfile:
    # Added encoding argument because of weird character at start of incidents.xml file

    icone_obj = translator_shared_library.parse_xml(inputfile)
    wzdx = wzdx_creator(icone_obj, translator_shared_library.initialize_info())
    if not validate_write(wzdx, outputfile, 'translator/sample files/validation_schema/wzdx_v3.0_feed.json'):
        print('validation error more message are printed above. output file is not created because the message failed validation.')
    else:
        print('huraaah ! your wzdx message is successfully generated and located here: ' + str(outputfile))

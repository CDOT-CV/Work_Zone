import xmltodict
import xml.etree.ElementTree as ET
import json
from datetime import datetime
import uuid
import random
import string
import pytest
import os.path
import sys, getopt
from jsonschema import validate
from jsonschema import ValidationError
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


# Translator
def wzdx_creator(messages, info):
    wzd = {}
    wzd['road_event_feed_info'] = {}
    # hardcode
    wzd['road_event_feed_info']['feed_info_id'] = info['feed_info_id']
    wzd['road_event_feed_info']['update_date'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    wzd['road_event_feed_info']['publisher'] = 'CDOT'
    wzd['road_event_feed_info']['contact_name'] = 'Abinash Konersman'
    wzd['road_event_feed_info']['contact_email'] = 'abinash.konersman@state.co.us'
    if info['metadata'].get('datafeed_frequency_update', False):
        wzd['road_event_feed_info']['update_frequency'] = info['metadata'][
            'datafeed_frequency_update']  # Verify data type
    wzd['road_event_feed_info']['version'] = '3.0'

    data_source = {}
    data_source['data_source_id'] = str(uuid.uuid4())
    data_source['feed_info_id'] = info['feed_info_id']
    data_source['organization_name'] = info['metadata']['issuing_organization']
    data_source['contact_name'] = info['metadata']['contact_name']
    data_source['contact_email'] = info['metadata']['contact_email']
    if info['metadata'].get('datafeed_frequency_update', False):
        data_source['update_frequency'] = info['metadata']['datafeed_frequency_update']
    data_source['update_date'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    # data_source['location_verify_method'] = info['metadata']['location_verify_method']
    data_source['location_method'] = info['metadata']['wz_location_method']
    data_source['lrs_type'] = info['metadata']['lrs_type']
    # data_source['lrs_url'] = "basic url"

    # data_source_icone= {}
    # data_source_icone['data_source_id'] = str(uuid.uuid4())
    # data_source_icone['feed_info_id'] = info['feed_info_id']
    # data_source_icone['organization_name'] = info['metadata']['issuing_organization']
    # data_source_icone['contact_name'] = info['metadata']['contact_name']
    # data_source_icone['contact_email'] = info['metadata']['contact_email']
    # if info['metadata'].get('datafeed_frequency_update', False):
    #     data_source_icone['update_frequency'] = info['metadata']['datafeed_frequency_update']
    # data_source_icone['update_date'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    # data_source_icone['location_verify_method'] = info['metadata']['location_verify_method']
    # data_source_icone['location_method'] = info['metadata']['wz_location_method']
    # data_source_icone['lrs_type'] = info['metadata']['lrs_type']
    # # data_source_icone['lrs_url'] = "basic url"

    wzd['road_event_feed_info']['data_sources'] = [data_source]

    wzd['type'] = 'FeatureCollection'
    nodes = []
    sub_identifier = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in
                             range(6))  # Create random 6 character digit/letter string
    road_event_id = str(uuid.uuid4())
    ids = {}
    ids['sub_identifier'] = sub_identifier
    ids['road_event_id'] = road_event_id

    wzd['features'] = []
    # print(messages)
    # print("")
    # print("")
    # print("")
    # print("")
    # print("")
    for incident in messages['incidents']['incident']:
        # print(incident)
        # print("")
        # print("")
        # Parse Incident to WZDx Feature
        polyline = parse_polyline(incident['location']['polyline'])
        avg_point = [(polyline[0][0] + polyline[-1][0]) / 2, (polyline[0][1] + polyline[-1][1]) / 2]

        if is_in_colorado(avg_point) or True:
            feature = parse_incident(incident)
            if feature:
                wzd['features'].append(feature)

    wzd = add_ids(wzd, True)
    return wzd


#################### Sample Incident ####################
#   <incident id="U13631714_202012161717">
#     <creationtime>2020-12-16T17:17:00Z</creationtime>
#     <updatetime>2020-12-16T17:47:00Z</updatetime>
#     <type>CONSTRUCTION</type>
#     <description>Roadwork - Lane Closed, MERGE LEFT [iCone]</description>
#     <location>
#       <direction>ONE_DIRECTION</direction>
#       <polyline>28.8060608,-96.9916512,28.8060608,-96.9916512</polyline>
#     </location>
#     <starttime>2020-12-16T17:17:00Z</starttime>
#   </incident>


def polygon_contains_point(point, polygon):
    return polygon.contains(point)


def is_in_colorado(coordinates):
    point = Point(coordinates[0], coordinates[1])
    colorado = Polygon(
        [(36.993016, -102.042089), (36.999084, -109.045223), (41.000659, -109.050076), (41.002361, -102.051721)])
    return polygon_contains_point(point, colorado)


is_in_colorado([40.703547, -102.584596])


# function to calculate vehicle impact
def get_vehicle_impact(description):
    vehicle_impact = 'all-lanes-open'
    if 'lane closed' in description.lower():
        vehicle_impact = 'some-lanes-closed'
    return vehicle_impact


# function to parse polyline to geometry line string
def parse_polyline(polylinestring):
    polyline = polylinestring.split(',')
    coordinates = []
    for i in range(0, len(polyline), 2):
        coordinates.append([float(polyline[i + 1]), float(polyline[i])])
    return coordinates


# function to get road direction by using geometry coordinates
def get_road_direction(coordinates):
    long_dif = coordinates[-1][0] - coordinates[0][0]
    lat_dif = coordinates[-1][1] - coordinates[0][1]
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


def parse_direction_from_street_name(street):
    # function to parse direction from street name
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


def create_description(incident):
    description = incident['description']

    if incident.get('sensor'):
        description += '\n sensors: '
        for sensor in incident['sensor']:
            if not isinstance(sensor, str):
                if sensor['@type'] == 'iCone':
                    description += '\n' + json.dumps(parse_icone_sensor(sensor), indent=2)
            else:
                sensor = incident['sensor']
                if sensor['@type'] == 'iCone':
                    description += '\n' + json.dumps(parse_icone_sensor(sensor), indent=2)

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
    icone['location'] = [float(sensor['@latitude']), float(sensor['@longitude'])]

    if sensor.get('radar', None):
        avg_speed = 0
        std_dev_speed = 0
        num_reads = 0
        for radar in sensor['radar']:
            timestamp=''
            if not isinstance(radar, str):
                curr_reads = int(radar['@numReads'])
                if curr_reads == 0:
                    continue
                curr_avg_speed = float(radar['@avgSpeed'])
                curr_dev_speed = float(radar['@stDevSpeed'])
                total_num_reads = num_reads + curr_reads
                avg_speed = (avg_speed * num_reads + curr_avg_speed * curr_reads) / total_num_reads
                std_dev_speed = (std_dev_speed * num_reads + curr_dev_speed * curr_reads) / total_num_reads
                num_reads = total_num_reads
                timestamp = radar['@intervalEnd']
            else:
                radar = sensor['radar']
                avg_speed = float(radar['@avgSpeed'])
                std_dev_speed = float(radar['@stDevSpeed'])
                timestamp = radar['@intervalEnd']

        radar = {}

        radar['average_speed'] = round(avg_speed,2)
        radar['std_dev_speed'] = round(std_dev_speed,2)
        radar['timestamp']=timestamp
        icone['radar'] = radar
    return icone


def parse_pcms_sensor(sensor):
    pcms = {}
    pcms['type'] = sensor['@type']
    pcms['id'] = sensor['@id']
    pcms['timestamp'] = sensor['@id']
    pcms['location'] = [float(sensor['@latitude']), float(sensor['@longitude'])]
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
def parse_incident(incident):
    feature = {}
    geometry = {}
    geometry['type'] = "LineString"
    geometry['coordinates'] = parse_polyline(incident['location']['polyline'])

    feature['type'] = "Feature"
    properties = {}

    #### I included a skeleton of the message, fill out all required fields and as many optional fields as you can. Below is a link to the spec page for a road event
    #### https://github.com/usdot-jpo-ode/jpo-wzdx/blob/master/spec-content/objects/RoadEvent.md

    # road_event_id
    #### Leave this empty, it will be populated by add_ids
    properties['road_event_id'] = ''

    # Event Type ['work-zone', 'detour']
    properties['event_type'] = 'work-zone'

    # data_source_id
    #### Leave this empty, it will be populated by add_ids
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
    road_name = incident['location'].get('street', '')
    if not road_name:
        return None
    properties['road_name'] = incident['location'].get('street', '')

    # direction
    direction = parse_direction_from_street_name(incident['location'].get('street', ''))
    if not direction:
        direction = get_road_direction(geometry['coordinates'])
        if not direction:
            return None

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

    # # beginning_milepost
    # properties['beginning_milepost'] = ""
    #
    # # ending_milepost
    # properties['ending_milepost'] = ""

    # event status
    start_time = datetime.strptime(incident['starttime'], "%Y-%m-%dT%H:%M:%SZ")

    properties['event_status'] = get_event_status(incident['starttime'], incident.get('endtime'))

    # event status
    properties['total_num_lanes'] = 1

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


# Add ids to message
#### This function may fail if some optional fields are not present (lanes, types_of_work, relationship, ...)
def add_ids(message, add_ids):
    if add_ids:
        feed_info_id = message['road_event_feed_info']['feed_info_id']
        data_source_id = message['road_event_feed_info']['data_sources'][0]['data_source_id']

        road_event_length = len(message['features'])
        road_event_ids = []
        for i in range(road_event_length):
            road_event_ids.append(str(uuid.uuid4()))

        for i in range(road_event_length):
            feature = message['features'][i]
            road_event_id = road_event_ids[i]
            feature['properties']['road_event_id'] = road_event_id
            # feature['properties']['feed_info_id'] = feed_info_id
            feature['properties']['data_source_id'] = data_source_id
            # feature['properties']['relationship'] = {}
            feature['properties']['relationship']['relationship_id'] = str(uuid.uuid4())
            feature['properties']['relationship']['road_event_id'] = road_event_id
            #### Relationship logic invalid. It assumes that each feature is part of the same work zone
            # if i == 0: feature['properties']['relationship']['first'] = road_event_ids
            # else: feature['properties']['relationship']['next'] = road_event_ids

            # for lane in feature['properties']['lanes']:
            #     lane_id = str(uuid.uuid4())
            #     lane['lane_id'] = lane_id
            #     lane['road_event_id'] = road_event_id
            #     for lane_restriction in lane.get('restrictions', []):
            #         lane_restriction_id = str(uuid.uuid4())
            #         lane_restriction['lane_restriction_id'] = lane_restriction_id
            #         lane_restriction['lane_id'] = lane_id
            # for types_of_work in feature['properties']['types_of_work']:
            #     types_of_work_id = str(uuid.uuid4())
            #     types_of_work['types_of_work_id'] = types_of_work_id
            #     types_of_work['road_event_id'] = road_event_id
    return message


def parse_arguments(argv):
    inputfile = ''
    outputfile = 'wzdx_translated_output_message.geojson'
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        # print ('test.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            #  print ('test.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
    # print ('Input file is "', inputfile)
    # print ('Output file is "', outputfile)
    return inputfile, outputfile


inputfile, outputfile = parse_arguments(sys.argv[1:])


def initialize_info():
    info = {}

    #### Consider whether this id needs to be hardcoded or generated
    info['feed_info_id'] = "104d7746-688c-44ed-b195-2ee948bf9dfa"

    #### This information is required, might want to hardcode
    info['metadata'] = {}
    info['metadata']['wz_location_method'] = "channel-device-method"
    info['metadata']['lrs_type'] = "lrs_type"
    # info['metadata']['location_verify_method'] = "location_verify_method"
    # info['metadata']['datafeed_frequency_update'] = 86400
    # info['metadata']['timestamp_metadata_update'] = "timestamp_metadata_update"
    info['metadata']['contact_name'] = "Abinash Konersman"  # we can consider to add a representive name from iCone
    info['metadata']['contact_email'] = "abinash.konersman@state.co.us"
    info['metadata']['issuing_organization'] = "iCone"

    return info


def parse_xml(inputfile):
    with open(inputfile, encoding='utf-8-sig') as frsm:
        # Read
        xmlSTRING = frsm.read()
        icone_obj = xmltodict.parse(xmlSTRING)
        return icone_obj


def validate_write(wzdx_obj, outputfile, location_schema):
    wzdx_schema = json.loads(open(location_schema).read())
    try:
        validate(instance=wzdx_obj, schema=wzdx_schema)
    except ValidationError as e:
        print(e)
        return False

    with open(outputfile, 'w') as fwzdx:
        fwzdx.write(json.dumps(wzdx_obj, indent=2))

    # if not os.path.exists(outputfile) or os.stat(outputfile).st_size == 0:
    #     print('Output file creation failed . file does not exist or is empty')
    #     return False
    # else:
    return True


if inputfile:
    # Added encoding argument because of weird character at start of incidents.xml file

    icone_obj = parse_xml(inputfile)
    wzdx = wzdx_creator(icone_obj, initialize_info())
    if not validate_write(wzdx, outputfile, '../sample files/validation_schema/wzdx_v3.0_feed.json'):
        print('validation error more messages are printed above')
    else:
        print('huraaah ! your wzdx message is successfully generated and located here: ' + str(outputfile))
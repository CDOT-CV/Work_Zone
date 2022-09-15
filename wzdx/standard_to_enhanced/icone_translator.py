
import argparse
import json
import logging
import copy
import uuid
from wzdx.sample_files.validation_schema import wzdx_v40_feed

from wzdx.tools import date_tools, polygon_tools, wzdx_translator, geospatial_tools

PROGRAM_NAME = 'IconeTranslator'
PROGRAM_VERSION = '1.0'


DEFAULT_ICONE_FEED_INFO_ID = '104d7746-688c-44ed-b195-2ee948bf9dfa'


def main():
    input_file, output_file = parse_icone_arguments()
    # Added encoding argument because of weird character at start of incidents.xml file

    icone_obj = json.loads(open(input_file, 'r').read())
    wzdx = wzdx_creator(icone_obj)
    wzdx_schema = wzdx_v40_feed.wzdx_v40_schema_string

    if not wzdx_translator.validate_wzdx(wzdx, wzdx_schema):
        logging.error(
            'validation error more message are printed above. output file is not created because the message failed validation.')
        return
    with open(output_file, 'w') as fwzdx:
        fwzdx.write(json.dumps(wzdx, indent=2))
        print('Your wzdx message was successfully generated and is located here: ' + str(output_file))


# parse script command line arguments
def parse_icone_arguments():
    parser = argparse.ArgumentParser(
        description='Translate iCone data to WZDx')
    parser.add_argument('--version', action='version',
                        version=f'{PROGRAM_NAME} {PROGRAM_VERSION}')
    parser.add_argument('iconeFile', help='icone file path')
    parser.add_argument('--outputFile', required=False,
                        default='icone_wzdx_translated_output_message.geojson', help='output file path')

    args = parser.parse_args()
    return args.iconeFile, args.outputFile


def wzdx_creator(message, info=None):
    if not message:
        print('returning None 50')
        return None
   # verify info obj
    if not info:
        info = wzdx_translator.initialize_info(
            DEFAULT_ICONE_FEED_INFO_ID)
    if not wzdx_translator.validate_info(info):
        print('returning None 57')
        return None

    wzd = wzdx_translator.initialize_wzdx_object(info)

    # Parse Incident to WZDx Feature
    feature = parse_incident(message)
    print(feature)
    if feature:
        wzd.get('features').append(feature)

    if not wzd.get('features'):
        print('returning None 69')
        return None
    wzd = wzdx_translator.add_ids(wzd)
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


# {
#     "rtdh_timestamp": 1633097202.1872184,
#     "rtdh_message_id": "bffd71cd-d35a-45c2-ba4d-a86e1ff12847",
#     "event": {
#         "type": "CONSTRUCTION",
#         "source": {
#         "id": 1245,
#         "last_updated_timestamp": 1598046722
#         },
#         "geometry": "",
#         "header": {
#         "description": "19-1245: Roadwork between MP 40 and MP 48",
#         "start_timestamp": 1581725296,
#         "end_timestamp": null
#         },
#         "detail": {
#         "road_name": "I-75 N",
#         "road_number": "I-75 N",
#         "direction": null
#         }
#     }
# }


# function to calculate vehicle impact
def get_vehicle_impact(description):
    vehicle_impact = 'all-lanes-open'
    if 'lane closed' in description.lower():
        vehicle_impact = 'some-lanes-closed'
    return vehicle_impact


# function to get description
def create_description(incident):
    description = incident.get('description')

    if incident.get('sensor'):
        description += '\n sensors: '
        for sensor in incident.get('sensor'):
            if not isinstance(sensor, str):
                if sensor['@type'] == 'iCone':
                    description += '\n' + \
                        json.dumps(parse_icone_sensor(sensor), indent=2)
            else:
                sensor = incident.get('sensor')
                if sensor['@type'] == 'iCone':
                    description += '\n' + \
                        json.dumps(parse_icone_sensor(sensor), indent=2)

    if incident.get('display'):
        description += '\n displays: '
        for display in incident.get('display'):
            if not isinstance(display, str):
                if display['@type'] == 'PCMS':
                    description += '\n' + json.dumps(parse_pcms_sensor(display),
                                                     indent=2)  # add baton,ab,truck beacon,ipin,signal
            else:
                display = incident.get('display')
                if display['@type'] == 'PCMS':
                    description += '\n' + json.dumps(parse_pcms_sensor(display),
                                                     indent=2)  # add baton,ab,truck beacon,ipin,signal

    return description


def parse_icone_sensor(sensor):
    icone = {}
    icone['type'] = sensor.get('@type')
    icone['id'] = sensor.get('@id')
    icone['location'] = [float(sensor.get('@latitude')),
                         float(sensor.get('@longitude'))]

    if sensor.get('radar', None):
        avg_speed = 0
        std_dev_speed = 0
        num_reads = 0
        for radar in sensor.get('radar'):
            timestamp = ''
            if not isinstance(radar, str):
                curr_reads = int(radar.get('@numReads'))
                if curr_reads == 0:
                    continue
                curr_avg_speed = float(radar.get('@avgSpeed'))
                curr_dev_speed = float(radar.get('@stDevSpeed'))
                total_num_reads = num_reads + curr_reads
                avg_speed = (avg_speed * num_reads +
                             curr_avg_speed * curr_reads) / total_num_reads
                std_dev_speed = (std_dev_speed * num_reads +
                                 curr_dev_speed * curr_reads) / total_num_reads
                num_reads = total_num_reads
                timestamp = radar.get('@intervalEnd')
            else:
                radar = sensor.get('radar')
                avg_speed = float(radar.get('@avgSpeed'))
                std_dev_speed = float(radar.get('@stDevSpeed'))
                timestamp = radar.get('@intervalEnd')

        radar = {}

        radar['average_speed'] = round(avg_speed, 2)
        radar['std_dev_speed'] = round(std_dev_speed, 2)
        radar['timestamp'] = timestamp
        icone['radar'] = radar
    return icone


def parse_pcms_sensor(sensor):
    pcms = {}
    pcms['type'] = sensor.get('@type')
    pcms['id'] = sensor.get('@id')
    pcms['timestamp'] = sensor.get('@id')
    pcms['location'] = [float(sensor.get('@latitude')),
                        float(sensor.get('@longitude'))]
    if sensor.get('message', None):
        pcms['messages'] = []
        for message in sensor.get('message'):
            if not isinstance(message, str):
                pcms['timestamp'] = message.get('@verified')
                if message.get('@text') not in pcms.get('messages'):
                    pcms.get('messages').append(message.get('@text'))
            else:
                message = sensor.get('message')
                pcms['timestamp'] = message.get('@verified')
                if message['@text'] not in pcms.get('messages'):
                    pcms.get('messages').append(message.get('@text'))
    return pcms


# Parse Icone Incident to WZDx
def parse_incident(incident):

    event = incident.get('event')

    source = event.get('source')
    header = event.get('header')
    detail = event.get('detail')

    geometry = {}
    geometry['type'] = "LineString"
    geometry['coordinates'] = event.get('geometry')
    properties = wzdx_translator.initialize_feature_properties()

    # I included a skeleton of the message, fill out all required fields and as many optional fields as you can. Below is a link to the spec page for a road event
    # https://github.com/usdot-jpo-ode/jpo-wzdx/blob/master/spec-content/objects/RoadEvent.md

    core_details = properties['core_details']

    # Event Type ['work-zone', 'detour']
    core_details['event_type'] = 'work-zone'

    # data_source_id - Leave this empty, it will be populated by add_ids
    core_details['data_source_id'] = ''

    # road_name
    road_names = [detail.get('road_name')]
    core_details['road_names'] = road_names

    # direction
    for road_name in road_names:
        direction = wzdx_translator.parse_direction_from_street_name(road_name)
        if direction:
            break
    if not direction:
        direction = geospatial_tools.get_road_direction_from_coordinates(
            geometry.get('coordinates'))
    if not direction:
        print('returning None')
        return None
    core_details['direction'] = direction

    # relationship
    core_details['relationship'] = {}

    # description
    core_details['description'] = header.get('description')

    # creation_date
    core_details['creation_date'] = date_tools.get_iso_string_from_unix(
        source.get('creation_timestamp'))

    # update_date
    core_details['update_date'] = date_tools.get_iso_string_from_unix(
        source.get('last_updated_timestamp'))

    # core_details
    properties['core_details'] = core_details

    start_time = date_tools.parse_datetime_from_unix(
        header.get('start_timestamp'))
    end_time = date_tools.parse_datetime_from_unix(header.get('end_timestamp'))

    # start_date
    properties['start_date'] = date_tools.get_iso_string_from_datetime(
        start_time)

    # end_date
    if end_time:
        properties['end_date'] = date_tools.get_iso_string_from_datetime(
            end_time)
    else:
        properties['end_date'] = None

    # start_date_accuracy
    properties['start_date_accuracy'] = "estimated"

    # end_date_accuracy
    properties['end_date_accuracy'] = "estimated"

    # beginning_accuracy
    properties['beginning_accuracy'] = "estimated"

    # ending_accuracy
    properties['ending_accuracy'] = "estimated"

    # location_method
    properties["location_method"] = "channel-device-method"

    # vehicle impact
    properties['vehicle_impact'] = get_vehicle_impact(
        header.get('description'))

    # lanes
    properties['lanes'] = []

    # beginning_cross_street
    properties['beginning_cross_street'] = ""

    # beginning_cross_street
    properties['ending_cross_street'] = ""

    # beginning_cross_street
    properties['beginning_milepost'] = ""

    # beginning_cross_street
    properties['ending_milepost'] = ""

    # event status
    properties['event_status'] = date_tools.get_event_status(
        start_time, end_time)

    # type_of_work
    # maintenance, minor-road-defect-repair, roadside-work, overhead-work, below-road-work, barrier-work, surface-work, painting, roadway-relocation, roadway-creation
    properties['types_of_work'] = []

    # worker_presence - not available

    # reduced_speed_limit_kph - not available

    # restrictions
    properties['restrictions'] = []

    filtered_properties = copy.deepcopy(properties)

    for key, value in properties.items():
        if not value:
            del filtered_properties[key]

    for key, value in properties['core_details'].items():
        if not value and key not in ['data_source_id']:
            del filtered_properties['core_details'][key]

    feature = {}
    feature['id'] = event.get('source', {}).get('id', uuid.uuid4())
    feature['type'] = "Feature"
    feature['properties'] = filtered_properties
    feature['geometry'] = geometry
    # feature['bbox'] = geometry

    return feature


if __name__ == "__main__":
    main()

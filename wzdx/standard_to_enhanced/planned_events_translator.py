
import argparse
import json
import logging
import copy
from collections import OrderedDict
from os import path
import uuid

from wzdx.sample_files.validation_schema import wzdx_v40_feed

from wzdx.tools import date_tools, polygon_tools, wzdx_translator

PROGRAM_NAME = 'PlannedEventsTranslator'
PROGRAM_VERSION = '1.0'


DEFAULT_PLANNED_EVENTS_FEED_INFO_ID = '49253be7-0c6a-4a65-8113-450f9041f989'


def main():
    input_file, output_file = parse_planned_events_arguments()
    # Added encoding argument because of weird character at start of incidents.xml file

    planned_events_obj = json.loads(open(input_file, 'r').read())
    wzdx = wzdx_creator(planned_events_obj)
    wzdx_schema = wzdx_v40_feed.wzdx_v40_schema_string
    # wzdx = json.loads(invalid_msg_str)

    if not wzdx_translator.validate_wzdx(wzdx, wzdx_schema):
        logging.error(
            'validation error more message are printed above. output file is not created because the message failed validation.')
        return
    with open(output_file, 'w') as fwzdx:
        fwzdx.write(json.dumps(wzdx, indent=2))
        print('Your wzdx message was successfully generated and is located here: ' + str(output_file))


# parse script command line arguments
def parse_planned_events_arguments():
    parser = argparse.ArgumentParser(
        description='Translate Planned Event data to WZDx')
    parser.add_argument('--version', action='version',
                        version=f'{PROGRAM_NAME} {PROGRAM_VERSION}')
    parser.add_argument('plannedEventsFile', help='planned_events file path')
    parser.add_argument('--outputFile', required=False,
                        default='planned_events_wzdx_translated_output_message.geojson', help='output file path')

    args = parser.parse_args()
    return args.plannedEventsFile, args.outputFile


def wzdx_creator(message, info=None):
    if not message:
        return None
   # verify info obj
    if not info:
        info = wzdx_translator.initialize_info(
            DEFAULT_PLANNED_EVENTS_FEED_INFO_ID)
    if not wzdx_translator.validate_info(info):
        return None

    wzd = wzdx_translator.initialize_wzdx_object_v3(info)

    # Parse Incident to WZDx Feature
    if message['event']['type'] == 'work-zone':
        feature = parse_work_zone(message)
    elif message['event']['type'] == 'restriction':
        feature = parse_road_restriction
    else:
        logging.warning(f"Unrecognized event type: {message['event']['type']}")

    if feature:
        wzd.get('features').append(feature)

    if not wzd.get('features'):
        return None
    wzd = wzdx_translator.add_ids(wzd)
    return wzd

# {
#   "rtdh_timestamp": 1641915055.3268929,
#   "rtdh_message_id": "abcbc502-09ca-4c4b-a499-8a2bd9872411",
#   "event": {
#     "type": {
#       "type_name": "below-road-work",
#       "is_architectural_change": true
#     },
#     "source": {
#       "id": "OpenTMS-Event1689408506",
#       "creation_timestamp": 1635531964000,
#       "last_updated_timestamp": 1635532501835
#     },
#     "geometry": [
#       [
#         -108.279106,
#         39.195663
#       ],
#       [
#         -108.218549,
#         39.302392
#       ]
#     ],
#     "header": {
#       "description": "Between Exit 49: CO 65; Grand Mesa (5 miles east of the Palisade area) and US 6 (Debeque) from Mile Point 50 to Mile Point 60. Road closed expect delays due to bridge construction. Until May 1, 2022 at about 12:26PM MDT.",
#       "start_timestamp": 1635531964000,
#       "end_timestamp": 1651429564000
#     },
#     "detail": {
#       "road_name": "I-70E",
#       "road_number": "I-70E",
#       "direction": "westbound"
#     },
#     "additional_info": {
#       "lanes": [
#         {
#           "order": 0,
#           "type": "shoulder",
#           "status": "open"
#         },
#         {
#           "order": 1,
#           "type": "general",
#           "status": "open"
#         },
#         {
#           "order": 2,
#           "type": "general",
#           "status": "open"
#         },
#         {
#           "order": 3,
#           "type": "shoulder",
#           "status": "open"
#         }
#       ]
#     }
#   }
# }

# function to calculate vehicle impact


def get_vehicle_impact(lanes):
    num_lanes = len(lanes)
    num_closed_lanes = 0
    for i in lanes:
        if i['status'] != 'open':
            num_closed_lanes += 1
    if num_closed_lanes == num_lanes:
        return 'all-lanes-closed'
    elif num_closed_lanes == 0:
        return 'all-lanes-open'
    else:
        return 'some-lanes-closed'


# Parse Icone Incident to WZDx
def parse_road_restriction(incident):
    if not incident or type(incident) != dict:
        return None

    event = incident.get('event')

    source = event.get('source')
    header = event.get('header')
    detail = event.get('detail')
    additional_info = event.get('additional_info', {})

    geometry = {}
    geometry['type'] = "LineString"
    geometry['coordinates'] = event.get('geometry')
    properties = {}

    # I included a skeleton of the message, fill out all required fields and as many optional fields as you can. Below is a link to the spec page for a road event
    # https://github.com/usdot-jpo-ode/jpo-wzdx/blob/master/spec-content/objects/RoadEvent.md

    core_details = {}

    # data_source_id
    # Leave this empty, it will be populated by add_ids_v3
    core_details['data_source_id'] = ''

    # Event Type ['work-zone', 'detour']
    core_details['event_type'] = event.get('type')

    # road_name
    road_names = [detail.get('road_name')]
    core_details['road_names'] = road_names

    # direction
    direction = None
    for road_name in road_names:
        direction = wzdx_translator.parse_direction_from_street_name(road_name)
        if direction:
            break
    if not direction:
        direction = polygon_tools.get_road_direction_from_coordinates(
            geometry.get('coordinates'))
    if not direction:
        return None
    core_details['direction'] = direction

    # Relationship
    core_details['relationship'] = {}

    # description
    core_details['description'] = header.get('description')

    # creation_date
    core_details['creation_date'] = date_tools.get_iso_string_from_unix(
        source.get('creation_timestamp'))

    # update_date
    core_details['update_date'] = date_tools.get_iso_string_from_unix(
        source.get('last_updated_timestamp'))

    properties['core_details'] = core_details

    properties['lanes'] = additional_info.get('lanes', [])

    # restrictions
    properties['restrictions'] = additional_info.get('restrictions', [])

    filtered_properties = copy.deepcopy(properties)

    for key, value in properties.items():
        if not value and key not in ['road_event_id', 'data_source_id']:
            del filtered_properties[key]

    feature = {}
    feature['type'] = "Feature"
    feature['properties'] = filtered_properties
    feature['geometry'] = geometry
    feature['id'] = event.get('source', {}).get('id', uuid.uuid4())
    print(feature)

    return feature


# Parse Icone Incident to WZDx
def parse_work_zone(incident):
    if not incident or type(incident) != dict:
        return None

    event = incident.get('event')

    source = event.get('source')
    header = event.get('header')
    detail = event.get('detail')
    additional_info = event.get('additional_info', {})

    geometry = {}
    geometry['type'] = "LineString"
    geometry['coordinates'] = event.get('geometry')
    properties = {}

    # I included a skeleton of the message, fill out all required fields and as many optional fields as you can. Below is a link to the spec page for a road event
    # https://github.com/usdot-jpo-ode/jpo-wzdx/blob/master/spec-content/objects/RoadEvent.md

    core_details = {}

    # # id
    # # Leave this empty, it will be populated by add_ids_v3
    # core_details['road_event_id'] = ''

    # data_source_id
    # Leave this empty, it will be populated by add_ids_v3
    core_details['data_source_id'] = ''

    # Event Type ['work-zone', 'detour']
    core_details['event_type'] = event.get('type')

    # road_name
    road_names = [detail.get('road_name')]
    core_details['road_names'] = road_names

    # direction
    direction = None
    for road_name in road_names:
        direction = wzdx_translator.parse_direction_from_street_name(road_name)
        if direction:
            break
    if not direction:
        direction = polygon_tools.get_road_direction_from_coordinates(
            geometry.get('coordinates'))
    if not direction:
        return None
    core_details['direction'] = direction

    # Relationship
    core_details['relationship'] = {}

    # description
    core_details['description'] = header.get('description')

    # creation_date
    core_details['creation_date'] = date_tools.get_iso_string_from_unix(
        source.get('creation_timestamp'))

    # update_date
    core_details['update_date'] = date_tools.get_iso_string_from_unix(
        source.get('last_updated_timestamp'))

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

    properties["location_method"] = "channel-device-method"

    # mileposts
    properties['beginning_milepost'] = additional_info.get(
        'beginning_milepost')

    # start_date_accuracy
    properties['ending_milepost'] = additional_info.get('ending_milepost')

    # start_date_accuracy
    properties['start_date_accuracy'] = "estimated"

    # end_date_accuracy
    properties['end_date_accuracy'] = "estimated"

    # beginning_accuracy
    properties['beginning_accuracy'] = "estimated"

    # ending_accuracy
    properties['ending_accuracy'] = "estimated"

    # vehicle impact
    lanes = additional_info.get('lanes', [])
    properties['vehicle_impact'] = get_vehicle_impact(lanes)

    # lanes
    properties['lanes'] = lanes

    # beginning_cross_street
    properties['beginning_cross_street'] = ""

    # beginning_cross_street
    properties['ending_cross_street'] = ""

    # event status
    properties['event_status'] = date_tools.get_event_status(
        start_time, end_time)

    # type_of_work
    # maintenance, minor-road-defect-repair, roadside-work, overhead-work, below-road-work, barrier-work, surface-work, painting, roadway-relocation, roadway-creation
    properties['types_of_work'] = event.get('types_of_work', [])

    # restrictions
    properties['restrictions'] = additional_info.get('restrictions', [])

    filtered_properties = copy.deepcopy(properties)

    for key, value in properties.items():
        if not value and key not in ['road_event_id', 'data_source_id', 'end_date']:
            del filtered_properties[key]

    feature = {}
    feature['type'] = "Feature"
    feature['properties'] = filtered_properties
    feature['geometry'] = geometry
    feature['id'] = event.get('source', {}).get('id', uuid.uuid4())
    print(feature)

    return feature


if __name__ == "__main__":
    main()

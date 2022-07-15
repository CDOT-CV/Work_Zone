
import argparse
import json
import logging
import copy
import uuid
import datetime

from wzdx.sample_files.validation_schema import wzdx_v40_feed, road_restriction_v40_feed

from wzdx.tools import date_tools, wzdx_translator

PROGRAM_NAME = 'PlannedEventsTranslator'
PROGRAM_VERSION = '1.0'


DEFAULT_PLANNED_EVENTS_FEED_INFO_ID = '49253be7-0c6a-4a65-8113-450f9041f989'


def main():
    input_file, output_file = parse_planned_events_arguments()

    planned_events_obj = json.loads(open(input_file, 'r').read())
    wzdx = wzdx_creator(planned_events_obj)
    try:
        event_type = wzdx['features'][0]['properties']['core_details']['event_type']
    except:
        event_type = 'work-zone'
    schemas = {
        'work-zone': wzdx_v40_feed.wzdx_v40_schema_string,
        'restriction': road_restriction_v40_feed.road_restriction_v40_schema_string
    }

    if not wzdx_translator.validate_wzdx(wzdx, schemas[event_type]):
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
    event_type = message['event']['type']

    # verify info obj
    if not info:
        info = wzdx_translator.initialize_info(
            DEFAULT_PLANNED_EVENTS_FEED_INFO_ID)
    if not wzdx_translator.validate_info(info):
        return None

    if event_type == 'work-zone':
        wzd = wzdx_translator.initialize_wzdx_object_v4(info)
        feature = parse_work_zone(message)
    elif event_type == 'restriction':
        wzd = wzdx_translator.initialize_wzdx_object_restriction(info)
        feature = parse_road_restriction(message)
    else:
        logging.warning(f"Unrecognized event type: {message['event']['type']}")
        return None

    if feature:
        wzd.get('features', []).append(feature)
    if not wzd.get('features'):
        return None

    wzd = wzdx_translator.add_ids_v4(wzd, event_type)
    return wzd


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
    core_details['direction'] = detail.get('direction')

    # Relationship
    core_details['relationship'] = {}

    # description
    core_details['description'] = header.get('description')

    # # creation_date
    # core_details['creation_date'] = date_tools.get_iso_string_from_unix(
    #     source.get('creation_timestamp'))

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
    properties = wzdx_translator.initialize_feature_properties()

    # I included a skeleton of the message, fill out all required fields and as many optional fields as you can. Below is a link to the spec page for a road event
    # https://github.com/usdot-jpo-ode/jpo-wzdx/blob/master/spec-content/objects/RoadEvent.md

    core_details = properties['core_details']

    # Event Type ['work-zone', 'detour']
    core_details['event_type'] = event.get('type')

    # road_name
    road_names = [detail.get('road_name')]
    core_details['road_names'] = road_names

    # direction
    core_details['direction'] = detail.get('direction')

    # description
    core_details['description'] = header.get('description')

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
    if not end_time:
        if start_time > datetime.datetime.utcnow():
            end_time = start_time + datetime.timedelta(days=7)
        else:
            end_time = datetime.datetime.utcnow() + datetime.timedelta(days=7)
    properties['end_date'] = date_tools.get_iso_string_from_datetime(end_time)

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

    return feature


if __name__ == "__main__":
    main()

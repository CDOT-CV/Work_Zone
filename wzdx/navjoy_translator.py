import argparse
import copy
import json
import logging
from collections import OrderedDict
from datetime import datetime

from wzdx.tools import array_tools, date_tools, polygon_tools, wzdx_translator

PROGRAM_NAME = 'NavJoy568Translator'
PROGRAM_VERSION = '1.0'

DEFAULT_NAVJOY_FEED_INFO_ID = '2ed141dc-b998-4f7a-8395-9ae9dc7df2f8'


def main():
    inputfile, outputfile = parse_navjoy_arguments()
    try:
        navjoy_obj = json.loads(open(inputfile).read())
    except ValueError as e:
        raise ValueError(
            'Invalid file type. Please specify a valid Json file!') from None
    wzdx_obj = wzdx_creator(navjoy_obj)

    location_schema = 'wzdx/sample_files/validation_schema/wzdx_v3.1_feed.json'
    wzdx_schema = json.loads(open(location_schema).read())

    if not wzdx_translator.validate_wzdx(wzdx_obj, wzdx_schema):
        logging.error(
            'validation error more message are printed above. output file is not created because the message failed validation.')
        return
    with open(outputfile, 'w') as fwzdx:
        fwzdx.write(json.dumps(wzdx_obj, indent=2))
        print(
            'Your wzdx message was successfully generated and is located here: ' + str(outputfile))


# parse script command line arguments
def parse_navjoy_arguments():
    parser = argparse.ArgumentParser(
        description='Translate iCone data to WZDx')
    parser.add_argument('--version', action='version',
                        version=f'{PROGRAM_NAME} {PROGRAM_VERSION}')
    parser.add_argument('navjoyFile', help='navjoy file path')
    parser.add_argument('--outputFile', required=False,
                        default='navjoy_wzdx_translated_output_message.geojson', help='output file path')

    args = parser.parse_args()
    return args.navjoyFile, args.outputFile


def wzdx_creator(message, info=None):
    if not message:
        return None
   # verify info obj
    if not info:
        info = wzdx_translator.initialize_info(DEFAULT_NAVJOY_FEED_INFO_ID)
    if not wzdx_translator.validate_info(info):
        return None

    wzd = wzdx_translator.initialize_wzdx_object(info)

    feature = parse_reduction_zone(message)
    if feature:
        wzd.get('features').append(feature)

    if not wzd.get('features'):
        return None
    wzd = wzdx_translator.add_ids(wzd)
    return wzd


# Parse standard Navjoy 568 form to WZDx
def parse_reduction_zone(incident):

    event = incident.get('event')

    source = event.get('source')
    header = event.get('header')
    detail = event.get('detail')

    geometry = {}
    geometry['type'] = "LineString"
    geometry['coordinates'] = event.get('geometry')
    properties = {}

    # id
    # Leave this empty, it will be populated by add_ids
    properties['road_event_id'] = ''

    # Event Type ['work-zone', 'detour']
    properties['event_type'] = 'work-zone'

    # data_source_id
    # Leave this empty, it will be populated by add_ids
    properties['data_source_id'] = ''

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
        properties['end_date'] = ''

    # start_date_accuracy
    properties['start_date_accuracy'] = "estimated"

    # end_date_accuracy
    properties['end_date_accuracy'] = "estimated"

    # beginning_accuracy
    properties['beginning_accuracy'] = "estimated"

    # ending_accuracy
    properties['ending_accuracy'] = "estimated"

    # road_name
    road_names = [detail.get('road_name')]
    properties['road_names'] = road_names

    # direction
    properties['direction'] = detail.get('direction')

    # vehicle impact
    properties['vehicle_impact'] = get_vehicle_impact(
        header.get('justification'))

    # Relationship
    properties['relationship'] = {}

    # lanes
    properties['lanes'] = []

    # beginning_cross_street
    properties['beginning_cross_street'] = ""

    # beginning_cross_street
    properties['ending_cross_street'] = ""

    # event status
    properties['event_status'] = date_tools.get_event_status(
        start_time, end_time)

    # type_of_work
    # maintenance, minor-road-defect-repair, roadside-work, overhead-work, below-road-work, barrier-work, surface-work, painting, roadway-relocation, roadway-creation
    projectDescription = header.get('description')
    types_of_work = get_types_of_work(projectDescription)
    if types_of_work:
        properties['types_of_work'] = types_of_work

    # restrictions
    properties['restrictions'] = []

    # description
    properties['description'] = header.get(
        'description', '') + '. ' + header.get('justification', '')

    # creation_date
    properties['creation_date'] = date_tools.get_iso_string_from_datetime(date_tools.parse_datetime_from_unix(
        incident.get('rtdh_timestamp')))

    # update_date
    properties['update_date'] = date_tools.get_iso_string_from_datetime(date_tools.parse_datetime_from_unix(
        source.get('last_updated_timestamp')))

    feature = {}
    feature['type'] = "Feature"
    feature['properties'] = properties
    feature['geometry'] = geometry

    return feature


# function to calculate vehicle impact
def get_vehicle_impact(travelRestriction):
    if not travelRestriction or type(travelRestriction) != str:
        return None
    travelRestriction = travelRestriction.lower()
    vehicle_impact = 'all-lanes-open'
    if 'lane closure' in travelRestriction.lower():
        vehicle_impact = 'some-lanes-closed'
    elif 'all lanes closed' in travelRestriction.lower():
        vehicle_impact = 'all-lanes-closed'

    return vehicle_impact


# TODO: Support more types of work
def get_types_of_work(field):
    if not field or type(field) != str:
        return None
    field = field.lower()
    # valid_types_of_work = ['maintenance',
    #                        'minor-road-defect-repair',
    #                        'roadside-work',
    #                        'overhead-work',
    #                        'below-road-work',
    #                        'barrier-work',
    #                        'surface-work',
    #                        'painting',
    #                        'roadway-relocation',
    #                        'roadway-creation']

    if not field or type(field) != str:
        return []

    types_of_work = []

    if 'crack seal' in field:
        types_of_work.append({'type_name': 'minor-road-defect-repair',
                              'is_architectural_change': False})
    if 'restriping' in field:
        types_of_work.append({'type_name': 'painting',
                              'is_architectural_change': False})
    if 'repaving' in field:
        types_of_work.append({'type_name': 'surface-work',
                              'is_architectural_change': False})
    if 'bridge' in field:
        types_of_work.append({'type_name': 'below-road-work',
                              'is_architectural_change': False})
    if 'traffic signal' in field:
        types_of_work.append({'type_name': 'overhead-work',
                              'is_architectural_change': False})
    if 'lane expansion' in field:
        types_of_work.append({'type_name': 'surface-work',
                              'is_architectural_change': True})

    return types_of_work


if __name__ == "__main__":
    main()

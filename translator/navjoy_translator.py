import argparse
import copy
import json
import logging
import re
import sys
from collections import OrderedDict
from datetime import datetime, timedelta, timezone

from translator.tools import wzdx_translator, polygon_to_line, date_tools

PROGRAM_NAME = 'NavJoyTranslator'
PROGRAM_VERSION = '1.0'


def main():
    inputfile, outputfile = parse_navjoy_arguments()
    try:
        navjoy_obj = json.loads(open(inputfile).read())
    except ValueError as e:
        raise ValueError(
            'Invalid file type. Please specify a valid Json file!') from None
    wzdx_obj = wzdx_creator(navjoy_obj)
    location_schema = 'translator/sample files/validation_schema/wzdx_v3.1_feed.json'
    wzdx_schema = json.loads(open(location_schema).read())

    if not wzdx_translator.validate_wzdx(wzdx_obj, wzdx_schema):
        print('validation error more message are printed above. output file is not created because the message failed validation.')
        return
    with open(outputfile, 'w') as fwzdx:
        fwzdx.write(json.dumps(wzdx_obj, indent=2))
        print(
            'huraaah ! your wzdx message is successfully generated and located here: ' + str(outputfile))


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


def wzdx_creator(messages, info=None, unsupported_message_callback=None):
    if not messages:
        return None
   # verify info obj
    if not info:
        info = wzdx_translator.initialize_info(
            '8d062f70-d53e-4029-b94e-b7fbcbde5885')
    if not wzdx_translator.validate_info(info):
        return None

    wzd = wzdx_translator.initialize_wzdx_object(info)

    for message in messages:
        # Parse closure to WZDx Feature
        feature = parse_closure(
            message, callback_function=unsupported_message_callback)
        if feature:
            wzd.get('features').append(feature)
    if not wzd.get('features'):
        return None
    wzd = wzdx_translator.add_ids(wzd)
    return wzd


# function to parse polyline to geometry line string
def parse_polyline(poly):
    if not poly or type(poly) != str:
        return None
    poly = poly[len('LINESTRING ('): -1]
    polyline = poly.split(', ')
    coordinates = []
    for i in polyline:
        coords = i.split(' ')

        # the regular rexpression '^-?([0-9]*[.])?[0-9]+$ matches an integer or decimals
        if len(coords) >= 2 and re.match('^-?([0-9]*[.])?[0-9]+$', coords[0]) and re.match('^-?([0-9]*[.])?[0-9]+$', coords[1]):
            coordinates.append([float(coords[0]), float(coords[1])])
    return coordinates

# function to get event status


def get_event_status(start_time_string, end_time_string):

    start_time = datetime.fromtimestamp(start_time_string)
    current_time = datetime.now()
    future_date_after_2weeks = current_time + \
        timedelta(days=14)
    event_status = "active"
    if current_time < start_time:
        if start_time < future_date_after_2weeks:
            event_status = "pending"
        else:
            event_status = "planned"

    elif end_time_string:
        end_time = datetime.fromtimestamp(end_time_string)
        if end_time < current_time:
            event_status = "completed"
    return event_status


# Parse Navjoy  to WZDx
def parse_closure(obj, callback_function=None):
    if not validate_alert(obj):
        if callback_function:
            callback_function(obj)
        return None

    event = obj.get('event', {})
    geometry = {}
    geometry['type'] = "LineString"
    geometry['coordinates'] = parse_polyline(event.get('geometry'))
    properties = wzdx_translator.initialize_feature_properties()

    # Event Type ['work-zone', 'detour']
    properties['event_type'] = 'work-zone'

    # start_date
    actual_start_date = event.get('data').get('actualStartDate')
    planned_start_date = event.get('data').get('plannedStartDate')
    properties['start_date'] = actual_start_date
    if not actual_start_date:
        properties['start_date'] = planned_start_date
        properties['start_date_accuracy'] = "estimated"

    # end_date
    actual_end_date = event.get('data').get('actualEndDate')
    planned_end_date = event.get('data').get('plannedEndDate')
    properties['end_date'] = actual_end_date
    if not actual_start_date:
        properties['end_date'] = planned_start_date
        properties['end_date_accuracy'] = "estimated"

    # start_date_accuracy
    properties['start_date_accuracy'] = "verified"

    # end_date_accuracy
    properties['end_date_accuracy'] = "verified"

    # beginning_accuracy
    properties['beginning_accuracy'] = "estimated"

    # ending_accuracy
    properties['ending_accuracy'] = "estimated"

    # road_name
    properties['road_names'] = [event.get('data').get('routeName')]
    road_number = event.get('data').get('routeName')
    if road_number and not road_number in properties['road_names']:
        properties['road_names'].append(road_number)

    # direction
    properties['direction'] = get_direction_from_routeName(routeName)

    # vehicle impact
    properties['vehicle_impact'] = get_vehicle_impact(
        event.get('data').get('travelRestriction'))

    # event status
    properties['event_status'] = event.get('data').get('closureStatus')

    # type_of_work
    # maintenance, minor-road-defect-repair, roadside-work, overhead-work, below-road-work, barrier-work, surface-work, painting, roadway-relocation, roadway-creation
    works = event.get('sub_type')
    types_of_work = get_types_of_work(works)
    if types_of_work:
        properties['types_of_work'] = types_of_work

    # reduced_speed_limit
    properties['reduced_speed_limit'] = get_rsz_from_event(event)

    # restrictions
    work_updates = event.get('detail').get('work_updates')
    restrictions = get_restrictions(work_updates)
    if restrictions:
        properties['restrictions'] = restrictions

    # description
    properties['description'] = event.get('data').get('description')

    # creation_date
    properties['creation_date'] = date_tools.reformat_datetime(
        event.get('source').get('collection_timestamp'))

    # update_date
    properties['update_date'] = date_tools.reformat_datetime(
        obj.get('rtdh_timestamp'))

    filtered_properties = copy.deepcopy(properties)

    for key, value in properties.items():
        if value == None and key not in ['road_event_id', 'data_source_id']:
            del filtered_properties[key]

    feature = {}
    feature['type'] = "Feature"
    feature['properties'] = filtered_properties
    feature['geometry'] = geometry

    return feature


# function to validate the alert
def validate_alert(obj):

    if not obj or (type(obj) != dict and type(obj) != OrderedDict):
        logging.warning('alert is empty or has invalid type')
        return False

    data = obj.get('data', {})
    street = data.get('routeName')

    workPlan = data.get('ConstructionWorkZonePlan', [{}])
    if type(workPlan) != list or len(workPlan) == 0:
        logging.warning(
            f'Invalid event with event id = {obj.get("sys_gUid")}. ConstructionWorkZonePlan object is either invalid or empty')

    polygon = workPlan[0].get('coordinates', [])[0]
    print(polygon)
    polyline = polygon_to_line.polygon_to_polyline(polygon)
    print(polyline)

    starttime = data.get('plannedStartDate')
    endtime = data.get('plannedEndDate', 'invalid datetime')

    description = data.get('description')
    direction = None
    # direction = data.get('detail', {}).get('direction')

    if not polyline:
        logging.warning(
            f'Invalid event with event id = {obj.get("sys_gUid")}. Unable to retrieve centerline from polygon')
        return False

    required_fields = [street, starttime, description, direction]
    for field in required_fields:
        if not field:
            logging.warning(
                f'Invalid event with event id = {obj.get("sys_gUid")}. not all required fields are present')
            return False

    try:
        datetime.strptime(starttime, "%Y-%m-%dT%H:%M:%SZ")
        if endtime:
            datetime.strptime(endtime, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        logging.warning(
            f'Invalid incident with id = {obj.get("sys_gUid")}. Invalid date time format')
        return False

    return True


# function to calculate vehicle impact
def get_vehicle_impact(travelRestriction):
    vehicle_impact = 'all-lanes-open'
    if 'right' in travelRestriction.lower():
        vehicle_impact = 'some-lanes-closed'
    elif 'all' in travelRestriction.lower():
        vehicle_impact = 'all-lanes-closed'

    return vehicle_impact


def get_types_of_work(constructionType):
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

    if not constructionType or type(constructionType) != str:
        return []

    types_of_work = []

    if constructionType == 'Lane Expansion':
        types_of_work.append({'type_name': 'surface-work',
                              'is_architectural_change': True})
    elif constructionType == 'Traffic Signal Installation':
        types_of_work.append({'type_name': 'overhead-work',
                              'is_architectural_change': False})
    elif constructionType == 'Median Work':
        types_of_work.append({'type_name': 'surface-work',
                              'is_architectural_change': False})
    elif constructionType == 'Road':
        types_of_work.append({'type_name': 'minor-road-defect-repair',
                              'is_architectural_change': False})
    elif constructionType == 'Bridge':
        types_of_work.append({'type_name': 'below-road-work',
                              'is_architectural_change': False})
    elif constructionType == 'Underground':
        types_of_work.append({'type_name': 'below-road-work',
                              'is_architectural_change': False})
    elif constructionType == 'Sidewalk':
        types_of_work.append({'type_name': 'roadside-work',
                              'is_architectural_change': False})
    elif constructionType == 'Other':
        pass
    return types_of_work


if __name__ == "__main__":
    main()

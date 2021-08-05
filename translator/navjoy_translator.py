import argparse
import copy
import json
import logging
import re
import sys
from collections import OrderedDict
from datetime import datetime, timedelta, timezone

from translator.tools import wzdx_translator, date_tools, polygon_tools

PROGRAM_NAME = 'NavJoy568Translator'
PROGRAM_VERSION = '1.0'

STRING_DIRECTION_MAP = {'north': 'northbound', 'south': 'southbound',
                        'west': 'westbound', 'east': 'eastbound'}

REVERSED_DIRECTION_MAP = {'northbound': 'southbound', 'southbound': 'northbound',
                          'eastbound': 'westbound', 'westbound': 'eastbound'}


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
        # closures can cover both directions
        directions = message.get('data', {}).get('directionOfTraffic')

        for direction in get_directions_from_string(directions):
            # Parse closure to WZDx Feature
            feature = parse_reduction_zone(
                copy.deepcopy(message), direction, callback_function=unsupported_message_callback)
            if feature:
                wzd.get('features').append(feature)
    if not wzd.get('features'):
        return None
    wzd = wzdx_translator.add_ids(wzd)
    return wzd


def get_linestring_index(map):
    for i in range(len(map)):
        if map[i].get("type") == "LineString":
            return i


def get_polygon_index(map):
    for i in range(len(map)):
        if map[i].get("type") == "Polygon":
            return i


def get_directions_from_string(directions_string) -> list:
    if not directions_string or type(directions_string) != str:
        return []

    directions = []

    # iterate over directions and convert short direction names to WZDx enum directions
    directions_string = directions_string.strip()
    for dir in directions_string.split('/'):
        direction = STRING_DIRECTION_MAP.get(dir.lower())
        if direction:
            directions.append(direction)

    return directions


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
def parse_reduction_zone(obj, direction, callback_function=None):
    if not validate_closure(obj):
        if callback_function:
            callback_function(obj)
        return None

    data = obj.get('data', {})

    map = data.get('srzmap')
    index = get_linestring_index(map)
    if index != None:
        coordinates = map[index].get("coordinates")
    else:
        index = get_polygon_index(map)
        if index != None:
            polygon = map[index].get("coordinates")
            coordinates = polygon_tools.polygon_to_polyline_center(polygon)
        else:
            logging.warning(f"Invalid event with id = {obj.get('sys_gUid')}. No polygon or linestring")
            return None

    if not coordinates:
        logging.warning(f"Invalid event with id = {obj.get('sys_gUid')}. Unable to parse linestring from polygon")
        return None

    # [0].get('coordinates')[0]
    # coordinates = polygon_tools.polygon_to_polyline_center(polygon)

    # Reverese polygon if it is in the opposide direction as the message
    polyline_direction = polygon_tools.get_road_direction_from_coordinates(
        coordinates)
    if direction == REVERSED_DIRECTION_MAP.get(polyline_direction):
        coordinates.reverse()

    geometry = {}
    if len(coordinates) > 2:
        geometry['type'] = "LineString"
    else:
        geometry['type'] = "MultiPoint"

    geometry['coordinates'] = coordinates
    properties = wzdx_translator.initialize_feature_properties()

    # Event Type ['work-zone', 'detour']
    properties['event_type'] = 'work-zone'

    # start_date
    start_date = date_tools.parse_datetime_from_iso_string(
        data.get('workStartDate'))
    properties['start_date'] = date_tools.get_iso_string_from_datetime(
        start_date)

    # end_date
    end_date = date_tools.parse_datetime_from_unix(data.get('workEndDate'))
    if end_date:
        properties['end_date'] = date_tools.get_iso_string_from_datetime(
            end_date)
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
    properties['road_names'] = [data.get('streetNameFrom')]

    # direction
    properties['direction'] = direction

    # vehicle impact
    properties['vehicle_impact'] = get_vehicle_impact(
        data.get('reductionJustification'))

    # event status
    properties['event_status'] = wzdx_translator.get_event_status(
        start_date, end_date)

    # type_of_work
    # maintenance, minor-road-defect-repair, roadside-work, overhead-work, below-road-work, barrier-work, surface-work, painting, roadway-relocation, roadway-creation
    projectDescription = data.get('descriptionForProject')
    types_of_work = get_types_of_work(projectDescription)
    if types_of_work:
        properties['types_of_work'] = types_of_work

    # reduced_speed_limit
    reducedSpeed = data.get('requestedTemporarySpeed')
    if reducedSpeed:
        properties['reduced_speed_limit'] = wzdx_translator.string_to_number(
            reducedSpeed)

    # restrictions
    reductionJustification = data.get('reductionJustification')
    restrictions = get_restrictions(reductionJustification)
    if restrictions:
        properties['restrictions'] = restrictions

    # description
    properties['description'] = reductionJustification

    # creation_date
    properties['creation_date'] = date_tools.get_iso_string_from_datetime(
        datetime.utcnow())

    # update_date
    properties['update_date'] = date_tools.get_iso_string_from_datetime(
        datetime.utcnow())

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
def validate_closure(obj):
    if not obj or (type(obj) != dict and type(obj) != OrderedDict):
        logging.warning('alert is empty or has invalid type')
        return False

    id = obj.get("sys_gUid")

    data = obj.get('data', {})
    street = data.get('streetNameFrom')

    map = data.get('srzmap', [{}])
    if type(map) != list or len(map) == 0:
        logging.warning(
            f'Invalid event with id = {id}. ConstructionWorkZonePlan object is either invalid or empty')

    index = get_linestring_index(map)
    if index != None:
        coordinates = map[index].get("coordinates")
    else:
        index = get_polygon_index(map)
        if index != None:
            polygon = map[index].get("coordinates")
            coordinates = polygon_tools.polygon_to_polyline_center(polygon)
            if not coordinates:
                logging.warning(
                    "Invalid event with id = {id}. Unable to retrieve centerline from polygon")
        else:
            logging.warning(
                "Invalid event with id = {id}. No LineString or Polygon found")
            return None

    starttime_string = data.get('workStartDate')
    endtime_string = data.get('workEndDate')

    description = data.get('reductionJustification')

    required_fields = [street, starttime_string, description]
    for field in required_fields:
        if not field:
            logging.warning(
                f'Invalid event with id = {id}. not all required fields are present')
            return False

    start_time = date_tools.parse_datetime_from_iso_string(starttime_string)
    end_time = date_tools.parse_datetime_from_iso_string(endtime_string)
    if not start_time:
        logging.error(
            f'Invalid incident with id = {id}. Unsupported start time format: {start_time}')
        return False
    elif endtime_string and not end_time:
        logging.error(
            f'Invalid incident with id = {id}. Unsupported end time format: {end_time}')
        return False

    return True


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

    if 'restriping' in field or 'crack seal' in field:
        types_of_work.append({'type_name': 'surface-work',
                              'is_architectural_change': True})
    return types_of_work


def get_restrictions(travelRestriction):
    if not travelRestriction or type(travelRestriction) != str:
        return None
    travelRestriction = travelRestriction.lower()
    # valid_type_of_restrictions = ['no-trucks',
    #                               'travel-peak-hours-only',
    #                               'hov-3',
    #                               'hov-2',
    #                               'no-parking',
    #                               'reduced-width',
    #                               'reduced-height',
    #                               'reduced-length',
    #                               'reduced-weight',
    #                               'axle-load-limit',
    #                               'gross-weight-limit',
    #                               'towing-prohibited',
    #                               'permitted-oversize-loads-prohibited',
    #                               'local-access-only']

    restrictions = []

    return restrictions


def get_rsz_from_restrictions(travelRestriction):
    match = re.search(
        'expect slower speed limits \([0-9]{2} mph\)', travelRestriction)
    if match:
        speed_limit = match.group(
            0)[len('expect slower speed limits ('):-len(' mph)')]
        return speed_limit


if __name__ == "__main__":
    main()

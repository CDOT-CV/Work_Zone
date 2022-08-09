import argparse
import copy
import json
import logging
import time
import uuid
from collections import OrderedDict

from wzdx.tools import date_tools, polygon_tools, wzdx_translator, cdot_geospatial_api
from wzdx.util.collections import PathDict

PROGRAM_NAME = 'GeotabAvlRawToStandard'
PROGRAM_VERSION = '1.0'

STRING_DIRECTION_MAP = {'north': 'northbound', 'south': 'southbound',
                        'west': 'westbound', 'east': 'eastbound'}

REVERSED_DIRECTION_MAP = {'northbound': 'southbound', 'southbound': 'northbound',
                          'eastbound': 'westbound', 'westbound': 'eastbound'}

DISTANCE_AHEAD = 2


# Look at planned events messages
# Find planned event that links to automated attenuator
#


def main():
    navjoy_file, output_dir = parse_rtdh_arguments()
    input_file_contents = open(navjoy_file, 'r').read()
    generated_messages = generate_standard_messages_from_string(
        input_file_contents)

    generated_files_list = []
    for message in generated_messages:
        output_path = f"{output_dir}/standard_{message['event']['source']['id']}_{round(message['rtdh_timestamp'])}_{message['event']['detail']['direction']}.json"
        open(output_path, 'w+').write(json.dumps(message, indent=2))
        generated_files_list.append(output_path)

    if generated_files_list:
        print(
            f"Successfully generated standard message files: {generated_files_list}")
    else:
        logging.warning(
            "Standard message generation failed. See messages printed above")


# parse script command line arguments
def parse_rtdh_arguments():
    parser = argparse.ArgumentParser(
        description='Translate Planned Event data to RTDH Standard')
    parser.add_argument('--version', action='version',
                        version=f'{PROGRAM_NAME} {PROGRAM_VERSION}')
    parser.add_argument('plannedEventsFile', help='planned event file path')
    parser.add_argument('--outputDir', required=False,
                        default='.').get('', help='output directory')

    args = parser.parse_args()
    return args.plannedEventsFile, args.outputDir


# Break event into
def expand_event_routes(message):

    lat = message.get('avl_location').get('position').get('latitude')
    lng = message.get('avl_location').get('position').get('longitude')
    bearing = message.get('avl_location').get('position').get('bearing')

    routes = get_route_names_and_geometry((lat, lng), bearing, DISTANCE_AHEAD)
    return routes


def generate_rtdh_standard_message_from_raw_single(obj):
    pd = PathDict(obj)
    standard_message = create_rtdh_standard_msg(pd)
    return standard_message


def generate_standard_messages_from_string(input_file_contents):
    raw_messages = generate_raw_messages(input_file_contents)
    standard_messages = []
    for message in raw_messages:
        standard_messages.append(
            generate_rtdh_standard_message_from_raw_single(message))
    return standard_messages


def generate_raw_messages(message_string):
    msg = json.loads(message_string)

    if validate_closure(msg):
        return msg


def map_direction_string(direction_string):
    return STRING_DIRECTION_MAP.get(direction_string)


def get_route_names_and_geometry(lat_lng, bearing, distance_ahead):
    route_info = cdot_geospatial_api.get_route_and_measure(lat_lng, bearing)
    routes_ahead = cdot_geospatial_api.get_routes_ahead(route_info['Route'], route_info['measure'],
                                                        route_info['direction'], distance_ahead)
    return routes_ahead


def get_linestring(geometry):
    if geometry.get('type') == "MultiPoint":
        return geometry['coordinates']
    elif geometry.get('type') == "Polygon":
        return polygon_tools.polygon_to_polyline_center(geometry['coordinates'])
    else:
        return []


def create_rtdh_standard_msg(pd):
    coordinates = get_linestring(pd.get('geometry'))

    direction = pd.get('properties').get('direction', default='unknown')

    beginning_milepost = pd.get('properties').get('startMarker', default='')
    ending_milepost = pd.get('properties').get('endMarker', default='')
    recorded_direction = pd.get('properties').get('recorded_direction')
    if direction == REVERSED_DIRECTION_MAP.get(recorded_direction):
        coordinates.reverse()
        beginning_milepost = pd.get('properties').get('endMarker', default='')
        ending_milepost = pd.get('properties').get('startMarker', default='')

    roadName = wzdx_translator.remove_direction_from_street_name(
        pd.get('properties').get('routeName'))

    start_date = pd.get('properties').get('startTime',
                                          date_tools.parse_datetime_from_iso_string)
    end_date = pd.get('properties').get('clearTime',
                                        date_tools.parse_datetime_from_iso_string)

    event_type = 'work-zone'
    types_of_work = [{'type_name': 'roadside-work',
                      'is_architectural_change': False}]

    restrictions = []
    if pd.get('properties').get('isOversizedLoadsProhibited'):
        restrictions.append({'type': 'permitted-oversize-loads-prohibited'})

    return {
        "rtdh_timestamp": time.time(),
        "rtdh_message_id": str(uuid.uuid4()),
        "event": {
            "type": event_type,
            "types_of_work": types_of_work,
            "source": {
                "id": pd.get('properties').get('id', default="") + '_' + direction,
                "creation_timestamp": pd.get("properties').get('startTime", date_tools.get_unix_from_iso_string, default=0),
                "last_updated_timestamp": pd.get('properties').get('lastUpdated', date_tools.get_unix_from_iso_string, default=0),
            },
            "geometry": coordinates,
            "header": {
                "description": pd.get("properties').get('travelerInformationMessage", default=""),
                "start_timestamp": date_tools.date_to_unix(start_date),
                "end_timestamp": date_tools.date_to_unix(end_date),
            },
            "detail": {
                "road_name": roadName,
                "road_number": roadName,
                "direction": direction,
            },
            "additional_info": {
                # "lanes": get_lane_impacts(pd.get("properties').get('laneImpacts"), pd.get("properties').get('direction")),
                "restrictions": restrictions,
                "beginning_milepost": beginning_milepost,
                "ending_milepost": ending_milepost,
                "vehicle_id1": 'stuff',
                "vehicle_id2": 'stuff',
            }
        }
    }


def validate_closure(obj):
    if not obj or (type(obj) != dict and type(obj) != OrderedDict):
        logging.warning('alert is empty or has invalid type')
        return False
    id = obj.get("sys_gUid")
    try:

        properties = obj.get('properties', {})

        coordinates = get_linestring(obj.get('geometry'))
        if not coordinates:
            logging.warning(
                f"Invalid event with id = {obj.get('sys_gUid')}. No valid coordinates found")
            return False

        starttime_string = properties.get('startTime')
        endtime_string = properties.get('clearTime')
        description = properties.get('travelerInformationMessage')
        direction = properties.get('direction')

        required_fields = [starttime_string, description, direction]
        for field in required_fields:
            if not field:
                logging.warning(
                    f'''Invalid event with id = {id}. not all required fields are present. Required fields are: 
                    streetNameFrom, workStartDate, and descriptionForProject''')
                return False

        start_time = date_tools.parse_datetime_from_iso_string(
            starttime_string)
        end_time = date_tools.parse_datetime_from_iso_string(endtime_string)
        if not start_time:
            logging.error(
                f'Invalid incident with id = {id}. Unsupported start time format: {start_time}')
            return False
        elif endtime_string and not end_time:
            logging.error(
                f'Invalid incident with id = {id}. Unsupported end time format: {end_time}')
            return False
    except Exception as e:
        logging.error(
            f"Invalid event with id = {id}. Error occured while validating: {e}")
        return False

    return True


if __name__ == "__main__":
    main()

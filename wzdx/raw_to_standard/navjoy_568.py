from collections import OrderedDict
import json
import time
import uuid
import argparse
import logging
import copy
from datetime import datetime

from wzdx.tools import polygon_tools, date_tools, array_tools

from wzdx.util.transformations import rfc_to_unix
from wzdx.util.transformations import int_or_none
from wzdx.util.transformations import to_dict
from wzdx.util.collections import PathDict

PROGRAM_NAME = 'Navjoy568RawToStandard'
PROGRAM_VERSION = '1.0'

STRING_DIRECTION_MAP = {'north': 'northbound', 'south': 'southbound',
                        'west': 'westbound', 'east': 'eastbound'}

REVERSED_DIRECTION_MAP = {'northbound': 'southbound', 'southbound': 'northbound',
                          'eastbound': 'westbound', 'westbound': 'eastbound'}

CORRECT_KEY_NAMES = {
    'street_name': 'streetNameFrom',
    'mile_marker_start': 'mileMarkerStart',
    'mile_marker_end': 'mileMarkerEnd',
    'directions_of_traffic': 'directionOfTraffic',
    'current_posted_speed': 'currentPostedSpeed',
    'reduced_speed_limit': 'requestedTemporarySpeed',
    'start_date': 'workStartDate',
    'end_date': 'workEndDate',
}

NUMBERED_KEY_NAMES = [
    {
        'street_name': 'streetNameFrom',
        'mile_marker_start': 'mileMarkerStart',
        'mile_marker_end': 'mileMarkerEnd',
        'directions_of_traffic': 'directionOfTraffic',
        'current_posted_speed': 'currentPostedSpeed',
        'reduced_speed_limit': 'requestedTemporarySpeed',
        'start_date': 'workStartDate',
        'end_date': 'workEndDate',
    },
    {
        'street_name': 'streetNameFrom2',
        'mile_marker_start': 'mileMarkerStart2',
        'mile_marker_end': 'mileMarkerEnd2',
        'directions_of_traffic': 'directionOfTraffic2',
        'current_posted_speed': 'currentPostedSpeed2',
        'reduced_speed_limit': 'requestedTemporarySpeed2',
        'start_date': 'workStartDate2',
        'end_date': 'workEndDate2',
    },
    {
        'street_name': 'streetNameFrom3',
        'mile_marker_start': 'mileMarkerStart3',
        'mile_marker_end': 'mileMarkerEnd3',
        'directions_of_traffic': 'directionOfTraffic3',
        'current_posted_speed': 'currentPostedSpeed3',
        'reduced_speed_limit': 'requestedTemporarySpeed3',
        'start_date': 'workStartDate3',
        'end_date': 'workEndDate3',
    },
    {
        'street_name': 'streetNameFrom4',
        'mile_marker_start': 'mileMarkerStart4',
        'mile_marker_end': 'mileMarkerEnd4',
        'directions_of_traffic': 'directionOfTraffic4',
        'current_posted_speed': 'currentPostedSpeed4',
        'reduced_speed_limit': 'requestedTemporarySpeed4',
        'start_date': 'workStartDate4',
        'end_date': 'workEndDate4',
    }
]


def main():
    navjoy_file, output_dir = parse_rtdh_arguments()
    input_file_contents = open(navjoy_file, 'r').read()
    generated_messages = generate_standard_messages_from_string(
        input_file_contents)

    generated_files_list = []
    for message in generated_messages:
        output_path = f"{output_dir}/standard_568_{message['event']['source']['id']}_{round(message['rtdh_timestamp'])}.json"
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
        description='Translate NavJoy 568 data to RTDH Standard')
    parser.add_argument('--version', action='version',
                        version=f'{PROGRAM_NAME} {PROGRAM_VERSION}')
    parser.add_argument('navjoyFile', help='navjoy file path')
    parser.add_argument('--outputDir', required=False,
                        default='./', help='output directory')

    args = parser.parse_args()
    return args.navjoyFile, args.outputDir


# take in individual message, spit out list of altered unique messages to be translated
# This function iterates over the list of NUMBERED_KEY_NAMES and correlates them to CORRECT_KEY_NAMES. For each
# set of numbered key names, generate a copy of the original message, check if the numbered keys exist, if they do
# then copy those values to the leys in CORRECT_KEY_NAMES. After, if directionOfTraffic yields more than one direction,
# generate a new message for each direction and save them with the key 'direction'

# TODO: consider deleting all numbered keys after they are copied
# TODO: consider removing duplicate messages
def expand_speed_zone(message):
    messages = []
    for key_set in NUMBERED_KEY_NAMES:
        # print(key_set)
        if not message.get('data', {}).get(key_set['street_name']):
            # print(key_set['street_name'])
            # # print(message.get('data', {}))
            # print("EXITING")
            continue
        new_message = copy.deepcopy(message)
        for key, value in key_set.items():
            new_message.get('data', {})[CORRECT_KEY_NAMES[key]] = message.get(
                'data', {}).get(value)

        directions = new_message.get('data', {}).get('directionOfTraffic')
        for direction in get_directions_from_string(directions):
            new_message_dir = copy.deepcopy(new_message)
            if new_message_dir.get('data', {}).get('directionOfTraffic'):
                del new_message_dir.get('data', {})['directionOfTraffic']
            new_message_dir.get('data', {})['direction'] = direction
            messages.append(new_message_dir)
    return messages


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


def generate_standard_messages_from_string(input_file_contents):
    raw_messages = generate_raw_messages(input_file_contents)
    standard_messages = []
    for message in raw_messages:
        standard_messages.append(
            generate_rtdh_standard_message_from_raw_single(message))
    return standard_messages


def generate_raw_messages(message_string, invalid_messages_callback=None):
    msg_lst = json.loads(message_string)
    messages = []

    # Loop through all elements and print each element to PubSub
    for obj in msg_lst:
        separated_messages = expand_speed_zone(obj)
        for msg in separated_messages:
            if not validate_closure(msg):
                if invalid_messages_callback:
                    invalid_messages_callback(msg)
            else:
                messages.append(msg)

    return messages


def generate_rtdh_standard_message_from_raw_single(obj):
    pd = PathDict(obj)
    standard_message = create_rtdh_standard_msg(pd)
    return standard_message


def get_linestring_index(map):
    for i in range(len(map)):
        if map[i].get("type") == "LineString":
            return i


def get_polygon_index(map):
    for i in range(len(map)):
        if map[i].get("type") == "Polygon":
            return i


def create_rtdh_standard_msg(pd):
    map = pd.get("data/srzmap", default=[])
    index = get_linestring_index(map)
    if index != None:
        coordinates = map[index].get("coordinates")
        coordinates = array_tools.get_2d_list(coordinates)
    else:
        index = get_polygon_index(map)
        if index != None:
            polygon = map[index].get("coordinates")
            coordinates = array_tools.get_2d_list(polygon)
            if coordinates:
                coordinates = polygon_tools.polygon_to_polyline_center(
                    coordinates)

    direction = pd.get("data/direction", default='unknown')

    # Reverse polygon if it is in the opposite direction as the message
    polyline_direction = polygon_tools.get_road_direction_from_coordinates(
        coordinates)
    if direction == REVERSED_DIRECTION_MAP.get(polyline_direction):
        coordinates.reverse()

    start_date = pd.get("data/workStartDate",
                        date_tools.parse_datetime_from_iso_string)
    end_date = pd.get("data/workStartDate",
                      date_tools.parse_datetime_from_iso_string)

    return {
        "rtdh_timestamp": time.time(),
        "rtdh_message_id": str(uuid.uuid4()),
        "event": {
            "type": pd.get("data/constructionType", default=""),
            "source": {
                "id": pd.get("sys_gUid", default=""),
                "last_updated_timestamp": time.time(),
            },
            "geometry": coordinates,
            "header": {
                "description": pd.get("data/descriptionForProject", default=""),
                "justification": pd.get("data/reductionJustification"),
                "start_timestamp": date_tools.date_to_unix(start_date),
                "end_timestamp": date_tools.date_to_unix(end_date),
            },
            "detail": {
                "road_name": pd.get("data/streetNameFrom"),
                "road_number": pd.get("data/streetNameFrom"),
                "direction": direction,
            },
            # "additional_info": [
            #
            # ]
        }
    }


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

    # TODO: Support MultiPoint
    index = get_linestring_index(map)
    if index != None:
        coordinates = map[index].get("coordinates", [None])[0]
    else:
        index = get_polygon_index(map)
        if index != None:
            polygon = map[index].get("coordinates", [None])[0]
            coordinates = polygon_tools.polygon_to_polyline_center(polygon)
        else:
            logging.warning(
                f"Invalid event with id = {id}. No LineString or Polygon found")
            return False

    if not coordinates:
        logging.warning(
            f"Invalid event with id = {obj.get('sys_gUid')}. No valid coordinates found")
        return False

    starttime_string = data.get('workStartDate')
    endtime_string = data.get('workEndDate')
    description = data.get('descriptionForProject')
    direction = data.get('direction')

    required_fields = [street, starttime_string, description, direction]
    for field in required_fields:
        if not field:
            logging.warning(
                f'''Invalid event with id = {id}. not all required fields are present. Required fields are: 
                streetNameFrom, workStartDate, and descriptionForProject''')
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


if __name__ == "__main__":
    main()

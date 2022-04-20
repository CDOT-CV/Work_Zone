import argparse
import copy
import json
import logging
import time
import uuid
from collections import OrderedDict

from wzdx.tools import date_tools, polygon_tools, wzdx_translator
from wzdx.util.collections import PathDict

PROGRAM_NAME = 'GeotabAvlRawToStandard'
PROGRAM_VERSION = '1.0'

STRING_DIRECTION_MAP = {'north': 'northbound', 'south': 'southbound',
                        'west': 'westbound', 'east': 'eastbound'}

REVERSED_DIRECTION_MAP = {'northbound': 'southbound', 'southbound': 'northbound',
                          'eastbound': 'westbound', 'westbound': 'eastbound'}


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
                        default='./', help='output directory')

    args = parser.parse_args()
    return args.plannedEventsFile, args.outputDir


def generate_standard_messages_from_string(input_file_contents):
    raw_messages = generate_raw_messages(input_file_contents)
    standard_messages = []
    for message in raw_messages:
        standard_messages.append(
            generate_rtdh_standard_message_from_raw_single(message))
    return standard_messages


def generate_raw_messages(message_string):
    msg = json.loads(message_string)
    messages = []

    separated_messages = expand_event_directions(msg)
    for indiv_msg in separated_messages:
        if validate_closure(indiv_msg):
            messages.append(indiv_msg)

    return messages


def map_lane_status(lane_status_bit):
    return 'open' if lane_status_bit == '0' else 'closed'


def map_direction_string(direction_string):
    return STRING_DIRECTION_MAP.get(direction_string)


def create_rtdh_standard_msg(pd):
    coordinates = get_linestring(pd.get('geometry', default={'type': None}))

    direction = pd.get("properties/direction", default='unknown')

    beginning_milepost = pd.get("properties/startMarker", default="")
    ending_milepost = pd.get("properties/endMarker", default="")
    recorded_direction = pd.get("properties/recorded_direction")
    if direction == REVERSED_DIRECTION_MAP.get(recorded_direction):
        coordinates.reverse()
        beginning_milepost = pd.get("properties/endMarker", default="")
        ending_milepost = pd.get("properties/startMarker", default="")

    roadName = wzdx_translator.remove_direction_from_street_name(
        pd.get("properties/routeName"))

    start_date = pd.get("properties/startTime",
                        date_tools.parse_datetime_from_iso_string)
    end_date = pd.get("properties/clearTime",
                      date_tools.parse_datetime_from_iso_string)

    event_type, types_of_work = map_event_type(
        pd.get("properties/type", default=""))

    restrictions = []
    if pd.get('properties/isOversizedLoadsProhibited'):
        restrictions.append({'type': 'permitted-oversize-loads-prohibited'})

    return {
        "rtdh_timestamp": time.time(),
        "rtdh_message_id": str(uuid.uuid4()),
        "event": {
            "type": event_type,
            "types_of_work": types_of_work,
            "source": {
                "id": pd.get("properties/id", default="") + '_' + direction,
                "creation_timestamp": pd.get("properties/startTime", date_tools.get_unix_from_iso_string, default=0),
                "last_updated_timestamp": pd.get('properties/lastUpdated', date_tools.get_unix_from_iso_string, default=0),
            },
            "geometry": coordinates,
            "header": {
                "description": pd.get("properties/travelerInformationMessage", default=""),
                "start_timestamp": date_tools.date_to_unix(start_date),
                "end_timestamp": date_tools.date_to_unix(end_date),
            },
            "detail": {
                "road_name": roadName,
                "road_number": roadName,
                "direction": direction,
            },
            "additional_info": {
                "lanes": get_lane_impacts(pd.get("properties/laneImpacts"), pd.get("properties/direction")),
                "restrictions": restrictions,
                "beginning_milepost": beginning_milepost,
                "ending_milepost": ending_milepost,
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

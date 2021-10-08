from collections import OrderedDict
import json
import time
import uuid
import xmltodict
import argparse
import logging

import xml.etree.ElementTree as ET

from wzdx.tools import wzdx_translator, polygon_tools, date_tools

from wzdx.util.transformations import rfc_to_unix
from wzdx.util.transformations import int_or_none
from wzdx.util.transformations import to_dict
from wzdx.util.collections import PathDict

PROGRAM_NAME = 'Navjoy568RawToStandard'
PROGRAM_VERSION = '1.0'


def main():
    input_file, output_dir = parse_rtdh_arguments()
    input_file_contents = open(input_file, 'r').read()
    generated_messages = generate_standard_messages_from_string(
        input_file_contents, output_dir)

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


def generate_standard_messages_from_string(input_file_contents, output_dir):
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
        if not validate_closure(obj):
            if invalid_messages_callback:
                invalid_messages_callback(obj)
        else:
            messages.append(obj)

    return messages


def generate_rtdh_standard_message_from_raw_single(raw_message_xml):
    obj = to_dict(raw_message_xml)
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


# parse script command line arguments
def parse_rtdh_arguments():
    parser = argparse.ArgumentParser(
        description='Translate NavJoy 568 data to RTDH Standard')
    parser.add_argument('--version', action='version',
                        version=f'{PROGRAM_NAME} {PROGRAM_VERSION}')
    parser.add_argument('iconeFile', help='icone file path')
    parser.add_argument('--outputDir', required=False,
                        default='./', help='output directory')

    args = parser.parse_args()
    return args.iconeFile, args.outputDir


def create_rtdh_standard_msg(pd):
    return {
        "rtdh_timestamp": time.time(),
        "rtdh_message_id": str(uuid.uuid4()),
        "event": {
            "type": pd.get("incident/type", default=""),
            "source": {
                "id": pd.get("incident/@id", default=""),
                "last_updated_timestamp": pd.get("incident/updatetime", rfc_to_unix, default=0),
            },
            "geometry": pd.get("incident/location/polyline", parse_polyline),
            "header": {
                "description": pd.get("incident/description", default=""),
                "start_timestamp": pd.get("incident/starttime", rfc_to_unix, default=None),
                "end_timestamp": pd.get("incident/endtime", rfc_to_unix, default=None)
            },
            "detail": {
                "road_name": pd.get("incident/location/street"),
                "road_number": pd.get("incident/location/street"),
                "direction": get_direction(pd.get("incident/location/street"), pd.get("incident/location/polyline"))
            },
            # "additional_info": [
            #
            # ]
        }
    }


def get_direction(street, coords):
    direction = wzdx_translator.parse_direction_from_street_name(street)
    if not direction:
        direction = polygon_tools.get_road_direction_from_coordinates(coords)
    return direction


# function to parse polyline to geometry line string
def parse_polyline(polylinestring):
    if not polylinestring or type(polylinestring) != str:
        return None
    # polyline rightnow is a list which has an empty string in it.
    polyline = polylinestring.split(',')
    coordinates = []
    for i in range(0, len(polyline)-1, 2):
        try:
            coordinates.append([float(polyline[i + 1]), float(polyline[i])])
        except ValueError as e:
            logging.warning('failed to parse polyline!')
            return []
    return coordinates


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

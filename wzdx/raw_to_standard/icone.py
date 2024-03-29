import argparse
import json
import logging
import time
import uuid
import xml.etree.ElementTree as ET
from collections import OrderedDict

from wzdx.tools import date_tools, polygon_tools, wzdx_translator
from wzdx.util.collections import PathDict

PROGRAM_NAME = 'iConeRawToStandard'
PROGRAM_VERSION = '1.0'


def main():
    input_file, output_dir = parse_rtdh_arguments()
    input_file_contents = open(input_file, 'r').read()
    generated_messages = generate_standard_messages_from_string(
        input_file_contents)

    generated_files_list = []
    for message in generated_messages:
        output_path = f"{output_dir}/standard_icone_{message['event']['source']['id']}_{round(message['rtdh_timestamp'])}.json"
        open(output_path, 'w+').write(json.dumps(message, indent=2))
        generated_files_list.append(output_path)

    if generated_files_list:
        print(
            f"Successfully generated standard message files: {generated_files_list}")
    else:
        logging.warning(
            "Standard message generation failed. See messages printed above")


def generate_standard_messages_from_string(input_file_contents):
    raw_messages = generate_raw_messages(input_file_contents)
    standard_messages = []
    for message in raw_messages:
        standard_messages.append(
            generate_rtdh_standard_message_from_raw_single(message))
    return standard_messages


def generate_raw_messages(message):
    response_xml = ET.fromstring(message)
    msg_lst = response_xml.findall('incident')
    messages = []

    # Loop through all elements and print each element to PubSub
    for msg in msg_lst:
        incident = ET.tostring(msg, encoding='utf8')
        obj = wzdx_translator.parse_xml_to_dict(incident)
        if validate_incident(obj.get('incident', {})):
            messages.append(incident)

    return messages


def generate_rtdh_standard_message_from_raw_single(raw_message_xml):
    obj = wzdx_translator.parse_xml_to_dict(raw_message_xml)
    pd = PathDict(obj)
    standard_message = create_rtdh_standard_msg(pd)
    return standard_message


# parse script command line arguments
def parse_rtdh_arguments():
    parser = argparse.ArgumentParser(
        description='Translate iCone data to RTDH Standard')
    parser.add_argument('--version', action='version',
                        version=f'{PROGRAM_NAME} {PROGRAM_VERSION}')
    parser.add_argument('iconeFile', help='icone file path')
    parser.add_argument('--outputDir', required=False,
                        default='./', help='output directory')

    args = parser.parse_args()
    return args.iconeFile, args.outputDir


# function to parse polyline to geometry line string
# input: "37.1571990,-84.1128540,37.1686478,-84.1238971" (lat, long)
# output: [[-84.1128540, 37.1571990], [-84.1238971, 37.1686478]] (long, lat)
def parse_icone_polyline(polylinestring):
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


def get_sensor_list(incident):
    devices = []
    for key in ['sensor', 'radar', 'display', 'message', 'marker', 'status']:
        obj = incident.get(f"{key}")
        if type(obj) in [dict, OrderedDict]:
            devices.append({'sensor_type': key, 'details': obj})
        elif type(obj) == list:
            for i in obj:
                devices.append({'sensor_type': key, 'details': i})
    return devices


def create_rtdh_standard_msg(pd):
    devices = get_sensor_list(pd.get(f"incident"))
    return {
        "rtdh_timestamp": time.time(),
        "rtdh_message_id": str(uuid.uuid4()),
        "event": {
            "type": pd.get("incident/type", default=""),
            "source": {
                "id": pd.get("incident/@id", default=""),
                "creation_timestamp": pd.get("incident/creationtime", date_tools.get_unix_from_iso_string, default=0),
                "last_updated_timestamp": pd.get("incident/updatetime", date_tools.get_unix_from_iso_string, default=0),
            },
            "geometry": pd.get("incident/location/polyline", parse_icone_polyline),
            "header": {
                "description": pd.get("incident/description", default=""),
                "start_timestamp": pd.get("incident/starttime", date_tools.get_unix_from_iso_string, default=None),
                "end_timestamp": pd.get("incident/endtime", date_tools.get_unix_from_iso_string, default=None)
            },
            "detail": {
                "road_name": pd.get("incident/location/street"),
                "road_number": pd.get("incident/location/street"),
                "direction": get_direction(pd.get("incident/location/street"), pd.get("incident/location/polyline"))
            },
            "additional_info": {
                "devices": devices,
                "directionality": pd.get("incident/location/direction")
            }
        }
    }


def get_direction(street, coords):
    direction = wzdx_translator.parse_direction_from_street_name(street)
    if not direction:
        direction = polygon_tools.get_road_direction_from_coordinates(coords)
    return direction


# function to validate the incident
def validate_incident(incident):
    if not incident or (type(incident) != dict and type(incident) != OrderedDict):
        logging.warning('incident is empty or has invalid type')
        return False

    id = incident.get("@id")

    location = incident.get('location')
    if not location:
        logging.warning(
            f'Invalid incident with id = {id}. Location object not present')
        return False

    polyline = location.get('polyline')
    coords = parse_icone_polyline(polyline)
    street = location.get('street', '')

    starttime_string = incident.get('starttime')
    endtime_string = incident.get('endtime')
    description = incident.get('description')
    creationtime = incident.get('creationtime')
    updatetime = incident.get('updatetime')
    direction = get_direction(street, coords)
    if not direction:
        logging.warning(
            f'Invalid incident with id = {id}. unable to parse direction from street name or polyline')
        return False
    required_fields = [location, polyline, coords, street,
                       starttime_string, description, creationtime, updatetime]
    for field in required_fields:
        if not field:
            logging.warning(
                f'''Invalid incident with id = {id}. Not all required fields are present. Required fields are:
                location, polyline, street, starttime, description, creationtime, and updatetime''')
            return False

    start_time = date_tools.parse_datetime_from_iso_string(starttime_string)
    end_time = date_tools.parse_datetime_from_iso_string(endtime_string)
    if not start_time:
        logging.warning(
            f'Invalid incident with id = {id}. Unsupported start time format: {start_time}')
        return False
    elif endtime_string and not end_time:
        logging.warning(
            f'Invalid incident with id = {id}. Unsupported end time format: {end_time}')
        return False

    return True


if __name__ == "__main__":
    main()

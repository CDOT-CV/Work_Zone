import argparse
import copy
import json
import logging
import time
import uuid
from collections import OrderedDict

from wzdx.tools import date_tools, polygon_tools, wzdx_translator
from wzdx.util.collections import PathDict

PROGRAM_NAME = 'PlannedEventsRawToStandard'
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
        output_path = f"{output_dir}/standard_568_{message['event']['source']['id']}_{round(message['rtdh_timestamp'])}_{message['event']['detail']['direction']}.json"
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
        standard_message = generate_rtdh_standard_message_from_raw_single(
            message)
        if standard_message:
            standard_messages.append(standard_message)
    return standard_messages


def generate_raw_messages(message_string):
    msg = json.loads(message_string)
    messages = []

    separated_messages = expand_event_directions(msg)
    for indiv_msg in separated_messages:
        if validate_closure(indiv_msg):
            messages.append(indiv_msg)

    return messages


# Break event into
def expand_event_directions(message):
    try:
        messages = []
        laneImpacts = message.get('properties', {}).get('laneImpacts')
        for laneImpact in laneImpacts:
            new_message = copy.deepcopy(message)
            direction_string = laneImpact['direction']
            direction = map_direction_string(direction_string)
            for laneImpact2 in new_message['properties']['laneImpacts']:
                if direction_string == laneImpact2['direction']:
                    new_message['properties']['laneImpacts'] = [laneImpact2]
                    new_message['properties']['recorded_direction'] = map_direction_string(
                        message['properties']['direction'])
                    new_message['properties']['laneImpacts'][0]['direction'] = direction
                    break
            new_message['properties'][
                'direction'] = direction
            messages.append(new_message)
        return messages
    except Exception as e:
        logging.error(e)
        return [message]


def generate_rtdh_standard_message_from_raw_single(obj):
    pd = PathDict(obj)
    standard_message = create_rtdh_standard_msg(pd)
    return standard_message


def get_linestring(geometry):
    if geometry['type'] == "MultiPoint":
        return geometry['coordinates']
    elif geometry['type'] == "Polygon":
        return polygon_tools.polygon_to_polyline_center(geometry['coordinates'])

# input:
# "laneImpacts": [
#     {
#         "direction": "east",
#         "laneCount": 2,
#         "laneClosures": "6000",
#         "closedLaneTypes": [
#             "left lane",
#             "right lane"
#         ]
#     },
#     {
#         "direction": "west",
#         "laneCount": 2,
#         "laneClosures": "0",
#         "closedLaneTypes": []
#     }
# ]

# Desired Output:
# lanes = [
#     {
#         "position": 0,
#         "closed": True,
#     },
#     {
#         "position": 1,
#         "closed": True
#     }
# ]


def hex_to_binary(hex_string):
    hexidecimal_scale = 16  # equals to hexadecimal
    num_of_bits = 16
    return bin(int(hex_string, hexidecimal_scale))[2:].zfill(num_of_bits)


# TODO: Consider support road closures
DEFAULT_EVENT_TYPE = ('work-zone', [{'type_name': 'roadside-work',
                      'is_architectural_change': False}])
EVENT_TYPE_MAPPING = {
    "Bridge Construction":              ('work-zone', [{'type_name': 'below-road-work',            'is_architectural_change': True}]),
    "Road Construction":                ('work-zone', [{'type_name': 'roadway-creation',           'is_architectural_change': True}]),
    "Bridge Maintenance Operations":    ('work-zone', [{'type_name': 'below-road-work',            'is_architectural_change': False}]),
    "Bridge Repair":                    ('work-zone', [{'type_name': 'below-road-work',            'is_architectural_change': False}]),
    "Chip Seal Operations":             ('work-zone', [{'type_name': 'minor-road-defect-repair',   'is_architectural_change': False}]),
    "Concrete Slab Replacement":        ('work-zone', [{'type_name': 'surface-work',               'is_architectural_change': False}]),
    "Crack Sealing":                    ('work-zone', [{'type_name': 'minor-road-defect-repair',   'is_architectural_change': False}]),
    "Culvert Maintenance":              ('work-zone', [{'type_name': 'roadside-work',              'is_architectural_change': False}]),
    "Electrical or Lighting":           ('work-zone', [{'type_name': 'roadside-work',              'is_architectural_change': False}]),
    "Emergency Maintenance":            ('work-zone', [{'type_name': 'roadside-work',              'is_architectural_change': False}]),
    "Fiber Optics Installation":        ('work-zone', [{'type_name': 'surface-work',               'is_architectural_change': False}]),
    "Guardrail":                        ('work-zone', [{'type_name': 'barrier-work',               'is_architectural_change': False}]),
    "IT or Fiber Optics":               ('work-zone', [{'type_name': 'surface-work',               'is_architectural_change': False}]),
    "Other":                            ('work-zone', [{'type_name': 'roadside-work',              'is_architectural_change': False}]),
    "Paving Operations":                ('work-zone', [{'type_name': 'surface-work',               'is_architectural_change': True}]),
    "Road Maintenance Operations":      ('work-zone', [{'type_name': 'surface-work',               'is_architectural_change': False}]),
    "Rock Work":                        ('work-zone', [{'type_name': 'roadside-work',              'is_architectural_change': False}]),
    "Sign Work":                        ('work-zone', [{'type_name': 'roadside-work',              'is_architectural_change': False}]),
    "Striping Operations":              ('work-zone', [{'type_name': 'painting',                   'is_architectural_change': True}]),
    "Traffic Sign Installation":        ('work-zone', [{'type_name': 'roadside-work',              'is_architectural_change': False}]),
    "Traffic Sign Maintenance":         ('work-zone', [{'type_name': 'roadside-work',              'is_architectural_change': False}]),
    "Traffic Signal Installation":      ('work-zone', [{'type_name': 'roadside-work',              'is_architectural_change': False}]),
    "Traffic Signal Maintenance":       ('work-zone', [{'type_name': 'roadside-work',              'is_architectural_change': False}]),
    "Tunnel Maintenance":               ('work-zone', [{'type_name': 'surface-work',               'is_architectural_change': False}]),
    "Utility Work":                     ('work-zone', [{'type_name': 'roadside-work',              'is_architectural_change': False}]),
    "Utility Installation":             ('work-zone', [{'type_name': 'roadside-work',              'is_architectural_change': False}]),
    "Wall Maintenance":                 ('work-zone', [{'type_name': 'barrier-work',               'is_architectural_change': False}]),

    "BAN Message":                      ('restriction', []),
    "Safety Campaign":                  ('restriction', []),
    "Smoke/Control Burn":               ('restriction', []),
    "Other":                            ('restriction', []),
    "Avalanche Control":                ('restriction', []),
    "Closed for the Season":            ('restriction', []),
    "Funeral Procession":               ('restriction', []),
    "Presidential Visit":               ('restriction', []),
    "Race Event":                       ('restriction', []),
    "Local Event":                      ('restriction', []),
    "Military Movement":                ('restriction', []),
    "OS/OW Limit":                      ('restriction', []),
}


LANE_TYPE_MAPPING = {
    "left shoulder": 'shoulder',
    "left lane": 'general',
    "center lane": 'general',
    "middle two lanes": 'general',
    'general': 'general',
    # this is a weird one
    "middle lanes": 'general',
    "right lane": 'general',
    "right shoulder": 'shoulder',
    "through lanes": 'general',
    "right entrance ramp": 'exit-ramp',
    "right exit ramp": 'exit-ramp'
}

INVALID_EVENT_DESCRIPTION = "511 event cannot be created in CARS because route does not exist."


def map_lane_type(lane_type):
    try:
        return LANE_TYPE_MAPPING[lane_type]
    except KeyError as e:
        logging.warning(
            f"Unrecognized lane type: {e}")
        return 'general'


def map_event_type(event_type):
    try:
        return EVENT_TYPE_MAPPING[event_type]
    except KeyError as e:
        logging.error(f"Unrecognized event type: {e}")
        return DEFAULT_EVENT_TYPE


def map_lane_status(lane_status_bit):
    return 'open' if lane_status_bit == '0' else 'closed'


def map_direction_string(direction_string):
    return STRING_DIRECTION_MAP.get(direction_string)


# This method parses a hex string and list of closed lane names into a WZDx lanes list. The hex string, lane_closures_hex,
# is a hexidecimal string which, when converted to binary and zero padded to length 16, yields the state of all lanes.
# 0 = open, 1 = closed. The 0th index is the left shoulder, the 15th index is the right shoulder, and all of the normal
# lanes start from the left, or 1st index.
def get_lanes_list(lane_closures_hex, num_lanes, closedLaneTypes):
    lanes_affected = hex_to_binary(lane_closures_hex)
    lane_bits = lanes_affected[1:(num_lanes+1)]
    lanes = []
    order = 1
    if map_lane_status(lanes_affected[0]) == 'closed':
        lanes.append({
            'order': order,
            'type': 'shoulder',
            'status': map_lane_status(lanes_affected[0]),
        })
        order += 1
    closedLaneTypes = [i for i in closedLaneTypes if 'shoulder' not in i]
    for i, bit in enumerate([char for char in lane_bits]):
        lanes.append({
            'order': order,
            'type': map_lane_type(closedLaneTypes[i] if (len(closedLaneTypes) > i) else 'general'),
            'status': map_lane_status(bit),
        })
        order += 1
    if map_lane_status(lanes_affected[15]) == 'closed':
        lanes.append({
            'order': order,
            'type': 'shoulder',
            'status': map_lane_status(lanes_affected[15]),
        })
        order += 1
    return lanes


def get_lane_impacts(lane_impacts, direction):
    for impact in lane_impacts:
        if impact['direction'] == direction:
            return get_lanes_list(impact['laneClosures'], impact['laneCount'], impact['closedLaneTypes'])


def all_lanes_open(lanes):
    for i in lanes:
        if i['status'] != 'open':
            return False
    return True


def create_rtdh_standard_msg(pd):
    if pd.get('properties/travelerInformationMessage') == INVALID_EVENT_DESCRIPTION:
        logging.warning(
            f"Invalid message with id: '{pd.get('properties/id')}'' because description matches invalid event description: '{INVALID_EVENT_DESCRIPTION}'")
        return {}

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

    lane_impacts = get_lane_impacts(
        pd.get("properties/laneImpacts"), pd.get("properties/direction"))
    if direction != recorded_direction and all_lanes_open(lane_impacts):
        return {}

    return {
        "rtdh_timestamp": time.time(),
        "rtdh_message_id": str(uuid.uuid4()),
        "event": {
            "type": event_type,
            "types_of_work": types_of_work,
            "source": {
                "id": pd.get("properties/id", default="") + '_' + direction,
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
                "lanes": lane_impacts,
                "restrictions": restrictions,
                "beginning_milepost": beginning_milepost,
                "ending_milepost": ending_milepost,
                "valid": False,
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

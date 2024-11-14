import argparse
import copy
import datetime
import json
import logging
import re
import time
from typing import Literal
import uuid
from collections import OrderedDict

import regex

from ..tools import (
    cdot_geospatial_api,
    date_tools,
    geospatial_tools,
    polygon_tools,
    wzdx_translator,
)
from ..util.collections import PathDict

PROGRAM_NAME = "PlannedEventsRawToStandard"
PROGRAM_VERSION = "1.0"

STRING_DIRECTION_MAP = {
    "north": "northbound",
    "south": "southbound",
    "west": "westbound",
    "east": "eastbound",
}

REVERSED_DIRECTION_MAP = {
    "northbound": "southbound",
    "southbound": "northbound",
    "eastbound": "westbound",
    "westbound": "eastbound",
}

WORK_ZONE_INCIDENT_TYPES = {
    "Maintenance Operations": {"Traffic": True},
    "Emergency Roadwork": {"Traffic": True},
}
INCIDENT_ID_REGEX = "^OpenTMS-Incident"


def main():
    cdotGeospatialApi: cdot_geospatial_api.GeospatialApi = (
        cdot_geospatial_api.GeospatialApi()
    )
    source_file, output_dir = parse_rtdh_arguments()
    input_file_contents = open(source_file, "r").read()
    generated_messages = generate_standard_messages_from_string(
        cdotGeospatialApi, input_file_contents
    )

    generated_files_list = []
    for message in generated_messages:
        output_path = f"{output_dir}/standard_planned_event_{message['event']['source']['id']}.json"
        open(output_path, "w+").write(json.dumps(message, indent=2))
        generated_files_list.append(output_path)

    if generated_files_list:
        print(f"Successfully generated standard message files: {generated_files_list}")
    else:
        print("Warning: Standard message generation failed. See messages printed above")


# parse script command line arguments
def parse_rtdh_arguments() -> tuple[str, str]:
    """Parse command line arguments for Planned Events to RTDH Standard translation

    Returns:
        str: planned event file path
        str: output directory path
    """
    parser = argparse.ArgumentParser(
        description="Translate Planned Event data to RTDH Standard"
    )
    parser.add_argument(
        "--version", action="version", version=f"{PROGRAM_NAME} {PROGRAM_VERSION}"
    )
    parser.add_argument("plannedEventsFile", help="planned event file path")
    parser.add_argument(
        "--outputDir", required=False, default="./", help="output directory"
    )

    args = parser.parse_args()
    return args.plannedEventsFile, args.outputDir


def generate_standard_messages_from_string(
    cdotGeospatialApi: cdot_geospatial_api.GeospatialApi, input_file_contents: str
) -> list[dict]:
    """Generate standard messages from a string of input file contents

    Args:
        cdotGeospatialApi (cdot_geospatial_api.GeospatialApi): customized GeospatialApi object, used for route details
        input_file_contents (str): string of input file contents

    Returns:
        list[dict]: list of generated RTDH standard messages
    """
    raw_messages = generate_raw_messages(input_file_contents)
    standard_messages = []
    for message in raw_messages:
        standard_message = generate_rtdh_standard_message_from_raw_single(
            cdotGeospatialApi, message
        )
        if standard_message:
            standard_messages.append(standard_message)
    return standard_messages


# TODO: Integrate Category
def is_incident_wz(msg: dict) -> tuple[bool, bool]:
    """Determine if a message is an incident or work zone

    Args:
        msg (dict): planned event message object

    Returns:
        is_incident (bool): whether the message is an incident
        is_wz (bool): whether the message is a work zone
    """
    id = msg.get("properties", {}).get("id", "")
    type = msg.get("properties", {}).get("type", "")
    # category = msg.get('properties', {}).get('Category')
    is_incident = re.match(INCIDENT_ID_REGEX, id) != None
    # is_wz = WORK_ZONE_INCIDENT_TYPES.get(type, {}).get(category)
    is_wz = WORK_ZONE_INCIDENT_TYPES.get(type, {}) != {}
    return is_incident, is_wz


def generate_raw_messages(message_string: str) -> list[dict]:
    """Generate raw messages from a string of input file contents using `expand_event_directions`

    Args:
        message_string (_type_): raw planned events message string

    Returns:
        _type_: list of raw planned events message objects, 1 for each lane impact direction
    """
    msg = json.loads(message_string)
    return expand_event_directions(msg)


# Break event into
def expand_event_directions(message: dict) -> list[dict]:
    """Expand a message into multiple messages, one for each lane impact direction

    Args:
        message (dict): planned event message object

    Returns:
        list[dict]: list of planned event message objects, 1 for each lane impact direction
    """
    try:
        messages = []
        laneImpacts = message.get("properties", {}).get("laneImpacts")
        for laneImpact in laneImpacts:
            new_message = copy.deepcopy(message)
            direction_string = laneImpact["direction"]
            direction = map_direction_string(direction_string)
            for laneImpact2 in new_message["properties"]["laneImpacts"]:
                if direction_string == laneImpact2["direction"]:
                    new_message["properties"]["laneImpacts"] = [laneImpact2]
                    new_message["properties"]["recorded_direction"] = (
                        map_direction_string(message["properties"]["direction"])
                    )
                    new_message["properties"]["laneImpacts"][0]["direction"] = direction
                    break
            new_message["properties"]["direction"] = direction
            messages.append(new_message)
        return messages
    except Exception as e:
        logging.error(e)
        return [message]


def generate_rtdh_standard_message_from_raw_single(
    cdotGeospatialApi: cdot_geospatial_api.GeospatialApi, obj: dict
) -> dict:
    """Generate a single RTDH standard message from a raw planned event message

    Args:
        cdotGeospatialApi (cdot_geospatial_api.GeospatialApi): customized GeospatialApi object, used for route details
        obj (dict): raw planned event message object

    Returns:
        dict: RTDH standard message object
    """
    is_incident_msg, is_wz = is_incident_wz(obj)
    if is_incident_msg and not is_wz:
        return {}
    pd = PathDict(obj)
    standard_message = create_rtdh_standard_msg(cdotGeospatialApi, pd, is_incident_msg)
    return standard_message


def get_linestring(geometry: dict) -> list[list[float]]:
    """Get a list of coordinates from a geometry object. Supports MultiPoint and Polygon types, and Polygons are converted to polylines with `polygon_tools.polygon_to_polyline_center`.

    Args:
        geometry (dict): GeoJSON geometry object, only supports MultiPoint and Polygon

    Returns:
        list[list[float]]: list of coordinates
    """
    if geometry.get("type") == "MultiPoint":
        return geometry["coordinates"]
    elif geometry.get("type") == "Polygon":
        return polygon_tools.polygon_to_polyline_center(geometry["coordinates"])
    else:
        return []


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


def hex_to_binary(hex_string: str) -> str:
    """Convert a hex string to a binary string

    Args:
        hex_string (str): hex string

    Returns:
        str: binary string
    """
    hexidecimal_scale = 16  # equals to hexadecimal
    num_of_bits = 16
    return bin(int(hex_string, hexidecimal_scale))[2:].zfill(num_of_bits)


# (event_type, types of work, work_zone_type)
DEFAULT_EVENT_TYPE = ("work-zone", [], "static")
EVENT_TYPE_MAPPING = {
    # Work Zones
    "Bridge Construction": (
        "work-zone",
        [{"type_name": "below-road-work", "is_architectural_change": True}],
        "static",
    ),
    "Road Construction": (
        "work-zone",
        [{"type_name": "roadway-creation", "is_architectural_change": True}],
        "static",
    ),
    "Bridge Maintenance Operations": (
        "work-zone",
        [{"type_name": "below-road-work", "is_architectural_change": False}],
        "static",
    ),
    "Bridge Repair": (
        "work-zone",
        [{"type_name": "below-road-work", "is_architectural_change": False}],
        "static",
    ),
    "Chip Seal Operations": (
        "work-zone",
        [{"type_name": "minor-road-defect-repair", "is_architectural_change": False}],
        "static",
    ),
    "Concrete Slab Replacement": (
        "work-zone",
        [{"type_name": "surface-work", "is_architectural_change": False}],
        "static",
    ),
    "Crack Sealing": (
        "work-zone",
        [{"type_name": "minor-road-defect-repair", "is_architectural_change": False}],
        "static",
    ),
    "Culvert Maintenance": (
        "work-zone",
        [{"type_name": "roadside-work", "is_architectural_change": False}],
        "static",
    ),
    "Electrical or Lighting": (
        "work-zone",
        [{"type_name": "roadside-work", "is_architectural_change": False}],
        "static",
    ),
    "Emergency Maintenance": (
        "work-zone",
        [{"type_name": "roadside-work", "is_architectural_change": False}],
        "static",
    ),
    "Fiber Optics Installation": (
        "work-zone",
        [{"type_name": "surface-work", "is_architectural_change": False}],
        "static",
    ),
    "Guardrail": (
        "work-zone",
        [{"type_name": "barrier-work", "is_architectural_change": False}],
        "static",
    ),
    "IT or Fiber Optics": (
        "work-zone",
        [{"type_name": "surface-work", "is_architectural_change": False}],
        "static",
    ),
    "Paving Operations": (
        "work-zone",
        [{"type_name": "surface-work", "is_architectural_change": True}],
        "static",
    ),
    "Road Maintenance Operations": (
        "work-zone",
        [{"type_name": "surface-work", "is_architectural_change": False}],
        "static",
    ),
    "Rock Work": (
        "work-zone",
        [{"type_name": "roadside-work", "is_architectural_change": False}],
        "static",
    ),
    "Sign Work": (
        "work-zone",
        [{"type_name": "roadside-work", "is_architectural_change": False}],
        "static",
    ),
    "Striping Operations": (
        "work-zone",
        [{"type_name": "painting", "is_architectural_change": True}],
        "planned-moving-area",
    ),
    "Traffic Sign Installation": (
        "work-zone",
        [{"type_name": "roadside-work", "is_architectural_change": False}],
        "static",
    ),
    "Traffic Sign Maintenance": (
        "work-zone",
        [{"type_name": "roadside-work", "is_architectural_change": False}],
        "static",
    ),
    "Traffic Signal Installation": (
        "work-zone",
        [{"type_name": "roadside-work", "is_architectural_change": False}],
        "static",
    ),
    "Traffic Signal Maintenance": (
        "work-zone",
        [{"type_name": "roadside-work", "is_architectural_change": False}],
        "static",
    ),
    "Tunnel Maintenance": (
        "work-zone",
        [{"type_name": "surface-work", "is_architectural_change": False}],
        "static",
    ),
    "Utility Work": (
        "work-zone",
        [{"type_name": "roadside-work", "is_architectural_change": False}],
        "static",
    ),
    "Utility Installation": (
        "work-zone",
        [{"type_name": "roadside-work", "is_architectural_change": False}],
        "static",
    ),
    "Wall Maintenance": (
        "work-zone",
        [{"type_name": "barrier-work", "is_architectural_change": False}],
        "static",
    ),
    # Road Closures
    "BAN Message": ("restriction", [], "static"),
    "Safety Campaign": ("restriction", [], "static"),
    "Smoke/Control Burn": ("restriction", [], "static"),
    "Avalanche Control": ("restriction", [], "static"),
    "Closed for the Season": ("restriction", [], "static"),
    "Funeral Procession": ("restriction", [], "static"),
    "Presidential Visit": ("restriction", [], "static"),
    "Race Event": ("restriction", [], "static"),
    "Local Event": ("restriction", [], "static"),
    "Military Movement": ("restriction", [], "static"),
    "OS/OW Limit": ("restriction", [], "static"),
    "Geological Drilling": ("restriction", [], "static"),
    # Incidents (work zones): *\(.]n
    "Emergency Roadwork": ("work-zone", [], "static"),
    "Maintenance Operations": ("work-zone", [], "static"),
}

LANE_TYPE_MAPPING = {
    "left shoulder": "shoulder",
    "left lane": "general",
    "center lane": "general",
    "middle two lanes": "general",
    "general": "general",
    "middle lanes": "general",  # this is a weird one
    "right lane": "general",
    "right shoulder": "shoulder",
    "through lanes": "general",
    "right entrance ramp": "exit-ramp",
    "right exit ramp": "exit-ramp",
}

INVALID_EVENT_DESCRIPTION = (
    "511 event cannot be created in CARS because route does not exist."
)


def map_lane_type(lane_type: str) -> str:
    """Map a planned event lane type to a standard lane type, using `LANE_TYPE_MAPPING`

    Args:
        lane_type (str): planned event lane type

    Returns:
        str: standard lane type
    """
    try:
        return LANE_TYPE_MAPPING[lane_type]
    except KeyError as e:
        logging.warning(f"Unrecognized lane type: {e}")
        return "general"


def map_event_type(event_type: str) -> tuple[str, list[dict], str]:
    """Map a planned event type to a standard event type, using `EVENT_TYPE_MAPPING`

    Args:
        event_type (str): planned event type

    Returns:
        tuple[str, list[dict], str]: work zone/restriction classification, types of work, planned-moving-area/static work zone type
    """
    try:
        return EVENT_TYPE_MAPPING[event_type]
    except KeyError as e:
        logging.warning(f"Unrecognized event type: {e}")
        return DEFAULT_EVENT_TYPE


def map_lane_status(lane_status_bit: Literal["1", "0"]) -> str:
    """Map a lane status bit to WZDx lane status

    Args:
        lane_status_bit (Literal[&quot;1&quot;, &quot;0&quot;]): lane status bit

    Returns:
        str: WZDx lane status
    """
    return "open" if lane_status_bit == "0" else "closed"


def map_direction_string(
    direction_string: str,
) -> Literal["undefined", "eastbound", "westbound", "northbound", "southbound"]:
    """Map a direction string to a standard direction string

    Args:
        direction_string (str): direction string, like 'north', 'south', 'east', 'west'

    Returns:
        Literal["undefined", "eastbound", "westbound", "northbound", "southbound"]: standard direction string
    """
    return STRING_DIRECTION_MAP.get(direction_string, "undefined")


# This method parses a hex string and list of closed lane names into a WZDx lanes list. The hex string, lane_closures_hex,
# is a hexidecimal string which, when converted to binary and zero padded to length 16, yields the state of all lanes.
# 0 = open, 1 = closed. The 0th index is the left shoulder, the 15th index is the right shoulder, and all of the normal
# lanes start from the left, or 1st index.
def get_lanes_list(lane_closures_hex: str, num_lanes: int, closedLaneTypes: list[str]):
    """This method parses a hex string and list of closed lane names into a WZDx lanes list. The hex string, lane_closures_hex, is a hexidecimal string which, when converted to binary and zero padded to length 16, yields the state of all lanes. 0 = open, 1 = closed. The 0th index is the left shoulder, the 15th index is the right shoulder, and all of the normal lanes start from the left, or 1st index.
    Args:
        lane_closures_hex (str): Planned event laneClosures hex string
        num_lanes (int): number of lanes
        closedLaneTypes (list[str]): Planned event closedLaneTypes list

    Returns:
        _type_: WZDx lanes list
    """
    lanes_affected = hex_to_binary(lane_closures_hex)
    lane_bits = lanes_affected[1 : (num_lanes + 1)]
    lanes = []
    order = 1
    if map_lane_status(lanes_affected[0]) == "closed":
        lanes.append(
            {
                "order": order,
                "type": "shoulder",
                "status": map_lane_status(lanes_affected[0]),
            }
        )
        order += 1
    closedLaneTypes = [i for i in closedLaneTypes if "shoulder" not in i]
    for i, bit in enumerate([char for char in lane_bits]):
        lanes.append(
            {
                "order": order,
                "type": map_lane_type(
                    closedLaneTypes[i] if (len(closedLaneTypes) > i) else "general"
                ),
                "status": map_lane_status(bit),
            }
        )
        order += 1
    if map_lane_status(lanes_affected[15]) == "closed":
        lanes.append(
            {
                "order": order,
                "type": "shoulder",
                "status": map_lane_status(lanes_affected[15]),
            }
        )
        order += 1
    return lanes


def get_lane_impacts(
    lane_impacts: list[dict],
    direction: Literal[
        "undefined", "eastbound", "westbound", "northbound", "southbound"
    ],
) -> list[dict]:
    """Get WZDx lane list from list of lane impacts and direction

    Args:
        lane_impacts (list[dict]): Planned event lane impacts
        direction (Literal["undefined", "eastbound", "westbound", "northbound", "southbound"]): Planned event direction

    Returns:
        list[dict]: _description_
    """
    for impact in lane_impacts:
        if impact["direction"] == direction:
            return get_lanes_list(
                impact["laneClosures"], impact["laneCount"], impact["closedLaneTypes"]
            )


def all_lanes_open(lanes: list[dict]) -> bool:
    """Check if all lanes are open

    Args:
        lanes (list[dict]): WZDx lanes list

    Returns:
        bool: whether all lanes are open
    """
    for i in lanes:
        if i["status"] != "open":
            return False
    return True


# On {roadName}, between mile markers {startMarker} and {endMarker}. {typeOfWork}. Running between {startTime} and {endTime}
def create_description(
    name: str,
    roadName: str,
    startMarker: float,
    endMarker: float,
    typeOfWork: str,
    startTime: str,
    endTime: str,
) -> str:
    """Create a description string from planned event details

    Args:
        name (str)
        roadName (str)
        startMarker (float)
        endMarker (float)
        typeOfWork (str)
        startTime (str)
        endTime (str)

    Returns:
        str: generated event description
    """
    return f"Event {name}, on {roadName}, between mile markers {startMarker} and {endMarker}. {typeOfWork}. Running between {startTime} and {endTime}"


def get_improved_geometry(
    cdotGeospatialApi: cdot_geospatial_api.GeospatialApi,
    coordinates: list[list[float]],
    event_status: str,
    route_details_start: dict,
    route_details_end: dict,
    id: str,
) -> list[list[float]]:
    """Get higher definition geometry from GIS endpoint for planned event. Do not improve geometry for completed events.

    Args:
        cdotGeospatialApi (cdot_geospatial_api.GeospatialApi): customized GeospatialApi object, for retrieving route geometry
        coordinates (list[list[float]]): planned event coordinates
        event_status (str): ["active", "pending", "planned", "completed"]
        route_details_start (dict): GIS route details for start of event
        route_details_end (dict): GIS route details for end of event
        id (str): ID of planned event, used for logging

    Returns:
        list[list[float]]: _description_
    """
    if event_status == "completed":
        return coordinates

    startPoint = [coordinates[0][-1], coordinates[0][0]]
    endPoint = [coordinates[-1][-1], coordinates[-1][0]]

    if startPoint == endPoint:
        return coordinates

    if not route_details_start or not route_details_end:
        logging.warning(
            f"1 or more routes not found, not generating improved geometry: {id}"
        )
        return coordinates
    if route_details_start["Route"] != route_details_end["Route"]:
        logging.warning(f"Routes did not match, not generating improved geometry: {id}")
        return coordinates

    initialDirection = geospatial_tools.get_road_direction_from_coordinates(coordinates)
    newCoordinates = cdotGeospatialApi.get_route_between_measures(
        route_details_start["Route"],
        route_details_start["Measure"],
        route_details_end["Measure"],
        compressed=True,
    )

    finalDirection = geospatial_tools.get_road_direction_from_coordinates(
        newCoordinates
    )

    # TODO: Implement Bi-directional carriageway
    if initialDirection == REVERSED_DIRECTION_MAP.get(finalDirection):
        newCoordinates.reverse()

    if not newCoordinates:
        return coordinates

    return newCoordinates


def get_cross_streets_from_description(description: str) -> tuple[str, str]:
    """Get cross streets from a description string using regular expression "^Between (.*?) and (.*?)(?= from)"

    Args:
        description (str): description string

    Returns:
        tuple[str, str]: beginning cross street, ending cross street
    """
    desc_regex = "^Between (.*?) and (.*?)(?= from)"
    m = regex.search(desc_regex, description)
    try:
        return m.group(1, 2)
    except:
        return ("", "")


def get_mileposts_from_description(message: str) -> tuple[str, str]:
    """Get mileposts from a description string using regular expression "^Between Exit ([0-9.]{0-4}): .*? and Exit  ([0-9.]{0-4}):"
    Args:
        description (str): description string
    Returns:
        tuple[str, str]: beginning milepost, ending milepost
    """
    desc_regex = "^Between Exit (.*?): .*? and Exit  (.*?):"
    m = regex.search(desc_regex, message)
    try:
        return m.group(1, 2)
    except:
        return ("", "")


def get_route_details_for_coordinates_lngLat(
    cdotGeospatialApi: cdot_geospatial_api.GeospatialApi,
    coordinates: list[list[float]],
    reversed: bool,
) -> tuple[dict, dict]:
    """Get GIS route details for start and end coordinates

    Args:
        cdotGeospatialApi (cdot_geospatial_api.GeospatialApi): customized GeospatialApi object, for retrieving route details
        coordinates (list[list[float]]): planned event coordinates
        reversed (bool): whether the coordinates are reversed

    Returns:
        tuple[dict, dict]: GIS route details for start and end coordinates
    """
    route_details_start = get_route_details(
        cdotGeospatialApi, coordinates[0][1], coordinates[0][0]
    )

    if len(coordinates) == 1 or (
        len(coordinates) == 2 and coordinates[0] == coordinates[1]
    ):
        route_details_end = None
    else:
        route_details_end = get_route_details(
            cdotGeospatialApi, coordinates[-1][1], coordinates[-1][0]
        )

    # Update route IDs based on directionality
    if route_details_start and route_details_end:
        if route_details_start["Route"].replace("_DEC", "") != route_details_end[
            "Route"
        ].replace("_DEC", ""):
            logging.warning(
                f"Routes did not match! route details: {route_details_start['Route']}, {route_details_end['Route']}"
            )
            return route_details_start, route_details_end
        else:
            if route_details_start["Measure"] > route_details_end["Measure"]:
                route_details_start["Route"] = route_details_start["Route"].replace(
                    "_DEC", ""
                )
                route_details_end["Route"] = route_details_end["Route"].replace(
                    "_DEC", ""
                )
            else:
                route_details_start["Route"] = (
                    route_details_start["Route"].replace("_DEC", "") + "_DEC"
                )
                route_details_end["Route"] = (
                    route_details_end["Route"].replace("_DEC", "") + "_DEC"
                )

    return route_details_start, route_details_end


def get_route_details(
    cdotGeospatialApi: cdot_geospatial_api.GeospatialApi, lat: float, lng: float
) -> dict:
    """Get GIS route details for a given latitude and longitude

    Args:
        cdotGeospatialApi (cdot_geospatial_api.GeospatialApi): customized GeospatialApi object, for retrieving route details
        lat (float): latitude
        lng (float): longitude

    Returns:
        dict: GIS route details
    """
    return cdotGeospatialApi.get_route_and_measure((lat, lng))


# isIncident is unused, could be useful later though
def create_rtdh_standard_msg(
    cdotGeospatialApi: cdot_geospatial_api.GeospatialApi, pd: PathDict, isIncident: bool
) -> dict:
    """Create a RTDH standard message from a planned event PathDict

    Args:
        cdotGeospatialApi (cdot_geospatial_api.GeospatialApi): customized GeospatialApi object, for retrieving route details and improved geometry
        pd (PathDict): planned event PathDict
        isIncident (bool): whether the event is an incident (modifies start_date parsing)

    Returns:
        dict: RTDH standard message
    """
    try:
        description = pd.get("properties/travelerInformationMessage", "")
        if description == INVALID_EVENT_DESCRIPTION:
            description = create_description(
                pd.get("properties/name"),
                pd.get("properties/routeName"),
                pd.get("properties/startMarker"),
                pd.get("properties/endMarker"),
                pd.get("properties/type"),
                pd.get("properties/startTime"),
                pd.get("properties/clearTime"),
            )

        beginning_milepost, ending_milepost = get_mileposts_from_description(
            description
        )

        begin_cross_street, end_cross_street = get_cross_streets_from_description(
            description
        )

        coordinates = get_linestring(pd.get("geometry"))
        if not coordinates:
            logging.warning(
                f'Unable to retrieve geometry coordinates for event: {pd.get("properties/id", default="")}'
            )
            return {}

        direction = pd.get("properties/direction", default="unknown")

        beginning_milepost = pd.get(
            "properties/startMarker", default=beginning_milepost
        )
        ending_milepost = pd.get("properties/endMarker", default=ending_milepost)
        recorded_direction = pd.get("properties/recorded_direction")
        reversed = False
        if (
            direction == REVERSED_DIRECTION_MAP.get(recorded_direction)
            and direction != "unknown"
        ):
            reversed = True
            coordinates.reverse()
            beginning_milepost = pd.get("properties/endMarker", default=ending_milepost)
            ending_milepost = pd.get(
                "properties/startMarker", default=beginning_milepost
            )

        roadName = wzdx_translator.remove_direction_from_street_name(
            pd.get("properties/routeName")
        )

        now = datetime.datetime.now(datetime.timezone.utc)
        start_date = pd.get(
            "properties/startTime", date_tools.parse_datetime_from_iso_string
        )
        end_date = pd.get(
            "properties/clearTime", date_tools.parse_datetime_from_iso_string
        )

        if not start_date and isIncident:
            start_date = now

        if not start_date:
            logging.warning(
                f'Unable to process event, no start date for event: {pd.get("properties/id", default="")}'
            )
            return {}
        if not end_date:
            end_date = pd.get(
                "properties/estimatedClearTime",
                date_tools.parse_datetime_from_iso_string,
            )

        if not end_date:
            # Since there is no end date, assume still active, set end date in future (12 hours + n days until after current time)
            end_date = start_date + datetime.timedelta(hours=12)

            delta_days = (now - end_date).days
            if delta_days > 0:
                end_date = end_date + datetime.timedelta(days=delta_days)

            end_date = end_date.replace(second=0, microsecond=0)

        event_type, types_of_work, work_zone_type = map_event_type(
            pd.get("properties/type", default="")
        )

        restrictions = []
        if pd.get("properties/isOversizedLoadsProhibited"):
            restrictions.append({"type": "permitted-oversize-loads-prohibited"})

        event_status = date_tools.get_event_status(start_date, end_date)

        condition_1 = event_status in ["active", "pending", "planned"]

        lane_impacts = get_lane_impacts(
            pd.get("properties/laneImpacts"), pd.get("properties/direction")
        )
        if direction != recorded_direction and all_lanes_open(lane_impacts):
            logging.info(
                f'Unable to retrieve geometry coordinates for event: {pd.get("properties/id", default="")}'
            )
            return {}

        route_details_start, route_details_end = (
            get_route_details_for_coordinates_lngLat(
                cdotGeospatialApi, coordinates, reversed
            )
        )

        return {
            "rtdh_timestamp": time.time(),
            "rtdh_message_id": str(uuid.uuid4()),
            "event": {
                "type": event_type,
                "types_of_work": types_of_work,
                "work_zone_type": work_zone_type,
                "source": {
                    "id": pd.get("properties/id", default="") + "_" + direction,
                    "last_updated_timestamp": pd.get(
                        "properties/lastUpdated",
                        date_tools.get_unix_from_iso_string,
                        default=0,
                    ),
                },
                "geometry": get_improved_geometry(
                    cdotGeospatialApi,
                    coordinates,
                    event_status,
                    route_details_start,
                    route_details_end,
                    pd.get("properties/id", default="") + "_" + direction,
                ),
                "header": {
                    "description": description,
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
                    "beginning_cross_street": begin_cross_street,
                    "ending_cross_street": end_cross_street,
                    "valid": False,
                    "route_details_start": route_details_start,
                    "route_details_end": route_details_end,
                    "condition_1": condition_1,
                },
            },
        }
    except Exception as e:
        logging.warning(
            f'Error ocurred generating standard message for message {pd.get("properties/id", default="")}: {e}'
        )
        return {}


def validate_closure(obj: dict | OrderedDict) -> bool:
    """Validate the planned event object

    Args:
        obj (dict): planned event object

    Returns:
        bool: whether the object is valid

    Validation Rules:
    - obj must be a dictionary
    - obj must have a sys_gUid
    - obj must have a properties object
    - obj must have a geometry object
    - obj must have a properties.startTime, which is a valid date
    - obj must have a properties.clearTime, which is a valid date
    - obj must have a properties.travelerInformationMessage
    - obj must have a properties.direction
    - obj must have a properties.laneImpacts
    - obj must have a properties.id
    - obj must have a properties.type

    """
    if not obj or (type(obj) != dict and type(obj) != OrderedDict):
        logging.warning("alert is empty or has invalid type")
        return False
    id = obj.get("sys_gUid")
    try:

        properties = obj.get("properties", {})

        coordinates = get_linestring(obj.get("geometry"))
        if not coordinates:
            logging.warning(
                f"Invalid event with id = {obj.get('sys_gUid')}. No valid coordinates found"
            )
            return False

        starttime_string = properties.get("startTime")
        endtime_string = properties.get("clearTime")
        description = properties.get("travelerInformationMessage")
        direction = properties.get("direction", "undefined")

        required_fields = [starttime_string, description, direction]
        for field in required_fields:
            if not field:
                logging.warning(
                    f"""Invalid event with id = {id}. not all required fields are present. Required fields are: 
                    streetNameFrom, workStartDate, and descriptionForProject"""
                )
                return False

        start_time = date_tools.parse_datetime_from_iso_string(starttime_string)
        end_time = date_tools.parse_datetime_from_iso_string(endtime_string)
        if not start_time:
            logging.warning(
                f"Invalid incident with id = {id}. Unsupported start time format: {start_time}"
            )
            return False
        elif endtime_string and not end_time:
            logging.warning(
                f"Invalid incident with id = {id}. Unsupported end time format: {end_time}"
            )
            return False
    except Exception as e:
        logging.error(
            f"Invalid event with id = {id}. Error ocurred while validating: {e}"
        )
        return False

    return True


if __name__ == "__main__":
    main()

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

from wzdx.models.enums import (
    Direction,
    EventType,
    LaneStatus,
    LaneType,
    VehicleImpact,
    WorkTypeName,
    WorkZoneType,
)
from wzdx.models.type_of_work import TypeOfWork

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
    "north": Direction.NORTHBOUND,
    "south": Direction.SOUTHBOUND,
    "west": Direction.WESTBOUND,
    "east": Direction.EASTBOUND,
}

REVERSED_DIRECTION_MAP = {
    Direction.NORTHBOUND: Direction.SOUTHBOUND,
    Direction.SOUTHBOUND: Direction.NORTHBOUND,
    Direction.EASTBOUND: Direction.WESTBOUND,
    Direction.WESTBOUND: Direction.EASTBOUND,
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
    is_incident = re.match(INCIDENT_ID_REGEX, id) is not None
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


INVALID_EVENT_DESCRIPTION = (
    "511 event cannot be created in CARS because route does not exist."
)


def map_lane_type(lane_type: str) -> LaneType:
    """Map a planned event lane type to a standard lane type, using `LANE_TYPE_MAPPING`

    Args:
        lane_type (str): planned event lane type

    Returns:
        str: standard lane type
    """
    match lane_type:
        case "left shoulder" | "right shoulder":
            return LaneType.SHOULDER
        case (
            "left lane"
            | "center lane"
            | "middle two lanes"
            | "general"
            | "middle lanes"
            | "right lane"
            | "through lanes"
        ):
            return LaneType.GENERAL
        case "right entrance ramp" | "right exit ramp":
            return LaneType.EXIT_RAMP
        case _:
            logging.warning(f"Unrecognized lane type: {lane_type}")
            return LaneType.GENERAL


def map_event_type(event_type: str) -> tuple[list[TypeOfWork], WorkZoneType]:
    """Map a planned event type to a standard event type, using `EVENT_TYPE_MAPPING`

    Args:
        event_type (str): planned event type

    Returns:
        tuple[str, list[TypeOfWork], WorkZoneType]: work zone/restriction classification, types of work, planned-moving-area/static work zone type
    """

    match event_type:
        case "Bridge Construction" | "Bridge Maintenance Operations" | "Bridge Repair":
            return (
                [
                    TypeOfWork(
                        type_name=WorkTypeName.BELOW_ROAD_WORK,
                        is_architectural_change=True,
                    )
                ],
                WorkZoneType.STATIC,
            )
        case "Road Construction":
            return (
                [
                    TypeOfWork(
                        type_name=WorkTypeName.ROADWAY_CREATION,
                        is_architectural_change=True,
                    )
                ],
                WorkZoneType.STATIC,
            )
        case "Chip Seal Operations" | "Crack Sealing":
            return (
                [
                    TypeOfWork(
                        type_name=WorkTypeName.MINOR_ROAD_DEFECT_REPAIR,
                        is_architectural_change=False,
                    )
                ],
                WorkZoneType.PLANNED_MOVING_AREA,
            )
        case (
            "Concrete Slab Replacement"
            | "Fiber Optics Installation"
            | "IT or Fiber Optics"
            | "Paving Operations"
            | "Road Maintenance Operations"
            | "Guardrail"
        ):
            return (
                [
                    TypeOfWork(
                        type_name=WorkTypeName.BARRIER_WORK,
                        is_architectural_change=False,
                    )
                ],
                WorkZoneType.STATIC,
            )
        case (
            "Culvert Maintenance"
            | "Electrical or Lighting"
            | "Emergency Maintenance"
            | "Rock Work"
            | "Sign Work"
            | "Traffic Sign Installation"
            | "Traffic Sign Maintenance"
            | "Traffic Signal Installation"
            | "Traffic Signal Maintenance"
            | "Utility Work"
            | "Utility Installation"
        ):
            return (
                [
                    TypeOfWork(
                        type_name=WorkTypeName.ROADSIDE_WORK,
                        is_architectural_change=False,
                    )
                ],
                WorkZoneType.STATIC,
            )
        case "Striping Operations":
            return (
                [
                    TypeOfWork(
                        type_name=WorkTypeName.PAINTING, is_architectural_change=True
                    )
                ],
                WorkZoneType.PLANNED_MOVING_AREA,
            )
        case "Tunnel Maintenance":
            return (
                [
                    TypeOfWork(
                        type_name=WorkTypeName.SURFACE_WORK,
                        is_architectural_change=False,
                    )
                ],
                WorkZoneType.STATIC,
            )
        case "Wall Maintenance":
            return (
                [
                    TypeOfWork(
                        type_name=WorkTypeName.BARRIER_WORK,
                        is_architectural_change=False,
                    )
                ],
                WorkZoneType.STATIC,
            )
        # Road Closures
        case (
            "BAN Message"
            | "Safety Campaign"
            | "Smoke/Control Burn"
            | "Avalanche Control"
            | "Closed for the Season"
            | "Funeral Procession"
            | "Presidential Visit"
            | "Race Event"
            | "Local Event"
            | "Military Movement"
            | "OS/OW Limit"
            | "Geological Drilling"
        ):
            return None

        # Incidents (work zones): *\(.]n
        case "Emergency Roadwork" | "Maintenance Operations":
            return (
                [],
                WorkZoneType.STATIC,
            )
        case _:
            logging.warning(f"Unrecognized event type: {event_type}")
            return (
                [],
                WorkZoneType.STATIC,
            )


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
) -> Direction:
    """Map a direction string to a standard direction string

    Args:
        direction_string (str): direction string, like 'north', 'south', 'east', 'west'

    Returns:
        Direction: standard direction enum
    """
    return STRING_DIRECTION_MAP.get(direction_string, Direction.UNDEFINED)


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
                "type": LaneType.SHOULDER,
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
                    closedLaneTypes[i]
                    if (len(closedLaneTypes) > i)
                    else LaneType.GENERAL
                ).value,
                "status": map_lane_status(bit),
            }
        )
        order += 1
    if map_lane_status(lanes_affected[15]) == "closed":
        lanes.append(
            {
                "order": order,
                "type": LaneType.SHOULDER,
                "status": map_lane_status(lanes_affected[15]),
            }
        )
        order += 1
    return lanes


def update_lanes_alternating_traffic(lanes: list[dict]) -> list[dict]:
    """Update lanes to indicate alternating traffic. Lane order 1 should be "alternating-flow", all other lanes should be "closed".

    Args:
        lanes (list[dict]): WZDx lanes list

    Returns:
        list[dict]: updated WZDx lanes list with alternating traffic
    """
    for lane in lanes:
        if lane["order"] == 1:
            lane["status"] = LaneStatus.ALTERNATING_FLOW.value
        else:
            lane["status"] = LaneStatus.CLOSED.value
    return lanes


def detect_alternating_traffic(additional_impacts: list[dict]) -> bool:
    """Check if there are any lane impacts indicating alternating traffic

    Args:
        lane_impacts (list[dict]): Planned event lane impacts

    Returns:
        bool: whether there are any alternating traffic impacts
    """
    if not additional_impacts:
        return False
    return "Alternating traffic" in additional_impacts


def get_lane_impacts(
    lane_impacts: list[dict],
    direction: Literal["undefined", "east", "west", "north", "south"],
    has_alternating_traffic: bool,
) -> list[dict]:
    """Get WZDx lane list from list of lane impacts and direction. If has_alternating_traffic is True, one lane will show alternating-flow while all other lanes will be closed

    Args:
        lane_impacts (list[dict]): Planned event lane impacts
        direction (Literal["undefined", "east", "west", "north", "south"]): Planned event direction

    Returns:
        list[dict]: _description_
    """
    for impact in lane_impacts:
        if impact["direction"] == direction:
            lanes = get_lanes_list(
                impact["laneClosures"], impact["laneCount"], impact["closedLaneTypes"]
            )
            if has_alternating_traffic:
                lanes = update_lanes_alternating_traffic(lanes)
            return lanes


def get_vehicle_impact(
    lanes: list[dict], has_alternating_traffic: bool
) -> VehicleImpact:
    """Determine the impact of lane closures on vehicle traffic and possible alternating traffic indicated by description

    Args:
        lanes (list[dict]): List of lane objects
        has_alternating_traffic (bool): Whether the event has alternating traffic

    Returns:
        str: Vehicle impact status
    """
    num_lanes = len(lanes)
    num_closed_lanes = 0

    # Specific phrase injected into descriptions. Want to match contents of auto-generated message, not the comment
    if has_alternating_traffic:
        return VehicleImpact.ALTERNATING_ONE_WAY

    for i in lanes:
        if i["status"] != "open":
            num_closed_lanes += 1
    if num_closed_lanes == num_lanes:
        return VehicleImpact.ALL_LANES_CLOSED
    elif num_closed_lanes == 0:
        return VehicleImpact.ALL_LANES_OPEN
    else:
        return VehicleImpact.SOME_LANES_CLOSED


def all_lanes_open(lanes: list[dict]) -> bool:
    """Check if all lanes are open, or if the description indicates alternating traffic

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


def _get_street_name_from_substring(substring: str) -> str:
    """Get street name from a substring
    Examples:
    - Exit 263: Colorado Mills Parkway (West Pleasant View) -> Colorado Mills Parkway
    - Exit 260: C-470 (1 mile west of Golden) -> C-470
    - C-470 (Golden) -> C-470
    - Exit 254: US 40; Genesee (Genesee) -> US 40

    Args:
        substring (str): substring containing street name

    Returns:
        str: street name
    """
    if ":" in substring:
        substring = substring.split(":")[1]
    substring = substring.split("(")[0]
    substring = substring.split(";")[0]
    return substring.strip()


def get_cross_streets_from_description(description: str) -> tuple[str, str]:
    """Get cross streets from a description string using regular expression "^Between (.*?) and (.*?)(?= from)"

    Args:
        description (str): description string

    Returns:
        tuple[str, str]: beginning cross street, ending cross street
    """
    desc_regex = "^Between (.*?) and (.*?)(?= from | at )"
    m = regex.search(desc_regex, description)
    try:
        return (_get_street_name_from_substring(s) for s in m.group(1, 2))
    except (AttributeError, IndexError):
        return ("", "")


def get_mileposts_from_description(description: str) -> tuple[str, str]:
    """Get mileposts from a description string using regular expression "^from Mile Point ([0-9.]{0-6}) to Mile Point ([0-9.]{0-6})."
    Args:
        description (str): description string
    Returns:
        tuple[str, str]: beginning milepost, ending milepost
    """
    start_regex = "( from | at )Mile Point ([0-9.]+)( to|\\. )"
    end_regex = "( to | at )Mile Point ([0-9.]+)\\."
    start_m = regex.search(start_regex, description)
    end_m = regex.search(end_regex, description)
    try:
        m1 = start_m.group(2)
        m2 = end_m.group(2)
        return float(m1), float(m2)
    except (AttributeError, IndexError):
        return (None, None)


def get_route_details_for_coordinates_lngLat(
    cdotGeospatialApi: cdot_geospatial_api.GeospatialApi,
    coordinates: list[list[float]],
) -> tuple[dict, dict]:
    """Get GIS route details for start and end coordinates

    Args:
        cdotGeospatialApi (cdot_geospatial_api.GeospatialApi): customized GeospatialApi object, for retrieving route details
        coordinates (list[list[float]]): planned event coordinates

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

        # Update route suffixes based on directionality
        if not cdot_geospatial_api.GeospatialApi.is_route_dec(
            route_details_start["Measure"], route_details_end["Measure"]
        ):
            route_details_start["Route"] = route_details_start["Route"].replace(
                "_DEC", ""
            )
            route_details_end["Route"] = route_details_end["Route"].replace("_DEC", "")
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
        description = pd.get("properties/travelerInformationMessage", default="")
        if not description or description == INVALID_EVENT_DESCRIPTION:
            description = create_description(
                pd.get("properties/name"),
                pd.get("properties/routeName"),
                pd.get("properties/startMarker"),
                pd.get("properties/endMarker"),
                pd.get("properties/type"),
                pd.get("properties/startTime"),
                pd.get("properties/clearTime"),
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

        beginning_milepost = pd.get("properties/startMarker")
        ending_milepost = pd.get("properties/endMarker")
        recorded_direction = pd.get("properties/recorded_direction")
        geometry_direction = geospatial_tools.get_road_direction_from_coordinates(
            coordinates
        )

        additional_impacts = pd.get("properties/additionalImpacts", [])
        has_alternating_traffic = detect_alternating_traffic(additional_impacts)
        lane_impacts = get_lane_impacts(
            pd.get("properties/laneImpacts"),
            pd.get("properties/direction"),
            has_alternating_traffic,
        )
        if direction != recorded_direction and all_lanes_open(lane_impacts):
            logging.info(
                f'Unable to retrieve geometry coordinates for event: {pd.get("properties/id", default="")}'
            )
            return {}

        if (
            direction == REVERSED_DIRECTION_MAP.get(geometry_direction)
            and direction != "unknown"
        ):
            coordinates.reverse()
            beginning_milepost = pd.get("properties/endMarker")
            ending_milepost = pd.get("properties/startMarker")

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

        types_of_work, work_zone_type = map_event_type(
            pd.get("properties/type", default="")
        )

        restrictions = []
        if pd.get("properties/isOversizedLoadsProhibited"):
            restrictions.append({"type": "permitted-oversize-loads-prohibited"})

        event_status = date_tools.get_event_status(start_date, end_date)

        condition_1 = event_status in ["active", "pending", "planned"]

        route_details_start, route_details_end = (
            get_route_details_for_coordinates_lngLat(cdotGeospatialApi, coordinates)
        )

        # Milepost Priority:
        # 1. Route Details (only if start and end are on the same route)
        # 2. properties/startMarker and properties/endMarker
        # 3. Description parsing
        beginning_milepost_from_description, ending_milepost_description = (
            get_mileposts_from_description(description)
        )
        if (
            route_details_start
            and route_details_end
            and route_details_start["Route"] == route_details_end["Route"]
        ):
            beginning_milepost = route_details_start["Measure"]
            ending_milepost = route_details_end["Measure"]

        if not beginning_milepost:
            beginning_milepost = beginning_milepost_from_description
        if not ending_milepost:
            ending_milepost = ending_milepost_description

        return {
            "rtdh_timestamp": time.time(),
            "rtdh_message_id": str(uuid.uuid4()),
            "event": {
                "type": EventType.WORK_ZONE.value,
                "types_of_work": [tow.to_dict() for tow in types_of_work],
                "work_zone_type": (
                    work_zone_type.value if work_zone_type is not None else None
                ),
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
                    "vehicle_impact": get_vehicle_impact(
                        lane_impacts, has_alternating_traffic
                    ).value,
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
        logging.error(
            f'Error occurred generating standard message for message {pd.get("properties/id", default="")}: {e}'
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
    if not obj or (type(obj) is not dict and type(obj) is not OrderedDict):
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
            f"Invalid event with id = {id}. Error occurred while validating: {e}"
        )
        return False

    return True


if __name__ == "__main__":
    main()

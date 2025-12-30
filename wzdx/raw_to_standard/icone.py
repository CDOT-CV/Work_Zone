import argparse
import datetime
import json
import logging
import time
import uuid
import xml.etree.ElementTree as ET
from collections import OrderedDict

from ..tools import date_tools, geospatial_tools, wzdx_translator, combination
from ..util.collections import PathDict

PROGRAM_NAME = "iConeRawToStandard"
PROGRAM_VERSION = "1.0"


def main():
    input_file, output_dir = parse_rtdh_arguments()
    input_file_contents = open(input_file, "r").read()
    generated_messages = generate_standard_messages_from_string(input_file_contents)

    generated_files_list = []
    features = []

    for message in generated_messages:
        output_path = f"{output_dir}/icone_{message['event']['source']['id']}_{round(message['rtdh_timestamp'])}_{message['event']['detail']['direction']}.json"
        open(output_path, "w+").write(json.dumps(message, indent=2))
        generated_files_list.append(output_path)

        features.append(
            {
                "type": "Feature",
                "properties": {
                    "id": message["event"]["source"]["id"],
                    "route_details": message["event"]["additional_info"][
                        "route_details_start"
                    ],
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": message["event"]["geometry"][0],
                },
            }
        )

    open(f"{output_dir}/icone_feature_collection.geojson", "w+").write(
        json.dumps(features, indent=2)
    )

    if generated_files_list:
        print(f"Successfully generated standard message files: {generated_files_list}")
    else:
        print(
            "Warning: Standard message generation failed. See logging messages printed above"
        )


def generate_standard_messages_from_string(input_file_contents: str):
    """Generate RTDH standard messages from iCone XML string

    Args:
        input_file_contents: iCone XML string data
    """
    raw_messages = generate_raw_messages(input_file_contents)
    standard_messages = []
    for message in raw_messages:
        standard_messages.append(
            generate_rtdh_standard_message_from_raw_single(message)
        )
    return standard_messages


def generate_raw_messages(message: str):
    """Parse iCone XML string and return list of validated xml incidents

    Args:
        message: iCone XML string data
    """
    response_xml = ET.fromstring(message)
    msg_lst = response_xml.findall("incident")
    messages = []

    # Loop through all elements and print each element to PubSub
    for msg in msg_lst:
        incident = ET.tostring(msg, encoding="utf8")
        obj = wzdx_translator.parse_xml_to_dict(incident)
        if validate_incident(obj.get("incident", {})):
            messages.append(incident)
        else:
            logging.warning("Invalid message")

    return messages


def generate_rtdh_standard_message_from_raw_single(raw_message_xml: str) -> dict:
    """Generate RTDH standard message from iCone XML string

    Args:
        raw_message_xml: xml string iCone incident

    Returns:
        dict: RTDH standard message
    """
    obj = wzdx_translator.parse_xml_to_dict(raw_message_xml)
    pd = PathDict(obj)
    standard_message = create_rtdh_standard_msg(pd)
    return standard_message


# parse script command line arguments
def parse_rtdh_arguments() -> tuple[str, str]:
    """Parse command line arguments for iCone to RTDH Standard translation

    Returns:
        tuple[str, str]: iCone file path, output directory
    """
    parser = argparse.ArgumentParser(
        description="Translate iCone data to RTDH Standard"
    )
    parser.add_argument(
        "--version", action="version", version=f"{PROGRAM_NAME} {PROGRAM_VERSION}"
    )
    parser.add_argument("iconeFile", help="icone file path")
    parser.add_argument(
        "--outputDir", required=False, default="./", help="output directory"
    )

    args = parser.parse_args()
    return args.iconeFile, args.outputDir


# function to parse polyline to geometry line string
# input: "37.1571990,-84.1128540,37.1686478,-84.1238971" (lat, long)
# output: [[-84.1128540, 37.1571990], [-84.1238971, 37.1686478]] (long, lat)
def parse_icone_polyline(polylineString: list[float]):
    """Parse iCone polyline string to geometry line string

    Args:
        polylineString: iCone polyline string
    """
    if not polylineString or type(polylineString) is not str:
        return None
    # polyline right now is a list which has an empty string in it.
    polyline = polylineString.split(",")
    coordinates = []
    for i in range(0, len(polyline) - 1, 2):
        try:
            coordinates.append([float(polyline[i + 1]), float(polyline[i])])
        except ValueError:
            logging.warning("failed to parse polyline!")
            return []
    return coordinates


def get_sensor_list(incident: dict | OrderedDict):
    """Get list of sensors from iCone incident

    Args:
        incident: iCone incident object
    """
    devices = []
    for key in ["sensor", "radar", "display", "message", "marker", "status"]:
        obj = incident.get(f"{key}")
        if type(obj) in [dict, OrderedDict]:
            devices.append({"sensor_type": key, "details": obj})
        elif type(obj) is list:
            for i in obj:
                devices.append({"sensor_type": key, "details": i})
    return devices


def create_rtdh_standard_msg(pd: PathDict):
    """Create RTDH standard message from iCone incident pathDict

    Args:
        pd: iCone incident pathDict
    """
    devices = get_sensor_list(pd.get("incident"))
    start_time = pd.get(
        "incident/starttime", date_tools.parse_datetime_from_iso_string, default=None
    )
    end_time = pd.get(
        "incident/endtime", date_tools.parse_datetime_from_iso_string, default=None
    )
    if not end_time:
        if start_time > datetime.datetime.now(datetime.timezone.utc):
            end_time = start_time + datetime.timedelta(days=7)
        else:
            end_time = datetime.datetime.now(
                datetime.timezone.utc
            ) + datetime.timedelta(days=7)
        # Added for unit test
        end_time = end_time.replace(second=0, microsecond=0)

    coordinates = pd.get("incident/location/polyline", parse_icone_polyline)

    route_details_start, route_details_end = (
        combination.get_route_details_for_coordinates_lngLat(coordinates)
    )

    direction = get_direction(
        pd.get("incident/location/street"), coordinates, route_details_start
    )

    road_name = pd.get("incident/location/street")
    if not road_name:
        road_name = get_road_name(route_details_start)

    return {
        "rtdh_timestamp": time.time(),
        "rtdh_message_id": str(uuid.uuid4()),
        "event": {
            "type": pd.get("incident/type", default=""),
            "source": {
                "id": pd.get("incident/@id", default=""),
                "creation_timestamp": pd.get(
                    "incident/creationtime",
                    date_tools.get_unix_from_iso_string,
                    default=0,
                ),
                "last_updated_timestamp": pd.get(
                    "incident/updatetime",
                    date_tools.get_unix_from_iso_string,
                    default=0,
                ),
            },
            "geometry": pd.get("incident/location/polyline", parse_icone_polyline),
            "header": {
                "description": pd.get("incident/description", default=""),
                "start_timestamp": date_tools.date_to_unix(start_time),
                "end_timestamp": date_tools.date_to_unix(end_time),
            },
            "detail": {
                "road_name": road_name,
                "road_number": road_name,
                "direction": direction,
            },
            "additional_info": {
                "devices": devices,
                "directionality": pd.get("incident/location/direction"),
                "route_details_start": route_details_start,
                "route_details_end": route_details_end,
                "condition_1": True,
            },
        },
    }


def get_direction(street: str, coords: list[float], route_details=None):
    """Get road direction from street, coordinates, or route details

    Args:
        street: Roadway name to pull direction from (I-25 NB, I-25 SB, etc.)
        coords: Coordinates to pull direction from
        route_details: Optional GIS route details to pull direction from. Defaults to None.

    Returns:
        Literal['unknown', 'eastbound', 'westbound', 'northbound', 'southbound']: direction of roadway
    """
    direction = wzdx_translator.parse_direction_from_street_name(street)
    if (not direction or direction == "unknown") and route_details:
        direction = get_direction_from_route_details(route_details)
    if not direction or direction == "unknown":
        direction = geospatial_tools.get_road_direction_from_coordinates(coords)
    return direction


def get_road_name(route_details: dict) -> str | None:
    """Get road name from GIS route details

    Args:
        route_details: GIS route details
    Returns:
        str | None: road name
    """
    return route_details.get("Route")


def get_direction_from_route_details(route_details: dict) -> str:
    """Get direction from GIS route details

    Args:
        route_details (dict): GIS route details

    Returns:
        str: direction | "unknown"
    """
    return route_details.get("Direction", "unknown")


# function to validate the incident
def validate_incident(incident: dict | OrderedDict):
    """Validate iCone Incident against predefined set of rules (see below)

    Args:
        incident: iCone incident object

    Returns:
        bool: True if incident is valid, False otherwise

    Validation Rules:
    - Incident must have a location object
    - Incident must have a polyline object
    - Incident must have a starttime field
    - Incident must have a description field
    - Incident must have a creationtime field
    - Incident must have an updatetime field
    - Incident must have a valid direction (parsable from street name or polyline)
    - Incident must have a valid start time (parsable from ISO string)
    - Incident must have a valid end time (parsable from ISO string)
    """
    if not incident or (
        type(incident) is not dict and type(incident) is not OrderedDict
    ):
        logging.warning("incident is empty or has invalid type")
        return False

    id = incident.get("@id")

    location = incident.get("location")
    if not location:
        logging.warning(f"Invalid incident with id = {id}. Location object not present")
        return False

    polyline = location.get("polyline")
    coords = parse_icone_polyline(polyline)
    street = location.get("street", "")

    starttime_string = incident.get("starttime")
    endtime_string = incident.get("endtime")
    description = incident.get("description")
    creationtime = incident.get("creationtime")
    updatetime = incident.get("updatetime")
    direction = get_direction(street, coords)
    if not direction:
        logging.warning(
            f"Invalid incident with id = {id}. unable to parse direction from street name or polyline"
        )
        return False

    required_fields = [
        location,
        polyline,
        coords,
        starttime_string,
        description,
        creationtime,
        updatetime,
    ]
    for field in required_fields:
        if not field:
            logging.warning(
                f"""Invalid incident with id = {id}. Not all required fields are present. Required fields are:
                location, polyline, starttime, description, creationtime, and updatetime"""
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

    return True


if __name__ == "__main__":
    main()

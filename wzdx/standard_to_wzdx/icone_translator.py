import argparse
import json
import logging
import copy
from typing import Literal
import uuid

from wzdx.models.enums import LocationMethod

from ..tools import date_tools, wzdx_translator

PROGRAM_NAME = "WZDxIconeTranslator"
PROGRAM_VERSION = "1.0"


def main():
    input_file, output_file = parse_icone_arguments()

    icone_obj = json.loads(open(input_file, "r").read())
    wzdx = wzdx_creator(icone_obj)

    if not wzdx:
        print("Error: WZDx message generation failed, see logs for more information.")
    else:
        with open(output_file, "w") as fWzdx:
            fWzdx.write(json.dumps(wzdx, indent=2))
            print(
                "Your wzdx message was successfully generated and is located here: "
                + str(output_file)
            )


# parse script command line arguments
def parse_icone_arguments() -> tuple[str, str]:
    """Parse command line arguments for standard RTDH iCone data translation to WZDx

    Returns:
        tuple[str, str]: iCone file path, output file path
    """
    parser = argparse.ArgumentParser(description="Translate iCone data to WZDx")
    parser.add_argument(
        "--version", action="version", version=f"{PROGRAM_NAME} {PROGRAM_VERSION}"
    )
    parser.add_argument("iconeFile", help="icone file path")
    parser.add_argument(
        "--outputFile",
        required=False,
        default="icone_wzdx_translated_output_message.geojson",
        help="output file path",
    )

    args = parser.parse_args()
    return args.iconeFile, args.outputFile


def wzdx_creator(message: dict, info: dict = None) -> dict:
    """Translate standard RTDH iCone data to WZDx

    Args:
        message (dict): iCone data
        info (dict, optional): WZDx info object. Defaults to None.

    Returns:
        dict: WZDx object
    """
    if not message or not validate_standard_msg(message):
        return None

    if not info:
        info = wzdx_translator.initialize_info()
    if not wzdx_translator.validate_info(info):
        return None

    wzdx = wzdx_translator.initialize_wzdx_object(info)

    # Parse Incident to WZDx Feature
    feature = parse_incident(message)
    if feature:
        wzdx.get("features").append(feature)

    if not wzdx.get("features"):
        return None
    wzdx = wzdx_translator.add_ids(wzdx)

    if not wzdx_translator.validate_wzdx(wzdx):
        logging.warning("WZDx message failed validation")
        return None

    return wzdx


#################### Sample Incident ####################
#   <incident id="U13631714_202012161717">
#     <creationtime>2020-12-16T17:17:00Z</creationtime>
#     <updatetime>2020-12-16T17:47:00Z</updatetime>
#     <type>CONSTRUCTION</type>
#     <description>Roadwork - Lane Closed, MERGE LEFT [iCone]</description>
#     <location>
#       <direction>ONE_DIRECTION</direction>
#       <polyline>[28.8060608,-96.9916512,28.8060608,-96.9916512]</polyline>
#     </location>
#     <starttime>2020-12-16T17:17:00Z</starttime>
#   </incident>


# {
#     "rtdh_timestamp": 1633097202.1872184,
#     "rtdh_message_id": "bffd71cd-d35a-45c2-ba4d-a86e1ff12847",
#     "event": {
#         "type": "CONSTRUCTION",
#         "source": {
#         "id": 1245,
#         "last_updated_timestamp": 1598046722
#         },
#         "geometry": "",
#         "header": {
#         "description": "19-1245: Roadwork between MP 40 and MP 48",
#         "start_timestamp": 1581725296,
#         "end_timestamp": null
#         },
#         "detail": {
#         "road_name": "I-75 N",
#         "road_number": "I-75 N",
#         "direction": null
#         }
#     }
# }


# function to calculate vehicle impact
def get_vehicle_impact(
    description: str,
) -> Literal["all-lanes-open", "some-lanes-closed"]:
    """Calculate vehicle impact based on description

    Args:
        description (str): Incident description

    Returns:
        Literal["all-lanes-open", "some-lanes-closed"]: Vehicle impact
    """
    vehicle_impact = "all-lanes-open"
    if "lane closed" in description.lower():
        vehicle_impact = "some-lanes-closed"
    return vehicle_impact


# function to get description
def create_description(incident: dict) -> str:
    """Create description from incident

    Args:
        incident (dict): RTDH standard incident object

    Returns:
        str: Description
    """
    description = incident.get("description")

    if incident.get("sensor"):
        description += "\n sensors: "
        for sensor in incident.get("sensor"):
            if not isinstance(sensor, str):
                if sensor["@type"] == "iCone":
                    description += "\n" + json.dumps(
                        parse_icone_sensor(sensor), indent=2
                    )
            else:
                sensor = incident.get("sensor")
                if sensor["@type"] == "iCone":
                    description += "\n" + json.dumps(
                        parse_icone_sensor(sensor), indent=2
                    )

    if incident.get("display"):
        description += "\n displays: "
        for display in incident.get("display"):
            if not isinstance(display, str):
                if display["@type"] == "PCMS":
                    description += "\n" + json.dumps(
                        parse_pcms_sensor(display), indent=2
                    )  # add baton,ab,truck beacon,ipin,signal
            else:
                display = incident.get("display")
                if display["@type"] == "PCMS":
                    description += "\n" + json.dumps(
                        parse_pcms_sensor(display), indent=2
                    )  # add baton,ab,truck beacon,ipin,signal

    return description


def parse_icone_sensor(sensor: dict) -> dict:
    """Parse iCone sensor data

    Args:
        sensor (dict): iCone sensor data

    Returns:
        dict: Parsed iCone sensor data
    """
    icone = {}
    icone["type"] = sensor.get("@type")
    icone["id"] = sensor.get("@id")
    icone["location"] = [
        float(sensor.get("@latitude")),
        float(sensor.get("@longitude")),
    ]

    if sensor.get("radar", None):
        avg_speed = 0
        std_dev_speed = 0
        num_reads = 0
        for radar in sensor.get("radar"):
            timestamp = ""
            if not isinstance(radar, str):
                curr_reads = int(radar.get("@numReads"))
                if curr_reads == 0:
                    continue
                curr_avg_speed = float(radar.get("@avgSpeed"))
                curr_dev_speed = float(radar.get("@stDevSpeed"))
                total_num_reads = num_reads + curr_reads
                avg_speed = (
                    avg_speed * num_reads + curr_avg_speed * curr_reads
                ) / total_num_reads
                std_dev_speed = (
                    std_dev_speed * num_reads + curr_dev_speed * curr_reads
                ) / total_num_reads
                num_reads = total_num_reads
                timestamp = radar.get("@intervalEnd")
            else:
                radar = sensor.get("radar")
                avg_speed = float(radar.get("@avgSpeed"))
                std_dev_speed = float(radar.get("@stDevSpeed"))
                timestamp = radar.get("@intervalEnd")

        radar = {}

        radar["average_speed"] = round(avg_speed, 2)
        radar["std_dev_speed"] = round(std_dev_speed, 2)
        radar["timestamp"] = timestamp
        icone["radar"] = radar
    return icone


def parse_pcms_sensor(sensor: dict) -> dict:
    """Parse PCMS sensor data

    Args:
        sensor (dict): iCone PCMS sensor data

    Returns:
        dict: Parsed PCMS sensor data
    """
    pcms = {}
    pcms["type"] = sensor.get("@type")
    pcms["id"] = sensor.get("@id")
    pcms["timestamp"] = sensor.get("@id")
    pcms["location"] = [float(sensor.get("@latitude")), float(sensor.get("@longitude"))]
    if sensor.get("message", None):
        pcms["messages"] = []
        for message in sensor.get("message"):
            if not isinstance(message, str):
                pcms["timestamp"] = message.get("@verified")
                if message.get("@text") not in pcms.get("messages"):
                    pcms.get("messages").append(message.get("@text"))
            else:
                message = sensor.get("message")
                pcms["timestamp"] = message.get("@verified")
                if message["@text"] not in pcms.get("messages"):
                    pcms.get("messages").append(message.get("@text"))
    return pcms


# Parse Icone Incident to WZDx
def parse_incident(incident: dict) -> dict:
    """Parse iCone incident to WZDx feature

    Args:
        incident (dict): standard RTDH iCone incident

    Returns:
        dict: WZDx feature
    """
    event = incident.get("event")

    source = event.get("source")
    header = event.get("header")
    detail = event.get("detail")
    additional_info = event.get("additional_info", {})

    geometry = {}
    geometry["type"] = "LineString"
    geometry["coordinates"] = event.get("geometry")
    properties = wzdx_translator.initialize_feature_properties()

    # I included a skeleton of the message, fill out all required fields and as many optional fields as you can. Below is a link to the spec page for a road event
    # https://github.com/usdot-jpo-ode/jpo-wzdx/blob/master/spec-content/objects/RoadEvent.md

    core_details = properties["core_details"]

    # Event Type ['work-zone', 'detour']
    core_details["event_type"] = "work-zone"

    # data_source_id - Leave this empty, it will be populated by add_ids
    core_details["data_source_id"] = ""

    # road_name
    road_names = [detail.get("road_name")]
    core_details["road_names"] = road_names

    # direction
    core_details["direction"] = detail.get("direction")

    # related_road_events - current approach generates a individual disconnected events, so no links are generated
    core_details["related_road_events"] = []

    # description
    core_details["description"] = header.get("description")

    # creation_date
    core_details["creation_date"] = date_tools.get_iso_string_from_unix(
        source.get("creation_timestamp")
    )

    # update_date
    core_details["update_date"] = date_tools.get_iso_string_from_unix(
        source.get("last_updated_timestamp")
    )

    # core_details
    properties["core_details"] = core_details

    start_time = date_tools.parse_datetime_from_unix(header.get("start_timestamp"))
    end_time = date_tools.parse_datetime_from_unix(header.get("end_timestamp"))

    # start_date
    properties["start_date"] = date_tools.get_iso_string_from_datetime(start_time)

    # end_date
    if end_time:
        properties["end_date"] = date_tools.get_iso_string_from_datetime(end_time)
    else:
        properties["end_date"] = None

    # is_start_date_verified
    properties["is_start_date_verified"] = False

    # is_end_date_verified
    properties["is_end_date_verified"] = False

    # is_start_position_verified
    properties["is_start_position_verified"] = False

    # is_end_position_verified
    properties["is_end_position_verified"] = False

    # location_method
    properties["location_method"] = LocationMethod.CHANNEL_DEVICE_METHOD

    # vehicle impact
    properties["vehicle_impact"] = get_vehicle_impact(header.get("description"))

    # lanes
    properties["lanes"] = []

    # beginning_cross_street
    properties["beginning_cross_street"] = ""

    # beginning_cross_street
    properties["ending_cross_street"] = ""

    # beginning_cross_street
    properties["beginning_milepost"] = ""

    # beginning_cross_street
    properties["ending_milepost"] = ""

    # type_of_work
    # maintenance, minor-road-defect-repair, roadside-work, overhead-work, below-road-work, barrier-work, surface-work, painting, roadway-relocation, roadway-creation
    properties["types_of_work"] = []

    # worker_presence - not available

    # reduced_speed_limit_kph - not available

    # restrictions
    properties["restrictions"] = []

    properties["route_details_start"] = additional_info.get("route_details_start")
    properties["route_details_end"] = additional_info.get("route_details_end")

    properties["condition_1"] = additional_info.get("condition_1", True)

    filtered_properties = copy.deepcopy(properties)

    INVALID_PROPERTIES = [None, "", []]

    for key, value in properties.items():
        if value in INVALID_PROPERTIES:
            del filtered_properties[key]

    for key, value in properties["core_details"].items():
        if not value and key not in ["data_source_id"]:
            del filtered_properties["core_details"][key]

    feature = {}
    feature["id"] = event.get("source", {}).get("id", uuid.uuid4())
    feature["type"] = "Feature"
    feature["properties"] = filtered_properties
    feature["geometry"] = geometry

    return feature


# function to validate the event
def validate_standard_msg(msg: dict) -> bool:
    """Validate the event

    Args:
        msg (dict): Event message

    Returns:
        bool: True if event is valid, False otherwise
    """
    if not msg or type(msg) is not dict:
        logging.warning("event is empty or has invalid type")
        return False

    event = msg.get("event")

    source = event.get("source")
    header = event.get("header")
    detail = event.get("detail")

    id = source.get("id")
    try:

        event = msg.get("event")

        source = event.get("source")
        header = event.get("header")
        detail = event.get("detail")

        id = source.get("id")

        geometry = event.get("geometry")
        road_name = detail.get("road_name")

        start_time = header.get("start_timestamp")
        end_time = header.get("end_timestamp")
        description = header.get("description")
        update_time = source.get("last_updated_timestamp")
        direction = detail.get("direction")

        if not (type(geometry) is list and len(geometry) >= 0):
            logging.warning(
                f"""Invalid event with id = {id}. Invalid geometry: {geometry}"""
            )
            return False
        if not (type(road_name) is str and len(road_name) >= 0):
            logging.warning(
                f"""Invalid event with id = {id}. Invalid road_name: {road_name}"""
            )
            return False
        if not (type(start_time) is float or type(start_time) is int):
            logging.warning(
                f"""Invalid event with id = {id}. Invalid start_time: {start_time}"""
            )
            return False
        if not (type(end_time) is float or type(end_time) is int or end_time is None):
            logging.warning(
                f"""Invalid event with id = {id}. Invalid end_time: {end_time}"""
            )
            return False
        if not (type(update_time) is float or type(update_time) is int):
            logging.warning(
                f"""Invalid event with id = {id}. Invalid update_time: {update_time}"""
            )
            return False
        if not (
            type(direction) is str
            and direction
            in [
                "unknown",
                "undefined",
                "northbound",
                "southbound",
                "eastbound",
                "westbound",
            ]
        ):
            logging.warning(
                f"""Invalid event with id = {id}. Invalid direction: {direction}"""
            )
            return False
        if not (type(description) is str and len(description) >= 0):
            logging.warning(
                f"""Invalid event with id = {id}. Invalid description: {description}"""
            )
            return False

        return True
    except Exception as e:
        logging.warning(f"""Invalid event with id = {id}. Error in validation: {e}""")
        return False


if __name__ == "__main__":
    main()

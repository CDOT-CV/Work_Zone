import argparse
import json
import logging
import copy

from ..sample_files.validation_schema import connected_work_zone_feed_v10

from ..tools import date_tools, cwz_translator, uuid_tools

PROGRAM_NAME = "CWZPlannedEventsTranslator"
PROGRAM_VERSION = "1.0"


def main():
    input_file, output_file = parse_planned_events_arguments()

    planned_events_obj = json.loads(open(input_file, "r").read())
    cwz_feed = cwz_creator(planned_events_obj)

    if not cwz_feed:
        print("Error: CWZ message generation failed, see logs for more information.")
    else:
        with open(output_file, "w") as f:
            f.write(json.dumps(cwz_feed, indent=2))
            print(
                "Your connected work zone message was successfully generated and is located here: "
                + str(output_file)
            )


# parse script command line arguments
def parse_planned_events_arguments() -> tuple[str, str]:
    """Parse command line arguments for Planned Event data translation

    Returns:
        tuple[str, str]: Planned Event file path, output file path
    """
    parser = argparse.ArgumentParser(description="Translate Planned Event data to CWZ")
    parser.add_argument(
        "--version", action="version", version=f"{PROGRAM_NAME} {PROGRAM_VERSION}"
    )
    parser.add_argument("plannedEventsFile", help="planned_events file path")
    parser.add_argument(
        "--outputFile",
        required=False,
        default="planned_events_cwz_translated_output_message.geojson",
        help="output file path",
    )

    args = parser.parse_args()
    return args.plannedEventsFile, args.outputFile


def cwz_creator(message: dict, info: dict | None = None) -> dict | None:
    """Translate Planned Event data to CWZ

    Args:
        message (dict): Planned Event data
        info (dict, optional): CWZ info object. Defaults to None.

    Returns:
        dict: CWZ object
    """
    if not message:
        return None
    event_type = message["event"]["type"]

    # verify info obj
    if not info:
        info = cwz_translator.initialize_info()
    if not cwz_translator.validate_info(info):
        return None

    if event_type == "work-zone":
        wzd = cwz_translator.initialize_feed_object(info)
        feature = parse_work_zone(message)
    else:
        logging.warning(f"Unrecognized event type: {message['event']['type']}")
        return None

    if feature:
        wzd.get("features", []).append(feature)
    if not wzd.get("features"):
        return None
    wzd = cwz_translator.add_ids(wzd)

    if not cwz_translator.validate_feed(
        wzd, connected_work_zone_feed_v10.connected_work_zone_feed_v10_schema_string
    ):
        logging.warning("CWZ message failed validation")
        return None

    return wzd


# Parse Icone Incident to CWZ
def parse_work_zone(incident: dict) -> dict | None:
    """Translate Planned Events RTDH standard work zone to CWZ

    Args:
        incident (dict): Planned event event data

    Returns:
        dict: CWZ object
    """
    if not incident or type(incident) is not dict:
        return None

    event = incident.get("event")

    source = event.get("source")
    header = event.get("header")
    detail = event.get("detail")
    additional_info = event.get("additional_info", {})

    geometry = {
        "type": "LineString",
        "coordinates": event.get("geometry", []),
    }
    properties = cwz_translator.initialize_feature_properties()

    core_details = properties["core_details"]

    # Event Type ['work-zone', 'detour']
    core_details["event_type"] = event.get("type")

    # data_source_id - Leave this empty, it will be populated by add_ids
    core_details["data_source_id"] = ""

    # road_name
    road_names = [detail.get("road_name")]
    core_details["road_names"] = road_names

    # direction
    core_details["direction"] = detail.get("direction", "unknown")

    # related_road_events
    core_details["related_road_events"] = []

    # name
    core_details["name"] = event.get("source", {}).get("id", None)

    # description
    core_details["description"] = header.get("description")

    # creation_date - not available

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
    properties["end_date"] = date_tools.get_iso_string_from_datetime(end_time)

    # is_start_date_verified
    properties["is_start_date_verified"] = False

    # is_end_date_verified
    properties["is_end_date_verified"] = False

    # is_start_position_verified
    properties["is_start_position_verified"] = False

    # is_end_position_verified
    properties["is_end_position_verified"] = False

    # location_method
    properties["location_method"] = "channel-device-method"

    # work_zone_type
    properties["work_zone_type"] = event.get("work_zone_type", "static")

    # vehicle impact
    properties["vehicle_impact"] = additional_info.get("vehicle_impact")

    # lanes
    properties["lanes"] = additional_info.get("lanes", [])

    # beginning_cross_street
    properties["beginning_cross_street"] = additional_info.get("beginning_cross_street")

    # beginning_cross_street
    properties["ending_cross_street"] = additional_info.get("ending_cross_street")

    # mileposts
    properties["beginning_milepost"] = additional_info.get("beginning_milepost")

    # ending_milepost
    properties["ending_milepost"] = additional_info.get("ending_milepost")

    # type_of_work
    # non-encroachment, minor-road-defect-repair, roadside-work, overhead-work, below-road-work, barrier-work, surface-work, painting, roadway-relocation, roadway-creation
    types_of_work = event.get("types_of_work", [])
    for type_of_work in types_of_work:
        if type_of_work.get("type_name") == "maintenance":
            type_of_work["type_name"] = "non-encroachment"
    properties["types_of_work"] = types_of_work

    # worker_presence - not available

    # reduced_speed_limit_kph - not available

    # restrictions
    properties["restrictions"] = additional_info.get("restrictions", [])

    properties["route_details_start"] = additional_info.get("route_details_start")
    properties["route_details_end"] = additional_info.get("route_details_end")

    properties["condition_1"] = additional_info.get("condition_1", True)

    filtered_properties = copy.deepcopy(properties)

    INVALID_PROPERTIES: list = [None, "", []]

    for key, value in properties.items():
        if value in INVALID_PROPERTIES:
            del filtered_properties[key]

    for key, value in properties["core_details"].items():
        if value in INVALID_PROPERTIES and key not in ["data_source_id"]:
            del filtered_properties["core_details"][key]

    feature = {}
    feature["id"] = uuid_tools.named_uuid_string(
        event.get("source", {}).get("id", None)
    )
    feature["type"] = "Feature"
    feature["properties"] = filtered_properties
    feature["geometry"] = geometry

    return feature


if __name__ == "__main__":
    main()

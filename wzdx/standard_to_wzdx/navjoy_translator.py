import argparse
import copy
import json
import logging
from datetime import datetime
import uuid  # This is necessary for unit test mocking
from ..tools import date_tools, wzdx_translator, units

PROGRAM_NAME = "WZDxNavJoy568Translator"
PROGRAM_VERSION = "1.0"


def main():
    inputfile, outputfile = parse_navjoy_arguments()

    navjoy_obj = json.loads(open(inputfile).read())
    wzdx = wzdx_creator(navjoy_obj)

    if not wzdx:
        print("Error: WZDx message generation failed, see logs for more information.")
    else:
        with open(outputfile, "w") as fWzdx:
            fWzdx.write(json.dumps(wzdx, indent=2))
            print(
                "Your wzdx message was successfully generated and is located here: "
                + str(outputfile)
            )


# parse script command line arguments
def parse_navjoy_arguments() -> tuple[str, str]:
    """Parse command line arguments for NavJoy 568 data translation

    Returns:
        tuple[str, str]: NavJoy 568 file path, output file path
    """
    parser = argparse.ArgumentParser(description="Translate iCone data to WZDx")
    parser.add_argument(
        "--version", action="version", version=f"{PROGRAM_NAME} {PROGRAM_VERSION}"
    )
    parser.add_argument("navjoyFile", help="navjoy file path")
    parser.add_argument(
        "--outputFile",
        required=False,
        default="navjoy_wzdx_translated_output_message.geojson",
        help="output file path",
    )

    args = parser.parse_args()
    return args.navjoyFile, args.outputFile


def wzdx_creator(message: dict, info: dict = None) -> dict:
    """Translate NavJoy 568 data to WZDx

    Args:
        message (dict): standard RTDH NavJoy 568 data
        info (dict, optional): WZDx info object. Defaults to None.

    Returns:
        dict: WZDx object
    """
    if not message:
        return None
    # verify info obj
    if not info:
        info = wzdx_translator.initialize_info()
    if not wzdx_translator.validate_info(info):
        return None

    wzd = wzdx_translator.initialize_wzdx_object(info)

    feature = parse_reduction_zone(message)
    if feature:
        wzd.get("features").append(feature)

    if not wzd.get("features"):
        return None
    wzd = wzdx_translator.add_ids(wzd)

    if not wzdx_translator.validate_wzdx(wzd):
        logging.warning("WZDx message failed validation")
        return None
    return wzd


# Parse standard Navjoy 568 form to WZDx
def parse_reduction_zone(incident: dict) -> dict:
    """Translate NavJoy 568 data to WZDx

    Args:
        incident (dict): standard RTDH NavJoy 568 data

    Returns:
        dict: WZDx object
    """
    if not incident or type(incident) != dict:
        return None

    event = incident.get("event")

    source = event.get("source")
    header = event.get("header")
    detail = event.get("detail")
    additional_info = event.get("additional_info", {})

    geometry = {}
    geometry["type"] = "LineString"
    geometry["coordinates"] = event.get("geometry")
    properties = wzdx_translator.initialize_feature_properties()

    core_details = properties["core_details"]

    # Event Type ['work-zone', 'detour']
    core_details["event_type"] = "work-zone"

    # data_source_id
    # Leave this empty, it will be populated by add_ids
    core_details["data_source_id"] = ""

    # road_name
    road_names = [detail.get("road_name")]
    core_details["road_names"] = road_names

    # direction
    core_details["direction"] = detail.get("direction", "unknown")

    # Relationship
    core_details["related_road_events"] = []

    # description
    core_details["description"] = (
        header.get("description", "") + ". " + header.get("justification", "")
    )

    # update_date
    core_details["update_date"] = date_tools.get_iso_string_from_datetime(
        date_tools.parse_datetime_from_unix(source.get("last_updated_timestamp"))
    )

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
    properties["location_method"] = "channel-device-method"

    # vehicle impact
    properties["vehicle_impact"] = get_vehicle_impact(header.get("justification"))

    # lanes
    properties["lanes"] = []

    # beginning_cross_street
    properties["beginning_cross_street"] = ""

    # beginning_cross_street
    properties["ending_cross_street"] = ""

    # mileposts
    properties["beginning_milepost"] = ""

    # ending_milepost
    properties["ending_milepost"] = ""

    # type_of_work
    # maintenance, minor-road-defect-repair, roadside-work, overhead-work, below-road-work, barrier-work, surface-work, painting, roadway-relocation, roadway-creation
    projectDescription = header.get("description")
    types_of_work = get_types_of_work(projectDescription)
    if types_of_work:
        properties["types_of_work"] = types_of_work

    # reduced_speed_limit
    if header.get("reduced_speed_limit"):
        properties["reduced_speed_limit_kph"] = units.miles_to_km(
            float(header.get("reduced_speed_limit")), 0
        )

    # location_method
    properties["location_method"] = "channel-device-method"

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


# function to calculate vehicle impact
def get_vehicle_impact(travelRestriction: str) -> str:
    """Calculate vehicle impact based on travel restriction

    Args:
        travelRestriction (str): Travel restriction

    Returns:
        str: Vehicle impact
    """
    if not travelRestriction or type(travelRestriction) != str:
        return None
    travelRestriction = travelRestriction.lower()
    vehicle_impact = "all-lanes-open"
    if "lane closure" in travelRestriction.lower():
        vehicle_impact = "some-lanes-closed"
    elif "all lanes closed" in travelRestriction.lower():
        vehicle_impact = "all-lanes-closed"

    return vehicle_impact


# TODO: Support more types of work
def get_types_of_work(field: str) -> list[dict]:
    """Get types of work based on project description

    Args:
        field (str): Project description

    Returns:
        list[dict]: Types of work
    """
    if not field or type(field) != str:
        return None
    field = field.lower()
    # valid_types_of_work = ['maintenance',
    #                        'minor-road-defect-repair',
    #                        'roadside-work',
    #                        'overhead-work',
    #                        'below-road-work',
    #                        'barrier-work',
    #                        'surface-work',
    #                        'painting',
    #                        'roadway-relocation',
    #                        'roadway-creation']

    if not field or type(field) != str:
        return []

    types_of_work = []

    if "crack seal" in field:
        types_of_work.append(
            {"type_name": "minor-road-defect-repair", "is_architectural_change": False}
        )
    if "restriping" in field:
        types_of_work.append(
            {"type_name": "painting", "is_architectural_change": False}
        )
    if "repaving" in field:
        types_of_work.append(
            {"type_name": "surface-work", "is_architectural_change": False}
        )
    if "bridge" in field:
        types_of_work.append(
            {"type_name": "below-road-work", "is_architectural_change": False}
        )
    if "traffic signal" in field:
        types_of_work.append(
            {"type_name": "overhead-work", "is_architectural_change": False}
        )
    if "lane expansion" in field:
        types_of_work.append(
            {"type_name": "surface-work", "is_architectural_change": True}
        )

    return types_of_work


if __name__ == "__main__":
    main()

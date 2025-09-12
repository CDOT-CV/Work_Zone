import argparse
import json

from wzdx.models.enums import Direction
from ..tools import (
    cdot_geospatial_api,
    geospatial_tools,
    combination,
    date_tools,
    wzdx_translator,
)
import logging
from datetime import datetime, timedelta

PROGRAM_NAME = "ExperimentalCombinationGeotabAttenuator"
PROGRAM_VERSION = "1.0"

ATTENUATOR_TIME_AHEAD_SECONDS = 30 * 60
ISO_8601_FORMAT_STRING = "%Y-%m-%dT%H:%M:%SZ"


def main():
    wzdxFile, geotabFile, output_dir, updateDates = parse_rtdh_arguments()
    wzdx = json.loads(open(wzdxFile, "r").read())
    geotab_avl = [json.loads(open(geotabFile, "r").read())]
    outputPath = output_dir + "/wzdx_attenuator_combined.geojson"
    if updateDates == "true":
        geotab_avl[0]["avl_location"]["source"]["collection_timestamp"] = datetime.now()
        wzdx[0]["features"][0]["properties"]["start_date"] = (
            date_tools.get_iso_string_from_datetime(datetime.now() - timedelta(days=2))
        )
        wzdx[0]["features"][0]["properties"]["end_date"] = (
            date_tools.get_iso_string_from_datetime(datetime.now() + timedelta(days=2))
        )

    combined_events = get_combined_events(geotab_avl, wzdx)

    if len(combined_events) == 0:
        print(
            "No overlapping events found between WZDx and Geotab ATMA data. See logs for more information."
        )
    else:
        with open(outputPath, "w+") as f:
            f.write(json.dumps(combined_events, indent=2))
            print(f"Successfully wrote combined WZDx file to: {outputPath}")


# parse script command line arguments
def parse_rtdh_arguments() -> tuple[str, str, str, str]:
    """Parse command line arguments for attenuator WZDx combination script

    Returns:
        str: WZDx file path
        str: Geotab file path
        str: Output directory
        str: Update dates boolean
    """
    parser = argparse.ArgumentParser(
        description="Combine WZDx and Geotab AVL (ATMA) data"
    )
    parser.add_argument(
        "--version", action="version", version=f"{PROGRAM_NAME} {PROGRAM_VERSION}"
    )
    parser.add_argument("wzdxFile", help="planned event file path")
    parser.add_argument("geotabFile", help="planned event file path")
    parser.add_argument(
        "--outputDir", required=False, default="./", help="output directory"
    )
    parser.add_argument(
        "--updateDates",
        required=False,
        default="false",
        help="Boolean (true/false), Update dates to the current date to pass time filter",
    )

    args = parser.parse_args()
    return args.wzdxFile, args.geotabFile, args.outputDir, args.updateDates


def validate_directionality(geotab: dict, wzdx: dict) -> bool:
    """Validate that the directionality of the Geotab and WZDx objects match

    Args:
        geotab (dict): Geotab AVL message
        wzdx (dict): WZDx message

    Returns:
        bool: Whether the directionality of the Geotab and WZDx objects match
    """
    geotab_bearing = geotab["avl_location"]["position"]["bearing"]
    wzdx_direction = Direction(
        wzdx["features"][0]["properties"]["core_details"]["direction"] or "unknown"
    )

    geotab_direction = geospatial_tools.get_closest_direction_from_bearing(
        geotab_bearing, wzdx_direction
    )

    return geotab_direction == wzdx_direction


def validate_dates(geotab: dict, wzdx: dict) -> bool:
    """Validate that the Geotab date falls within the WZDx date range

    Args:
        geotab (dict): Geotab AVL message
        wzdx (dict): WZDx message

    Returns:
        bool: Whether the Geotab date falls within the WZDx date range
    """
    if type(geotab["avl_location"]["source"]["collection_timestamp"]) is datetime:
        geotab_date = date_tools.date_to_unix(
            geotab["avl_location"]["source"]["collection_timestamp"]
        )
    elif type(geotab["avl_location"]["source"]["collection_timestamp"]) is str:
        geotab_date = date_tools.get_unix_from_iso_string(
            geotab["avl_location"]["source"]["collection_timestamp"]
        )
    else:
        logging.error(
            f"Invalid Geotab date format: avl_location.source.collection_timestamp is type {type(geotab['avl_location']['source']['collection_timestamp'])}"
        )
        return False
    logging.debug(f"Geotab: {json.dumps(geotab)}")
    if not geotab_date:
        geotab_date = (
            geotab["avl_location"]["source"]["collection_timestamp"] * 1000
            if geotab["avl_location"]["source"]["collection_timestamp"]
            else None
        )
    if not geotab_date:
        logging.debug("No geotab date found")
        return False

    wzdx_start_date = date_tools.get_unix_from_iso_string(
        wzdx["features"][0]["properties"]["start_date"]
    )
    wzdx_end_date = date_tools.get_unix_from_iso_string(
        wzdx["features"][0]["properties"]["end_date"]
    )

    logging.debug(f"Dates: {wzdx_start_date}, {geotab_date}, {wzdx_end_date}")

    return wzdx_start_date <= geotab_date <= wzdx_end_date


def get_combined_events(geotab_msgs: list[dict], wzdx_msgs: list[dict]) -> list[dict]:
    """Combine/integrate overlapping Geotab AVL ATMA messages into WZDx messages

    Args:
        icone_standard_msgs (list[dict]): iCone RTDH standard messages
        wzdx_msgs (list[dict]): WZDx messages

    Returns:
        list[dict]: Combined WZDx messages
    """
    active_wzdx_msgs = wzdx_translator.filter_active_wzdx(wzdx_msgs)

    combined_events = []
    for i in identify_overlapping_features(geotab_msgs, active_wzdx_msgs):
        geotab_msg, wzdx_msg = i
        event_status = wzdx_translator.get_event_status(wzdx_msg["features"][0])
        if event_status in ["active"]:
            wzdx = combine_geotab_with_wzdx(geotab_msg, wzdx_msg)
            combined_events.append(wzdx)
    return combined_events


def identify_overlapping_features(
    geotab_msgs: list[dict], wzdx_msgs: list[dict]
) -> list[tuple[dict, dict]]:
    """Identify overlapping Geotab AVL ATMA and WZDx messages

    Args:
        geotab_msgs (list[dict]): Geotab avl messages
        wzdx_msgs (list[dict]): WZDx messages

    Returns:
        list[tuple[dict, dict]]: List of tuples of Geotab and WZDx messages that overlap
    """
    geotab_routes = {}
    matching_routes = []

    for geotab_msg in geotab_msgs:
        geometry = geotab_msg["avl_location"]["position"]

        route_details = cdot_geospatial_api.GeospatialApi().get_route_and_measure(
            (geometry["latitude"], geometry["longitude"])
        )
        if not route_details:
            logging.debug(
                f"No route details for Geotab object: {geotab_msg['rtdh_message_id']}"
            )
            continue
        geotab_msg["route_details_start"] = route_details
        geotab_msg["route_details_end"] = None

        if route_details["Route"] in geotab_routes:
            geotab_routes[route_details["Route"]].append(geotab_msg)
        else:
            geotab_routes[route_details["Route"]] = [geotab_msg]

    if not geotab_routes:
        return []
    for wzdx in wzdx_msgs:
        wzdx["route_details_start"] = wzdx["features"][0]["properties"].get(
            "route_details_start"
        )
        wzdx["route_details_end"] = wzdx["features"][0]["properties"].get(
            "route_details_end"
        )
        if (
            wzdx.get("route_details_start")
            and not wzdx.get("route_details_end")
            or not wzdx.get("route_details_start")
            and wzdx.get("route_details_end")
        ):
            logging.debug(
                f"Missing route_details for WZDx object: {wzdx['features'][0]['id']}"
            )
            continue
        if not wzdx.get("route_details_start") or not wzdx.get("route_details_end"):
            route_details_start, route_details_end = (
                combination.get_route_details_for_wzdx(wzdx["features"][0])
            )

            if not route_details_start or not route_details_end:
                logging.debug(
                    f"Missing route_details for WZDx object: {wzdx['features'][0]['id']}"
                )
                continue
            wzdx["route_details_start"] = route_details_start
            wzdx["route_details_end"] = route_details_end
            logging.debug(
                json.dumps(route_details) + ", " + json.dumps(route_details_end)
            )

        if not wzdx.get("route_details_start"):
            logging.debug(
                f"Unable to retrieve start point route details for WZDx event {wzdx['features'][0].get('id')}"
            )
            continue

        matching_geotab_routes = geotab_routes.get(
            wzdx["route_details_start"]["Route"], []
        )
        if matching_geotab_routes:
            logging.debug(
                f"FOUND MATCHING GEOTAB ROUTE FOR {wzdx['features'][0]['id']}"
            )

            if not wzdx.get("route_details_end"):
                logging.debug(
                    f"Unable to retrieve start point route details for WZDx event {wzdx['features'][0].get('id')}"
                )
                continue
            if (
                wzdx["route_details_start"]["Route"]
                != wzdx["route_details_end"]["Route"]
            ):

                logging.debug(
                    f"Start/End don't match: {wzdx['route_details_start']['Route']}, {wzdx['route_details_end']['Route']}"
                )
                continue
            for geotab in matching_geotab_routes:
                logging.debug(
                    f"VALIDATING MATCH: {combination.does_route_overlap(geotab, wzdx)}, {validate_directionality(geotab, wzdx)}, {validate_dates(geotab, wzdx)}"
                )
                if (
                    combination.does_route_overlap(geotab, wzdx)
                    and validate_directionality(geotab, wzdx)
                    and validate_dates(geotab, wzdx)
                ):
                    matching_routes.append((geotab, wzdx))
                    return matching_routes

    return matching_routes


def combine_geotab_with_wzdx(geotab_avl: dict, wzdx_wzdx: dict) -> dict:
    """Combine Geotab AVL ATMA message with WZDx message. Converts WZDx message to planned-moving-area, with geometry and mile markers from ATMA position and speed.

    Args:
        geotab_avl (dict): Geotab AVL ATMA message
        wzdx_wzdx (dict): WZDx message

    Returns:
        dict: Combined WZDx message
    """
    combined_feature = wzdx_wzdx["features"][0]

    # determine distance ahead to use in moving area
    speed = geotab_avl["avl_location"]["position"]["speed"]
    bearing = geotab_avl["avl_location"]["position"]["bearing"]
    route_details = geotab_avl["route_details_start"]
    distance_ahead = get_distance_ahead_miles(speed, ATTENUATOR_TIME_AHEAD_SECONDS)

    # determine new geometry and mile markers
    event_start_marker = wzdx_wzdx["route_details_start"]["Measure"]
    event_end_marker = wzdx_wzdx["route_details_end"]["Measure"]
    mMin = min(event_start_marker, event_end_marker)
    mMax = max(event_start_marker, event_end_marker)
    geometry, startMarker, endMarker = get_geometry_for_distance_ahead(
        distance_ahead, route_details, bearing, mMin, mMax
    )
    combined_feature["properties"]["beginning_milepost"] = startMarker
    combined_feature["properties"]["ending_milepost"] = endMarker
    combined_feature["geometry"]["coordinates"] = geometry

    # update route details for whichever side was overwritten by geotab
    if (
        combined_feature["properties"]["beginning_milepost"]
        == geotab_avl["route_details_start"]["Measure"]
    ):
        combined_feature["properties"]["route_details_start"] = geotab_avl[
            "route_details_start"
        ]
    elif (
        combined_feature["properties"]["ending_milepost"]
        == geotab_avl["route_details_start"]["Measure"]
    ):
        combined_feature["properties"]["route_details_end"] = geotab_avl[
            "route_details_start"
        ]

    # update description and data sources
    combined_feature["properties"]["core_details"][
        "description"
    ] += f" Moving area updated by Geotab ATMA {geotab_avl['avl_location']['vehicle']['id']}"

    # add fields for traceability
    combined_feature["properties"]["experimental_source_type"] = "geotab"
    combined_feature["properties"]["experimental_source_id"] = geotab_avl[
        "rtdh_message_id"
    ]
    combined_feature["properties"]["geotab_id"] = geotab_avl["avl_location"]["vehicle"][
        "id"
    ]
    combined_feature["properties"]["geotab_message"] = geotab_avl

    # update update_dates
    update_date = date_tools.get_iso_string_from_datetime(datetime.now())
    combined_feature["properties"]["core_details"]["update_date"] = update_date
    wzdx_wzdx["feed_info"]["data_sources"][0]["update_date"] = update_date

    wzdx_wzdx["features"][0] = combined_feature
    return wzdx_wzdx


def get_geometry_for_distance_ahead(
    distance_ahead: float, route_details: dict, bearing: float, mMin: float, mMax: float
) -> tuple[list[list[float]], float, float]:
    """Get the geometry for a distance ahead on a route, within the bounds of mile markers

    Args:
        distance_ahead (float): Distance ahead of vehicle
        route_details (dict): GIS route details
        bearing (float): Vehicle bearing
        mMin (float): Minimum mile marker of event, to generate geometry within
        mMax (float): Maximum mile marker of event, to generate geometry within

    Returns:
        tuple[list[list[float]], float, float]: Geometry, start mile marker, end mile marker
    """
    route_ahead = cdot_geospatial_api.GeospatialApi().get_route_geometry_ahead(
        route_details["Route"],
        route_details["Measure"],
        bearing,
        distance_ahead,
        routeDetails=route_details,
        mMin=mMin,
        mMax=mMax,
    )
    if not route_details:
        return [], mMin, mMax
    return (
        route_ahead["coordinates"],
        route_ahead["start_measure"],
        route_ahead["end_measure"],
    )


# Speed in mph, time in seconds
def get_distance_ahead_miles(speed: float, time: float) -> float:
    """Get the distance ahead in miles given a speed and time. Vehicle speed is "floored" at 5 mph.

    Args:
        speed (float): Speed of vehicle, in mph
        time (float): Time ahead of vehicle, in seconds

    Returns:
        float: Distance ahead of vehicle, in miles
    """
    speed = max(speed, 5)
    return speed * time / 3600


if __name__ == "__main__":
    main()

import argparse
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Literal
from wzdx.models.field_device_feed.device_feed import DeviceFeed
from wzdx.models.field_device_feed.field_device_feature import FieldDeviceFeature
from wzdx.models.geometry.geojson_geometry import GeoJsonGeometry

from ..tools import combination, wzdx_translator, geospatial_tools, date_tools

PROGRAM_NAME = "ExperimentalCombinationFieldDevices"
PROGRAM_VERSION = "1.0"

ISO_8601_FORMAT_STRING = "%Y-%m-%dT%H:%M:%SZ"
START_TIME_THRESHOLD_MILLISECONDS = 1000 * 60 * 60 * 24 * 31  # 31 days
END_TIME_THRESHOLD_MILLISECONDS = 1000 * 60 * 60 * 24 * 31  # 31 days


def main(outputPath="./tests/data/output/wzdx_field_devices_combined.json"):
    wzdxFile, fieldDevicesFile, output_dir, updateDates = parse_rtdh_arguments()
    wzdx = json.loads(open(wzdxFile, "r").read())
    field_device_collection: DeviceFeed = DeviceFeed.model_validate_json(
        open(fieldDevicesFile).read()
    )
    outputPath = output_dir + "/wzdx_experimental.geojson"
    if updateDates == "true":
        for i in field_device_collection.features:
            i.properties.core_details.update_date = datetime.now(timezone.utc)
        wzdx[0]["features"][0]["properties"]["start_date"] = (
            date_tools.get_iso_string_from_datetime(
                datetime.now(timezone.utc) - timedelta(days=3)
            )
        )
        wzdx[0]["features"][0]["properties"]["end_date"] = (
            date_tools.get_iso_string_from_datetime(
                datetime.now(timezone.utc) - timedelta(days=1)
            )
        )

    field_device_collection.features = [
        pre_process_field_device_feature(i) for i in field_device_collection.features
    ]

    combined_events = get_combined_events(field_device_collection.features, wzdx)

    if len(combined_events) == 0:
        print(
            "No overlapping events found between WZDx and iCone data. See logs for more information."
        )
    else:
        with open(outputPath, "w+") as f:
            f.write(json.dumps(combined_events, indent=2))
            print(f"Successfully wrote combined WZDx file to: {outputPath}")


# parse script command line arguments
def parse_rtdh_arguments() -> tuple[str, str, str, str]:
    """Parse command line arguments for WZDx field device combination script

    Returns:
        str: WZDx event file path
        str: WZDx field device file path
        str: output directory path
        str: updateDates flag (true/false)
    """
    parser = argparse.ArgumentParser(
        description="Combine WZDx event and WZDx field device data"
    )
    parser.add_argument(
        "--version", action="version", version=f"{PROGRAM_NAME} {PROGRAM_VERSION}"
    )
    parser.add_argument("wzdxFile", help="Incoming WZDx event file path (JSON)")
    parser.add_argument("fieldDevicesFile", help="WZDx field device file path (JSON)")
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
    return args.wzdxFile, args.fieldDevicesFile, args.outputDir, args.updateDates


def parse_field_device_feature(raw: str) -> FieldDeviceFeature:
    """Parse raw JSON string into WZDx field device feature

    Args:
        raw (str): Raw JSON string

    Returns:
        FieldDeviceFeature: WZDx field device feature
    """
    return FieldDeviceFeature.model_validate_json(raw)


def pre_process_field_device_feature(
    field_device_feature: FieldDeviceFeature,
) -> FieldDeviceFeature:
    """Pre-process field device feature for combination

    Args:
        field_device_feature (FieldDeviceFeature): WZDx field device feature
    Returns:
        FieldDeviceFeature: Pre-processed WZDx field device feature
    """
    route_details_start, route_details_end = get_route_details_for_feature(
        field_device_feature.geometry
    )
    field_device_feature.route_details_start = route_details_start
    field_device_feature.route_details_end = route_details_end
    return field_device_feature


def get_direction_from_route_details(route_details: dict) -> str:
    """Get direction from GIS route details

    Args:
        route_details (dict): GIS route details

    Returns:
        str: direction | "unknown"
    """
    return route_details.get("Direction")


def get_direction(
    street: str, coords: list[list[float]], route_details: dict = None
) -> str:
    """Get road direction from street name, coordinates, or route details

    Args:
        street (str): Street name, like "I-25 NB"
        coords (list[list[float]]): List of coordinates, to pull direction from
        route_details (dict, optional): GIS route details, defaults to None

    Returns:
        Literal['unknown', 'eastbound', 'westbound', 'northbound', 'southbound']: Road direction
    """
    direction = wzdx_translator.parse_direction_from_street_name(street)
    if not direction and route_details:
        direction = get_direction_from_route_details(route_details)
    if not direction:
        direction = geospatial_tools.get_road_direction_from_coordinates(coords)
    return direction


def get_combined_events(
    field_device_features: list[FieldDeviceFeature], wzdx_msgs: list[dict]
) -> list[dict]:
    """Combine/integrate overlapping iCone messages into WZDx messages

    Args:
        field_device_features (list[FieldDeviceFeature]): WZDx field device features
        wzdx_msgs (list[dict]): WZDx messages

    Returns:
        list[dict]: Combined WZDx messages
    """
    combined_events: list[dict] = []
    filtered_wzdx_msgs = wzdx_translator.filter_wzdx_by_event_status(
        wzdx_msgs, ["pending", "completed_recently"]
    )

    for i in identify_overlapping_features(field_device_features, filtered_wzdx_msgs):
        icone_msg, wzdx_msg = i
        event_status = wzdx_translator.get_event_status(wzdx_msg["features"][0])
        wzdx = combine_field_device_with_wzdx(icone_msg, wzdx_msg, event_status)
        if wzdx:
            combined_events.append(wzdx)
    return combined_events


def combine_field_device_with_wzdx(
    field_device_feature: FieldDeviceFeature,
    wzdx_wzdx: dict,
    event_status: Literal["active", "pending", "planned", "completed"],
) -> dict:
    """Combine iCone message with WZDx message

    Args:
        field_device_feature (FieldDeviceFeature): WZDx field device feature
        wzdx_wzdx (dict): WZDx message
        event_status (Literal[&quot;active&quot;, &quot;pending&quot;, &quot;planned&quot;, &quot;completed&quot;]): WZDx event status

    Returns:
        dict: Combined WZDx message
    """
    combined_event = wzdx_wzdx
    updated = False

    if event_status == "pending":
        # Start event early
        # Field device has already been verified to be updated within the past 2 hours
        combined_event["features"][0]["properties"]["start_date"] = (
            date_tools.get_iso_string_from_datetime(datetime.now(timezone.utc))
        )
        updated = True
    elif event_status == "completed_recently":
        # Keep event open longer
        # Field device has already been verified to be updated within the past 2 hours
        combined_event["features"][0]["properties"]["end_date"] = (
            date_tools.get_iso_string_from_datetime(
                datetime.now(timezone.utc) + timedelta(hours=2)
            )
        )
        combined_event["features"][0]["properties"]["core_details"]["description"] += (
            " " + field_device_feature.properties.core_details.description
        )
        updated = True
    if updated:
        update_date = date_tools.get_iso_string_from_datetime(
            datetime.now(timezone.utc)
        )
        combined_event["features"][0]["properties"]["core_details"][
            "update_date"
        ] = update_date
        combined_event["feed_info"]["data_sources"][0]["update_date"] = update_date

        combined_event["features"][0]["properties"][
            "experimental_source_type"
        ] = "icone"
        combined_event["features"][0]["properties"][
            "experimental_source_id"
        ] = field_device_feature.id
        combined_event["features"][0]["properties"][
            "icone_id"
        ] = field_device_feature.id
        combined_event["features"][0]["properties"]["icone_message"] = (
            field_device_feature.model_dump(
                by_alias=True, exclude_none=True, mode="json"
            )
        )

        for i in ["route_details_start", "route_details_end"]:
            if i in combined_event:
                del combined_event[i]
        return combined_event
    else:
        return None


def get_route_details_for_feature(geometry: GeoJsonGeometry) -> tuple[dict, dict]:
    """Get route details for iCone message

    Args:
        geometry (GeoJsonGeometry): Geometry object

    Returns:
        tuple[dict, dict]: Route details for start and end coordinates
    """

    match geometry.type:
        case "Point":
            coordinates = [geometry.coordinates]
        case "MultiPoint":
            coordinates = geometry.coordinates
        case "LineString":
            coordinates = [geometry.coordinates[0], geometry.coordinates[-1]]
        case "Polygon":
            coordinates = [geometry.coordinates[0][0], geometry.coordinates[-1][-1]]

    route_details_start = combination.get_route_details(
        coordinates[0][1], coordinates[0][0]
    )

    if len(coordinates) == 1 or (
        len(coordinates) == 2 and coordinates[0] == coordinates[1]
    ):
        route_details_end = None
    else:
        route_details_end = combination.get_route_details(
            coordinates[-1][1], coordinates[-1][0]
        )

    return route_details_start, route_details_end


def validate_directionality_wzdx_field_device(
    field_device: FieldDeviceFeature, wzdx: dict
) -> bool:
    """Validate directionality between field device and WZDx messages

    Args:
        field_device (FieldDeviceFeature): Field device feature
        wzdx (dict): WZDx message

    Returns:
        bool: Directionality match
    """
    direction_1 = field_device.properties.core_details.road_direction
    direction_2 = wzdx["features"][0]["properties"]["core_details"]["direction"]

    return direction_1 in [None, "unknown", "undefined"] or direction_1 == direction_2


def verify_recent(field_device: FieldDeviceFeature) -> bool:
    """Validate that the field device information is recent (within 2 hours)

    Args:
        field_device (FieldDeviceFeature): Field device feature

    Returns:
        bool: Is recent information
    """
    return field_device.properties.core_details.update_date > datetime.now(
        timezone.utc
    ) - timedelta(hours=2)


def identify_overlapping_features(
    field_device_features: list[FieldDeviceFeature], wzdx_msgs: list[dict]
) -> list[tuple[dict, dict]]:
    """Identify overlapping WZDx events and field devices

    Args:
        field_device_features (list[FieldDeviceFeature]): Field device features
        wzdx_msgs (list[dict]): WZDx messages

    Returns:
        list[tuple[dict, dict]]: Overlapping field device and WZDx messages
    """
    field_device_routes: dict[str, list[FieldDeviceFeature]] = {}
    wzdx_event_routes: dict[str, list[dict]] = {}
    matching_routes: list[tuple[dict, dict]] = []

    recent_field_device_features = [
        i for i in field_device_features if verify_recent(i)
    ]

    # Step 1: Add route info to field device features
    for field_device_feature in recent_field_device_features:
        if not field_device_feature.route_details_start:
            logging.debug(
                f"Invalid route details for field device: {field_device_feature.id}"
            )
            continue

        if (
            field_device_feature.route_details_end
            and field_device_feature.route_details_start["Route"]
            != field_device_feature.route_details_end["Route"]
        ):
            logging.debug(
                f"Mismatched routes for field device feature {field_device_feature.id}"
            )
            continue

        if field_device_feature.route_details_start["Route"] in field_device_routes:
            field_device_routes[
                field_device_feature.route_details_start["Route"]
            ].append(field_device_feature)
        else:
            field_device_routes[field_device_feature.route_details_start["Route"]] = [
                field_device_feature
            ]

    # Step 2: Add route info to WZDx messages
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
        if not wzdx.get("route_details_start") and not wzdx.get("route_details_end"):
            route_details_start, route_details_end = (
                combination.get_route_details_for_wzdx(wzdx["features"][0])
            )

            if not route_details_start or not route_details_end:
                logging.debug(f"Missing WZDx route details {wzdx['features'][0]['id']}")
                continue
            wzdx["route_details_start"] = route_details_start
            wzdx["route_details_end"] = route_details_end
        else:
            route_details_start = wzdx["route_details_start"]
            route_details_end = wzdx["route_details_end"]

        if route_details_start["Route"] != route_details_end["Route"]:
            logging.debug(f"Mismatched routes for feature {wzdx['features'][0]['id']}")
            continue

        logging.debug(
            "Route details: " + str(route_details_start) + str(route_details_end)
        )

        if route_details_start["Route"] in wzdx_event_routes:
            wzdx_event_routes[route_details_start["Route"]].append(wzdx)
        else:
            wzdx_event_routes[route_details_start["Route"]] = [wzdx]

    if not field_device_routes:
        logging.debug("No routes found for icone")
        return []
    if not wzdx_event_routes:
        logging.debug("No routes found for wzdx")
        return []

    # Step 3: Identify overlapping events
    for wzdx_route_id, wzdx_matched_msgs in wzdx_event_routes.items():
        matching_field_device_routes = field_device_routes.get(wzdx_route_id, [])

        for match_field_device in matching_field_device_routes:
            for match_wzdx in wzdx_matched_msgs:
                # require routes to overlap, directionality to match, and dates to match
                if combination.does_route_overlap(
                    match_field_device.model_dump(), match_wzdx
                ) and validate_directionality_wzdx_field_device(
                    match_field_device, match_wzdx
                ):

                    matching_routes.append((match_field_device, match_wzdx))

    return matching_routes


if __name__ == "__main__":
    main()

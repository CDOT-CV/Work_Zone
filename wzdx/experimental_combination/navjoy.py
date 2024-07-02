import argparse
import json

from ..tools import combination, date_tools, wzdx_translator
from datetime import datetime, timedelta

PROGRAM_NAME = "ExperimentalCombinationNavjoy568"
PROGRAM_VERSION = "1.0"

ISO_8601_FORMAT_STRING = "%Y-%m-%dT%H:%M:%SZ"


def main():
    wzdxFile, navjoyFile, output_dir, updateDates = parse_rtdh_arguments()
    wzdx = json.loads(open(wzdxFile, "r").read())
    navjoy = [json.loads(open(navjoyFile, "r").read())]
    outputPath = output_dir + "/wzdx_attenuator_combined.geojson"
    if updateDates == "true":
        navjoy[0]["features"][0]["properties"]["start_date"] = (
            date_tools.get_iso_string_from_datetime(datetime.now() - timedelta(days=1))
        )
        navjoy[0]["features"][0]["properties"]["end_date"] = (
            date_tools.get_iso_string_from_datetime(datetime.now() + timedelta(days=1))
        )
        wzdx[0]["features"][0]["properties"]["start_date"] = (
            date_tools.get_iso_string_from_datetime(datetime.now() - timedelta(days=2))
        )
        wzdx[0]["features"][0]["properties"]["end_date"] = (
            date_tools.get_iso_string_from_datetime(datetime.now() + timedelta(days=2))
        )

    combined_events = get_combined_events(navjoy, wzdx)

    if len(combined_events) == 0:
        print("No overlapping events found between WZDx and Navjoy 568 data. See logs for more information.")
    else:
        with open(outputPath, "w+") as f:
            f.write(json.dumps(combined_events, indent=2))
            print(f"Successfully wrote combined WZDx file to: {outputPath}")


# parse script command line arguments
def parse_rtdh_arguments() -> tuple[str, str, str, str]:
    """Parse command line arguments for experimental combination of WZDx and Navjoy 568 data

    Returns:
        str: WZDx file path
        str: navjoy 568 file path
        str: output directory
        str: Boolean (true/false), Update dates to the current date to pass time filter
    """
    parser = argparse.ArgumentParser(
        description="Combine WZDx and Geotab AVL (ATMA) data"
    )
    parser.add_argument(
        "--version", action="version", version=f"{PROGRAM_NAME} {PROGRAM_VERSION}"
    )
    parser.add_argument("wzdxFile", help="planned event file path")
    parser.add_argument("navjoyWzdxFile", help="planned event file path")
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
    return args.wzdxFile, args.navjoyWzdxFile, args.outputDir, args.updateDates


def get_combined_events(
    navjoy_wzdx_msgs: list[dict], wzdx_msgs: list[dict]
) -> list[dict]:
    """Combine/integrate overlapping Navjoy 568 messages into WZDx messages

    Args:
        navjoy_wzdx_msgs (list[dict]): Navjoy 568 messages
        wzdx_msgs (list[dict]): WZDx messages

    Returns:
        list[dict]: Combined WZDx messages
    """
    combined_events = []
    active_navjoy_wzdx_msgs = wzdx_translator.filter_active_wzdx(navjoy_wzdx_msgs)
    active_wzdx_msgs = wzdx_translator.filter_active_wzdx(wzdx_msgs)
    for i in combination.identify_overlapping_features_wzdx(
        active_navjoy_wzdx_msgs, active_wzdx_msgs
    ):
        navjoy_msg, wzdx_msg = i
        event_status = wzdx_translator.get_event_status(wzdx_msg["features"][0])
        if event_status in ["active"]:
            combined = combine_navjoy_with_wzdx(navjoy_msg, wzdx_msg)
            wzdx_msg["features"] = combined["features"]
            combined_events.append(wzdx_msg)
    return combined_events


def combine_navjoy_with_wzdx(navjoy_wzdx: dict, wzdx_wzdx: dict) -> dict:
    """Combine Navjoy 568 message with WZDx message. Update WZDx message speed limit and description

    Args:
        navjoy_wzdx (dict): Navjoy 568 message
        wzdx_wzdx (dict): WZDx message

    Returns:
        dict: Combined WZDx message
    """
    combined_event = wzdx_wzdx

    combined_feature = combined_event["features"][0]

    combined_feature["properties"]["reduced_speed_limit_kph"] = navjoy_wzdx["features"][
        0
    ]["properties"]["reduced_speed_limit_kph"]
    combined_feature["properties"]["core_details"][
        "description"
    ] += f" Moving area updated by Geotab ATMA {combined_feature['id']}"

    # add fields for traceability
    combined_feature["properties"]["experimental_source_type"] = "navjoy"
    combined_feature["properties"]["experimental_source_id"] = combined_feature["id"]
    combined_feature["properties"]["navjoy_id"] = combined_feature["id"]
    combined_feature["properties"]["navjoy_message"] = navjoy_wzdx

    for i in ["route_details_start", "route_details_end"]:
        if i in combined_event:
            del combined_event[i]
    return combined_event


if __name__ == "__main__":
    main()

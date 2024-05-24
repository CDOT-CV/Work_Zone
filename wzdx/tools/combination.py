import logging
from . import cdot_geospatial_api, date_tools


ROUTE_OVERLAP_INDIVIDUAL_DISTANCE = 0.25


def validate_directionality_wzdx(wzdx_1, wzdx_2):
    direction_1 = wzdx_1["features"][0]["properties"]["core_details"]["direction"]
    direction_2 = wzdx_2["features"][0]["properties"]["core_details"]["direction"]

    return direction_1 == direction_2


def validate_date_overlap_wzdx(wzdx_1, wzdx_2):
    start_date_1 = date_tools.get_unix_from_iso_string(
        wzdx_1["features"][0]["properties"]["start_date"]
    )
    end_date_1 = date_tools.get_unix_from_iso_string(
        wzdx_1["features"][0]["properties"]["end_date"]
    )

    start_date_2 = date_tools.get_unix_from_iso_string(
        wzdx_2["features"][0]["properties"]["start_date"]
    )
    end_date_2 = date_tools.get_unix_from_iso_string(
        wzdx_2["features"][0]["properties"]["end_date"]
    )

    # return whether the dates overlap
    return (start_date_1 <= start_date_2 <= end_date_1) or (
        start_date_2 <= start_date_1 <= end_date_2
    )


def does_route_overlap(obj1, obj2):
    number_valid_1 = 0
    number_valid_1 += 1 if obj1["route_details_start"] else 0
    number_valid_1 += 1 if obj1["route_details_end"] else 0

    number_valid_2 = 0
    number_valid_2 += 1 if obj2["route_details_start"] else 0
    number_valid_2 += 1 if obj2["route_details_end"] else 0

    if number_valid_1 == 0 or number_valid_2 == 0:
        return None
    elif number_valid_1 == 1 and number_valid_2 == 1:
        individual_valid_1 = (
            obj1["route_details_start"]["Measure"]
            if obj1["route_details_start"]
            else obj1["route_details_end"]["Measure"]
        )
        individual_valid_2 = (
            obj2["route_details_start"]["Measure"]
            if obj2["route_details_start"]
            else obj2["route_details_end"]["Measure"]
        )
        return does_route_overlap_2(individual_valid_1, individual_valid_2)
    elif number_valid_1 == 2 and number_valid_2 == 1:
        start_1_m = min(
            obj1["route_details_start"]["Measure"], obj1["route_details_end"]["Measure"]
        )
        end_1_m = max(
            obj1["route_details_start"]["Measure"], obj1["route_details_end"]["Measure"]
        )
        individual_valid_2 = (
            obj2["route_details_start"]["Measure"]
            if obj2["route_details_start"]
            else obj2["route_details_end"]["Measure"]
        )
        return does_route_overlap_3(start_1_m, end_1_m, individual_valid_2)
    elif number_valid_1 == 1 and number_valid_2 == 2:
        start_2_m = min(
            obj2["route_details_start"]["Measure"], obj2["route_details_end"]["Measure"]
        )
        end_2_m = max(
            obj2["route_details_start"]["Measure"], obj2["route_details_end"]["Measure"]
        )
        individual_valid_1 = (
            obj1["route_details_start"]["Measure"]
            if obj1["route_details_start"]
            else obj1["route_details_end"]["Measure"]
        )
        return does_route_overlap_3(start_2_m, end_2_m, individual_valid_1)
    else:
        start_1_m = min(
            obj1["route_details_start"]["Measure"], obj1["route_details_end"]["Measure"]
        )
        end_1_m = max(
            obj1["route_details_start"]["Measure"], obj1["route_details_end"]["Measure"]
        )
        start_2_m = min(
            obj2["route_details_start"]["Measure"], obj2["route_details_end"]["Measure"]
        )
        end_2_m = max(
            obj2["route_details_start"]["Measure"], obj2["route_details_end"]["Measure"]
        )
        return does_route_overlap_4(start_1_m, end_1_m, start_2_m, end_2_m)


def does_route_overlap_2(mm1, mm2):
    return abs(mm1 - mm2) <= ROUTE_OVERLAP_INDIVIDUAL_DISTANCE


def does_route_overlap_3(start_1_m, end_1_m, mm2):
    return mm2 >= start_1_m and mm2 <= end_1_m


def does_route_overlap_4(start_1_m, end_1_m, start_2_m, end_2_m):
    if start_2_m >= start_1_m and start_2_m <= end_1_m:
        # Start of route 2 in route 1
        return True
    elif end_2_m >= start_1_m and end_2_m <= end_1_m:
        # End of route 2 in route 1
        return True
    elif end_2_m >= end_1_m and start_2_m <= start_1_m:
        # Route 2 goes over route 1
        return True
    else:
        return False


def get_route_details_for_coordinates_lnglat(coordinates):
    route_details_start = get_route_details(coordinates[0][1], coordinates[0][0])

    if len(coordinates) == 1 or (
        len(coordinates) == 2 and coordinates[0] == coordinates[1]
    ):
        route_details_end = None
    else:
        route_details_end = get_route_details(coordinates[-1][1], coordinates[-1][0])

    return route_details_start, route_details_end


def get_route_details(lat, lng):
    return cdot_geospatial_api.GeospatialApi().get_route_and_measure((lat, lng))


def add_route_details(wzdx_msgs, overwrite=False, keepInvalid=True):
    output = []
    for wzdx in wzdx_msgs:
        if (
            wzdx.get("route_details_start", "missing") == "missing"
            or wzdx.get("route_details_end") == "missing"
        ) or overwrite:
            route_details_start, route_details_end = get_route_details_for_wzdx(
                wzdx["features"][0]
            )

            wzdx["route_details_start"] = (
                route_details_start if route_details_start else None
            )
            wzdx["route_details_end"] = route_details_end if route_details_end else None

            if (route_details_start and route_details_end) or keepInvalid:
                output.append(wzdx)
        else:
            output.append(wzdx)
    return output


def get_route_details_for_wzdx(wzdx_feature):
    coordinates = wzdx_feature["geometry"]["coordinates"]
    route_details_start = get_route_details(coordinates[0][1], coordinates[0][0])

    route_details_end = get_route_details(coordinates[-1][1], coordinates[-1][0])

    return route_details_start, route_details_end


def identify_overlapping_features_wzdx(wzdx_msgs_1, wzdx_msgs_2):
    wzdx_routes_1 = {}
    wzdx_routes_2 = {}

    # Step 1: Add route info to iCone messages
    for wzdx_1 in wzdx_msgs_1:
        wzdx_1["route_details_start"] = wzdx_1["features"][0]["properties"].get(
            "route_details_start"
        )
        wzdx_1["route_details_end"] = wzdx_1["features"][0]["properties"].get(
            "route_details_end"
        )
        
        if (
            wzdx_1.get("route_details_start")
            and not wzdx_1.get("route_details_end")
            or not wzdx_1.get("route_details_start")
            and wzdx_1.get("route_details_end")
        ):
            logging.debug(
                f"Missing route_details for WZDx object: {wzdx_1['features'][0]['id']}"
            )
            continue
        if not wzdx_1.get("route_details_start") or not wzdx_1.get("route_details_end"):
            route_details_start, route_details_end = get_route_details_for_wzdx(
                wzdx_1["features"][0]
            )

            if not route_details_start or not route_details_end:
                logging.debug(
                    f"No route details for WZDx 1 feature {wzdx_1['features'][0]['id']}"
                )
                continue
            wzdx_1["route_details_start"] = route_details_start
            wzdx_1["route_details_end"] = route_details_end
        else:
            route_details_start = wzdx_1["route_details_start"]
            route_details_end = wzdx_1["route_details_end"]

        if route_details_start["Route"] != route_details_end["Route"]:
            logging.debug(
                f"Mismatched routes for WZDx 1 feature {wzdx_1['features'][0]['id']}"
            )
            continue

        if route_details_start["Route"] in wzdx_routes_1:
            wzdx_routes_1[route_details_start["Route"]].append(wzdx_1)
        else:
            wzdx_routes_1[route_details_start["Route"]] = [wzdx_1]

    # Step 2: Add route info to WZDx messages
    for wzdx_2 in wzdx_msgs_2:
        wzdx_2["route_details_start"] = wzdx_2["features"][0]["properties"].get(
            "route_details_start"
        )
        wzdx_2["route_details_end"] = wzdx_2["features"][0]["properties"].get(
            "route_details_end"
        )
        
        if (
            wzdx_2.get("route_details_start")
            and not wzdx_2.get("route_details_end")
            or not wzdx_2.get("route_details_start")
            and wzdx_2.get("route_details_end")
        ):
            logging.debug(
                f"Missing route_details for WZDx object: {wzdx_2['features'][0]['id']}"
            )
            continue
        if not wzdx_2.get("route_details_start") or not wzdx_2.get("route_details_end"):
            route_details_start, route_details_end = get_route_details_for_wzdx(
                wzdx_2["features"][0]
            )

            if not route_details_start or not route_details_end:
                logging.debug(
                    f"Missing route details for WZDx 2 feature {wzdx_2['features'][0]['id']}"
                )
                continue
            wzdx_2["route_details_start"] = route_details_start
            wzdx_2["route_details_end"] = route_details_end
        else:
            route_details_start = wzdx_2["route_details_start"]
            route_details_end = wzdx_2["route_details_end"]

        if route_details_start["Route"] != route_details_end["Route"]:
            logging.debug(
                f"Mismatched routes for WZDx 2 feature {wzdx_2['features'][0]['id']}"
            )
            continue

        if route_details_start["Route"] in wzdx_routes_2:
            wzdx_routes_2[route_details_start["Route"]].append(wzdx_2)
        else:
            wzdx_routes_2[route_details_start["Route"]] = [wzdx_2]

    if not wzdx_routes_1:
        logging.debug("No routes found for dataset 1")
        return []
    if not wzdx_routes_2:
        logging.debug("No routes found for dataset 2")
        return []

    matching_routes = []

    # Step 3: Identify overlapping events
    for wzdx_route_id, wzdx_matched_msgs in wzdx_routes_2.items():
        matching_routes_1 = wzdx_routes_1.get(wzdx_route_id, [])

        for match_1 in matching_routes_1:
            for match_2 in wzdx_matched_msgs:
                if (
                    does_route_overlap(match_1, match_2)
                    and validate_directionality_wzdx(match_1, match_2)
                    and validate_date_overlap_wzdx(match_1, match_2)
                ):
                    matching_routes.append((match_1, match_2))

    return matching_routes

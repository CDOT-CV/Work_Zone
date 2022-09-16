import logging
import cdot_geospatial_api


def validate_directionality_wzdx(wzdx_1, wzdx_2):
    direction_1 = wzdx_1['features'][0]['properties']['core_details']['direction']
    direction_2 = wzdx_2['features'][0]['properties']['core_details']['direction']

    return direction_1 == direction_2


def does_route_overlap(obj1, obj2):
    start_1_m = min(obj1['route_details_start']['Measure'],
                    obj1['route_details_end']['Measure'])
    end_1_m = max(obj1['route_details_start']['Measure'],
                  obj1['route_details_end']['Measure'])
    start_2_m = min(obj2['route_details_start']['Measure'],
                    obj2['route_details_end']['Measure'])
    end_2_m = max(obj2['route_details_start']['Measure'],
                  obj2['route_details_end']['Measure'])
    if start_2_m > start_1_m and start_2_m < end_1_m:
        # Start of route 2 in route 1
        return True
    elif end_2_m > start_1_m and end_2_m < end_1_m:
        # End of route 2 in route 1
        return True
    elif start_2_m < start_1_m and end_2_m > end_1_m:
        # Route 2 goes over route 1
        return True
    else:
        return False


def get_route_details(lat, lng):
    return cdot_geospatial_api.get_route_and_measure((lat, lng))


def get_route_details_for_wzdx(wzdx_feature):
    coordinates = wzdx_feature['geometry']['coordinates']
    route_details_start = get_route_details(
        coordinates[0][1], coordinates[0][0])

    route_details_end = get_route_details(
        coordinates[-1][1], coordinates[-1][0])

    return route_details_start, route_details_end


def identify_overlapping_features_wzdx(wzdx_msgs_1, wzdx_msgs_2):
    wzdx_routes_1 = {}
    wzdx_routes_2 = {}
    matching_routes = []

    # Step 1: Add route info to iCone messages
    for wzdx_1 in wzdx_msgs_1:
        route_details_start, route_details_end = get_route_details_for_wzdx(
            wzdx_1['features'][0])

        if not route_details_start or not route_details_end:
            logging.info(
                f"No geotab route info for feature {wzdx_1['features'][0]['id']}")
            continue
        wzdx_1['route_details_start'] = route_details_start
        wzdx_1['route_details_end'] = route_details_end

        if route_details_start['Route'] != route_details_end['Route']:
            logging.info(
                f"Mismatched routes for feature {wzdx_1['features'][0]['id']}")
            continue

        if route_details_start['Route'] in wzdx_routes_1:
            wzdx_routes_1[route_details_start['Route']].append(wzdx_1)
        else:
            wzdx_routes_1[route_details_start['Route']] = [wzdx_1]

    # Step 2: Add route info to WZDx messages
    for wzdx_2 in wzdx_msgs_2:
        route_details_start, route_details_end = get_route_details_for_wzdx(
            wzdx_2['features'][0])

        if not route_details_start or not route_details_end:
            logging.info(
                f"No geotab route info for feature {wzdx_2['features'][0]['id']}")
            continue
        wzdx_2['route_details_start'] = route_details_start
        wzdx_2['route_details_end'] = route_details_end

        if route_details_start['Route'] != route_details_end['Route']:
            logging.info(
                f"Mismatched routes for feature {wzdx_2['features'][0]['id']}")
            continue

        if route_details_start['Route'] in wzdx_routes_2:
            wzdx_routes_2[route_details_start['Route']].append(wzdx_2)
        else:
            wzdx_routes_2[route_details_start['Route']] = [wzdx_2]

    if not wzdx_routes_1:
        logging.debug('No routes found for dataset 1')
        return []
    if not wzdx_routes_2:
        logging.debug('No routes found for dataset 2')
        return []

    # Step 3: Identify overlapping events
    for wzdx_route_id, wzdx_matched_msgs in wzdx_routes_2:
        matching_routes_1 = wzdx_routes_1.get(wzdx_route_id, [])

        for match_1 in matching_routes_1:
            for match_2 in wzdx_matched_msgs:
                if does_route_overlap(match_1, match_2) and validate_directionality_wzdx(match_1, match_2):
                    matching_routes.append((match_1, match_2))

    return matching_routes

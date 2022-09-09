import json
from datetime import datetime
from ..tools import cdot_geospatial_api, geospatial_tools, wzdx_translator
import logging

ISO_8601_FORMAT_STRING = "%Y-%m-%dT%H:%M:%SZ"


def main():
    with open('./wzdx/sample_files/raw/geotab_avl/geotab_all.json') as f:
        geotab_avl = json.loads(f.read())
    with open('./wzdx/sample_files/enhanced/wzdxs/wzdx_all.json') as f:
        wzdx = json.loads(f.read())

    combined_events = get_combined_events(geotab_avl, wzdx)

    with open('./wzdx/sample_files/enhanced/wzdxs/wzdx_combined.json', 'w+') as f:
        f.write(json.dumps(combined_events, indent=2))


def validate_directionality(wzdx_icone, wzdx):
    icone_direction = wzdx_icone['features'][0]['properties']['core_details']['direction']
    wzdx_direction = wzdx['features'][0]['properties']['core_details']['direction']

    return icone_direction == wzdx_direction


def get_combined_events(icone_msgs, wzdx_msgs):
    combined_events = []
    for i in identify_overlapping_features(icone_msgs, wzdx_msgs):
        feature = combine_icone_with_wzdx(*i)
        wzdx = i[1]
        wzdx['features'] = [feature]
        combined_events.append(wzdx)
    return combined_events


def get_route_details_for_wzdx(wzdx_feature):
    coordinates = wzdx_feature['geometry']['coordinates']
    route_details_start = get_route_details(
        coordinates[0][1], coordinates[0][0])

    route_details_end = get_route_details(
        coordinates[-1][1], coordinates[-1][0])

    return route_details_start, route_details_end


def identify_overlapping_features(icone_wzdx_msgs, wzdx_msgs):
    icone_wzdx_routes = {}
    wzdx_routes = {}
    matching_routes = []

    # Step 1: Add route info to iCone messages
    for icone_wzdx in icone_wzdx_msgs:
        route_details_start, route_details_end = get_route_details_for_wzdx(
            icone_wzdx['features'][0])

        if not route_details_start or not route_details_end:
            logging.info(
                f"No geotab route info for feature {icone_wzdx['features'][0]['id']}")
            continue
        icone_wzdx['route_details_start'] = route_details_start
        icone_wzdx['route_details_end'] = route_details_end

        if route_details_start['Route'] != route_details_end['Route']:
            logging.info(
                f"Mismatched routes for feature {icone_wzdx['features'][0]['id']}")
            continue

        if route_details_start['Route'] in icone_wzdx_routes:
            icone_wzdx_routes[route_details_start['Route']].append(icone_wzdx)
        else:
            icone_wzdx_routes[route_details_start['Route']] = [icone_wzdx]

    # Step 2: Add route info to WZDx messages
    for wzdx in wzdx_msgs:
        route_details_start, route_details_end = get_route_details_for_wzdx(
            wzdx['features'][0])

        if not route_details_start or not route_details_end:
            logging.info(
                f"No geotab route info for feature {wzdx['features'][0]['id']}")
            continue
        wzdx['route_details_start'] = route_details_start
        wzdx['route_details_end'] = route_details_end

        if route_details_start['Route'] != route_details_end['Route']:
            logging.info(
                f"Mismatched routes for feature {wzdx['features'][0]['id']}")
            continue

        if route_details_start['Route'] in wzdx_routes:
            wzdx_routes[route_details_start['Route']].append(icone_wzdx)
        else:
            wzdx_routes[route_details_start['Route']] = [icone_wzdx]

    if not wzdx_routes:
        logging.warn('No WZDx route data found!!!')
        return []
    if not icone_wzdx_routes:
        logging.info('No iCone routes found')
        return []

    # Step 3: Identify overlapping events
    for wzdx_route_id, wzdx_matched_msgs in wzdx_routes:
        icone_matching_routes = icone_wzdx_routes.get(wzdx_route_id, [])

        for icone_match in icone_matching_routes:
            for wzdx_match in wzdx_matched_msgs:
                if does_route_overlap(icone_match, wzdx_match) and validate_directionality(icone_match, wzdx_match):
                    matching_routes.append((icone_match, wzdx_match))

    return matching_routes


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


def add_route(obj, lat, lng, name='route_details'):
    route_details = cdot_geospatial_api.get_route_and_measure((lat, lng))
    print(lat, lng, route_details)
    obj[name] = route_details
    return obj


def combine_icone_with_wzdx(icone_wzdx, wzdx_wzdx):
    combined_event = wzdx_wzdx

    combined_event['features'][0]['properties']['start_date'] = icone_wzdx['features'][0]['properties']['start_date']
    combined_event['features'][0]['properties']['core_details']['description'] += ' ' + \
        icone_wzdx['features'][0]['properties']['core_details']['description']

    for i in ['route_details_start', 'route_details_end']:
        if i in combined_event:
            del combined_event[i]
    return combined_event


if __name__ == "__main__":
    main()

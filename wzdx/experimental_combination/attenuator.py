import json
from ..tools import cdot_geospatial_api, geospatial_tools, combination, date_tools
import logging

ATTENUATOR_TIME_AHEAD_SECONDS = 30 * 60
ISO_8601_FORMAT_STRING = "%Y-%m-%dT%H:%M:%SZ"


def main(outputPath='./tests/data/output/wzdx_attenuator_combined.json'):
    with open('./wzdx/sample_files/raw/geotab_avl/attenuator_combination_geotab.json') as f:
        geotab_avl = [json.loads(f.read())]
    with open('./wzdx/sample_files/enhanced/attenuator/attenuator_combination_wzdx.json') as f:
        wzdx = [json.loads(f.read())]

    combined_events = get_combined_events(geotab_avl, wzdx)

    with open(outputPath, 'w+') as f:
        f.write(json.dumps(combined_events, indent=2))


def validate_directionality(geotab, wzdx):
    geotab_bearing = geotab['avl_location']['position']['bearing']
    wzdx_direction = wzdx['features'][0]['properties']['core_details']['direction']

    geotab_direction = geospatial_tools.get_closest_direction_from_bearing(
        geotab_bearing, wzdx_direction)

    return geotab_direction == wzdx_direction


def validate_dates(geotab, wzdx):
    # convert to milliseconds
    geotab_date = geotab['avl_location']['source']['collection_timestamp'] * 1000

    wzdx_start_date = date_tools.get_unix_from_iso_string(
        wzdx['features'][0]['properties']['start_date'])
    wzdx_end_date = date_tools.get_unix_from_iso_string(
        wzdx['features'][0]['properties']['end_date'])

    return wzdx_start_date <= geotab_date <= wzdx_end_date


def get_combined_events(geotab_msgs, wzdx_msgs):
    active_wzdx_msgs = filter(combination.filter_active_wzdx, wzdx_msgs)

    combined_events = []
    for i in identify_overlapping_features(geotab_msgs, active_wzdx_msgs):
        wzdx = combine_geotab_with_wzdx(*i)
        combined_events.append(wzdx)
    logging.info("combined_events")
    return combined_events


def identify_overlapping_features(geotab_msgs, wzdx_msgs):
    geotab_routes = {}
    matching_routes = []

    for geotab_msg in geotab_msgs:
        geometry = geotab_msg['avl_location']['position']

        route_details = cdot_geospatial_api.get_route_and_measure(
            (geometry['latitude'], geometry['longitude']))
        geotab_msg['route_details_start'] = route_details
        geotab_msg['route_details_end'] = None

        if not route_details:
            logging.info(
                f"No geotab route info for {geotab_msg['rtdh_message_id']}")
            continue
        if route_details['Route'] in geotab_routes:
            geotab_routes[route_details['Route']].append(geotab_msg)
        else:
            geotab_routes[route_details['Route']] = [geotab_msg]

    if not geotab_routes:
        return []
    for wzdx in wzdx_msgs:
        if not wzdx.get('route_details_start') or not wzdx.get('route_details_end'):
            route_details_start, route_details_end = combination.get_route_details_for_wzdx(
                wzdx['features'][0])

            if not route_details_start or not route_details_end:
                logging.info(
                    f"No geotab route info for feature {wzdx['features'][0]['id']}")
                continue
            wzdx['route_details_start'] = route_details_start
            wzdx['route_details_end'] = route_details_end
        # else:
        #     route_details_start = wzdx['route_details_start']
        #     route_details_end = wzdx['route_details_end']

        if not wzdx.get('route_details_start'):
            logging.warn(
                f"Unable to retrieve start point route details for event {wzdx['features'][0].get('id')}")
            continue

        matching_geotab_routes = geotab_routes.get(
            wzdx['route_details_start']['Route'], [])
        if matching_geotab_routes:
            logging.info(
                f"FOUND MATCHING GEOTAB ROUTE FOR {wzdx['features'][0]['id']}")

            if not wzdx.get('route_details_end'):
                logging.warn(
                    f"Unable to retrieve start point route details for event {wzdx['features'][0].get('id')}")
                continue
            if (wzdx['route_details_start']['Route'] != wzdx['route_details_end']['Route']):
                continue

            for geotab in matching_geotab_routes:
                logging.debug("Mile markers. geotab: {}, wzdx start: {}, wzdx_end: {}".format(
                    geotab['route_details_start']['Measure'], wzdx['route_details_start']['Measure'], wzdx['route_details_end']['Measure']))
                if (combination.does_route_overlap(geotab, wzdx)
                        and validate_directionality(geotab, wzdx)
                        and validate_dates(geotab, wzdx)):
                    matching_routes.append((geotab, wzdx))
                    return matching_routes

    return matching_routes


def add_route(obj, lat, lng, name='route_details_start'):
    return obj


def combine_geotab_with_wzdx(geotab_avl, wzdx_wzdx):
    wzdx_wzdx_feature = wzdx_wzdx['features'][0]
    speed = geotab_avl['avl_location']['position']['speed']
    bearing = geotab_avl['avl_location']['position']['bearing']
    route_details = geotab_avl['route_details_start']
    distance_ahead = get_distance_ahead_miles(
        speed, ATTENUATOR_TIME_AHEAD_SECONDS)
    combined_event = combine_with_wzdx(
        wzdx_wzdx_feature,
        route_details,
        distance_ahead,
        bearing,
        wzdx_wzdx['route_details_start']['Measure'],
        wzdx_wzdx['route_details_end']['Measure'])

    # update route details for whichever side was overwritten by geotab
    if (combined_event['properties']['beginning_milepost'] == geotab_avl['route_details_start']['Measure']):
        combined_event['properties']['route_details_start'] = geotab_avl['route_details_start']
    elif (combined_event['properties']['ending_milepost'] == geotab_avl['route_details_start']['Measure']):
        combined_event['properties']['route_details_end'] = geotab_avl['route_details_start']

    wzdx_wzdx['features'][0] = combined_event
    return wzdx_wzdx


def combine_with_wzdx(wzdx_wzdx_feature, route_details, distance_ahead, bearing, event_start_marker, event_end_marker):
    mmin = min(event_start_marker, event_end_marker)
    mmax = max(event_start_marker, event_end_marker)
    geometry, startMarker, endMarker = get_geometry_for_distance_ahead(
        distance_ahead, route_details, bearing, mmin, mmax)
    wzdx_wzdx_feature['properties']['beginning_milepost'] = startMarker
    wzdx_wzdx_feature['properties']['ending_milepost'] = endMarker
    wzdx_wzdx_feature['geometry']['coordinates'] = geometry

    return wzdx_wzdx_feature


def get_geometry_for_distance_ahead(distance_ahead, route_details, bearing, mmin, mmax):
    logging.debug("Found matching events, generating geometry ahead:",
                  route_details['Measure'], mmin, mmax)
    route_ahead = cdot_geospatial_api.get_route_geometry_ahead(
        route_details['Route'], route_details['Measure'], bearing, distance_ahead, routeDetails=route_details, mmin=mmin, mmax=mmax)
    return route_ahead['coordinates'], route_ahead['start_measure'], route_ahead['end_measure']


# Speed in mph, time in seconds
def get_distance_ahead_miles(speed, time):
    speed = max(speed, 5)
    return speed * time / 3600


if __name__ == "__main__":
    main()

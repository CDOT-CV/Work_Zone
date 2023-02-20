import json
from ..tools import cdot_geospatial_api, geospatial_tools, combination
import logging

from ..tools import cdot_geospatial_api, geospatial_tools

ATTENUATOR_TIME_AHEAD_SECONDS = 30 * 60
ISO_8601_FORMAT_STRING = "%Y-%m-%dT%H:%M:%SZ"


def main(outputPath='./tests/data/output/wzdx_navjoy_combined.json'):
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


def get_combined_events(geotab_msgs, wzdx_msgs):
    combined_events = []
    for i in identify_overlapping_features(geotab_msgs, wzdx_msgs):
        logging.info("identify_overlapping_features")
        if not validate_directionality(*i):
            logging.info(
                "Ignoring matching Geotab message because the direction does not match the planned event")
            continue
        logging.info("validate_directionality")
        feature = combine_geotab_with_wzdx(*i)
        logging.info("combine_geotab_with_wzdx")
        wzdx = i[1]
        wzdx['features'] = [feature]
        combined_events.append(wzdx)
    logging.info("combined_events")
    return combined_events


def identify_overlapping_features(geotab_msgs, wzdx_msgs):
    geotab_routes = {}
    matching_routes = []

    for geotab_msg in geotab_msgs:
        geometry = geotab_msg['avl_location']['position']
        geotab_msg = add_route(
            geotab_msg, geometry['latitude'], geometry['longitude'])
        geotab_route_details = cdot_geospatial_api.get_route_and_measure(
            (geometry['latitude'], geometry['longitude']))
        if not geotab_route_details:
            logging.info(
                f"No geotab route info for {geotab_msg['rtdh_message_id']}")
            continue
        if geotab_route_details['Route'] in geotab_routes:
            geotab_routes[geotab_route_details['Route']].append(geotab_msg)
        else:
            geotab_routes[geotab_route_details['Route']] = [geotab_msg]

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
                    geotab['route_details']['Measure'], wzdx['route_details_start']['Measure'], wzdx['route_details_end']['Measure']))
                if wzdx['route_details_start']['Measure'] >= geotab['route_details']['Measure'] and wzdx['route_details_end']['Measure'] <= geotab['route_details']['Measure']:
                    matching_routes.append((geotab, wzdx))
                    return matching_routes
                elif wzdx['route_details_start']['Measure'] <= geotab['route_details']['Measure'] and wzdx['route_details_end']['Measure'] >= geotab['route_details']['Measure']:
                    matching_routes.append((geotab, wzdx))
                    return matching_routes

    return matching_routes


def add_route(obj, lat, lng, name='route_details'):
    route_details = cdot_geospatial_api.get_route_and_measure((lat, lng))
    obj[name] = route_details
    return obj


def combine_geotab_with_wzdx(geotab_avl, wzdx_wzdx):
    wzdx_wzdx_feature = wzdx_wzdx['features'][0]
    speed = geotab_avl['avl_location']['position']['speed']
    bearing = geotab_avl['avl_location']['position']['bearing']
    route_details = geotab_avl['route_details']
    distance_ahead = get_distance_ahead_miles(
        speed, ATTENUATOR_TIME_AHEAD_SECONDS)
    combined_event = combine_with_wzdx(
        wzdx_wzdx_feature,
        route_details,
        distance_ahead,
        bearing,
        wzdx_wzdx['route_details_start']['Measure'],
        wzdx_wzdx['route_details_end']['Measure'])

    for i in ['route_details', 'route_details_start', 'route_details_end']:
        if i in combined_event:
            del combined_event[i]
    return combined_event


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

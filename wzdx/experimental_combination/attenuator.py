import json
from datetime import datetime
from wzdx.tools import cdot_geospatial_api, polygon_tools
import logging

ATTENUATOR_TIME_AHEAD_SECONDS = 30 * 60
ISO_8601_FORMAT_STRING = "%Y-%m-%dT%H:%M:%SZ"


def main():
    with open('./wzdx/sample_files/raw/geotab_avl/geotab_all.json') as f:
        geotab_avl = json.loads(f.read())
    with open('./wzdx/sample_files/enhanced/planned_events/planned_event_all.json') as f:
        planned_event = json.loads(f.read())

    combined_events = get_combined_events(geotab_avl, planned_event)

    with open('./wzdx/sample_files/enhanced/planned_events/planned_event_combined.json', 'w+') as f:
        f.write(json.dumps(combined_events, indent=2))


def validate_directionality(geotab, planned_event):
    geotab_bearing = geotab['avl_location']['position']['bearing']
    planned_event_direction = planned_event['features'][0]['properties']['core_details']['direction']

    geotab_direction = polygon_tools.get_closest_direction_from_bearing(
        geotab_bearing, planned_event_direction)

    return geotab_direction == planned_event_direction


def get_combined_events(geotab_msgs, planned_events):
    combined_events = []
    for i in identify_overlapping_features(geotab_msgs, planned_events):
        if not validate_directionality(*i):
            logging.info(
                "Ignoring matching Geotab message because the direction does not match the planned event")
            continue
        feature = combine_geotab_with_planned_event(*i)
        wzdx = i[1]
        wzdx['features'] = [feature]
        combined_events.append(wzdx)
    return combined_events


def identify_overlapping_features(geotab_msgs, planned_events):
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
    for planned_event in planned_events:
        # assume 1 feature per wzdx planned_event
        coordinates = planned_event['features'][0]['geometry']['coordinates']
        planned_event = add_route(
            planned_event, coordinates[0][1], coordinates[0][0], 'route_details_start')

        matching_geotab_routes = geotab_routes.get(
            planned_event['route_details_start']['Route'], [])
        if matching_geotab_routes:
            logging.info(
                f"FOUND MATCHING GEOTAB ROUTE FOR {planned_event['features'][0]['id']}")

            planned_event = add_route(
                planned_event, coordinates[-1][1], coordinates[-1][0], 'route_details_end')
            if (planned_event['route_details_start']['Route'] != planned_event['route_details_end']['Route']):
                continue

            for geotab in matching_geotab_routes:
                logging.debug("Mile markers. geotab: {}, planned_event start: {}, planned_event_end: {}".format(
                    geotab['route_details']['Measure'], planned_event['route_details_start']['Measure'], planned_event['route_details_end']['Measure']))
                if planned_event['route_details_start']['Measure'] >= geotab['route_details']['Measure'] and planned_event['route_details_end']['Measure'] <= geotab['route_details']['Measure']:
                    matching_routes.append((geotab, planned_event))
                    return matching_routes
                elif planned_event['route_details_start']['Measure'] <= geotab['route_details']['Measure'] and planned_event['route_details_end']['Measure'] >= geotab['route_details']['Measure']:
                    matching_routes.append((geotab, planned_event))
                    return matching_routes

    return matching_routes


def add_route(obj, lat, lng, name='route_details'):
    route_details = cdot_geospatial_api.get_route_and_measure((lat, lng))
    obj[name] = route_details
    return obj


def combine_geotab_with_planned_event(geotab_avl, planned_event_wzdx):
    planned_event_wzdx_feature = planned_event_wzdx['features'][0]
    speed = geotab_avl['avl_location']['position']['speed']
    bearing = geotab_avl['avl_location']['position']['bearing']
    route_details = geotab_avl['route_details']
    distance_ahead = get_distance_ahead_miles(
        speed, ATTENUATOR_TIME_AHEAD_SECONDS)
    combined_event = combine_with_planned_event(
        planned_event_wzdx_feature,
        route_details,
        distance_ahead,
        bearing,
        planned_event_wzdx['route_details_start']['Measure'],
        planned_event_wzdx['route_details_end']['Measure'])

    for i in ['route_details', 'route_details_start', 'route_details_end']:
        if i in combined_event:
            del combined_event[i]
    return combined_event


def combine_with_planned_event(planned_event_wzdx_feature, route_details, distance_ahead, bearing, event_start_marker, event_end_marker):
    mmin = min(event_start_marker, event_end_marker)
    mmax = max(event_start_marker, event_end_marker)
    geometry, startMarker, endMarker = get_geometry_for_distance_ahead(
        distance_ahead, route_details, bearing, mmin, mmax)
    planned_event_wzdx_feature['properties']['beginning_milepost'] = startMarker
    planned_event_wzdx_feature['properties']['ending_milepost'] = endMarker
    planned_event_wzdx_feature['geometry']['coordinates'] = geometry

    return planned_event_wzdx_feature


def get_geometry_for_distance_ahead(distance_ahead, route_details, bearing, mmin, mmax):
    route_ahead = cdot_geospatial_api.get_route_geometry_ahead(
        route_details['Route'], route_details['Measure'], bearing, distance_ahead, routeDetails=route_details, mmin=mmin, mmax=mmax)
    return route_ahead['coordinates'], route_ahead['start_measure'], route_ahead['end_measure']


# Speed in mph, time in seconds
def get_distance_ahead_miles(speed, time):
    speed = max(speed, 5)
    return speed * time / 3600


if __name__ == "__main__":
    main()

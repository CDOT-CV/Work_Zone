import json
from datetime import datetime
from wzdx.tools import cdot_geospatial_api, date_tools
from operator import itemgetter


ATTENUATOR_TIME_AHEAD_SECONDS = 30 * 60


def main():
    with open('./sample_file/sraw/geotab_avl/2022_04_13.json') as f:
        geotab_avl = json.loads(f.read())
        speed = geotab_avl['position']['speed']
        bearing = geotab_avl['position']['bearing']
        lat = geotab_avl['position']['latitude']
        long = geotab_avl['position']['longitude']
    with open('./sample_files/enhanced/planned_events/planned_event_v4.json') as f:
        planned_event = json.loads(f.read())
        planned_event_wzdx_feature = planned_event['features'][0]
    distance_ahead = get_distance_ahead(ATTENUATOR_TIME_AHEAD_SECONDS, speed)
    combined_event = combine_with_planned_event(
        planned_event_wzdx_feature, (lat, long), distance_ahead, bearing)
    raise NotImplementedError("main method not implemented")


def combine_with_planned_event(planned_event_wzdx_feature, curr_long_lat, distance_ahead, bearing):
    geometry = get_geometry_for_distance_ahead(
        distance_ahead, curr_long_lat, bearing)
    planned_event_wzdx_feature['geometry']['coordinates'] = geometry

    return planned_event_wzdx_feature


def get_geometry_for_distance_ahead(distance_ahead, curr_long_lat, bearing):
    reoutId, startMeasure = itemgetter('Route', 'Measure')(
        cdot_geospatial_api.get_route_and_measure(curr_long_lat))
    routes = cdot_geospatial_api.get_routes_ahead(
        route['Route'], route['measure'], route['direction'], distance_ahead)
    geometry = []
    for route in routes:
        geometry.extend(cdot_geospatial_api.get_route_between_measures(
            route['Route'], route['MMin'], route['MMax']))
    return geometry


# Speed in mph, time in seconds
def get_distance_ahead(speed, time):
    return speed * time / 3600


if __name__ == "__main__":
    main()

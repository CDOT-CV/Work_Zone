import json
from datetime import datetime
from wzdx.tools import cdot_geospatial_api, date_tools
from operator import itemgetter


ATTENUATOR_TIME_AHEAD_SECONDS = 30 * 60


def main():
    with open('./wzdx/sample_files/raw/geotab_avl/2022_04_13.json') as f:
        geotab_avl = json.loads(f.read())
        speed = geotab_avl['avl_location']['position']['speed']
        bearing = geotab_avl['avl_location']['position']['bearing']
        lat = geotab_avl['avl_location']['position']['latitude']
        long = geotab_avl['avl_location']['position']['longitude']
    with open('./wzdx/sample_files/enhanced/planned_events/planned_event_v4.json') as f:
        planned_event = json.loads(f.read())
        planned_event_wzdx_feature = planned_event['features'][0]
    distance_ahead = get_distance_ahead(ATTENUATOR_TIME_AHEAD_SECONDS, speed)
    combined_event = combine_with_planned_event(
        planned_event_wzdx_feature, (lat, long), distance_ahead, bearing)
    with open('./wzdx/sample_files/enhanced/planned_events/planned_event_v4_combined.json', 'w+') as f:
        f.write(json.dumps(combined_event, indent='  '))


def combine_with_planned_event(planned_event_wzdx_feature, curr_long_lat, distance_ahead, bearing):
    geometry, startMeasure, endMeasure = get_geometry_for_distance_ahead(
        distance_ahead, curr_long_lat, bearing)
    planned_event_wzdx_feature['properties']['beginning_milepost'] = startMeasure
    planned_event_wzdx_feature['properties']['ending_milepost'] = endMeasure
    planned_event_wzdx_feature['geometry']['coordinates'] = geometry

    return planned_event_wzdx_feature


def get_geometry_for_distance_ahead(distance_ahead, curr_long_lat, bearing):
    curr_lat_long = (curr_long_lat[1], curr_long_lat[0])
    routeDetails = cdot_geospatial_api.get_route_and_measure(curr_lat_long)
    if not routeDetails:
        return []

    routeId, measure = itemgetter('Route', 'Measure')(routeDetails)
    route_ahead = cdot_geospatial_api.get_route_geometry_ahead(
        routeId, measure, bearing, distance_ahead)
    return route_ahead['coordinates'], route_ahead['start_measure'], route_ahead['end_measure']


# Speed in mph, time in seconds
def get_distance_ahead(speed, time):
    return speed * time / 3600


if __name__ == "__main__":
    main()

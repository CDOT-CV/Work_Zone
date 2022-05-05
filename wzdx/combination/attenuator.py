from datetime import datetime
from wzdx.tools import cdot_geospatial_api, date_tools


ATTENUATOR_DISTANCE_AHEAD_MILES = 4


def main():
    raise NotImplementedError("main method not implemented")


def combine_with_planned_event(planned_event_wzdx_feature, curr_long_lat, bearing):
    geometry = get_geometry_for_distance_ahead(
        ATTENUATOR_DISTANCE_AHEAD_MILES, curr_long_lat, bearing)
    planned_event_wzdx_feature['geometry']['coordinates'] = geometry

    return planned_event_wzdx_feature


def get_geometry_for_distance_ahead(distance_ahead, curr_long_lat, bearing):
    route = cdot_geospatial_api.get_route_and_measure(curr_long_lat, bearing)
    routes = cdot_geospatial_api.get_routes_ahead(
        route['Route'], route['measure'], route['direction'], distance_ahead)
    geometry = []
    for route in routes:
        geometry.extend(cdot_geospatial_api.get_route_between_measures(
            route['Route'], route['MMin'], route['MMax']))
    return geometry


if __name__ == "__main__":
    main()

from typing import Tuple
from shapely import LineString, Point
import geopandas as gpd
import math


def lazy_dist(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def get_closest_pt(p, line):
    closest_dist = float("inf")
    closest_pt = None
    for pt in line:
        dist = lazy_dist(p, pt)
        if dist < closest_dist:
            closest_dist = dist
            closest_pt = pt
    return closest_pt


class RouteApi:
    def __init__(self, routes: dict):
        self.routes = routes

    def get_routes_list(self) -> list[dict]:
        return self.routes.values()

    def get_route_details(self, route_id) -> dict:
        return self.routes.get(route_id)

    def get_route_and_measure(
        self, lng: float, lat: float, threshold_meters=10000
    ) -> tuple[str, float, list[tuple[str, float]]]:
        # find the closest route to the point
        all_routes = []
        closest_route = (None, None)
        closest_distance = threshold_meters
        for route_id, route in self.routes.items():
            if not route["Geometry"]:
                continue
            line = gpd.GeoSeries(LineString(route["Geometry"]), crs="EPSG:4326")

            # Reproject the line to EPSG:3857
            line = line.to_crs("EPSG:3857")

            # Create a Point object with the given latitude and longitude
            point = gpd.GeoSeries([Point(lng, lat)], crs="EPSG:4326")

            # Reproject the point to EPSG:3857
            point = point.to_crs("EPSG:3857")

            # Calculate the distance in meters
            distance = line.distance(point.iloc[0])[0]

            if distance < threshold_meters:
                all_routes.append((route_id, distance))
            if distance < closest_distance:
                closest_distance = distance
                closest_index = list(route["Geometry"]).index(
                    get_closest_pt((lng, lat), route["Geometry"])
                )
                closest_route = (
                    route_id,
                    self.routes[route_id]["Distances"][closest_index],
                )
        all_routes.sort(key=lambda x: x[1])
        return closest_route[0], closest_route[1], closest_distance, all_routes

    def get_point_at_measure(self, route_id: str, measure: float) -> list[float]:
        route = self.routes.get(route_id)
        if not route:
            return None
        # find the closest point along the line to the measure
        closest_point = None
        distance = float("inf")
        for i, mm in enumerate(route["Distances"]):
            if abs(mm - measure) < distance:
                distance = abs(mm - measure)
                closest_point = route["Geometry"][i]
        return closest_point

    def get_route_between_measures(
        self, route_id: str, start_measure: float, end_measure: float
    ) -> list[list[float]]:
        geometry = []
        route = self.routes.get(route_id)
        if not route["Geometry"]:
            return None
        l = len(geometry)
        for i, p in enumerate(route["Geometry"]):
            if i == 0:
                continue
            if (
                start_measure <= route["Distances"][i] <= end_measure
                or start_measure >= route["Distances"][i] >= end_measure
            ):
                if start_measure > end_measure and len(geometry) != l:
                    geometry.insert(l, p)
                else:
                    geometry.append(p)
        return geometry

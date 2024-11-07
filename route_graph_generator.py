from wzdx.tools.cdot_geospatial_api import GeospatialApi
from wzdx.tools import geospatial_tools
import json

geospatial_api = GeospatialApi()


def do_routes_intersect(route1, route2):
    if not route1["Geometry"] or not route2["Geometry"]:
        return None
    # check if any of the end/starting points of the routes are the same
    if route1["Geometry"][0] == route2["Geometry"][0]:
        return (
            (route1["MMin"], route1["Geometry"][0]),
            (route2["MMin"], route2["Geometry"][0]),
            0,
        )
    elif route1["Geometry"][0] == route2["Geometry"][-1]:
        return (
            (route1["MMin"], route1["Geometry"][0]),
            (route2["MMax"], route2["Geometry"][-1]),
            0,
        )
    elif route1["Geometry"][-1] == route2["Geometry"][0]:
        return (
            (route1["MMax"], route1["Geometry"][-1]),
            (route2["MMin"], route2["Geometry"][0]),
            0,
        )
    elif route1["Geometry"][-1] == route2["Geometry"][-1]:
        return (
            (route1["MMax"], route1["Geometry"][-1]),
            (route2["MMax"], route2["Geometry"][-1]),
            0,
        )

    if (
        route1["Route"] == route2["Route"]
        or f'{route1["Route"]}_DEC' == route2["Route"]
        or route1["Route"] == f'{route2["Route"]}_DEC'
    ):
        return None

    # check if the start of route1 intersects with route2
    for i, point1 in enumerate([route1["Geometry"][0], route1["Geometry"][-1]]):
        for point2 in route2["Geometry"]:
            dist = geospatial_tools.getDist(
                [point1[1], point1[0]], [point2[1], point2[0]]
            )
            if dist < 100:
                if i == 0:
                    p1 = route1["MMin"]
                else:
                    p1 = route1["MMax"]
                p2 = geospatial_api.get_route_and_measure([point2[1], point2[0]])
                if (
                    p2["Route"] != route2["Route"]
                    and p2["Route"] != f'{route2["Route"]}_DEC'
                    and f'{p2["Route"]}_DEC' != route2["Route"]
                ):
                    print(f"ROUTE MISMATCH {route2['Route']}, {p2['Route']}, {point2}")
                else:
                    return (p1, point1), (p2["Measure"], point2), dist
    return None


# get all routes
# routes = geospatial_api.get_routes_list()
# json.dump(routes, open("routes.json", "w"), indent=2)

routes = json.load(open("routes_with_geometry.json"))

# for route in routes:
#     # get the route geometry
#     if not route.get("Geometry"):
#         geometry = geospatial_api.get_route_between_measures(
#             route["Route"], route["MMin"], route["MMax"], compressed=False
#         )
#         route["Geometry"] = geometry

# json.dump(routes, open("routes_with_geometry.json", "w"), indent=2)

# iterate over routes, identify possible intersections
for route in routes:
    for other_route in routes:
        if route["Route"] == other_route["Route"]:
            continue
        if route["Geometry"] == other_route["Geometry"]:
            continue
        prev_intersections = route.get("intersections", [])
        for intersection in prev_intersections:
            if intersection["Route"] == other_route["Route"]:
                break
        # check if the routes intersect
        intersection = do_routes_intersect(route, other_route)
        if intersection:
            print(
                f"Routes {route['Route']} and {other_route['Route']} intersect {intersection}"
            )
            props1, props2, dist = intersection
            r1_mm, p1 = props1
            r2_mm, p2 = props2
            if not route.get("intersections"):
                route["intersections"] = []
            if not other_route.get("intersections"):
                other_route["intersections"] = []
            route["intersections"].append(
                {
                    "mm": r1_mm,
                    "position": p1,
                    "mm_other": r2_mm,
                    "position_other": p2,
                    "distance": dist,
                    "Route": other_route["Route"],
                }
            )
            other_route["intersections"].append(
                {
                    "mm": r2_mm,
                    "position": p1,
                    "mm_other": r1_mm,
                    "position_other": p2,
                    "distance": dist,
                    "Route": route["Route"],
                }
            )
json.dump(routes, open("routes_with_intersections.json", "w"), indent=2)
routes_without_geometry = []
for route in routes:
    routes_without_geometry.append(
        {
            "Route": route["Route"],
            "MMin": route["MMin"],
            "MMax": route["MMax"],
            "intersections": route.get("intersections", []),
        }
    )
json.dump(
    routes_without_geometry,
    open("routes_with_intersections_no_geometry.json", "w"),
    indent=2,
)

routes = json.load(open("routes_with_intersections.json"))

# convert into geojson
geojson = {
    "type": "FeatureCollection",
    "features": [],
}
for route in routes:
    feature = {
        "type": "Feature",
        "properties": {
            "Route": route["Route"],
            "MMin": route["MMin"],
            "MMax": route["MMax"],
            "intersections": route.get("intersections"),
        },
        "geometry": {"type": "LineString", "coordinates": route["Geometry"]},
    }
    for i, intersection in enumerate(route.get("intersections", [])):
        feature["properties"][f"intersection{i}_route"] = intersection["Route"]
    geojson["features"].append(feature)


json.dump(geojson, open("routes.geojson", "w"), indent=2)

# convert into geojson
intersection_points = {
    "type": "FeatureCollection",
    "features": [],
}
for route in routes:
    for intersection in route.get("intersections", []):
        feature = {
            "type": "Feature",
            "properties": {
                "Route": route["Route"],
                "OtherRoute": intersection["Route"],
                "mm": intersection["mm"],
                "mm_other": intersection["mm_other"],
                "distance": intersection["distance"],
                "p1": intersection["position"],
                "p2": intersection["position_other"],
                "Color": (
                    "#00FF00"
                    if intersection["distance"] < 5
                    else ("#ff9900" if intersection["distance"] < 25 else "#FF0000")
                ),
            },
            "geometry": {"type": "Point", "coordinates": intersection["position"]},
        }
        intersection_points["features"].append(feature)


json.dump(intersection_points, open("intersection_points.geojson", "w"), indent=2)

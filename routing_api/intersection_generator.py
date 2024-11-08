from wzdx.tools.cdot_geospatial_api import GeospatialApi
from wzdx.tools.geospatial_tools import getDist
import json
import geopandas as gpd
from shapely.geometry import LineString


geospatial_api = GeospatialApi()


# # get all routes
# routes = geospatial_api.get_routes_list()
# json.dump(routes, open("routes.json", "w"), indent=2)

# # Add geometry
# for route in routes:
#     # get the route geometry
#     if not route.get("Geometry"):
#         geometry = geospatial_api.get_route_between_measures(
#             route["Route"], route["MMin"], route["MMax"], compressed=False
#         )
#         route["Geometry"] = geometry

# json.dump(routes, open("routes_with_geometry.json", "w"), indent=2)
routes = json.load(open("routing_api/routes_with_geometry.json"))

# add mile marker estimates to routes
for route in routes:
    start = route["MMin"]
    end = route["MMax"]
    distances = []
    if not route["Geometry"]:
        route["Distances"] = []
        continue
    for i, p in enumerate(route["Geometry"]):
        if i == 0:
            distances.append(0)
            continue
        distances.append(
            getDist(
                [route["Geometry"][i - 1][1], route["Geometry"][i - 1][0]],
                [p[1], p[0]],
            )
            * 0.000621371
        )
    total_distance = sum(distances)
    distance_factor = (end - start) / total_distance
    print("Distance factor", route["Route"], distance_factor)
    route["Distances"] = []
    for i, d in enumerate(distances):
        if i == 0:
            route["Distances"].append(start)
            continue
        route["Distances"].append(
            min(route["Distances"][i - 1] + d * distance_factor, end)
        )

json.dump(routes, open("routing_api/routes_with_mile_markers.json", "w"), indent=2)
# routes = json.load(open("routing_api/routes_with_mile_markers.json"))

data = {"route_id": [], "geometry": [], "mileposts": []}
for i, route in enumerate(routes):
    data["route_id"].append(i)
    data["geometry"].append(LineString(route["Geometry"]))
    data["mileposts"].append(route["Distances"])


# Create a GeoDataFrame
gdf = gpd.GeoDataFrame(data, geometry="geometry", crs="EPSG:4326")

# Reproject to a CRS suitable for distance calculations (e.g., EPSG:3857 for meters)
gdf = gdf.to_crs("EPSG:3857")

# Perform spatial join to find intersections
intersections = gpd.sjoin(
    gdf,
    gdf,
    how="inner",
    predicate="intersects",
    lsuffix="index_left",
    rsuffix="index_right",
)

intersections = intersections[
    intersections["route_id_index_left"] != intersections["route_id_index_right"]
]

# Collect intersection data in array and JSON dict formats
intersection_data_array = []

for idx, row in intersections.iterrows():
    line1 = gdf.loc[row["route_id_index_left"], "geometry"]
    line2 = gdf.loc[row["route_id_index_right"], "geometry"]
    intersection_point = line1.intersection(line2)

    # Access mileposts and geometries for each intersecting route
    mileposts_1 = gdf.loc[row["route_id_index_left"], "mileposts"]
    mileposts_2 = gdf.loc[row["route_id_index_right"], "mileposts"]

    if intersection_point.geom_type == "Point":
        # Calculate the distance along each LineString to the intersection point
        distance_along_1_meters = line1.project(intersection_point)
        distance_along_2_meters = line2.project(intersection_point)

        # Convert distances to miles (1 mile ≈ 1609.34 meters)
        distance_along_1 = distance_along_1_meters / 1609.34
        distance_along_2 = distance_along_2_meters / 1609.34

        # Find the closest milepost for each route based on calculated distance
        closest_milepost_1 = min(mileposts_1, key=lambda mp: abs(mp - distance_along_1))
        closest_milepost_2 = min(mileposts_2, key=lambda mp: abs(mp - distance_along_2))

        # Collect data as dictionary for array
        intersection_info = {
            "route_id_1": routes[gdf.loc[row["route_id_index_left"], "route_id"]][
                "Route"
            ],
            "route_id_2": routes[gdf.loc[row["route_id_index_right"], "route_id"]][
                "Route"
            ],
            "milepost_1": closest_milepost_1,
            "milepost_2": closest_milepost_2,
            "coordinates": gpd.GeoSeries([intersection_point], crs="EPSG:3857")
            .to_crs("EPSG:4326")
            .iloc[0]
            .coords[0],  # Back to lat/lon,
        }
        intersection_data_array.append(intersection_info)

# Convert to JSON string for output or save to file
json.dump(
    intersection_data_array,
    open("routing_api/intersection_data_array.json", "w"),
    indent=2,
    default=str,
)

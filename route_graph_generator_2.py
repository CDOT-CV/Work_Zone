from wzdx.tools.cdot_geospatial_api import GeospatialApi
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
routes = json.load(open("routes_with_geometry.json"))


data = {"route_id": [], "geometry": []}
for i, route in enumerate(routes):
    data["route_id"].append(i)
    data["geometry"].append(LineString(route["Geometry"]))


# Create a GeoDataFrame
gdf = gpd.GeoDataFrame(data, geometry="geometry", crs="EPSG:4326")

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


# Print the column names to debug
print(intersections.columns)

# # Remove self-intersections
# intersections = [
#     intersection
#     for intersection in intersections
#     if intersection["left"] != intersection["right"]
# ]

# Collect intersection data in array and JSON dict formats
intersection_data_array = []

for idx, row in intersections.iterrows():
    temp = row["route_id_index_left"]
    print(temp)
    line1 = gdf.loc[row["route_id_index_left"], "geometry"]
    line2 = gdf.loc[row["route_id_index_right"], "geometry"]
    intersection_point = line1.intersection(line2)

    # Collect data as dictionary for array
    intersection_info = {
        "route_id_1": gdf.loc[row["route_id_index_left"], "route_id"],
        "route_id_2": gdf.loc[row["route_id_index_right"], "route_id"],
        "coordinates": (
            (intersection_point.x, intersection_point.y)
            if intersection_point.geom_type == "Point"
            else None
        ),
    }
    intersection_data_array.append(intersection_info)

# Convert to JSON string for output or save to file
json.dump(
    intersection_data_array,
    open("intersection_data_array.json", "w"),
    indent=2,
    default=str,
)

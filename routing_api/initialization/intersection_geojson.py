import json

intersections = json.load(
    open("./routing_api/initialization/intersection_data_array.json")
)

geojson = [
    {
        "type": "Feature",
        "properties": {
            "route_id_1": intersection["route_id_1"],
            "route_id_2": intersection["route_id_2"],
            "milepost_1": intersection["milepost_1"],
            "milepost_2": intersection["milepost_2"],
        },
        "geometry": {
            "type": "Point",
            "coordinates": intersection["coordinates"],
        },
    }
    for intersection in intersections
]

json.dump(
    {"type": "FeatureCollection", "features": geojson},
    open("./routing_api/initialization/intersections.geojson", "w"),
    indent=2,
)

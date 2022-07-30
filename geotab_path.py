import json


locations = json.loads(
    open('./testing_results/geotab/geotab_all_20220728-151954.json').read())
locations.sort(key=lambda x: x['rtdh_timestamp'])

open('geotab_path_sorted.json', 'w').write(
    json.dumps(locations, indent=2, default=str))


path = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "LineString",
                "coordinates": [[float(i['avl_location']['position']['longitude']),
                                 float(i['avl_location']['position']['latitude'])] for i in locations]
            }
        }
    ]
}


open('geotab_path_geo.json', 'w').write(
    json.dumps(path, indent=2, default=str))

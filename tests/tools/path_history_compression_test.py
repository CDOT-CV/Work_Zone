import json
from wzdx.tools import path_history_compression, cdot_geospatial_api

route_details = cdot_geospatial_api.get_route_and_measure(
    (37.195715860000064, -105.42818103399998))
path = cdot_geospatial_api.get_route_between_measures(
    route_details['Route'], 15, 30)


wzdx = json.loads(open('geotab_path_geo.json').read())

wzdx['features'][0]['geometry']['coordinates'] = path
open('path_normal.json', 'w').write(json.dumps(wzdx, indent=2))

print(len(path))
path_comp = path_history_compression.generage_compressed_path(path)
print(len(path_comp))


wzdx['features'][0]['geometry']['coordinates'] = path_comp
open('path_concise.json', 'w').write(json.dumps(wzdx, indent=2))

path_concise_2 = cdot_geospatial_api.get_route_between_measures(
    route_details['Route'], 15, 30, compressed=True)

wzdx['features'][0]['geometry']['coordinates'] = path_comp
open('path_concise_2.json', 'w').write(json.dumps(wzdx, indent=2))

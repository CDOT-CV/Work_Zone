import requests
import json

import cdot_geospatial_api

print(cdot_geospatial_api.get_route_details('070A', pointsToSkip=100))
# print(cdot_geospatial_api.get_route_and_measure((39.670497, -104.096042), ))
# print(cdot_geospatial_api.get_routes_ahead())
# print(cdot_geospatial_api.get_route_between_measures(
#     '070A', 50, 60, pointsToSkip=10))

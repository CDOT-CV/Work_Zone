import requests
import json

BASE_URL = "https://dtdapps.coloradodot.info/arcgis/rest/services/LRS/Routes/MapServer/exts/CdotLrsAccessRounded"
ROUTE_BETWEEN_MEASURES_API = "RouteBetweenMeasures"
GET_ROUTE_AND_MEASURE_API = "GetMeasure"
GET_ROUTES = "ROUTES"
SR = "4326"

def get_route_details(routeId=None):
    parameters = []
    if routeId:
        parameters.append(f'routeId={routeId}')
    parameters.append(f"f=pjson")

    url = f"{BASE_URL}/{GET_ROUTES}?{'&'.join(parameters)}"

    #https://dtdapps.coloradodot.info/arcgis/rest/services/LRS/Routes/MapServer/exts/CdotLrsAccessRounded/Routes?f=pjson
    #https://dtdapps.coloradodot.info/arcgis/rest/services/LRS/Routes/MapServer/exts/CdotLrsAccessRounded/Route?routeId=070A&outSR=4326&f=pjson

    # response = requests.get(url)
    response = [{'routeID': '070A', 'MMin': 0, 'MMax': 499}]
    return response

def get_route_and_measure(latLng, bearing):
    # Get route ID and mile marker from lat/long and heading
    lat, lng = latLng

    parameters = []
    parameters.append(f"latitude={lat}")
    parameters.append(f"longitude={lng}")
    parameters.append(f"heading={bearing}")
    parameters.append(f"inSR={SR}")
    parameters.append(f"f=pjson")

    url = f"{BASE_URL}/{GET_ROUTE_AND_MEASURE_API}?{'&'.join(parameters)}"

    # response = requests.get(url)
    response = {}

    return "070A", 50.0

def get_routes_ahead(route, startMeasure, direction, distanceAhead):
    # Get list of routes and mile markers for a distance ahead and distance

    parameters = []
    parameters.append(f"routeId={route}")
    parameters.append(f"startMeasure={startMeasure}")
    parameters.append(f"direction={direction}")
    parameters.append(f"distance={distanceAhead}")
    parameters.append(f"inSR={SR}")
    parameters.append(f"f=pjson")

    url = f"{BASE_URL}/{GET_ROUTE_AND_MEASURE_API}?{'&'.join(parameters)}"

    # response = requests.get(url)
    response = [
        {"Route": "070A", "MMin": 12, 'MMax': 499}, 
        {"Route": "070B", 'MMin': 0, 'MMax': 2}
    ]

    return response

def get_route_between_measures(routeId, startMeasure, endMeasure, pointsToSkip=1):
    # Get lat/long points between two mile markers on route

    parameters = []
    parameters.append(f"routeId={routeId}")
    parameters.append(f"fromMeasure={startMeasure}")
    parameters.append(f"toMeasure={endMeasure}")
    parameters.append(f"outSR={SR}")
    parameters.append(f"f=pjson")

    url = f"{BASE_URL}/{ROUTE_BETWEEN_MEASURES_API}?{'&'.join(parameters)}"

    # call api
    # response = requests.get(url)
    response = json.loads(open('./wzdx/sample_files/raw/geotab_avl/geospatial_endpoint_response.json').read())

    linestring = []
    for feature in response.get('features', []):
        for path in feature.get('geometry', {}).get('paths', []):
                linestring.extend(path)

    linestring = [v for i, v in enumerate(linestring) if i % (pointsToSkip+1) == 0]
    
    return linestring

    
    # RouteBetweenMeasures?routeId=070A&fromMeasure=50&toMeasure=60&outSR=4326&f=pjson
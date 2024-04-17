import json
import logging

import requests

from ..tools import geospatial_tools, path_history_compression

BASE_URL = "https://dtdapps.coloradodot.info/arcgis/rest/services/LRS/Routes_withDEC/MapServer/exts/CdotLrsAccessRounded"
# BASE_URL = "https://dtdapps.colorado.gov/server/rest/services/LRS/Routes_withDEC/MapServer/exts/CdotLrsAccessRounded"
ROUTE_BETWEEN_MEASURES_API = "RouteBetweenMeasures"
GET_ROUTE_AND_MEASURE_API = "MeasureAtPoint"
GET_POINT_AT_MEASURE_API = "PointAtMeasure"
GET_ROUTES_API = "ROUTES"
GET_ROUTE_API = "ROUTE"
SR = "4326"


class GeospatialApi:
    def __init__(
        self, getCachedRequest=lambda x: None, setCachedRequest=lambda x, y: None
    ):
        self.getCachedRequest = getCachedRequest
        self.setCachedRequest = setCachedRequest

    def _make_web_request(self, url: str, timeout):
        resp = requests.get(url, timeout=timeout).content.decode("utf-8")
        return resp

    def get_routes_list(self):
        parameters = []
        parameters.append(f"f=pjson")

        url = f"{BASE_URL}/{GET_ROUTES_API}?{'&'.join(parameters)}"
        logging.debug(url)

        # https://dtdapps.coloradodot.info/arcgis/rest/services/LRS/Routes/MapServer/exts/CdotLrsAccessRounded/Routes?f=pjson
        # https://dtdapps.coloradodot.info/arcgis/rest/services/LRS/Routes/MapServer/exts/CdotLrsAccessRounded/Route?routeId=070A&outSR=4326&f=pjson

        resp = self._make_cached_web_request(url)
        if not resp:
            return None
        # response = [{'routeID': '070A', 'MMin': 0, 'MMax': 499}]
        return resp

    def get_route_details(self, routeId):
        parameters = []
        parameters.append(f"routeId={routeId}")
        parameters.append(f"outSR={SR}")
        parameters.append(f"f=pjson")

        url = f"{BASE_URL}/{GET_ROUTE_API}?{'&'.join(parameters)}"
        logging.debug(url)

        # https://dtdapps.coloradodot.info/arcgis/rest/services/LRS/Routes/MapServer/exts/CdotLrsAccessRounded/Routes?f=pjson
        # https://dtdapps.coloradodot.info/arcgis/rest/services/LRS/Routes/MapServer/exts/CdotLrsAccessRounded/Route?routeId=070A&outSR=4326&f=pjson

        resp = self._make_cached_web_request(url)
        if not resp:
            return None
        # response = {'routeID': '070A', 'MMin': 0, 'MMax': 499}

        route_details = {
            "Route": resp["features"][0]["attributes"]["Route"],
            "MMin": float(resp["features"][0]["attributes"]["MMin"]),
            "MMax": float(resp["features"][0]["attributes"]["MMax"]),
        }

        return route_details

    def get_route_and_measure(self, latLng, heading=None, tolerance=10000):
        # Get route ID and mile marker from lat/long and heading
        lat, lng = latLng

        parameters = []
        parameters.append(f"x={lng}")
        parameters.append(f"y={lat}")
        parameters.append(f"tolerance={tolerance}")
        parameters.append(f"inSR={SR}")
        parameters.append(f"outSR={SR}")
        parameters.append(f"f=pjson")

        url = f"{BASE_URL}/{GET_ROUTE_AND_MEASURE_API}?{'&'.join(parameters)}"
        logging.debug(url)

        # https://dtdapps.coloradodot.info/arcgis/rest/services/LRS/Routes/MapServer/exts/CdotLrsAccessRounded/MeasureAtPoint?x=-105&y=39.5&inSR=4326&tolerance=10000&outSR=&f=html
        resp = self._make_cached_web_request(url)
        if not resp:
            return None

        if not resp.get("features"):
            return {}
        route_details = {
            "Route": resp["features"][0]["attributes"]["Route"],
            "Measure": float(resp["features"][0]["attributes"]["Measure"]),
            "MMin": float(resp["features"][0]["attributes"]["MMin"]),
            "MMax": float(resp["features"][0]["attributes"]["MMax"]),
            "Distance": float(resp["features"][0]["attributes"]["Distance"]),
        }

        if heading:
            step = 0.1  # 500 ft
            route = route_details["Route"]
            measure = route_details["Measure"]
            mmin = route_details["MMin"]
            mmax = route_details["MMax"]
            startMeasure = measure - step
            endMeasure = measure
            if startMeasure < mmin:
                # reverse order
                startMeasure = measure
                endMeasure = measure + step
            coords = self.get_route_between_measures(route, startMeasure, endMeasure)
            bearing = geospatial_tools.get_heading_from_coordinates(coords)

            if bearing > 180:
                bearing -= 360
            if abs(bearing - heading) < 90:
                route_details["Direction"] = "+"
            else:
                route_details["Direction"] = "-"

        return route_details

    def get_point_at_measure(self, routeId, measure):
        # Get lat/long points between two mile markers on route

        parameters = []
        parameters.append(f"routeId={routeId}")
        parameters.append(f"measure={measure}")
        parameters.append(f"outSR={SR}")
        parameters.append(f"f=pjson")

        url = f"{BASE_URL}/{GET_POINT_AT_MEASURE_API}?{'&'.join(parameters)}"
        logging.debug(url)

        # call api
        response = self._make_cached_web_request(url)
        if not response:
            return None

        lat = response["features"][0]["geometry"]["y"]
        long = response["features"][0]["geometry"]["x"]

        return (lat, long)

    def get_route_geometry_ahead(
        self,
        routeId,
        startMeasure,
        heading,
        distanceAhead,
        compressed=False,
        routeDetails=None,
        mmin=None,
        mmax=None,
    ):
        # Get list of routes and mile markers for a distance ahead and distance

        # TODO: Integrate direction to determine whether to add/subtract distance
        if not routeDetails:
            latLng = self.get_point_at_measure(routeId, startMeasure)
            routeDetails = self.get_route_and_measure(latLng, heading)
            if not latLng or not routeDetails:
                return None

        # process direction here
        if routeDetails.get("Direction", "+") == "+":
            endMeasure = startMeasure + distanceAhead
            endMeasure = min(endMeasure, routeDetails["MMax"])
        else:
            endMeasure = startMeasure - distanceAhead
            endMeasure = max(endMeasure, routeDetails["MMin"])

        if mmin != None and mmax != None:
            # Force mmin > mmax
            if mmin > mmax:
                temp = mmin
                mmin = mmax
                mmax = temp

            # Force measures between bounds
            startMeasure = min(max(startMeasure, mmin), mmax)
            endMeasure = min(max(endMeasure, mmin), mmax)

        return {
            "start_measure": startMeasure,
            "end_measure": endMeasure,
            "coordinates": self.get_route_between_measures(
                routeId, startMeasure, endMeasure, compressed=compressed
            ),
        }

    def get_route_between_measures(
        self, routeId, startMeasure, endMeasure, dualCarriageway=True, compressed=False
    ):
        # Get lat/long points between two mile markers on route
        if dualCarriageway and self.is_route_dec(routeId, startMeasure, endMeasure):
            routeId = f"{routeId}_dec"

        parameters = []
        parameters.append(f"routeId={routeId}")
        parameters.append(f"fromMeasure={startMeasure}")
        parameters.append(f"toMeasure={endMeasure}")
        parameters.append(f"outSR={SR}")
        parameters.append(f"f=pjson")

        url = f"{BASE_URL}/{ROUTE_BETWEEN_MEASURES_API}?{'&'.join(parameters)}"
        logging.debug(url)

        # call api
        response = self._make_cached_web_request(url)
        if not response:
            return None

        linestring = []
        for feature in response.get("features", []):
            for path in feature.get("geometry", {}).get("paths", []):
                linestring.extend(path)

        if compressed:
            linestring = path_history_compression.generate_compressed_path(linestring)

        return linestring

        # RouteBetweenMeasures?routeId=070A&fromMeasure=50&toMeasure=60&outSR=4326&f=pjson

    def is_route_dec(self, routeId, startMeasure, endMeasure):
        return endMeasure > startMeasure

    # def get_cache_info():
    #     CacheData = namedtuple('CacheData', ['currsize', 'hits', 'misses'])

    #     return CacheData(0, 0, 0)
    #     # return _make_web_request.cache_info()

    def _make_cached_web_request(
        self, url: str, timeout: int = 5, retryOnTimeout: bool = False
    ):
        try:
            response = self.getCachedRequest(url)
            if not response:
                response = self._make_web_request(url, timeout=timeout)
                self.setCachedRequest(url, response)
            return json.loads(response)
        except requests.exceptions.Timeout as e:
            if retryOnTimeout:
                logging.debug(
                    f"Geospatial Request Timed Out for URL: {url}. Timeout: {timeout}. Retrying with double timeout"
                )
                return self._make_cached_web_request(
                    url, timeout=timeout * 2, retryOnTimeout=False
                )
            else:
                logging.warn(
                    f"Geospatial Request Timed Out for URL: {url}. Timeout: {timeout}. Error: {e}"
                )
                return None
        except requests.exceptions.RequestException as e:
            logging.warn(
                f"Geospatial Request Failed for URL: {url}. Timeout: {timeout}. Error: {e}"
            )
            return None


# # average request size is 1000b, so 10MB cache is roughly 10k requests
# @cached(cache=Cache(maxsize=1024*10))
# def _make_web_request(url: str, timeout):
#     resp = requests.get(url, timeout=timeout).content.decode('utf-8')
#     return resp

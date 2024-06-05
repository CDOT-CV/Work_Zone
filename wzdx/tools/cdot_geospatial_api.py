import json
import logging
import time

import requests
import os
import sys

from ..tools import geospatial_tools, path_history_compression


class GeospatialApi:
    def __init__(
        self,
        getCachedRequest=lambda x: None,
        setCachedRequest=lambda x, y: None,
        BASE_URL=os.getenv(
            "CDOT_GEOSPATIAL_API_BASE_URL",
            "https://dtdapps.colorado.gov/server/rest/services/LRS/Routes_withDEC/MapServer/exts/CdotLrsAccessRounded",
        ),
    ):
        self.getCachedRequest = getCachedRequest
        self.setCachedRequest = setCachedRequest
        self.BASE_URL = BASE_URL
        self.ROUTE_BETWEEN_MEASURES_API = "RouteBetweenMeasures"
        self.GET_ROUTE_AND_MEASURE_API = "MeasureAtPoint"
        self.GET_POINT_AT_MEASURE_API = "PointAtMeasure"
        self.GET_ROUTES_API = "ROUTES"
        self.GET_ROUTE_API = "ROUTE"
        self.SR = "4326"
        self.responseTimes = []

    def _make_web_request(self, url: str, timeout):
        resp = requests.get(url, timeout=timeout).content.decode("utf-8")
        return resp

    def get_routes_list(self):
        parameters = []
        parameters.append(f"f=pjson")

        url = f"{self.BASE_URL}/{self.GET_ROUTES_API}?{'&'.join(parameters)}"
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
        parameters.append(f"outSR={self.SR}")
        parameters.append(f"f=pjson")

        url = f"{self.BASE_URL}/{self.GET_ROUTE_API}?{'&'.join(parameters)}"
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
        parameters.append(f"inSR={self.SR}")
        parameters.append(f"outSR={self.SR}")
        parameters.append(f"f=pjson")

        url = f"{self.BASE_URL}/{self.GET_ROUTE_AND_MEASURE_API}?{'&'.join(parameters)}"
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
            mMin = route_details["MMin"]
            mMax = route_details["MMax"]
            startMeasure = measure - step
            endMeasure = measure
            if startMeasure < mMin:
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
        parameters.append(f"outSR={self.SR}")
        parameters.append(f"f=pjson")

        url = f"{self.BASE_URL}/{self.GET_POINT_AT_MEASURE_API}?{'&'.join(parameters)}"
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
        mMin=None,
        mMax=None,
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

        if mMin != None and mMax != None:
            # Force mMin > mMax
            if mMin > mMax:
                temp = mMin
                mMin = mMax
                mMax = temp

            # Force measures between bounds
            startMeasure = min(max(startMeasure, mMin), mMax)
            endMeasure = min(max(endMeasure, mMin), mMax)

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
            routeId = f"{routeId}_DEC"

        parameters = []
        parameters.append(f"routeId={routeId}")
        parameters.append(f"fromMeasure={startMeasure}")
        parameters.append(f"toMeasure={endMeasure}")
        parameters.append(f"outSR={self.SR}")
        parameters.append(f"f=pjson")

        url = (
            f"{self.BASE_URL}/{self.ROUTE_BETWEEN_MEASURES_API}?{'&'.join(parameters)}"
        )
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

    def _make_cached_web_request(
        self, url: str, timeout: int = 15, retryOnTimeout: bool = False
    ):
        startTime = time.time()
        try:
            response = self.getCachedRequest(url)
            if not response:
                response = self._make_web_request(url, timeout=timeout)
                self.setCachedRequest(url, response)
            self.responseTimes.append(time.time() - startTime)
            logging.debug(
                f"Average Response Time: {sum(self.responseTimes)/len(self.responseTimes)}"
            )
            logging.debug("Max Response Time: " + str(max(self.responseTimes)))
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

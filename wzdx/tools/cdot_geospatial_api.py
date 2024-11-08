import json
import logging
import time
from typing import Any, Callable

import requests
import os

from ..tools import geospatial_tools, path_history_compression


class GeospatialApi:
    """Class to encompass all Geospatial API calls. Specify the getCachedRequest and setCachedRequest overrides to use custom caching."""

    def __init__(
        self,
        getCachedRequest: Callable[[str], str] = lambda url: None,
        setCachedRequest: Callable[[str, str], None] = lambda url, response: None,
        BASE_URL: str = os.getenv(
            "CDOT_GEOSPATIAL_API_BASE_URL",
            "https://dtdapps.colorado.gov/server/rest/services/LRS/Routes_withDEC/MapServer/exts/CdotLrsAccessRounded",
        ),
    ):
        """Initialize the Geospatial API

        Args:
            getCachedRequest ((url: str) => cached_response: str, optional): Optional method to enable custom caching. This method is called with a request url to retrieve the cached result.
            setCachedRequest ((url: str, response: str) => None, optional): Optional method to enable custom caching. This method is called with a request url and response to write the cached result.
            BASE_URL (str, optional): Optional override of GIS server base url, should end with CdotLrsAccessRounded. Defaults first to the env variable CDOT_GEOSPATIAL_API_BASE_URL, then to https://dtdapps.colorado.gov/server/rest/services/LRS/Routes_withDEC/MapServer/exts/CdotLrsAccessRounded.
        """
        self.getCachedRequest = getCachedRequest
        self.setCachedRequest = setCachedRequest
        self.BASE_URL = BASE_URL
        self.ROUTE_BETWEEN_MEASURES_API = "RouteBetweenMeasures"
        self.GET_ROUTE_AND_MEASURE_API = "MeasureAtPoint"
        self.GET_POINT_AT_MEASURE_API = "PointAtMeasure"
        self.GET_ROUTES_API = "ROUTES"
        self.GET_ROUTE_API = "ROUTE"
        self.SR = "4326"
        self.responseTimes: list[float] = (
            []
        )  # recorded response times, for debugging purposes

    def _make_web_request(self, url: str, timeout: int) -> str:
        """Make a GET request to a URL

        Args:
            url (str): URL to make the request to
            timeout (_type_): Timeout, in seconds

        Returns:
            str: Decoded response from the request
        """
        resp = requests.get(url, timeout=timeout).content.decode("utf-8")
        return resp

    def get_routes_list(self) -> list[dict | None]:
        """Return a list of all known routes and mile markers

        Returns:
            list[dict | None]: List of routes
        """
        parameters = []
        parameters.append(f"f=pjson")

        url = f"{self.BASE_URL}/{self.GET_ROUTES_API}?{'&'.join(parameters)}"
        logging.debug(
            f"Making GET request to GIS server for get_routes_list with url {url}"
        )

        # https://dtdapps.coloradodot.info/arcgis/rest/services/LRS/Routes/MapServer/exts/CdotLrsAccessRounded/Routes?f=pjson
        # https://dtdapps.coloradodot.info/arcgis/rest/services/LRS/Routes/MapServer/exts/CdotLrsAccessRounded/Route?routeId=070A&outSR=4326&f=pjson

        resp = self._make_cached_web_request(url, source="get_routes_list")
        if not resp:
            return None
        # response = [{'routeID': '070A', 'MMin': 0, 'MMax': 499}]
        return resp["routes"]

    def get_route_details(self, routeId: str) -> dict | None:
        """Get route details from route ID

        Args:
            routeId (str): GIS server route ID

        Returns:
            dict | None: Route details (Route, MMin, MMax)
        """
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

    def get_route_and_measure(
        self, latLng: tuple[float, float], heading: float = None, tolerance: int = 10000
    ) -> dict | None:
        """Get route ID and mile marker from lat/long and optional heading

        Args:
            latLng (tuple[float, float]): Lat/long coordinates
            heading (float, optional): Heading of object. Defaults to None.
            tolerance (int, optional): Tolerance in meters. Defaults to 10000.

        Returns:
            dict | None: Route details (Route, Measure, MMin, MMax, Distance)
        """
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
            step = 0.1  # miles, ~500 ft
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
            if (endMeasure > mMax) or (startMeasure < mMin):
                logging.warning(
                    "get_route_and_measure bearing computation failed, measure out of bounds. MMin: {mMin}, MMax: {mMax}, startMeasure: {startMeasure}, endMeasure: {endMeasure}, step: {step}"
                )
                return route_details
            coords = self.get_route_between_measures(route, startMeasure, endMeasure)
            bearing = geospatial_tools.get_heading_from_coordinates(coords)

            if bearing > 180:
                bearing -= 360
            if abs(bearing - heading) < 90:
                route_details["Direction"] = "+"
            else:
                route_details["Direction"] = "-"

        return route_details

    def get_point_at_measure(
        self, routeId: str, measure: float
    ) -> tuple[float, float] | None:
        """Get lat/long points at a mile marker on route

        Args:
            routeId (str): GIS server route ID
            measure (float): Measure on route (miles)

        Returns:
            tuple[float, float] | None: Lat/long of mile marker
        """
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
        routeId: str,
        startMeasure: float,
        heading: float,
        distanceAhead: float,
        compressed: bool = False,
        routeDetails: dict = None,
        mMin: float = None,
        mMax: float = None,
    ) -> dict | None:
        """Get route geometry ahead of a mile marker given a distance ahead and heading

        Args:
            routeId (str): GIS server route ID
            startMeasure (float): Start measure on route (miles)
            heading (float): Heading of the object (degrees)
            distanceAhead (float): Distance ahead to get route geometry (miles)
            compressed (bool, optional): Whether to compress route geometry. Defaults to False. See `tools/path_history_compression.generate_compressed_path` for more details
            routeDetails (dict, optional): Optional pre-generated route details. Defaults to None.
            mMin (float, optional): Optional minimum mile marker to limit route geometry generation. Defaults to None, should be specified with mMax.
            mMax (float, optional): Optional maximum mile marker to limit route geometry generation. Defaults to None, should be specified with mMin.

        Returns:
            dict | None: Route geometry ahead (start_measure, end_measure, coordinates)
        """

        # TODO: Integrate direction to determine whether to add/subtract distance
        if not routeDetails:
            latLng = self.get_point_at_measure(routeId, startMeasure)
            routeDetails = self.get_route_and_measure(latLng, heading)
            if not latLng or not routeDetails:
                logging.warning(
                    "get_route_geometry_ahead failed to get route details for routeId: {routeId}, startMeasure: {startMeasure}, heading: {heading}"
                )
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
        self,
        routeId: str,
        startMeasure: float,
        endMeasure: float,
        dualCarriageway: bool = True,
        compressed: bool = False,
    ) -> list[list[float]]:
        """Get lat/long points between two mile markers on route

        Args:
            routeId (str): GIS server route ID
            startMeasure (float): Start measure on route (miles)
            endMeasure (float): End measure on route (miles)
            dualCarriageway (bool, optional): Whether route is reversed dual carriageway. Defaults to True.
            compressed (bool, optional): Whether to compress route geometry (remove unnecessary points). Defaults to False. See `tools/path_history_compression.generate_compressed_path` for more details

        Returns:
            list[list[float]]: Route, as Linestring of lat/long points
        """
        # Get lat/long points between two mile markers on route
        if dualCarriageway and self.is_route_dec(startMeasure, endMeasure):
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

    def is_route_dec(self, startMeasure: float, endMeasure: float) -> bool:
        """Check if the route is a reversed dual carriageway

        Args:
            startMeasure (float): Start mile marker
            endMeasure (float): End mile marker

        Returns:
            bool: True if route is a reversed dual carriageway
        """
        return endMeasure > startMeasure

    def _make_cached_web_request(
        self,
        url: str,
        timeout: int = 15,
        retryOnTimeout: bool = False,
        source: str = "cdot_geospatial_api",
    ) -> Any:
        """Make a GET request and cache the response

        Args:
            url (str): URL to make the request to
            timeout (int, optional): Request timeout in seconds. Defaults to 15.
            retryOnTimeout (bool, optional): Retry request on timeout. Defaults to False.
            source (str, optional): Source to include in logging. Defaults to "unknown".

        Returns:
            Any: Response from the request
        """
        logging.debug(f"Making GET request to GIS server for {source} with url {url}")
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
                    f"Geospatial Request Timed Out for {source} with url : {url}. Timeout: {timeout}. Retrying with double timeout"
                )
                return self._make_cached_web_request(
                    url, timeout=timeout * 2, retryOnTimeout=False
                )
            else:
                logging.warning(
                    f"Geospatial Request Timed Out for {source} with url : {url}. Timeout: {timeout}. Error: {e}"
                )
                return None
        except requests.exceptions.RequestException as e:
            logging.warning(
                f"Geospatial Request Failed for {source} with url : {url}. Timeout: {timeout}. Error: {e}"
            )
            return None

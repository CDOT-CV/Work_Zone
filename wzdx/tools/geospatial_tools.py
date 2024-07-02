import math
from typing import Literal

import pyproj


# Helper mappings for road directions and orientations
ROAD_DIRECTIONS_MAP = {0: "northbound", 1: "eastbound", 2: "southbound", 3: "westbound"}
ROAD_ORIENTATIONS_MAP = {
    "northbound": 0,
    "eastbound": 90,
    "southbound": 0,
    "westbound": 90,
}
ROAD_ORIENTATIONS_DIRECTIONS_MAP = {
    0: ["northbound", "southbound", "southbound", "northbound"],
    90: ["eastbound", "westbound", "westbound", "eastbound"],
}


# function to get road direction by using geometry coordinates
def get_road_direction_from_coordinates(
    coordinates: list[list[float]],
) -> Literal["unknown", "northbound", "eastbound", "southbound", "westbound"]:
    """Return the direction of the road based on the coordinates of the road

    Args:
        coordinates (list[list[float]]): List of coordinates of the road

    Returns:
        Literal["unknown", "northbound", "eastbound", "southbound", "westbound"]: Direction of the road
    """
    if not coordinates or type(coordinates) != list or len(coordinates) < 2:
        return "unknown"

    try:
        long_dif = coordinates[-1][0] - coordinates[0][0]
        lat_dif = coordinates[-1][1] - coordinates[0][1]
    except ValueError as e:
        return "unknown"
    except IndexError as e:
        return "unknown"

    if abs(long_dif) > abs(lat_dif):
        if long_dif > 0:
            direction = "eastbound"
        else:
            direction = "westbound"
    elif lat_dif > 0:
        direction = "northbound"
    else:
        direction = "southbound"

    if lat_dif == 0 and long_dif == 0:
        direction = "unknown"

    return direction


def get_heading_from_coordinates(coordinates: list[list[float]]) -> float:
    """Return the heading between two long/lat coordinates"""
    if not coordinates or type(coordinates) != list or len(coordinates) < 2:
        return None

    geodesic_pyproj = pyproj.Geod(ellps="WGS84")

    fwd_heading, _, __ = geodesic_pyproj.inv(
        coordinates[0][0], coordinates[0][1], coordinates[1][0], coordinates[1][1]
    )

    return fwd_heading % 360


# This method is very condensed
def get_closest_direction_from_bearing(
    bearing: float,
    road_orientation: Literal["northbound", "eastbound", "southbound", "westbound"],
) -> Literal["northbound", "eastbound", "southbound", "westbound"]:
    """Return the direction of the object, by snapping the bearing to the road orientation (allows reversals, e.g. northbound or southbound can be returned for a northbound road orientation)

    Args:
        bearing (float): bearing/heading of the object
        road_orientation (Literal["northbound", "eastbound", "southbound", "westbound"]):

    Returns:
        Literal["northbound", "eastbound", "southbound", "westbound"]: direction of the object snapped to the roadway orientation
    """
    orientation = ROAD_ORIENTATIONS_MAP[road_orientation]
    return ROAD_ORIENTATIONS_DIRECTIONS_MAP[orientation][
        math.floor(abs(orientation - (bearing % 360)) / 90)
    ]


def getEndPoint(
    lat1: float, lon1: float, bearing: float, d: float
) -> tuple[float, float]:
    """Computes lat and lon for a point distance "d" meters and bearing (heading) from an origin
    with known lat1, lon1.

    See https://www.movable-type.co.uk/scripts/latlong.html for more detail.

     Args:
         lat1 (float): Latitude of origin
         lon1 (float): Longitude of origin
         bearing (float): Destination direction in degree
         d (float): Destination distance in km

     Returns:
         tuple[float, float]: lat/long of the destination point
    """
    R = 6371.0 * 1000  # Radius of the Earth in meters
    brng = math.radians(bearing)  # convert degrees to radians
    lat1 = math.radians(lat1)  # Current lat point converted to radians
    lon1 = math.radians(lon1)  # Current long point converted to radians
    lat2 = math.asin(
        math.sin(lat1) * math.cos(d / R)
        + math.cos(lat1) * math.sin(d / R) * math.cos(brng)
    )
    lon2 = lon1 + math.atan2(
        math.sin(brng) * math.sin(d / R) * math.cos(lat1),
        math.cos(d / R) - math.sin(lat1) * math.sin(lat2),
    )
    lat2 = math.degrees(lat2)
    lon2 = math.degrees(lon2)
    return lat2, lon2


###
#   Following function computes distance between two lat/lon points in meters...
#   Added on - 8-28-2017...
###
def getDist(origin: tuple[float, float], destination: tuple[float, float]) -> float:
    """Computes distance between two lat/lon points in meters

    Args:
        origin (tuple[float, float]): origin point, in long/lat
        destination (tuple[float, float]): destination point, in long/lat

    Returns:
        float: distance between the two points in meters
    """
    lon1, lat1 = origin  # lon/lat of origin
    lon2, lat2 = destination  # lon/lat of dest
    radius = 6371.0 * 1000  # meters

    dLat = math.radians(lat2 - lat1)  # in radians
    dLon = math.radians(lon2 - lon1)

    a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(
        math.radians(lat1)
    ) * math.cos(math.radians(lat2)) * math.sin(dLon / 2) * math.sin(dLon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c

    return d

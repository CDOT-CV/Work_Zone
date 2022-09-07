import math

import numpy as np
import pyproj

ROAD_DIRECTIONS_MAP = {
    0: "northbound",
    1: "eastbound",
    2: "southbound",
    3: "westbound"
}

ROAD_ORIENTATIONS_MAP = {
    "northbound": 0,
    "eastbound": 180,
    "southbound": 0,
    "westbound": 180
}

ROAD_OREINTATIONS_DIRECTIONS_MAP = {
    0: ["northbound", "southbound", "southbound", "northbound"],
    180: ["eastbound", "westbound", "westbound", "eastbound"]
}


# function to get road direction by using geometry coordinates
def get_road_direction_from_coordinates(coordinates):
    if not coordinates or type(coordinates) != list or len(coordinates) < 2:
        return None

    try:
        long_dif = coordinates[-1][0] - coordinates[0][0]
        lat_dif = coordinates[-1][1] - coordinates[0][1]
    except ValueError as e:
        return None
    except IndexError as e:
        return None

    if abs(long_dif) > abs(lat_dif):
        if long_dif > 0:
            direction = 'eastbound'
        else:
            direction = 'westbound'
    elif lat_dif > 0:
        direction = 'northbound'
    else:
        direction = 'southbound'

    if lat_dif == 0 and long_dif == 0:
        direction = None

    return direction


def get_heading_from_coordinates(coordinates):
    """Return the heading between two long/lat coordinates"""
    if not coordinates or type(coordinates) != list or len(coordinates) < 2:
        return None

    geodesic_pyproj = pyproj.Geod(ellps='WGS84')

    fwd_heading, _, __ = geodesic_pyproj.inv(
        coordinates[0][0], coordinates[0][1], coordinates[1][0], coordinates[1][1])

    return fwd_heading % 360


# unecessarily condensed just because
def get_direction_from_bearing(bearing):
    return ROAD_DIRECTIONS_MAP[math.floor((bearing + 45)/90) % 4]


# unecessarily condensed just because
def get_closest_direction_from_bearing(bearing, road_orientation):
    orientation = ROAD_ORIENTATIONS_MAP[road_orientation]
    return ROAD_OREINTATIONS_DIRECTIONS_MAP[orientation][math.floor(abs(orientation - (bearing % 360))/90)]


###
#   The following function computes lat and lon for a point distance "d" meters and bearing (heading)from an origin
#   with known lat1, lat2.
#
#   See https://www.movable-type.co.uk/scripts/latlong.html for more detail.
#
#   The function computes node point lat/lon for the adjacent lane's lane width (d) apart and 90 degree bearing
#   from the vehicle path data lane.
#
#   lat1    = Latitude of origin
#   lon1    = Longitude of origin
#   bearing = Destination direction in degree
#   dist    = Destination distance in km
###
def getEndPoint(lat1, lon1, bearing, d):
    R = 6371.0*1000  # Radius of the Earth in meters
    brng = math.radians(bearing)  # convert degrees to radians
    dist = d  # convert distance in meters
    lat1 = math.radians(lat1)  # Current lat point converted to radians
    lon1 = math.radians(lon1)  # Current long point converted to radians
    lat2 = math.asin(math.sin(lat1)*math.cos(d/R) +
                     math.cos(lat1)*math.sin(d/R)*math.cos(brng))
    lon2 = lon1 + math.atan2(math.sin(brng)*math.sin(d/R) *
                             math.cos(lat1), math.cos(d/R)-math.sin(lat1)*math.sin(lat2))
    lat2 = math.degrees(lat2)
    lon2 = math.degrees(lon2)
    return lat2, lon2


###
#   Following function computes distance between two lat/lon points in meters...
#   Added on - 8-28-2017...
###
def getDist(origin, destination):
    lon1, lat1 = origin  # lon/lat of origin
    lon2, lat2 = destination  # lonlat of dest
    radius = 6371.0*1000  # meters

    dlat = math.radians(lat2-lat1)  # in radians
    dlon = math.radians(lon2-lon1)

    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d

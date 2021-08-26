import math

import numpy as np
import pyproj
import logging

import geopy
import pyproj
from geopy.distance import geodesic
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


CORNER_PRECISION_DEGREES = 10


def generate_buffer_polygon_from_linestring(geometry: list, polygon_width_in_meters: float):
    """Generate a polygon from a Linestring using polygon_width_in_meters as a buffer.

    Args:
        geometry: Linestring
        polygon_width_in_meters: width in meters
    """

    if not geometry or type(geometry) != list or len(geometry) <= 1:
        return None
    geodesic_pyproj = pyproj.Geod(ellps='WGS84')

    # Initializing lists to create polygon
    polygon_left_points = []
    polygon_right_points = []

    for i in range(0, len(geometry)):
        # Set up points to calculate heading
        if i == 0:
            # first point, heading from first to second point
            p1 = geometry[i]
            p2 = geometry[i+1]
        else:
            # Not first point, heading from previous point to current point
            p1 = geometry[i-1]
            p2 = geometry[i]

        # Get forward heading between 2 points
        fwd_heading, _, __ = geodesic_pyproj.inv(
            p1[0], p1[1], p2[0], p2[1])

        # Get left and right vectors
        left = fwd_heading - 90
        right = fwd_heading + 90

        # Reset p1 to current point
        p1 = geometry[i]

        # get left and right points from direction and distance
        origin = geopy.Point(p1[1], p1[0])
        left_point = geodesic(
            meters=polygon_width_in_meters/2).destination(origin, left)
        right_point = geodesic(meters=polygon_width_in_meters /
                               2).destination(origin, right)

        # Append points to left and right lists
        polygon_left_points.append([left_point.latitude, left_point.longitude])
        polygon_right_points.append(
            [right_point.latitude, right_point.longitude])

    # Create list of points in correct order (all left points, then all right points in reverse order)
    # This order is critical to prevent criss-crossing in the polygon
    polygon_points = []

    for i in polygon_left_points:
        polygon_points.append(i)

    for i in reversed(polygon_right_points):
        polygon_points.append(i)

    # Add first point again, to close polygon
    polygon_points.append(polygon_left_points[0])

    # Return generated polygon
    polygon = Polygon(polygon_points)
    return polygon


# Check if point is in polygon
def isPointInPolygon(point: Point, polygon: Polygon) -> bool:
    """Determine if a point falls within a given polygon

    Args:
        point: Lat/long point
        polygon: polygon

    Returns:
        Boolean of whether point is in polygon
    """

    if not point or not polygon or type(point) != Point or type(polygon) != Polygon:
        return None
    return polygon.contains(point)


# function to get road direction by using geometry coordinates
def get_road_direction_from_coordinates(coordinates):
    if not coordinates or type(coordinates) != list or len(coordinates) < 2:
        return None

    try:
        long_dif = coordinates[-1][0] - coordinates[0][0]
        lat_dif = coordinates[-1][1] - coordinates[0][1]
    except ValueError as e:
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


def angle_between_vectors_degrees(u, v):
    """Return the angle between two vectors in any dimension space,
    in degrees."""
    return np.degrees(
        math.acos(np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))))


def average_coordinates(coord1: list, coord2: list) -> list:
    if len(coord1) != 2 or len(coord2) != 2:
        return None
    return [(coord1[0]+coord2[0])/2, (coord1[1]+coord2[1])/2]


def average_symmetric_polygon_to_centerline(polygon):
    """Take in correctly ordered polygon and average all points to get 
    centerline"""
    centerline = []
    for i in range(0, len(polygon), 2):
        centerline.append(average_coordinates(polygon[i], polygon[i+1]))
    return centerline


def rotate(l, n):
    """Rotate a polygon l by n positions"""
    return l[-n:] + l[:-n]


def polygon_to_polyline_center(coordinates):
    """Convert a polygon to a polyline by finding the 2 segments farthest from the center of mass"""
    if not coordinates or type(coordinates) != list or len(coordinates) < 5:
        return None

    geodesic = pyproj.Geod(ellps='WGS84')

    center_lon = 0
    center_lat = 0

    for coord in coordinates:
        center_lon += coord[0]
        center_lat += coord[1]

    center_lon /= len(coordinates)
    center_lat /= len(coordinates)

    distances = []

    for i in range(len(coordinates) - 1):
        avg_lon = (coordinates[i][0] + coordinates[i+1][0]) / 2
        avg_lat = (coordinates[i][1] + coordinates[i+1][1]) / 2
        _, __, distance = geodesic.inv(
            avg_lon, avg_lat, center_lon, center_lat)
        distances.append([distance, [avg_lon, avg_lat]])

    distances = sorted(distances, key=lambda ls: -ls[0])

    polyline = []
    polyline.append(distances[0][1])
    polyline.append(distances[1][1])

    return polyline


# Welp, this is now worthless. None of the polygons NavJoy is generating follow the roadway and thus don't have
# 90 degree corners. So this can never find any good corners except on the 4 (5) point rectangular polygons,
# which the centers function handles better. who doesn't love wasting time am I right?
def polygon_to_polyline_corners(coordinates):
    """Convert a polygon to a polyline by finding corners"""
    if not coordinates or type(coordinates) != list:
        return None
    corners = []
    geodesic = pyproj.Geod(ellps='WGS84')
    coordinates_padded = coordinates[:-1] + coordinates[0:3]
    for i in range(len(coordinates_padded) - 3):
        i0 = i
        i1 = i + 1
        i2 = i + 2
        i3 = i + 3

        bearing_1, _, distance_1 = geodesic.inv(
            coordinates_padded[i0][0], coordinates_padded[i0][1], coordinates_padded[i1][0], coordinates_padded[i1][1])
        bearing_2, _, distance_2 = geodesic.inv(
            coordinates_padded[i1][0], coordinates_padded[i1][1], coordinates_padded[i2][0], coordinates_padded[i2][1])
        bearing_3, _, distance_3 = geodesic.inv(
            coordinates_padded[i2][0], coordinates_padded[i2][1], coordinates_padded[i3][0], coordinates_padded[i3][1])

        angle_1 = bearing_1 - bearing_2
        angle_2 = bearing_2 - bearing_3

        net_angle = abs(angle_1 + angle_2)
        if abs(net_angle - 180) < CORNER_PRECISION_DEGREES:
            corners.append([i1, i2, net_angle, distance_2])

    # If 4 corners, assume the polygon is a rectangle. Select shortest 2 sides as ends
    if len(corners) == 4:
        # lowest to highest
        corners = sorted(corners, key=lambda corner: corner[3])
        corners = corners[:2]

    # If not 4 or 2 corners, return None because this polygon cannot be parsed
    elif len(corners) != 2:
        logging.debug("Unable to find exactly 2 180 degree corners")
        return None

    # Check that corners are on opposite sides. If not, generate simple centerline
    lengthCoords = len(coordinates) - 1
    # will return False if corners are not opposite or if polygon has odd number of edges
    if abs(corners[0][0] - corners[1][0]) != lengthCoords/2:
        logging.debug(
            "Corners found are not opposite within the polygon. Generating limited centerline")
        # average corner coordinates to get start and end points
        return [average_coordinates(coordinates_padded[corners[0][0]], coordinates_padded[corners[0][1]]),
                average_coordinates(coordinates_padded[corners[1][0]], coordinates_padded[corners[1][1]])]

    # found polygon corners, now rotate polygon and average to centerline
    # ignore last point which is duplicate for first
    rotated_coordinates = coordinates[:-1]
    rotated_coordinates = rotate(rotated_coordinates, corners[0][0])
    return average_symmetric_polygon_to_centerline(rotated_coordinates)

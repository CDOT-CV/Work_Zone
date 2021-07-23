import math

import numpy as np
import pyproj
import logging


CORNER_PRECISION_DEGREES = 10


def angle_between_vectors_degrees(u, v):
    """Return the angle between two vectors in any dimension space,
    in degrees."""
    return np.degrees(
        math.acos(np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))))


def average_coordinates(coord1: list, coord2: list) -> list:
    if len(coord1) != 2 or len(coord2) != 2:
        return None
    return [(coord1[0]+coord2[0])/2, (coord1[1]+coord2[1])/2]


def average_polygon_to_centerline(polygon):
    """Take in correctly ordered polygon and average all points to get 
    centerline"""
    centerline = []
    for i in range(0, len(polygon), 2):
        centerline.append(average_coordinates(polygon[i], polygon[i+1]))
    return centerline


def average_symmetric_polygon_to_centerline(polygon):
    """Take in correctly ordered polygon and average all points to get 
    centerline"""
    centerline = []
    for i in range(0, len(polygon), 2):
        centerline.append(average_coordinates(polygon[i], polygon[i+1]))
    return centerline


def rotate(l, n):
    return l[-n:] + l[:-n]


def polygon_to_polyline(coordinates):
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
        print("Unable to find exactly 2 180 degree corners")
        return None

    # Check that corners are on opposite sides. If not, generate simple centerline
    lengthCoords = len(coordinates) - 1
    # will return False if corners are not opposite or if polygon has odd number of edges
    if abs(corners[0][0] - corners[1][0]) != lengthCoords/2:
        logging.debug(
            "Corners found are not opposite within the polygon. Generating limited centerline")
        # average coner coordinates to get start and end points
        return [average_coordinates(coordinates[corners[0][0]], coordinates[corners[0][1]]),
                average_coordinates(coordinates[corners[1][0]], coordinates[corners[1][1]])]

    # found polygon corners, now rotate polygon and average to centerline
    # ignore last point which is duplicate for first
    rotated_coordinates = coordinates[:-1]
    rotated_coordinates = rotate(rotated_coordinates, corners[0][0])
    print(rotated_coordinates)
    return average_symmetric_polygon_to_centerline(rotated_coordinates)

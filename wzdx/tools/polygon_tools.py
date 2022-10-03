import geopy
import pyproj
from geopy.distance import geodesic
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

CORNER_PRECISION_DEGREES = 10


def generate_buffer_polygon_from_linestring(geometry: list, polygon_width_in_meters: float):
    """Generate a polygon from a Linestring using polygon_width_in_meters as a buffer.

    Args:
        geometry: Linestring (long/lat)
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


def list_to_polygon(coordinates):
    """Convert a list of lat/longs to a shapely.geometry.polygon.Polygon

    Args:
        polygon: list of lat/long pairs

    Returns:
        shapely.geometry.polygon.Polygon
    """
    if not coordinates or type(coordinates) != list:
        return None
    return Polygon(coordinates)


def polygon_to_list(polygon):
    """Convert a shapely.geometry.polygon.Polygon to a list of lat/longs

    Args:
        polygon: Polygon

    Returns:
        List of lat/long pairs
    """
    if not polygon or type(polygon) != Polygon:
        return None
    return [list(i) for i in list(polygon.exterior.coords)]


# Check if point is in polygon
def is_point_in_polygon(point: Point, polygon: Polygon) -> bool:
    """Determine if a point falls within a given polygon

    Args:
        point: lat/long or shapely.geometry.polygon.Point
        polygon: list of lat/longs or shapely.geometry.polygon.Polygon

    Returns:
        Boolean of whether point is in polygon
    """
    if type(point) == list or type(point) == tuple:
        point = Point(point[0], point[1])

    if type(polygon) == list:
        polygon = list_to_polygon(polygon)

    if not point or not polygon or type(point) != Point or type(polygon) != Polygon:
        return None
    return polygon.contains(point)


def average_coordinates(coord1: list, coord2: list) -> list:
    """Average two sets of coordinates to one center coordinate"""
    if len(coord1) != 2 or len(coord2) != 2:
        return None
    return [(coord1[0]+coord2[0])/2, (coord1[1]+coord2[1])/2]


def average_symmetric_polygon_to_centerline(polygon):
    """Take in correctly ordered polygon and average all points to get
    centerline"""
    centerline = []
    for i in range(0, len(polygon) - 1, 2):
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

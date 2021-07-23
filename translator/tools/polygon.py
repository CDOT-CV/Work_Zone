import getopt
import sys

import geopy
import pyproj
from geopy.distance import geodesic
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


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


def parse_arguments(argv: list, default_output_file_name: str = 'combined_wzdx_message.geojson') -> tuple:
    """Determine if a point falls within a given polygon

    Args:
        argv: List of command line arguments
        default_output_file_name: Output file name with default value of 'combined_wzdx_message.geojson'

    Returns:
        tuple(iCone argument, COtrip argument, output argument)
    """

    icone = None
    cotrip = None
    outputfile = default_output_file_name

    try:
        opts, _ = getopt.getopt(
            argv, "hi:c:o:", ["icone=", "cotrip=", "output="])
    except getopt.GetoptError as e:
        print('Invalid arguments: '+str(e))
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(help_string)
            sys.exit()
        elif opt in ("-i", "--icone"):
            icone = arg
        elif opt in ("-c", "--cotrop"):
            cotrip = arg
        elif opt in ("-o", "--output"):
            outputfile = arg

    return icone, cotrip, outputfile

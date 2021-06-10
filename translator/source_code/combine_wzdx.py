import json
import copy
from shapely.geometry.polygon import Polygon
from shapely.geometry import Point
import geopy
from geopy.distance import geodesic
import pyproj
import getopt
import sys

polygon_width_meters = 100


def main():

    icone_file, cotrip_file, outputfile = parse_arguments(
        sys.argv[1:], default_output_file_name='combined_wzdx_message.geojson')

    if icone_file and cotrip_file:
        try:
            with open(outputfile, 'w+') as f:
                wzdx_icone = json.loads(open(
                    icone_file, 'r').read())
                wzdx_cotrip = json.loads(open(
                    cotrip_file, 'r').read())
        except ValueError as e:
            raise ValueError(
                'One or more files specified are invalid. Please specify valid geojson files!') from None

        polygon = generate_polygon(
            wzdx_cotrip['features'][0]['geometry']['coordinates'], polygon_width_meters)
        feature = iterate_feature(polygon, wzdx_icone)
        if feature:

            f.write(json.dumps(combine_wzdx(
                wzdx_cotrip, wzdx_icone, feature), indent=2))
            print(
                'Combined WZDx message was written to combined_wzdx_message.geojson file.')

        else:
            print('no duplicate messages were found')
    else:
        print('please specify an input json file with -i and -c')
        print(help_string)


def combine_wzdx(wzdx_cotrip, wzdx_icone, icone_feature):
    combined_wzdx = copy.deepcopy(wzdx_cotrip)
    combined_wzdx['features'][0]['properties']['vehicle_impact'] = icone_feature['properties']['vehicle_impact']
    combined_wzdx['road_event_feed_info']['data_sources'].extend(
        wzdx_icone['road_event_feed_info']['data_sources'][0])

    return combined_wzdx


def iterate_feature(polygon, wzdx_message):
    for feature in wzdx_message['features']:
        for coord in feature['geometry']['coordinates']:
            if isPointInPolygon(Point(coord[1], coord[0]), polygon):
                return feature


# generate polygon from list of geometry ([[long, lat], ...]) and width in meters
def generate_polygon(geometry, polygon_width_in_meters):
    """generate polygon from list of geometry ([[long, lat], ...]) as linestring and width in meters

    Args: 
        geometry: Linestring
        polygon_width: width in meters
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
def isPointInPolygon(point, polygon):
    if not point or not polygon or type(point) != Point or type(polygon) != Polygon:
        return None
    return polygon.contains(point)


help_string = """ 

Usage: python **script_name** [arguments]

Global options:
-h, --help                  Print this usage information.
-i, --icone                 specify the WZDx icone file to compare/combine
-c, --cotrip                specify the WZDx cotrip file to compare/combine
-o, --output                specify the output file for generated wzdx geojson message """


def parse_arguments(argv, default_output_file_name='combined_wzdx_message.geojson'):
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


if __name__ == "__main__":
    main()

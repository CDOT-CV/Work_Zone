import argparse
import copy
import getopt
import json
import sys

import geopy
import pyproj
from geopy.distance import geodesic
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

PROGRAM_NAME = 'WZDxCombiner'
PROGRAM_VERSION = '1.0'

POLYGON_WIDTH_METERS = 100

# Severity hierarchy for vehicle_impacts
VEHICLE_IMPACT_SEVERITIES = {
    "unknown": 0,
    "all-lanes-open": 1,
    "some-lanes-closed": 2,
    "alternating-one-way": 3,
    "all-lanes-closed": 4,
}


def main():
    icone_file, cotrip_file, outputfile = parse_combined_arguments()

    try:
        wzdx_icone = json.loads(open(
            icone_file, 'r').read())
        wzdx_cotrip = json.loads(open(
            cotrip_file, 'r').read())
    except ValueError as e:
        raise ValueError(
            'One or more files specified are invalid. Please specify valid geojson files!') from None

    combined_wzdx = find_duplicate_features_and_combine(
        wzdx_icone, wzdx_cotrip)

    if combined_wzdx:
        with open(outputfile, 'w+') as f:
            f.write(json.dumps(combined_wzdx, indent=2))
        print(f'Combined WZDx message was written to {outputfile}.')
    else:
        print('No duplicate WZDx messages were found. Output file was not created')


# parse combination script command line arguments
def parse_combined_arguments() -> tuple:
    """Parse command line arguments for combination script

    Returns: 
        Tuple of (iCone file path, cotrip file path, output file path)
    """
    parser = argparse.ArgumentParser(
        description='Detect and combine duplicate iCone and COTrip WZDx work zone messages')
    parser.add_argument('--version', action='version',
                        version=f'{PROGRAM_NAME} {PROGRAM_VERSION}')
    parser.add_argument('iconeFile', help='icone file path')
    parser.add_argument('cotripFile', help='cotrip file path')
    parser.add_argument('--outputFile', required=False,
                        default='combined_wzdx_message.geojson', help='WZDx output file path')

    args = parser.parse_args()
    return args.iconeFile, args.cotripFile, args.outputFile


def find_duplicate_features_and_combine(wzdx_source: dict, wzdx_destination: dict) -> dict:
    """Find duplicate features in WZDx messages and combine source duplicates into destination message

    Args:
        wzdx_source: Source WZDx message
        wzdx_destination: Destination WZDx message

    Returns: 
        Destination WZDx message, updated from source if new data was found
    """

    # Make copy of destination object to combine duplicates into
    combined_wzdx = copy.deepcopy(wzdx_destination)

    # Iterate over destination features, for each search for duplicate source features. If any are found, combine them into the
    # combined_wzdx feature
    for index, destination_feature in enumerate(wzdx_destination["features"]):

        # Generate polygon from destination feature
        polygon = generate_buffer_polygon_from_linestring(
            destination_feature['geometry']['coordinates'], POLYGON_WIDTH_METERS)

        # Get list of duplicate source features
        iconeIndexes = iterate_feature(polygon, wzdx_source)

        # Iteratively combine them with the combined feature
        for iconeIndex in iconeIndexes:
            combined_wzdx = combine_wzdx(
                combined_wzdx, index, wzdx_source, iconeIndex)

    # If features are identical, then no duplicates were found, return None. Else return combined message
    if combined_wzdx == wzdx_destination:
        return None
    else:
        return combined_wzdx


def combine_wzdx(wzdx_destination: dict, destination_feature_index: int, wzdx_source: dict, source_feature_index: int) -> dict:
    """Combine WZDx messages given duplicate feature indexes

    Args:
        combined_wzdx: Destination WZDx message (dict)
        combined_feature_index: Index of destination feature to combine (int)
        wzdx_icone: Destination WZDx message (dict)
        icone_feature_index: Index of source feature to combine (int)

    Returns: 
        Destination WZDx message, updated from source if new data was found
    """

    # If indexes do not exist for either source or destination, immediately return destination object
    if len(wzdx_destination['features']) <= destination_feature_index or len(wzdx_source['features']) <= source_feature_index:
        return wzdx_destination

    # check if vehicle impact severity of source is higher than that of destination. If it is, overwrite destination with source
    wzdx_destination['features'][destination_feature_index]['properties']['vehicle_impact'] = combine_vehicle_impacts(
        wzdx_source["features"][source_feature_index]['properties']['vehicle_impact'],
        wzdx_destination['features'][destination_feature_index]['properties']['vehicle_impact']
    )

    # Append any data sources from source that are not in destination
    for source_data_source in wzdx_source['road_event_feed_info']['data_sources']:
        if source_data_source not in wzdx_destination['road_event_feed_info']['data_sources']:
            wzdx_destination['road_event_feed_info']['data_sources'].append(
                source_data_source)

    return wzdx_destination


# check if vehicle impact severity of source is higher than that of destination.
# If it is, return source impact, else return destination impact.
def combine_vehicle_impacts(source_impact: str, destination_impact: str) -> str:
    """Combine 2 vehicle impacts based on severity. If source > destination, return source. else return destination

    Args:
        source_impact: Source vehicle impact
        destination_impact: Destination vehicle impact

    Returns: 
        combined vehicle impact
    """

    source_impact_severity = VEHICLE_IMPACT_SEVERITIES.get(source_impact, 0)
    destination_impact_severity = VEHICLE_IMPACT_SEVERITIES.get(
        destination_impact, 0)

    if source_impact_severity > destination_impact_severity:
        return source_impact
    else:
        return destination_impact


# Iterate over features in message, return list of indexes within given polygon
def iterate_feature(polygon: Polygon, wzdx_message: dict) -> list:
    """iterate over WZDx message and return indexes of features with >= 1 point within given polygon

    Args:
        polygon: Polygon to evaulate feature geometry against
        wzdx_message: WZDx message to iterate over

    Returns: 
        List of indexes for features in polygon
    """

    indexes = []
    for index, feature in enumerate(wzdx_message['features']):
        for coord in feature['geometry']['coordinates']:
            if isPointInPolygon(Point(coord[1], coord[0]), polygon):
                indexes.append(index)
                break
    return indexes


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


if __name__ == "__main__":
    main()

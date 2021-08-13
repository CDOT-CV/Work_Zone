import argparse
import copy
import json
import logging

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

from translator.tools import polygon_tools

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

    combined_wzdx = find_overlapping_features_and_combine(
        wzdx_icone, wzdx_cotrip)

    if combined_wzdx:
        with open(outputfile, 'w+') as f:
            f.write(json.dumps(combined_wzdx, indent=2))
        logging.info(f'Combined WZDx message was written to {outputfile}.')
    else:
        logging.warning(
            'No overlapping WZDx messages were found. Output file was not created')


# parse combination script command line arguments
def parse_combined_arguments() -> tuple:
    """Parse command line arguments for combination script

    Returns: 
        Tuple of (iCone file path, cotrip file path, output file path)
    """
    parser = argparse.ArgumentParser(
        description='Detect and combine overlapping iCone and COTrip WZDx work zone messages')
    parser.add_argument('--version', action='version',
                        version=f'{PROGRAM_NAME} {PROGRAM_VERSION}')
    parser.add_argument('iconeFile', help='icone file path')
    parser.add_argument('cotripFile', help='cotrip file path')
    parser.add_argument('--outputFile', required=False,
                        default='combined_wzdx_message.geojson', help='WZDx output file path')

    args = parser.parse_args()
    return args.iconeFile, args.cotripFile, args.outputFile


def find_overlapping_features_and_combine(wzdx_source: dict, wzdx_destination: dict) -> dict:
    """Find overlapping features in WZDx messages and combine into destination message

    Args:
        wzdx_source: Source WZDx message
        wzdx_destination: Destination WZDx message

    Returns: 
        Destination WZDx message, updated from source if new data was found
    """

    # Make copy of destination object to combine overlapping messages into
    combined_wzdx = copy.deepcopy(wzdx_destination)

    # Iterate over destination features, for each search for overlapping source features. If any are found, combine them into the
    # combined_wzdx feature
    for index, destination_feature in enumerate(wzdx_destination["features"]):

        # Generate polygon from destination feature
        polygon = polygon_tools.generate_buffer_polygon_from_linestring(
            destination_feature['geometry']['coordinates'], POLYGON_WIDTH_METERS)

        # Get list of overlapping source features
        iconeIndexes = iterate_feature(polygon, wzdx_source)

        # Iteratively combine them with the combined feature
        for iconeIndex in iconeIndexes:
            combined_wzdx = combine_wzdx(
                combined_wzdx, index, wzdx_source, iconeIndex)

    # If features are identical, then no overlapping messages were found, return None. Else return combined message
    if combined_wzdx == wzdx_destination:
        return None
    else:
        return combined_wzdx


def combine_wzdx(wzdx_destination: dict, destination_feature_index: int, wzdx_source: dict, source_feature_index: int) -> dict:
    """Combine WZDx messages given overlapping feature indexes

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
            if polygon_tools.isPointInPolygon(Point(coord[1], coord[0]), polygon):
                indexes.append(index)
                break
    return indexes


if __name__ == "__main__":
    main()

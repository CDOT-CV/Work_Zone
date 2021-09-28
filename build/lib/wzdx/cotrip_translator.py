import argparse
import copy
import json
import logging
import re
from collections import OrderedDict

from translator.tools import date_tools, wzdx_translator

PROGRAM_NAME = 'CotripTranslator'
PROGRAM_VERSION = '1.0'

DEFAULT_COTRIP_FEED_INFO_ID = '8d062f70-d53e-4029-b94e-b7fbcbde5885'


def main():
    inputFile, outputFile = parse_cotrip_arguments()

    try:
        cotrip_obj = json.loads(open(inputFile).read())
    except ValueError as e:
        raise ValueError(
            'Invalid file type. Please specify a valid Json file!') from None
    wzdx_obj = wzdx_creator(cotrip_obj)
    location_schema = 'translator/sample files/validation_schema/wzdx_v3.1_feed.json'
    wzdx_schema = json.loads(open(location_schema).read())

    if not wzdx_translator.validate_wzdx(wzdx_obj, wzdx_schema):
        logging.error(
            'validation error more message are printed above. output file is not created because the message failed validation.')
        return
    with open(outputFile, 'w') as fwzdx:
        fwzdx.write(json.dumps(wzdx_obj, indent=2))
        print(
            'Your wzdx message was successfully generated and is located here: ' + str(outputFile))


# parse cotrip script command line arguments
def parse_cotrip_arguments():
    parser = argparse.ArgumentParser(
        description='Translate COTrip data to WZDx')
    parser.add_argument('--version', action='version',
                        version=f'{PROGRAM_NAME} {PROGRAM_VERSION}')
    parser.add_argument('cotripFile', help='cotrip file path')
    parser.add_argument('--outputFile', required=False,
                        default='cotrip_wzdx_translated_output_message.geojson', help='WZDx output file path')

    args = parser.parse_args()
    return args.cotripFile, args.outputFile


def wzdx_creator(message, info=None, unsupported_message_callback=None):
    if not message:
        return None

    if not info:
        info = wzdx_translator.initialize_info(
            DEFAULT_COTRIP_FEED_INFO_ID)
    if not wzdx_translator.validate_info(info):
        return None

    wzd = wzdx_translator.initialize_wzdx_object(info)

    # Parse alert to WZDx Feature
    feature = parse_alert(
        message, callback_function=unsupported_message_callback)
    if feature:
        wzd.get('features').append(feature)
    if not wzd.get('features'):
        return None
    wzd = wzdx_translator.add_ids(wzd)
    return wzd


# function to parse polyline to geometry line string
def parse_polyline(poly):
    if not poly or type(poly) != str:
        return None
    poly = poly[len('LINESTRING ('): -1]
    polyline = poly.split(', ')
    coordinates = []
    for i in polyline:
        coords = i.split(' ')

        # the regular rexpression '^-?([0-9]*[.])?[0-9]+$ matches an integer or decimals
        if len(coords) >= 2 and re.match('^-?([0-9]*[.])?[0-9]+$', coords[0]) and re.match('^-?([0-9]*[.])?[0-9]+$', coords[1]):
            coordinates.append([float(coords[0]), float(coords[1])])
    return coordinates


# Parse COtrip alert to WZDx
def parse_alert(alert, callback_function=None):
    if not validate_alert(alert):
        if callback_function:
            callback_function(alert)
        return None

    event = alert.get('event', {})
    geometry = {}
    geometry['type'] = "LineString"
    geometry['coordinates'] = parse_polyline(event.get('geometry'))
    properties = wzdx_translator.initialize_feature_properties()

    header = event.get('header', {})
    detail = event.get('detail', {})
    source = event.get('source', {})

    # Event Type ['work-zone', 'detour']
    properties['event_type'] = 'work-zone'

    # start_date
    start_date = date_tools.parse_datetime_from_unix(
        header.get('start_timestamp'))
    properties['start_date'] = date_tools.get_iso_string_from_datetime(
        start_date)

    # end_date
    end_date = date_tools.parse_datetime_from_unix(header.get('end_timestamp'))
    properties['end_date'] = date_tools.get_iso_string_from_datetime(end_date)

    # start_date_accuracy
    properties['start_date_accuracy'] = "estimated"

    # end_date_accuracy
    properties['end_date_accuracy'] = "estimated"

    # beginning_accuracy
    properties['beginning_accuracy'] = "estimated"

    # ending_accuracy
    properties['ending_accuracy'] = "estimated"

    # road_name
    properties['road_names'] = [detail.get('road_name')]
    road_number = detail.get('road_number')
    if road_number and not road_number in properties['road_names']:
        properties['road_names'].append(road_number)

    # direction
    Direction_map = {'North': 'northbound', 'South': 'southbound',
                     'West': 'westbound', 'East': 'eastbound'}

    properties['direction'] = Direction_map.get(
        detail.get('direction'))

    # vehicle impact
    properties['vehicle_impact'] = 'unknown'

    # event status
    properties['event_status'] = date_tools.get_event_status(
        start_date, end_date)

    # type_of_work
    # maintenance, minor-road-defect-repair, roadside-work, overhead-work, below-road-work, barrier-work, surface-work, painting, roadway-relocation, roadway-creation
    works = event.get('sub_type')
    types_of_work = get_types_of_work(works)
    if types_of_work:
        properties['types_of_work'] = types_of_work

    # reduced_speed_limit
    properties['reduced_speed_limit'] = get_rsz_from_event(event)

    # restrictions
    work_updates = detail.get('work_updates')
    restrictions = get_restrictions(work_updates)
    if restrictions:
        properties['restrictions'] = restrictions

    # description
    properties['description'] = header.get('description')

    # creation_date
    creation_date = date_tools.parse_datetime_from_unix(
        source.get('collection_timestamp'))
    properties['creation_date'] = date_tools.get_iso_string_from_datetime(
        creation_date)

    # update_date
    update_date = date_tools.parse_datetime_from_unix(
        alert.get('rtdh_timestamp'))
    properties['update_date'] = date_tools.get_iso_string_from_datetime(
        update_date)

    filtered_properties = copy.deepcopy(properties)

    for key, value in properties.items():
        if value == None and key not in ['road_event_id', 'data_source_id']:
            del filtered_properties[key]

    feature = {}
    feature['type'] = "Feature"
    feature['properties'] = filtered_properties
    feature['geometry'] = geometry

    return feature


# function to validate the alert
def validate_alert(alert):

    if not alert or (type(alert) != dict and type(alert) != OrderedDict):
        logging.warning('alert is empty or has invalid type')
        return False

    id = alert.get("rtdh_message_id")

    event = alert.get('event', {})

    header = event.get('header', {})
    detail = event.get('detail', {})

    polyline = event.get('geometry')
    coords = parse_polyline(polyline)
    street = detail.get('road_name')

    starttime_string = header.get('start_timestamp')
    endtime_string = header.get('end_timestamp', 0)
    description = header.get('description')
    direction = event.get('detail', {}).get('direction')

    required_fields = [polyline, coords, street,
                       starttime_string, description, direction]
    for field in required_fields:
        if not field:
            logging.warning(
                f'''Invalid event with event id = {id}. not all required fields are present. Required fields are: 
                polyline, street, start_timestamp, description, and direction''')
            return False

    start_time = date_tools.parse_datetime_from_unix(starttime_string)
    end_time = date_tools.parse_datetime_from_unix(endtime_string)
    if not start_time:
        logging.warning(
            f'Invalid incident with id = {id}. Unsupported start time format: {starttime_string}')
        return False
    elif endtime_string and not end_time:
        logging.warning(
            f'Invalid incident with id = {id}. Unsupported end time format: {endtime_string}')
        return False
    return True


def get_types_of_work(sub_type):
    if not sub_type or type(sub_type) != str:
        return []
    sub_type_split = sub_type.split(':')
    if len(sub_type_split) < 2:
        return []
    type_of_work = sub_type_split[1]

    valid_types_of_work = ['maintenance',
                           'minor-road-defect-repair',
                           'roadside-work',
                           'overhead-work',
                           'below-road-work',
                           'barrier-work',
                           'surface-work',
                           'painting',
                           'roadway-relocation',
                           'roadway-creation']
    work_type = {'type_name': type_of_work,
                 'is_architectural_change': True}
    if type_of_work in valid_types_of_work:
        return [work_type]
    else:
        return []


def get_restrictions(work_updates):
    restrictions = []
    if work_updates == [] or work_updates == None:
        return []

    valid_type_of_restrictions = ['no-trucks',
                                  'travel-peak-hours-only',
                                  'hov-3',
                                  'hov-2',
                                  'no-parking',
                                  'reduced-width',
                                  'reduced-height',
                                  'reduced-length',
                                  'reduced-weight',
                                  'axle-load-limit',
                                  'gross-weight-limit',
                                  'towing-prohibited',
                                  'permitted-oversize-loads-prohibited',
                                  'local-access-only']
    for work_update in work_updates:
        if type(work_update) == dict and work_update.get('restrictions'):
            for restriction in work_update.get('restrictions'):
                if type(restriction) == dict:
                    restrict = restriction.get('type')
                    if restrict in valid_type_of_restrictions:
                        restrictions.append(restrict)
    return restrictions


def parse_reduced_speed_limit_from_description(description) -> str:
    search = re.search('speed limit ([0-9]{2}) mph', description)
    if search:
        return search[0][12:14]

    search = re.search('speed limit reduced to ([0-9]{2})mph', description)
    if search:
        return search[0][23:25]


def get_rsz_from_event(event):
    rsz = parse_reduced_speed_limit_from_description(
        event.get('header', {}).get('description', ""))
    if rsz:
        return rsz

    rsz = parse_reduced_speed_limit_from_description(
        event.get('detail', {}).get('description', ""))

    if rsz:
        return rsz

    for work_update in event.get('detail', {}).get('work_updates', []):
        rsz = parse_reduced_speed_limit_from_description(
            work_update.get('description', ""))
        if rsz:
            return rsz


if __name__ == "__main__":
    main()

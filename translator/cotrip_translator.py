import json
from datetime import datetime, timedelta
import logging
from collections import OrderedDict
import re
from translator import tools
import copy
import argparse


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

    if not tools.wzdx_translator.validate_wzdx(wzdx_obj, wzdx_schema):
        print('validation error more message are printed above. output file is not created because the message failed validation.')
        return
    with open(outputFile, 'w') as fwzdx:
        fwzdx.write(json.dumps(wzdx_obj, indent=2))
        print(
            'huraaah ! your wzdx message is successfully generated and located here: ' + str(outputFile))


# parse cotrip script command line arguments
def parse_cotrip_arguments():
    parser = argparse.ArgumentParser(
        description='Translate COTrip data to WZDx')
    parser.add_argument('cotripFilePath', help='cotrip file path')
    parser.add_argument('--out', required=False,
                        default='cotrip_wzdx_translated_output_message.geojson', help='WZDx output file path')

    args = parser.parse_args()
    return args.cotripFilePath, args.outputFilePath


def wzdx_creator(message, info=None, unsupported_message_callback=None):
    if not message:
        return None

    if not info:
        info = tools.wzdx_translator.initialize_info(
            DEFAULT_COTRIP_FEED_INFO_ID)
    if not tools.wzdx_translator.validate_info(info):
        return None

    wzd = tools.wzdx_translator.initialize_wzdx_object(info)

    # Parse alert to WZDx Feature
    feature = parse_alert(
        message, callback_function=unsupported_message_callback)
    if feature:
        wzd.get('features').append(feature)
    if not wzd.get('features'):
        return None
    wzd = tools.wzdx_translator.add_ids(wzd)
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


# function to get event status
def get_event_status(start_time_string, end_time_string):

    start_time = datetime.fromtimestamp(start_time_string)
    current_time = datetime.now()
    future_date_after_2weeks = current_time + \
        timedelta(days=14)
    event_status = "active"
    if current_time < start_time:
        if start_time < future_date_after_2weeks:
            event_status = "pending"
        else:
            event_status = "planned"

    elif end_time_string:
        end_time = datetime.fromtimestamp(end_time_string)
        if end_time < current_time:
            event_status = "completed"
    return event_status


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
    properties = initialize_feature_properties()

    # Event Type ['work-zone', 'detour']
    properties['event_type'] = 'work-zone'

    # start_date
    properties['start_date'] = tools.date.reformat_datetime(
        event.get('header').get('start_timestamp'))

    # end_date
    properties['end_date'] = tools.date.reformat_datetime(
        event.get('header').get('end_timestamp'))

    # start_date_accuracy
    properties['start_date_accuracy'] = "estimated"

    # end_date_accuracy
    properties['end_date_accuracy'] = "estimated"

    # beginning_accuracy
    properties['beginning_accuracy'] = "estimated"

    # ending_accuracy
    properties['ending_accuracy'] = "estimated"

    # road_name
    properties['road_names'] = [event.get('detail').get('road_name')]
    road_number = event.get('detail').get('road_number')
    if road_number and not road_number in properties['road_names']:
        properties['road_names'].append(road_number)

    # direction
    Direction_map = {'North': 'northbound', 'South': 'southbound',
                     'West': 'westbound', 'East': 'eastbound'}

    properties['direction'] = Direction_map.get(
        event.get('detail').get('direction'))

    # vehicle impact
    properties['vehicle_impact'] = 'unknown'

    # event status
    properties['event_status'] = get_event_status(
        event.get('header').get('start_timestamp'), event.get('header').get('end_timestamp'))

    # type_of_work
    # maintenance, minor-road-defect-repair, roadside-work, overhead-work, below-road-work, barrier-work, surface-work, painting, roadway-relocation, roadway-creation
    works = event.get('sub_type')
    types_of_work = get_types_of_work(works)
    if types_of_work:
        properties['types_of_work'] = types_of_work

    # reduced_speed_limit

    properties['reduced_speed_limit'] = get_rsz_from_event(event)

    # restrictions

    work_updates = event.get('detail').get('work_updates')
    restrictions = get_restrictions(work_updates)
    if restrictions:
        properties['restrictions'] = restrictions

    # description
    properties['description'] = event.get('header').get('description')

    # creation_date
    properties['creation_date'] = tools.date.reformat_datetime(
        event.get('source').get('collection_timestamp'))

    # update_date
    properties['update_date'] = tools.date.reformat_datetime(
        alert.get('rtdh_timestamp'))

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

    event = alert.get('event', {})
    polyline = event.get('geometry')
    coords = parse_polyline(polyline)
    street = event.get('detail', {}).get('road_name')

    header = event.get('header', {})
    starttime = header.get('start_timestamp')
    endtime = header.get('end_timestamp', 0)
    description = header.get('description')
    direction = event.get('detail', {}).get('direction')

    required_fields = [polyline, coords, street,
                       starttime, description, direction]
    for field in required_fields:
        if not field:
            logging.warning(
                f'Invalid event with event id = {alert.get("rtdh_message_id")}. not all required fields are present')
            return False

        if type(starttime) != int or type(endtime) != int:
            logging.warning(
                f'Invalid event with id = {alert.get("rtdh_message_id")}. Invalid datetime format')
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


def initialize_feature_properties():
    properties = {}
    properties['road_event_id'] = None
    properties['event_type'] = None
    properties['data_source_id'] = None
    properties['start_date'] = None
    properties['end_date'] = None
    properties['start_date_accuracy'] = None
    properties['end_date_accuracy'] = None
    properties['beginning_accuracy'] = None
    properties['ending_accuracy'] = None
    properties['road_name'] = None
    properties['direction'] = None
    properties['vehicle_impact'] = None
    properties['relationship'] = None
    properties['lanes'] = None
    properties['beginning_cross_street'] = None
    properties['ending_cross_street'] = None
    properties['beginning_mile_post'] = None
    properties['ending_mile_post'] = None
    properties['event_status'] = None
    properties['types_of_work'] = None
    properties['workers_present'] = None
    properties['reduced_speed_limit'] = None
    properties['restrictions'] = None
    properties['description'] = None
    properties['creation_date'] = None
    properties['update_date'] = None

    return properties


if __name__ == "__main__":
    main()

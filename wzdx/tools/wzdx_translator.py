import logging
import os
import os.path
import random
import re
import string
import uuid
from collections import OrderedDict
from datetime import datetime
from ..sample_files.validation_schema import work_zone_feed_v42
import date_tools

import jsonschema
import xmltodict


def initialize_feature_properties():
    properties = {}
    properties['core_details'] = {
        'event_type': None,
        'data_source_id': None,
        'road_names': None,
        'direction': None,
        'related_road_events': [],
        'name': None,
        'description': None,
        'creation_date': None,
        'update_date': None,
    }
    properties['start_date'] = None
    properties['end_date'] = None
    properties['is_start_date_verified'] = None
    properties['is_end_date_verified'] = None
    properties['is_start_position_verified'] = None
    properties['is_end_position_verified'] = None
    properties['location_method'] = None
    properties['work_zone_type'] = None
    properties['vehicle_impact'] = None
    properties['lanes'] = None
    properties['beginning_cross_street'] = None
    properties['ending_cross_street'] = None
    properties['beginning_mile_post'] = None
    properties['ending_mile_post'] = None
    properties['types_of_work'] = None
    properties['worker_presence'] = None
    properties['reduced_speed_limit_kph'] = None
    properties['restrictions'] = None

    return properties


def validate_info(info):

    if ((not info) or (type(info) != dict and type(info) != OrderedDict)):
        logging.warning('invalid type')
        return False

    contact_name = info.get('contact_name')
    contact_email = info.get('contact_email')
    publisher = info.get('publisher')
    required_fields = [contact_name, contact_email, publisher]
    for field in required_fields:
        if not field:
            logging.warning(
                'invalid supplimentary information object. Not all required fields are present')
            return False

    return True


def parse_xml_to_dict(xml_string):
    d = xmltodict.parse(xml_string)
    return d


def validate_wzdx(wzdx_obj, wzdx_schema=work_zone_feed_v42.wzdx_v42_schema_string):
    if not wzdx_schema or not wzdx_obj:
        return False
    try:
        jsonschema.validate(instance=wzdx_obj, schema=wzdx_schema)
    except jsonschema.ValidationError as e:
        logging.error(RuntimeError(str(e)))
        return False
    return True


def initialize_info():
    info = {}
    info['contact_name'] = os.getenv(
        'contact_name', 'Heather Pickering-Hilgers')
    info['contact_email'] = os.getenv(
        'contact_email', 'heather.pickeringhilgers@state.co.us')
    info['publisher'] = os.getenv(
        'publisher', 'CDOT')

    return info


# Add ids to message
# This function may fail if some optional fields are not present (lanes, types_of_work, relationship, ...)
def add_ids(message, event_type="work-zone"):
    if not message or type(message) != dict:
        return None

    if event_type == 'work-zone':
        data_source_id = message.get('feed_info').get(
            'data_sources')[0].get('data_source_id')
    elif event_type == 'restriction':
        data_source_id = message.get('feed_info').get(
            'data_sources')[0].get('data_source_id')

    road_event_length = len(message.get('features'))
    road_event_ids = []
    for i in range(road_event_length):
        road_event_ids.append(str(uuid.uuid4()))

    for i in range(road_event_length):
        feature = message.get('features')[i]
        id = road_event_ids[i]
        feature['properties']['core_details']['data_source_id'] = data_source_id

        # TODO: Implement related_road_events
        # if feature['properties']['core_details'].get('related_road_events'):
        #     related_road_events = feature['properties']['core_details']['related_road_events']
        #     road_event = {}
        #     feature['properties']['core_details']['related_road_events']['relationship_id'] = str(
        #         uuid.uuid4())
        #     feature['properties']['core_details']['related_road_events']['road_event_id'] = feature.get(
        #         'id', id)
    return message

# Add ids to message
# This function may fail if some optional fields are not present (lanes, types_of_work, relationship, ...)


def add_ids(message, event_type="work-zone"):
    if not message or type(message) != dict:
        return None

    if event_type == 'work-zone':
        data_source_id = message.get('feed_info').get(
            'data_sources')[0].get('data_source_id')
    elif event_type == 'restriction':
        data_source_id = message.get('feed_info').get(
            'data_sources')[0].get('data_source_id')

    road_event_length = len(message.get('features'))
    road_event_ids = []
    for i in range(road_event_length):
        road_event_ids.append(str(uuid.uuid4()))

    for i in range(road_event_length):
        feature = message.get('features')[i]
        id = road_event_ids[i]
        feature['properties']['core_details']['data_source_id'] = data_source_id
        if feature['properties']['core_details'].get('relationship'):
            feature['properties']['core_details']['relationship']['relationship_id'] = str(
                uuid.uuid4())
            feature['properties']['core_details']['relationship']['road_event_id'] = feature.get(
                'id', id)
    return message


def initialize_wzdx_object(info):
    wzd = {}
    wzd['feed_info'] = {}
    wzd['feed_info']['publisher'] = info.get('publisher')
    wzd['feed_info']['version'] = '4.2'
    wzd['feed_info']['license'] = "https://creativecommons.org/publicdomain/zero/1.0/"

    data_source = {}
    data_source['data_source_id'] = str(uuid.uuid4())
    data_source['organization_name'] = info.get('publisher')
    data_source['update_date'] = datetime.utcnow().strftime(
        "%Y-%m-%dT%H:%M:%SZ")
    data_source['update_frequency'] = info.get(
        'datafeed_frequency_update', 300)
    data_source['contact_name'] = info.get('contact_name')
    data_source['contact_email'] = info.get('contact_email')
    wzd['feed_info']['data_sources'] = [data_source]

    wzd['feed_info']['update_date'] = datetime.utcnow().strftime(
        "%Y-%m-%dT%H:%M:%SZ")
    wzd['feed_info']['update_frequency'] = info.get(
        'datafeed_frequency_update', 300)
    wzd['feed_info']['contact_name'] = info.get('contact_name')
    wzd['feed_info']['contact_email'] = info.get('contact_email')

    wzd['type'] = 'FeatureCollection'

    wzd['features'] = []

    return wzd


def initialize_wzdx_object_restriction(info):
    wzd = {}
    wzd['feed_info'] = {}
    # hardcode
    wzd['feed_info']['update_date'] = datetime.utcnow().strftime(
        "%Y-%m-%dT%H:%M:%SZ")
    wzd['feed_info']['publisher'] = info.get('publisher')
    wzd['feed_info']['contact_name'] = info.get('contact_name')
    wzd['feed_info']['contact_email'] = info.get('contact_email')
    if info.get('datafeed_frequency_update', False):
        wzd['feed_info']['update_frequency'] = info[
            'datafeed_frequency_update']  # Verify data type
    wzd['feed_info']['version'] = '4.0'
    wzd['feed_info']['license'] = "https://creativecommons.org/publicdomain/zero/1.0/"

    data_source = {}
    data_source['data_source_id'] = str(uuid.uuid4())
    data_source['organization_name'] = info.get('publisher')
    data_source['contact_name'] = info.get('contact_name')
    data_source['contact_email'] = info.get('contact_email')
    if info.get('datafeed_frequency_update', False):
        data_source['update_frequency'] = info.get('datafeed_frequency_update')
    data_source['update_date'] = datetime.utcnow().strftime(
        "%Y-%m-%dT%H:%M:%SZ")
    wzd['feed_info']['data_sources'] = [data_source]

    wzd['type'] = 'FeatureCollection'
    sub_identifier = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in
                             range(6))  # Create random 6 character digit/letter string
    id = str(uuid.uuid4())
    ids = {}
    ids['sub_identifier'] = sub_identifier
    ids['id'] = id

    wzd['features'] = []

    return wzd


def string_to_number(field):
    try:
        return int(field)
    except ValueError:
        try:
            return float(field)
        except ValueError:
            return None


# function to parse direction from street name
def parse_direction_from_street_name(street):
    if not street or type(street) != str:
        return None
    street_char = street[-1]
    street_chars = street[-2:]
    if street_char == 'N' or street_chars == 'NB':
        direction = 'northbound'
    elif street_char == 'S' or street_chars == 'SB':
        direction = 'southbound'
    elif street_char == 'W' or street_chars == 'WB':
        direction = 'westbound'
    elif street_char == 'E' or street_chars == 'EB':
        direction = 'eastbound'
    else:
        direction = 'unknown'

    return direction


# function to remove direction from street name
def remove_direction_from_street_name(street):
    SINGLE_CHARACTER_DIRECTIONS = ['N', 'E', 'S', 'W']
    MULTIPLE_CHARACTER_DIRECTIONS = ['NB', 'EB', 'SB', 'WB']

    if not street or type(street) != str:
        return None
    street_char = street[-1]
    street_chars = street[-2:]
    if street_char in SINGLE_CHARACTER_DIRECTIONS:
        street = street[:-1]
    if street_chars in MULTIPLE_CHARACTER_DIRECTIONS:
        street = street[:-2]

    return street


# function to parse polyline to geometry line string
def parse_polyline_from_linestring(poly):
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


# Remove additional fields added for internal processing, if they are present
def remove_unnecessary_fields(wzdx):
    for feature in wzdx['features']:
        if 'route_details_start' in feature.get('properties', {}):
            del feature['properties']['route_details_start']
        if 'route_details_end' in feature.get('properties', {}):
            del feature['properties']['route_details_end']
        if 'condition_1' in feature.get('properties', {}):
            del feature['properties']['condition_1']
    return wzdx


# Remove additional fields added for internal processing, if they are present
def remove_unnecessary_fields_feature(feature):
    if 'route_details_start' in feature.get('properties', {}):
        del feature['properties']['route_details_start']
    if 'route_details_end' in feature.get('properties', {}):
        del feature['properties']['route_details_end']
    if 'condition_1' in feature.get('properties', {}):
        del feature['properties']['condition_1']
    return feature


def get_event_status(feature):
    start_date = date_tools.parse_datetime_from_iso_string(
        feature['properties']['start_date'])
    end_date = date_tools.parse_datetime_from_iso_string(
        feature['properties']['end_date'])
    return date_tools.get_event_status(
        start_date, end_date)


def filter_active_wzdx(wzdx_msgs):
    return filter(lambda x: get_event_status(x['features'][0]) == 'active', wzdx_msgs)


def filter_wzdx_by_event_status(wzdx_msgs, event_status_list):
    return filter(lambda x: get_event_status(x['features'][0]) in event_status_list, wzdx_msgs)

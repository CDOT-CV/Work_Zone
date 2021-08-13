import logging
import os
import os.path
import random
import re
import string
import uuid
from collections import OrderedDict
from datetime import datetime

import jsonschema
import xmltodict


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


def validate_info(info):

    if ((not info) or (type(info) != dict and type(info) != OrderedDict)):
        logging.warning('invalid type')
        return False

    feed_info_id = str(info.get('feed_info_id', ''))
    check_feed_info_id = re.match(
        '[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}', feed_info_id)

    metadata = info.get('metadata', {})
    wz_location_method = metadata.get('wz_location_method')
    lrs_type = metadata.get('lrs_type')
    contact_name = metadata.get('contact_name')
    contact_email = metadata.get('contact_email')
    issuing_organization = metadata.get('issuing_organization')
    required_fields = [check_feed_info_id, metadata, wz_location_method,
                       lrs_type, contact_name, contact_email, issuing_organization]
    for field in required_fields:
        if not field:
            logging.warning(
                'invalid supplimentary information object. Not all required fields are present')
            return False

    return True


def parse_xml(inputfile):
    if not inputfile or not os.path.isfile(inputfile):
        return None
    with open(inputfile, encoding='utf-8-sig') as f:
        xml_string = f.read()
        inputfile_obj = xmltodict.parse(xml_string)
        return inputfile_obj


def validate_wzdx(wzdx_obj, wzdx_schema):
    if not wzdx_schema or not wzdx_obj:
        return False
    try:
        jsonschema.validate(instance=wzdx_obj, schema=wzdx_schema)
    except jsonschema.ValidationError as e:
        logging.error(RuntimeError(str(e)))
        return False
    return True


def initialize_info(feed_info_id):
    info = {}
    info['feed_info_id'] = feed_info_id
    info['metadata'] = {}
    info['metadata']['wz_location_method'] = "channel-device-method"
    info['metadata']['lrs_type'] = "lrs_type"
    info['metadata']['contact_name'] = os.getenv('contact_name')
    if info['metadata']['contact_name'] == None:
        raise RuntimeError(
            'The environment variable contact_name is not present')
    info['metadata']['contact_email'] = os.getenv('contact_email')
    if info['metadata']['contact_email'] == None:
        raise RuntimeError(
            'The environment variable contact_email is not present')
    info['metadata']['issuing_organization'] = os.getenv(
        'issuing_organization')
    if info['metadata']['issuing_organization'] == None:
        raise RuntimeError(
            'The environment variable issuing_organization is not present')

    return info


# Add ids to message
# This function may fail if some optional fields are not present (lanes, types_of_work, relationship, ...)
def add_ids(message):
    if not message or type(message) != dict:
        return None

    data_source_id = message.get('road_event_feed_info').get(
        'data_sources')[0].get('data_source_id')
    road_event_length = len(message.get('features'))
    road_event_ids = []
    for i in range(road_event_length):
        road_event_ids.append(str(uuid.uuid4()))

    for i in range(road_event_length):
        feature = message.get('features')[i]
        id = road_event_ids[i]
        feature['properties']['road_event_id'] = id
        feature['properties']['data_source_id'] = data_source_id
        if feature['properties'].get('relationship'):
            feature['properties']['relationship']['relationship_id'] = str(
                uuid.uuid4())
            feature['properties']['relationship']['road_event_id'] = id
    return message


def initialize_wzdx_object(info):
    wzd = {}
    wzd['road_event_feed_info'] = {}
    # hardcode
    wzd['road_event_feed_info']['feed_info_id'] = info.get('feed_info_id')
    wzd['road_event_feed_info']['update_date'] = datetime.utcnow().strftime(
        "%Y-%m-%dT%H:%M:%SZ")
    wzd['road_event_feed_info']['publisher'] = info.get(
        'metadata').get('issuing_organization')
    wzd['road_event_feed_info']['contact_name'] = info.get(
        'metadata').get('contact_name')
    wzd['road_event_feed_info']['contact_email'] = info.get(
        'metadata').get('contact_email')
    if info['metadata'].get('datafeed_frequency_update', False):
        wzd['road_event_feed_info']['update_frequency'] = info.get('metadata')[
            'datafeed_frequency_update']  # Verify data type
    wzd['road_event_feed_info']['version'] = '3.1'
    wzd['road_event_feed_info']['license'] = "https://creativecommons.org/publicdomain/zero/1.0/"

    data_source = {}
    data_source['data_source_id'] = str(uuid.uuid4())
    data_source['feed_info_id'] = info.get('feed_info_id')
    data_source['organization_name'] = info.get(
        'metadata').get('issuing_organization')
    data_source['contact_name'] = info.get('metadata').get('contact_name')
    data_source['contact_email'] = info.get('metadata').get('contact_email')
    if info['metadata'].get('datafeed_frequency_update', False):
        data_source['update_frequency'] = info.get(
            'metadata').get('datafeed_frequency_update')
    data_source['update_date'] = datetime.utcnow().strftime(
        "%Y-%m-%dT%H:%M:%SZ")
    data_source['location_method'] = info.get(
        'metadata').get('wz_location_method')
    data_source['lrs_type'] = info.get('metadata').get('lrs_type')
    wzd['road_event_feed_info']['data_sources'] = [data_source]

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

import xmltodict
import uuid
import sys
import getopt
from jsonschema import validate
from jsonschema import ValidationError
import logging
from collections import OrderedDict
import re
import os
from datetime import datetime
import os.path
import random
import string


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
            logging.warning('Not all required fields are present')
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
        validate(instance=wzdx_obj, schema=wzdx_schema)
    except ValidationError as e:
        logging.error(RuntimeError(str(e)))
        return False
    return True


def initialize_info():
    info = {}
    info['feed_info_id'] = "104d7746-688c-44ed-b195-2ee948bf9dfa"
    info['metadata'] = {}
    info['metadata']['wz_location_method'] = "channel-device-method"
    info['metadata']['lrs_type'] = "lrs_type"
    info['metadata']['contact_name'] = "Abinash Konersman"
    info['metadata']['contact_email'] = "abinash.konersman@state.co.us"
    info['metadata']['issuing_organization'] = "CDOT"

    return info


help_string = """ 

Usage: python **script_name** [arguments]

Global options:
-h, --help                  Print this usage information.
-i, --input                 specify the file to translate
-o, --output                specify the output file for generated wzdx geojson message """


def parse_arguments(argv, default_output_file_name='wzdx_translated_output_message.geojson'):
    inputfile = ''
    outputfile = default_output_file_name

    try:
        opts, _ = getopt.getopt(argv, "hi:o:", ["input=", "output="])
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(help_string)
            sys.exit()
        elif opt in ("-i", "--input"):
            inputfile = arg
        elif opt in ("-o", "--output"):
            outputfile = arg

    return inputfile, outputfile

# Add ids to message
# This function may fail if some optional fields are not present (lanes, types_of_work, relationship, ...)


def add_ids(message):
    if not message or type(message) != dict:
        return None
    try:

        data_source_id = message.get('road_event_feed_info').get(
            'data_sources')[0].get('data_source_id')
        road_event_length = len(message.get('features'))
        road_event_ids = []
        for i in range(road_event_length):
            road_event_ids.append(str(uuid.uuid4()))

        for i in range(road_event_length):
            feature = message.get('features')[i]
            road_event_id = road_event_ids[i]
            feature['properties']['road_event_id'] = road_event_id
            feature['properties']['data_source_id'] = data_source_id
            feature['properties']['relationship']['relationship_id'] = str(
                uuid.uuid4())
            feature['properties']['relationship']['road_event_id'] = road_event_id
        return message
    except:
        return message


def initialize_wzdx_object(info):
    wzd = {}
    wzd['road_event_feed_info'] = {}
    # hardcode
    wzd['road_event_feed_info']['feed_info_id'] = info.get('feed_info_id')
    wzd['road_event_feed_info']['update_date'] = datetime.now().strftime(
        "%Y-%m-%dT%H:%M:%SZ")
    wzd['road_event_feed_info']['publisher'] = 'CDOT'
    wzd['road_event_feed_info']['contact_name'] = 'Abinash Konersman'
    wzd['road_event_feed_info']['contact_email'] = 'abinash.konersman@state.co.us'
    if info['metadata'].get('datafeed_frequency_update', False):
        wzd['road_event_feed_info']['update_frequency'] = info.get('metadata')[
            'datafeed_frequency_update']  # Verify data type
    wzd['road_event_feed_info']['version'] = '3.0'

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
    data_source['update_date'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    data_source['location_method'] = info.get(
        'metadata').get('wz_location_method')
    data_source['lrs_type'] = info.get('metadata').get('lrs_type')
    wzd['road_event_feed_info']['data_sources'] = [data_source]

    wzd['type'] = 'FeatureCollection'
    sub_identifier = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in
                             range(6))  # Create random 6 character digit/letter string
    road_event_id = str(uuid.uuid4())
    ids = {}
    ids['sub_identifier'] = sub_identifier
    ids['road_event_id'] = road_event_id

    wzd['features'] = []

    return wzd

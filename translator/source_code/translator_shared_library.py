import xmltodict
import json
from datetime import datetime
import uuid
import random
import string
import sys, getopt
from jsonschema import validate
from jsonschema import ValidationError
import logging
from collections import OrderedDict
import re
import os



def validate_info(info):

    if ((not info) or (type(info) != dict and type(info) != OrderedDict)):
        logging.warning('invalid type')
        return False

    feed_info_id = str(info.get('feed_info_id', ''))
    check_feed_info_id = re.match('[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}', feed_info_id)
    

    metadata=info.get('metadata', {})
    wz_location_method = metadata.get('wz_location_method')
    lrs_type = metadata.get('lrs_type')
    contact_name = metadata.get('contact_name')
    contact_email = metadata.get('contact_email') 
    issuing_organization=metadata.get('issuing_organization')
    required_fields = [ check_feed_info_id, metadata, wz_location_method, lrs_type, contact_name, contact_email, issuing_organization]
    for field in required_fields:
        if not field:
            logging.warning( 'Not all required fields are present') 
            return False
            
    return True

def parse_xml(inputfile):
    with open(inputfile, encoding='utf-8-sig') as ficone:
        xml_string = ficone.read()
        icone_obj = xmltodict.parse(xml_string)
        return icone_obj

def validate_wzdx(wzdx_obj, wzdx_schema):
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
    info['metadata']['issuing_organization'] = "COtrip"

    return info



help_string = """ 

Usage: python icone_translator.py [arguments]

Global options:
-h, --help                  Print this usage information.
-i, --input                 specify the xml file to translate
-o, --output                specify the output file for generated wzdx geojson message """

def parse_arguments(argv, default_output_file_name = 'wzdx_translated_output_message.geojson'):
    inputfile = ''
    outputfile = default_output_file_name

    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["input=", "output="])
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

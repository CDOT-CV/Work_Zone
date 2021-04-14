import json
from datetime import datetime, timezone, timedelta
import uuid
import random
import string
import sys, getopt
from jsonschema import validate
from jsonschema import ValidationError
import logging
from collections import OrderedDict
import re
import dateutil.parser
from translator.source_code import translator_shared_library

# Translator

def main():
    
    inputfile, outputfile = translator_shared_library.parse_arguments(sys.argv[1:], default_output_file_name = 'cotrip_wzdx_translated_output_message.geojson')
    if inputfile:

        cotrip_obj = json.loads(open(inputfile).read())
        wzdx_obj = wzdx_creator(cotrip_obj)
        location_schema = '../sample files/validation_schema/wzdx_v3.0_feed.json'
        wzdx_schema = json.loads(open(location_schema).read())
        if not translator_shared_library.validate_wzdx(wzdx_obj, wzdx_schema):
            print('validation error more message are printed above')
        with open(outputfile, 'w') as fwzdx:
            fwzdx.write(json.dumps(wzdx_obj, indent=2))
            print('huraaah ! your wzdx message is successfully generated and located here: ' + str(outputfile))
    else:
        print('please specify the input file with -i')
        print(translator_shared_library.help_string)


    
def wzdx_creator(message, info=None, unsupported_message_callback=None):
    if not message:
        return None
   #verify info obj 
    if not info:
        info = translator_shared_library.initialize_info()
    if not translator_shared_library.validate_info(info):
        return None
    wzd = {}
    wzd['road_event_feed_info'] = {}
    # hardcode
    wzd['road_event_feed_info']['feed_info_id'] = info['feed_info_id']
    wzd['road_event_feed_info']['update_date'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    wzd['road_event_feed_info']['publisher'] = 'CDOT'
    wzd['road_event_feed_info']['contact_name'] = 'Abinash Konersman'
    wzd['road_event_feed_info']['contact_email'] = 'abinash.konersman@state.co.us'
    if info['metadata'].get('datafeed_frequency_update', False):
        wzd['road_event_feed_info']['update_frequency'] = info['metadata'][
            'datafeed_frequency_update']  # Verify data type
    wzd['road_event_feed_info']['version'] = '3.0'

    data_source = {}
    data_source['data_source_id'] = str(uuid.uuid4())
    data_source['feed_info_id'] = info['feed_info_id']
    data_source['organization_name'] = info['metadata']['issuing_organization']
    data_source['contact_name'] = info['metadata']['contact_name']
    data_source['contact_email'] = info['metadata']['contact_email']
    if info['metadata'].get('datafeed_frequency_update', False):
        data_source['update_frequency'] = info['metadata']['datafeed_frequency_update']
    data_source['update_date'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    data_source['location_method'] = info['metadata']['wz_location_method']
    data_source['lrs_type'] = info['metadata']['lrs_type']
    wzd['road_event_feed_info']['data_sources'] = [data_source]

    wzd['type'] = 'FeatureCollection'
    sub_identifier = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in
                             range(6))  # Create random 6 character digit/letter string
    road_event_id = str(uuid.uuid4())
    ids = {}
    ids['sub_identifier'] = sub_identifier
    ids['road_event_id'] = road_event_id

    wzd['features'] = []

    
    # Parse alert to WZDx Feature    
    feature = parse_alert(message, callback_function=unsupported_message_callback)
    if feature:
        wzd['features'].append(feature)
    if not wzd['features']:
        return None
    wzd =translator_shared_library.add_ids(wzd, True)
    return wzd





# function to parse polyline to geometry line string
def parse_polyline(poly):
    if not poly or type(poly) != str:
        return None
    poly= poly[len('LINESTRING (' ): -1]
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
                        timedelta(days = 14)
    event_status = "active"
    if current_time < start_time:
        if start_time < future_date_after_2weeks  :
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
    feature = {}
    geometry = {}
    geometry['type'] = "LineString"
    geometry['coordinates'] = parse_polyline(event['geometry'])

    feature['type'] = "Feature"
    properties = {}

    # road_event_id
    #### Leave this empty, it will be populated by add_ids
    properties['road_event_id'] = ''

    # Event Type ['work-zone', 'detour']
    properties['event_type'] = 'work-zone'

    # data_source_id
    #### Leave this empty, it will be populated by add_ids
    properties['data_source_id'] = ''

    # start_date
    properties['start_date'] = reformat_datetime(event['header']['start_timestamp'])

    # end_date
    properties['end_date'] = reformat_datetime(event['header'].get('end_timestamp'))

    # start_date_accuracy
    properties['start_date_accuracy'] = "estimated"

    # end_date_accuracy
    properties['end_date_accuracy'] = "estimated"

    # beginning_accuracy
    properties['beginning_accuracy'] = "estimated"

    # ending_accuracy
    properties['ending_accuracy'] = "estimated"

    # road_name
    properties['road_name'] = event['detail']['road_name']

    # direction
    Direction_map = {'North': 'northbound', 'South': 'southbound', 'West': 'westbound', 'East': 'eastbound'}
 
    properties['direction'] = Direction_map.get(event['detail']['direction'])

    # vehicle impact
    properties['vehicle_impact'] = 'unknown'

    # Relationship
    properties['relationship'] = {}

    # lanes
    properties['lanes'] = []

    # beginning_cross_street
    properties['beginning_cross_street'] = ""

    # beginning_cross_street
    properties['ending_cross_street'] = ""

    # event status
    properties['event_status'] = get_event_status(event['header']['start_timestamp'], event['header'].get('end_timestamp'))

    # type_of_work
    # maintenance, minor-road-defect-repair, roadside-work, overhead-work, below-road-work, barrier-work, surface-work, painting, roadway-relocation, roadway-creation
    properties['types_of_work'] = event.get('subtype')

    # restrictions
    properties['restrictions'] = [] 

    # description
    properties['description'] = event['header']['description']

    # creation_date
    properties['creation_date'] = reformat_datetime(event['source']['collection_timestamp'])

    # update_date
    properties['update_date'] = reformat_datetime(alert['rtdh_timestamp'])

    feature = {}
    feature['type'] = "Feature"
    feature['properties'] = properties
    feature['geometry'] = geometry

    return feature

#function to validate the alert
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
   
    required_fields = [ polyline, coords, street, starttime, description, direction]
    for field in required_fields:
        if not field:
            logging.warning(f'Invalid event with event id = {alert.get("rtdh_message_id")}. not all required fields are present')
            return False
            
        
        if type(starttime) != int or type(endtime) != int:
            logging.warning(f'Invalid event with id = {alert.get("rtdh_message_id")}. Invalid datetime format')
            return False
    
    return True

def reformat_datetime(datetime_string):
    if not datetime_string:
        return ''
    elif type(datetime_string) == str:
        if re.match('^-?([0-9]*[.])?[0-9]+$', datetime_string):
            datetime_string = float(datetime_string)
        else:
            return ''
    time = datetime.fromtimestamp(datetime_string)
    wzdx_format_datetime = time.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return wzdx_format_datetime




if __name__ == "__main__":
    main()




import xmltodict
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
import translator_shared_library

# Translator

def main():
    
    inputfile, outputfile = translator_shared_library.parse_arguments(sys.argv[1:], default_output_file_name = 'cotrip_wzdx_translated_output_message.geojson')
    if inputfile:

        cotrip_obj = translator_shared_library.parse_xml(inputfile)
        wzdx_obj = wzdx_creator(cotrip_obj)
        location_schema = '../sample files/validation_schema/wzdx_v3.0_feed.json'
        wzdx_schema = json.loads(open(location_schema).read())
        if not translator_shared_library.validate_wzdx(wzdx_obj, wzdx_schema):
            print('validation error more messages are printed above')
        with open(outputfile, 'w') as fwzdx:
            fwzdx.write(json.dumps(wzdx_obj, indent=2))
            print('huraaah ! your wzdx message is successfully generated and located here: ' + str(outputfile))
    else:
        print('please specify the input file with -i')
        print(translator_shared_library.help_string)


    
def wzdx_creator(messages, info=None, unsupported_message_callback=None):
    if not messages:
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

    if not messages.get('alert:Alerts', {}).get('alert:Alert'):
        return None

    for alert in messages['alert:Alerts']['alert:Alert']:
        # Parse alert to WZDx Feature    
        feature = parse_alert(alert, callback_function=unsupported_message_callback)
        if feature:
            wzd['features'].append(feature)
    if not wzd['features']:
        return None
    wzd = add_ids(wzd, True)
    return wzd





# function to parse polyline to geometry line string
def parse_polyline(polylinestring):
    if not polylinestring or type(polylinestring) != str:
        return None
    polyline = polylinestring.split(' ')
    geometry=[]
    for i in polyline:
        coordinates = i.split(',')
        coords=[]
        for j in coordinates:
            coords.append(float(j))
        geometry.append(coords)
    return geometry

# function to calculate vehicle impact
def get_vehicle_impact(closure_type):

    all_lanes_closed = ['All Lanes Closed', 'Intersection Closure', 'Bridge Closed' ]
    some_lanes_closed = ['Single Lane Closure', 'Left Lane Closed', 'Right Lane Closed','Various Lane Closures', 'Express Lanes Closed', 'Mobile Lane Closure', 'Left Two Lanes Closed',
    'Left Turn Lane Closure', 'Center Lanes Closed', 'Right Turn Lane Closure', 'Alternating Single Lane Closures','Intermittent Lane Closure'  ]
    all_lanes_open = ['No Closure', -'Intermittent Traffic Stops', 'Shoulder Closure', 'Right Shoulder Closed', 'Off-Ramp Closure', 'On-Ramp Closure',  ]
    alternating_one_way = ['Single Lane Traffic', 'Alternating Traffic' ]
    
    vehicle_impact = 'unknown'    
    if closure_type in all_lanes_closed:
        vehicle_impact = 'all-lanes-closed'
    elif closure_type in some_lanes_closed:
        vehicle_impact = 'some-lanes-closed'
    elif closure_type in all_lanes_open:
        vehicle_impact = 'all-lanes-open'
    elif closure_type in alternating_one_way:
        vehicle_impact = 'alternating-one-way'
    return vehicle_impact



# function to get event status
def get_event_status(start_time_string, end_time_string):  

    start_time = dateutil.parser.parse(start_time_string)
    current_time = datetime.now(timezone.utc)
    future_date_after_2weeks = current_time + \
                        timedelta(days = 14)
    event_status = "active"
    if current_time < start_time:
        event_status = "planned"
    elif start_time < future_date_after_2weeks:
        event_status = "pending"
    elif end_time_string:
        end_time = dateutil.parser.parse(end_time_string)

        if end_time < current_time:
            event_status = "completed"
    return event_status



# Parse COtrip alert to WZDx
def parse_alert(alert, callback_function=None):
    if not validate_alert(alert):
        if callback_function:    
            callback_function(alert)
        return None
    feature = {}
    geometry = {}
    geometry['type'] = "LineString"
    geometry['coordinates'] = parse_polyline(alert['alert:Polyline'])

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
    properties['start_date'] = reformat_datetime(alert['alert:ReportedTime'])

    # end_date
    properties['end_date'] = reformat_datetime(alert.get('alert:ExpectedEndTime', ''))

    # start_date_accuracy
    properties['start_date_accuracy'] = "estimated"

    # end_date_accuracy
    properties['end_date_accuracy'] = "estimated"

    # beginning_accuracy
    properties['beginning_accuracy'] = "estimated"

    # ending_accuracy
    properties['ending_accuracy'] = "estimated"

    # road_name
    road_name = alert['alert:RoadName']
    properties['road_name'] = road_name

    # direction
    Direction_map = {'North': 'northbound', 'South': 'southbound', 'West': 'westbound', 'East': 'eastbound'}
 
    properties['direction'] = Direction_map.get(alert['alert:Direction'])

    # vehicle impact
    properties['vehicle_impact'] = 'unknown'

    # Relationship
    properties['relationship'] = {}

    # lanes
    properties['lanes'] = []

    # road_name
    properties['road_number'] = ""

    # beginning_cross_street
    properties['beginning_cross_street'] = ""

    # beginning_cross_street
    properties['ending_cross_street'] = ""

    # event status
    properties['event_status'] = get_event_status(alert['alert:ReportedTime'], alert.get('alert:ExpectedEndTime'))

    # type_of_work
    # maintenance, minor-road-defect-repair, roadside-work, overhead-work, below-road-work, barrier-work, surface-work, painting, roadway-relocation, roadway-creation
    properties['types_of_work'] = []

    # reduced speed limit
    properties['reduced_speed_limit'] = 25

    # workers present
    properties['workers_present'] = False

    # restrictions
    properties['restrictions'] = [] 

    # description
    properties['description'] = alert['alert:Description']

    # creation_date
    properties['creation_date'] = reformat_datetime(alert['alert:ReportedTime'])

    # update_date
    properties['update_date'] = reformat_datetime(alert['alert:LastUpdatedDate'])

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
    

    polyline = alert.get('alert:Polyline')
    coords = parse_polyline(polyline)
    street = alert.get('alert:RoadName', '')

    starttime = alert.get('alert:ReportedTime')
    endtime = alert.get('alert:ExpectedEndTime')
    description = alert.get('alert:Description')
   
    required_fields = [ polyline, coords, street, starttime, endtime, description]
    for field in required_fields:
        if not field:
            logging.warning(f'Invalid alert with alert id = {alert.get("alert:AlertId")}. not all required fields are present')
            return False
            
    try:
        dateutil.parser.parse(alert['alert:ReportedTime'])
        if alert.get('alert:ExpectedEndTime'):
            dateutil.parser.parse(alert['alert:ExpectedEndTime'])
    except ValueError:
        logging.warning('Invalid alert with id . Invalid datetime format')
        return False
    
    return True

def reformat_datetime(datetime_string):
    time = dateutil.parser.parse(datetime_string)
    wzdx_format_datetime = time.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return wzdx_format_datetime

# Add ids to message
#### This function may fail if some optional fields are not present (lanes, types_of_work, relationship, ...)
def add_ids(message, add_ids):
    if add_ids:
        feed_info_id = message['road_event_feed_info']['feed_info_id']
        data_source_id = message['road_event_feed_info']['data_sources'][0]['data_source_id']

        road_event_length = len(message['features'])
        road_event_ids = []
        for i in range(road_event_length):
            road_event_ids.append(str(uuid.uuid4()))

        for i in range(road_event_length):
            feature = message['features'][i]
            road_event_id = road_event_ids[i]
            feature['properties']['road_event_id'] = road_event_id
            feature['properties']['data_source_id'] = data_source_id
            feature['properties']['relationship']['relationship_id'] = str(uuid.uuid4())
            feature['properties']['relationship']['road_event_id'] = road_event_id 

    return message


if __name__ == "__main__":
    main()



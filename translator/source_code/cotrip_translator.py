
import xmltodict
import json
from datetime import datetime, timezone
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





# Translator


def wzdx_creator(messages, info=None, unsupported_message_callback=None):
    if not messages:
        return None
   #verify info obj 
    if not info:
        info=initialize_info()
    if not validate_info(info):
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



def validate_info(info):

    if ((not info) or (type(info) != dict and type(info) != OrderedDict)):
        logging.warning('invalid type')
        return False
    
    #### Consider whether this id needs to be hardcoded or generated
    feed_info_id = str(info.get('feed_info_id', ''))
    check_feed_info_id = re.match('[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}', feed_info_id)
    #### This information is required, might want to hardcode
    metadata=info.get('metadata', {})
    wz_location_method = metadata.get('wz_location_method')
    lrs_type = metadata.get('lrs_type')
    contact_name = metadata.get('contact_name')
    contact_email = metadata.get('contact_email') 
    issuing_organization=metadata.get('issuing_organization')
    required_fields = [ check_feed_info_id, metadata, wz_location_method, lrs_type, contact_name, contact_email, issuing_organization]
    for field in required_fields:
        if not field:
            return False
            logging.warning( 'Not all required fields are present') 
    return True



# function to calculate vehicle impact
def get_vehicle_impact(closure_type):

    all_lanes_closed = ['All Lanes Closed', 'Intersection Closure', 'Bridge Closed' ]
    some_lanes_closed = ['Single Lane Closure', 'Left Lane Closed', 'Right Lane Closed','Various Lane Closures', 'Express Lanes Closed', 'Mobile Lane Closure', 'Left Two Lanes Closed',
    'Left Turn Lane Closure', 'Center Lanes Closed', 'Right Turn Lane Closure', 'Alternating Single Lane Closures','Intermittent Lane Closure'  ]
    all_lanes_open = ['No Closure', -'Intermittent Traffic Stops', 'Shoulder Closure', 'Right Shoulder Closed', 'Off-Ramp Closure', 'On-Ramp Closure',  ]
    alternating_one_way = ['Single Lane Traffic', 'Alternating Traffic' ]
    unknown = []
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



# function to get event status
def get_event_status(start_time_string, end_time_string):
    start_time = dateutil.parser.parse(start_time_string)

    event_status = "active"
    if datetime.now(timezone.utc) < start_time:
        event_status = "planned"  # if < 2 to 3 weeks make it pending instead of planned
    elif end_time_string:
        end_time = dateutil.parser.parse(end_time_string)

        if end_time < datetime.now(timezone.utc):
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

    #### I included a skeleton of the message, fill out all required fields and as many optional fields as you can. Below is a link to the spec page for a road event
    #### https://github.com/usdot-jpo-ode/jpo-wzdx/blob/master/spec-content/objects/RoadEvent.md

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

    properties['vehicle_impact'] = 'unknown' #get_vehicle_impact(alert['alert:ClosureType'])

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
    properties['restrictions'] = [] #will work with it late

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
            logging.warning('Invalid alert with id =. Not all required fields are present')
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


help_string = """ 

Usage: python icone_translator.py [arguments]

Global options:
-h, --help                  Print this usage information.
-i, --input                 specify the xml file to translate
-o, --output                specify the output file for generated wzdx geojson message """

def parse_arguments(argv):
    inputfile = ''
    outputfile = 'cotrip_wzdx_translated_output_message.geojson'
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
inputfile, outputfile = parse_arguments(sys.argv[1:])


def initialize_info():
    info = {}

    #### Consider whether this id needs to be hardcoded or generated
    info['feed_info_id'] = "104d7746-688c-44ed-b195-2ee948bf9dfa"

    #### This information is required, might want to hardcode
    info['metadata'] = {}
    info['metadata']['wz_location_method'] = "channel-device-method"
    info['metadata']['lrs_type'] = "lrs_type"
    info['metadata']['contact_name'] = "Abinash Konersman"  # we can consider to add a representive name from iCone
    info['metadata']['contact_email'] = "abinash.konersman@state.co.us"
    info['metadata']['issuing_organization'] = "COtrip"

    return info


def parse_xml(inputfile):
    with open(inputfile, encoding='utf-8-sig') as ficone:
        # Read
        xml_string = ficone.read()
        cotrip_obj = xmltodict.parse(xml_string)
        return cotrip_obj

def validate_wzdx(wzdx_obj, wzdx_schema):
    try:
      validate(instance=wzdx_obj, schema=wzdx_schema)
    except ValidationError as e:
      logging.error(RuntimeError(str(e)))
      return False
    return True

def validate_write(wzdx_obj, outputfile, location_schema):
    wzdx_schema = json.loads(open(location_schema).read())
    if not validate_wzdx(wzdx_obj, wzdx_schema):
        return False
    with open(outputfile, 'w') as fwzdx:
        fwzdx.write(json.dumps(wzdx_obj, indent=2))
    return True


if inputfile:
    # Added encoding argument because of weird character at start of alerts.xml file

    cotrip_obj = parse_xml(inputfile)
    wzdx = wzdx_creator(cotrip_obj, initialize_info())
    if not validate_write(wzdx, outputfile, '../validation_schema/wzdx_v3.0_feed.json'):
        print('validation error more messages are printed above')
    else:
        print('huraaah ! your wzdx message is successfully generated and located here: ' + str(outputfile))
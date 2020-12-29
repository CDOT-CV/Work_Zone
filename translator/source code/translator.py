import xmltodict
import xml.etree.ElementTree as ET
import json
from datetime import datetime
import uuid
import random
import string


# Translator
def wzdx_creator(messages, info):
    wzd = {}
    wzd['road_event_feed_info'] = {}
    # hardcode
    wzd['road_event_feed_info']['feed_info_id'] = info['feed_info_id']
    wzd['road_event_feed_info']['update_date'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    wzd['road_event_feed_info']['publisher'] = 'CDOT '
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
    data_source['location_verify_method'] = info['metadata']['location_verify_method']
    data_source['location_method'] = info['metadata']['wz_location_method']
    data_source['lrs_type'] = info['metadata']['lrs_type']
    # data_source['lrs_url'] = "basic url"

    wzd['road_event_feed_info']['data_sources'] = [data_source]

    wzd['type'] = 'FeatureCollection'
    nodes = []
    sub_identifier = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in
                             range(6))  # Create random 6 character digit/letter string
    road_event_id = str(uuid.uuid4())
    ids = {}
    ids['sub_identifier'] = sub_identifier
    ids['road_event_id'] = road_event_id

    wzd['features'] = []
    print(messages)
    print("")
    print("")
    print("")
    print("")
    print("")
    for incident in messages['incidents']['incident']:
        print(incident)
        print("")
        print("")
        # Parse Incident to WZDx Feature
        wzd['features'].append(parse_incident(incident))



    wzd = add_ids(wzd, True)
    return wzd


#################### Sample Incident ####################
#   <incident id="U13631714_202012161717">
#     <creationtime>2020-12-16T17:17:00Z</creationtime>
#     <updatetime>2020-12-16T17:47:00Z</updatetime>
#     <type>CONSTRUCTION</type>
#     <description>Roadwork - Lane Closed, MERGE LEFT [iCone]</description>
#     <location>
#       <direction>ONE_DIRECTION</direction>
#       <polyline>28.8060608,-96.9916512,28.8060608,-96.9916512</polyline>
#     </location>
#     <starttime>2020-12-16T17:17:00Z</starttime>
#   </incident>

# Parse Icone Incident to WZDx
def parse_incident(incident):



    feature = {}
    geometry ={}
    geometry['type'] = "LineString"
    geometry['coordinates']= []


    polyline= incident['location']['polyline'].split(',')
    for i in  range(0,len(polyline),2) :
        geometry['coordinates'].append([float(polyline[i+1]),float(polyline[i])])





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
    properties['start_date'] = incident['starttime']

    # end_date
    properties['end_date'] = incident.get('endtime','')

    # start_date_accuracy
    properties['start_date_accuracy'] = "estimated"

    # end_date_accuracy
    properties['end_date_accuracy'] = "estimated"

    # beginning_accuracy
    properties['beginning_accuracy'] = "estimated"

    # ending_accuracy
    properties['ending_accuracy'] = "estimated"

    # road_name
    properties['road_name'] = incident['location'].get('street','')

    # direction
    direction = ''
    long_dif = geometry['coordinates'][-1][0] - geometry['coordinates'][0][0]
    lat_dif = geometry['coordinates'][-1][1] - geometry['coordinates'][0][1]
    if abs(long_dif) > abs(lat_dif):
        if long_dif > 0:
            direction = 'eastbound'
        else:
            direction = 'westbound'
    elif lat_dif > 0:
        direction = 'northbound'
    else:
        direction = 'southbound'
    properties['direction'] = direction

    # vehicle impact
    vehicle_impact = 'all-lanes-open'
    if 'lane closed' in incident['description'].lower() :
        vehicle_impact = 'some-lanes-closed'
    properties['vehicle_impact'] = vehicle_impact

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

    # beginning_milepost
    properties['beginning_milepost'] = ""

    # ending_milepost
    properties['ending_milepost'] = ""

    # event status
    start_time=datetime.strptime(incident['starttime'],"%Y-%m-%dT%H:%M:%SZ")

    event_status="active"
    if datetime.now() < start_time :
        event_status="planned" #if < 2 to 3 weeks make it pending instead of planned
    elif 'endtime' in incident  :
        end_time = datetime.strptime(incident.get('endtime', ''), "%Y-%m-%dT%H:%M:%SZ")

        if end_time < datetime.now() :
            event_status = "completed"

    properties['event_status'] = event_status

    # event status
    properties['total_num_lanes'] = 1

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
    properties['description']= incident['description']

    # creation_date
    properties['creation_date'] = incident['creationtime']

    # update_date
    properties['update_date'] = incident['updatetime']

    feature = {}
    feature['type'] = "Feature"
    feature['properties'] = properties
    feature['geometry']= geometry

    return feature






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
            # feature['properties']['feed_info_id'] = feed_info_id
            feature['properties']['data_source_id'] = data_source_id
            # feature['properties']['relationship'] = {}
            feature['properties']['relationship']['relationship_id'] = str(uuid.uuid4())
            feature['properties']['relationship']['road_event_id'] = road_event_id
            #### Relationship logic invalid. It assumes that each feature is part of the same work zone
            # if i == 0: feature['properties']['relationship']['first'] = road_event_ids
            # else: feature['properties']['relationship']['next'] = road_event_ids

            for lane in feature['properties']['lanes']:
                lane_id = str(uuid.uuid4())
                lane['lane_id'] = lane_id
                lane['road_event_id'] = road_event_id
                for lane_restriction in lane.get('restrictions', []):
                    lane_restriction_id = str(uuid.uuid4())
                    lane_restriction['lane_restriction_id'] = lane_restriction_id
                    lane_restriction['lane_id'] = lane_id
            for types_of_work in feature['properties']['types_of_work']:
                types_of_work_id = str(uuid.uuid4())
                types_of_work['types_of_work_id'] = types_of_work_id
                types_of_work['road_event_id'] = road_event_id
    return message


# Added encoding argument because of weird character at start of incidents.xml file
with open('incidents_extended.xml', encoding='utf-8-sig') as frsm:
    # Read
    xmlSTRING = frsm.read()
    icone_obj = xmltodict.parse(xmlSTRING)

    info = {}

    #### Consider whether this id needs to be hardcoded or generated
    info['feed_info_id'] = "feed_info_id"

    #### This information is required, might want to hardcode
    info['metadata'] = {}
    info['metadata']['wz_location_method'] = "wz_location_method"
    info['metadata']['lrs_type'] = "lrs_type"
    info['metadata']['location_verify_method'] = "location_verify_method"
    info['metadata']['datafeed_frequency_update'] = 86400
    info['metadata']['timestamp_metadata_update'] = "timestamp_metadata_update"
    info['metadata']['contact_name'] = "contact_name"
    info['metadata']['contact_email'] = "contact_email"
    info['metadata']['issuing_organization'] = "issuing_organization"

    wzdx = wzdx_creator(icone_obj, info)
    with open('icone_to_wzdx_test.geojson', 'w') as fwzdx:
        fwzdx.write(json.dumps(wzdx, indent=2))

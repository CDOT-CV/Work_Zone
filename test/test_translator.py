import sys
sys.path.append("..")
from translator.source_code import icone_translator
import xmltodict
import json
from jsonschema import validate
from datetime import datetime





#Unit testing code
def test_parse_incident() :
    test_var=""" <incident id="U13631595_202012160845">
    <creationtime>2020-12-16T08:45:03Z</creationtime>
    <updatetime>2020-12-16T17:18:00Z</updatetime>
    <type>CONSTRUCTION</type>
    <description>Roadwork - Lane Closed, MERGE LEFT [Trafficade, iCone]</description>
    <location>
      <direction>ONE_DIRECTION</direction>
      <polyline>34.8380671,-114.1450650,34.8380671,-114.1450650</polyline>
    </location>
    <starttime>2020-12-16T08:45:03Z</starttime>
    </incident> """

    icone_obj = xmltodict.parse(test_var)
    test_feature = icone_translator.parse_incident(icone_obj['incident'])
    valid_feature = {
      "type": "Feature",
      "properties": {
        "road_event_id": "",
        "event_type": "work-zone",
        "data_source_id": "",
        "start_date": "2020-12-16T08:45:03Z",
        "end_date": "",
        "start_date_accuracy": "estimated",
        "end_date_accuracy": "estimated",
        "beginning_accuracy": "estimated",
        "ending_accuracy": "estimated",
        "road_name": "",
        "direction": "southbound",
        "vehicle_impact": "some-lanes-closed",
        "relationship": {

        },
        "lanes": [],
        "road_number": "",
        "beginning_cross_street": "",
        "ending_cross_street": "",
        "event_status": "active",
        "total_num_lanes": 1,
        "types_of_work": [],
        "reduced_speed_limit": 25,
        "workers_present": False,
        "restrictions": [],
        "description": "Roadwork - Lane Closed, MERGE LEFT [Trafficade, iCone]",
        "creation_date": "2020-12-16T08:45:03Z",
        "update_date": "2020-12-16T17:18:00Z"
      },
      "geometry": {
        "type": "LineString",
        "coordinates": [
          [
            -114.145065,
            34.8380671
          ],
          [
            -114.145065,
            34.8380671
          ]
        ]
      }
    }

    assert test_feature == valid_feature


def test_parse_polyline() :
    test_polyline= "34.8380671,-114.1450650,34.8380671,-114.1450650"
    test_coordinates=icone_translator.parse_polyline(test_polyline)
    valid_coordinates= [
          [
            -114.145065,
            34.8380671
          ],
          [
            -114.145065,
            34.8380671
          ]
        ]
    assert  test_coordinates == valid_coordinates


def test_get_road_direction():
    test_coordinates = [
          [
            -114.145065,
            34.8380671
          ],
          [
            -114.145065,
            34.8380671
          ]
        ]
    test_direction=icone_translator.get_road_direction(test_coordinates)
    valid_direction= "southbound"

    assert test_direction==valid_direction


def test_get_vehicle_impact():
    test_description= "Roadwork - Lane Closed, MERGE LEFT [Trafficade, iCone]"
    test_vehicle_impact=icone_translator.get_vehicle_impact(test_description)
    valid_vehicle_impact = "some-lanes-closed"

    assert test_vehicle_impact==valid_vehicle_impact

def test_get_event_status():
    test_starttime_string = "2020-12-16T08:45:03Z"
    test_endtime_string=''
    test_event_status=icone_translator.get_event_status(test_starttime_string,test_endtime_string)
    valid_event_status= "active"

    assert  test_event_status==valid_event_status

def test_wzdx_creator() :
    wzdx_schema = json.loads(open('translator/source_code/wzdx_v3.0_feed.json').read())
    icone_data =open('translator/sample files/Icone Data/incidents_extended.xml').read()


    icone_obj = xmltodict.parse(icone_data)

    info={}
    info['feed_info_id'] = "feed_info_id"

    #### This information is required, might want to hardcode
    info['metadata'] = {}
    info['metadata']['wz_location_method'] = "channel-device-method"
    info['metadata']['lrs_type'] = "lrs_type"
    info['metadata']['location_verify_method'] = "location_verify_method"
    info['metadata']['datafeed_frequency_update'] = 86400
    info['metadata']['timestamp_metadata_update'] = "timestamp_metadata_update"
    info['metadata']['contact_name'] = "contact_name"
    info['metadata']['contact_email'] = "contact_email"
    info['metadata']['issuing_organization'] = "issuing_organization"
    test_wzdx=icone_translator.wzdx_creator(icone_obj,info)

    validate(instance=test_wzdx,schema=wzdx_schema)








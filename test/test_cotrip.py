import sys
from translator.source_code import translator_shared_library
sys.modules['translator_shared_library'] = translator_shared_library
from translator.source_code import cotrip_translator
import json
import re


def test_wzdx_creator() :
  cotrip_obj = {
    "rtdh_timestamp": 1615866698.393723,
    "rtdh_message_id": "dd962abd-0afa-4810-aac0-165edb834e71",
    "event": {
        "type": "Construction",
        "sub_type": "Work Zone:roadway-relocation",
        "source": {
            "id": "349611",
            "type": "Road Work",
            "sub_type": "Road Construction",
            "collection_timestamp": 1615482720
        },
        "lrs": None,
        "geometry": "LINESTRING (-104.48011 37.007645, -104.480103 37.008034, -104.480125 37.008469, -104.480202 37.008904, -104.48024 37.009048, -104.480324 37.009338, -104.482475 37.015327, -104.482712 37.015945, -104.48288 37.016335, -104.482979 37.016521, -104.483208 37.016884, -104.483467 37.01722, -104.483612 37.01738, -104.483925 37.017681, -104.484253 37.017948, -104.484772 37.018295, -104.485138 37.01849, -104.485504 37.018661, -104.485886 37.01881, -104.486473 37.019005, -104.488014 37.019493)",
        "header": {
            "description": "Road Construction - I-25 (Main St.) business loop from MP 1-2",
            "start_timestamp": 1615813200,
            "end_timestamp": 1638255600
        },
        "detail": {       
            "road_name": "I-25",
            "road_number": "I-25",
            "direction": "North"
        },
    }
}

  wzdx_re='{"road_event_feed_info": {"feed_info_id": "104d7746-688c-44ed-b195-2ee948bf9dfa","update_date": "[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z","publisher": "CDOT","contact_name": "Abinash Konersman","contact_email": "abinash\\.konersman@state\\.co\\.us","version": "3\\.0","data_sources": \\[{"data_source_id": "[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}","feed_info_id": "104d7746-688c-44ed-b195-2ee948bf9dfa","organization_name": "COtrip","contact_name": "Abinash Konersman","contact_email": "abinash\\.konersman@state\\.co\\.us","update_date": "[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z","location_method": "channel-device-method","lrs_type": "lrs_type"}\\]},"type": "FeatureCollection","features": \\[{"type": "Feature","properties": {"road_event_id": "[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}","event_type": "work-zone","data_source_id": "[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}","start_date": "2021-03-15T13:00:00Z","end_date": "2021-11-30T07:00:00Z","start_date_accuracy": "estimated","end_date_accuracy": "estimated","beginning_accuracy": "estimated","ending_accuracy": "estimated","road_name": "I-25","direction": "northbound","vehicle_impact": "unknown","relationship": {"relationship_id": "[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}","road_event_id": "[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}"},"lanes": \\[\\],"beginning_cross_street": "","ending_cross_street": "","event_status": "active","types_of_work": \\[\\],"workers_present": false,"restrictions": \\[\\],"description": "Road Construction - I-25 (Main St.) business loop from MP 1-2","creation_date": "2021-03-11T17:12:00Z","update_date": "2021-03-16T03:51:38Z"},"geometry": {"type": "LineString","coordinates": \\[\\\\[-104\\.48011,37\\.007645\\],\\[-104\\.480103,37\\.008034\\],\\[-104\\.480125,37\\.008469\\],\\[-104\\.480202,37\\.008904\\],\\[-104\\.48024,37\\.009048\\],\\[-104\\.480324,37\\.009338\\],\\[-104\\.482475,37\\.015327\\],\\[-104\\.482712,37\\.015945\\],\\[-104\\.48288,37\\.016335\\],\\[-104\\.482979,37\\.016521\\],\\[-104\\.483208,37\\.016884\\],\\[-104\\.483467,37\\.01722\\],\\[-104\\.483612,37\\.01738\\],\\[-104\\.483925,37\\.017681\\],\\[-104\\.484253,37\\.017948\\],\\[-104\\.484772,37\\.018295\\],\\[-104\\.485138,37\\.01849\\],\\[-104\\.485504,37\\.018661\\],\\[-104\\.485886,37\\.01881\\],\\[-104\\.486473,37\\.019005\\],\\[-104\\.488014,37\\.019493\\]\\]}}\\]}'
  test_wzdx = cotrip_translator.wzdx_creator(cotrip_obj)
  print(json.dumps(test_wzdx))
  assert re.match(wzdx_re,json.dumps(test_wzdx)) != None





# def test_wzdx_creator_empty_icone_object() :
#   icone_obj = None
#   test_wzdx = icone_translator.wzdx_creator(icone_obj)
#   assert test_wzdx == None

# def test_wzdx_creator_no_info_object() :
#   icone_obj = {'incidents': {'incident': [{
#     '@id': 'U13631595_202012160845',
#     'updatetime': '2020-12-16T17:18:00Z',
#     'starttime': '2020-12-07T14:18:00Z',
#     'creationtime': '2020-12-13T14:18:00Z', 
#     'description': 'Road constructions are going on',
#     'location': {
#       'polyline': '34.8380671,-114.1450650,34.8380671,-114.1450650',
#       'street': 'I-70 N'
#     }
#   }]}}

#   wzdx_re='{"road_event_feed_info": {"feed_info_id": "104d7746-688c-44ed-b195-2ee948bf9dfa", "update_date": "[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", "publisher": "CDOT", "contact_name": "Abinash Konersman", "contact_email": "abinash\\.konersman@state\\.co\\.us", "version": "3\\.0", "data_sources": \\[{"data_source_id": "[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}", "feed_info_id": "104d7746-688c-44ed-b195-2ee948bf9dfa", "organization_name": "iCone", "contact_name": "Abinash Konersman", "contact_email": "abinash\\.konersman@state\\.co\\.us", "update_date": "[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", "location_method": "channel-device-method", "lrs_type": "lrs_type"}\\]}, "type": "FeatureCollection", "features": \\[{"type": "Feature", "properties": {"road_event_id": "[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}", "event_type": "work-zone", "data_source_id": "[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}", "start_date": "2020-12-07T14:18:00Z", "end_date": "", "start_date_accuracy": "estimated", "end_date_accuracy": "estimated", "beginning_accuracy": "estimated", "ending_accuracy": "estimated", "road_name": "I-70 N", "direction": "northbound", "vehicle_impact": "all-lanes-open", "relationship": {"relationship_id": "[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}", "road_event_id": "[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}"}, "lanes": \\[\\], "road_number": "", "beginning_cross_street": "", "ending_cross_street": "", "event_status": "active", "types_of_work": \\[\\], "reduced_speed_limit": 25, "workers_present": false, "restrictions": \\[\\], "description": "Road constructions are going on", "creation_date": "2020-12-13T14:18:00Z", "update_date": "2020-12-16T17:18:00Z"}, "geometry": {"type": "LineString", "coordinates": \\[\\[-114\\.145065, 34\\.8380671\\], \\[-114\\.145065, 34\\.8380671\\]\\]}}\\]}'
#   test_wzdx = icone_translator.wzdx_creator(icone_obj)
#   assert re.match(wzdx_re,json.dumps(test_wzdx)) != None

# def test_wzdx_creator_no_incidents() :
#   icone_obj = {'incidents': {'@timestamp': '2020-12-16T17:18:00Z'}}
#   test_wzdx = icone_translator.wzdx_creator(icone_obj)
#   assert test_wzdx == None
  
# def test_wzdx_creator_invalid_incidents_no_description() :
#   icone_obj = {'incidents': {'incident': [{
#     '@id': 'U13631595_202012160845',
#     'updatetime': '2020-12-16T17:18:00Z',
#     'starttime': '2020-12-07T14:18:00Z',
#     'creationtime': '2020-12-13T14:18:00Z', 
#     'location': {
#       'polyline': '34.8380671,-114.1450650,34.8380671,-114.1450650',
#       'street': 'I-70 N'
#     }
#   }]}} 
#   test_wzdx = icone_translator.wzdx_creator(icone_obj)
#   assert test_wzdx == None

# def test_wzdx_creator_invalid_info_object() :
#   icone_obj = {'incidents': {'incident': [{
#     '@id': 'U13631595_202012160845',
#     'updatetime': '2020-12-16T17:18:00Z',
#     'starttime': '2020-12-07T14:18:00Z',
#     'creationtime': '2020-12-13T14:18:00Z', 
#     'location': {
#       'polyline': '34.8380671,-114.1450650,34.8380671,-114.1450650',
#       'street': 'I-70 N'
#     }
#   }]}}

#   test_invalid_info_object =  {
#     'feed_info_id': "104d7746-e948bf9dfa",
#     'metadata':{
#       'wz_location_method': "channel-device-method",
#       'lrs_type': "lrs_type",
#       'contact_name':"Abinash Konersman",
#       'contact_email': "abinash.konersman@state.co.us",
#       'issuing_organization': "iCone",
#       }
#     }
  
#   test_wzdx = icone_translator.wzdx_creator(icone_obj, test_invalid_info_object)
#   assert test_wzdx == None

# def test_wzdx_creator_valid_and_invalid() :
#   icone_obj = {'incidents': {'incident': [{
#     '@id': 'U13631595_202012160845',
#     'updatetime': '2020-12-16T17:18:00Z',
#     'starttime': '2020-12-07T14:18:00Z',
#     'creationtime': '2020-12-13T14:18:00Z', 
#     'description': 'Road constructions are going on',
#     'location': {
#       'polyline': '34.8380671,-114.1450650,34.8380671,-114.1450650',
#       'street': 'I-70 N'
#     }
#   },{
#     '@id': 'U13631595_202012160845',
#     'updatetime': '2020-12-16T17:18:00Z',
#     'starttime': '2020-12-07T14:18:00Z',
#     'creationtime': '2020-12-13T14:18:00Z', 
#     'location': {
#       'polyline': '34.8380671,-114.1450650,34.8380671,-114.1450650',
#       'street': 'I-70 N'
#     }
#   }]}}

#   wzdx_re='{"road_event_feed_info": {"feed_info_id": "104d7746-688c-44ed-b195-2ee948bf9dfa", "update_date": "[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", "publisher": "CDOT", "contact_name": "Abinash Konersman", "contact_email": "abinash\\.konersman@state\\.co\\.us", "version": "3\\.0", "data_sources": \\[{"data_source_id": "[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}", "feed_info_id": "104d7746-688c-44ed-b195-2ee948bf9dfa", "organization_name": "iCone", "contact_name": "Abinash Konersman", "contact_email": "abinash\\.konersman@state\\.co\\.us", "update_date": "[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", "location_method": "channel-device-method", "lrs_type": "lrs_type"}\\]}, "type": "FeatureCollection", "features": \\[{"type": "Feature", "properties": {"road_event_id": "[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}", "event_type": "work-zone", "data_source_id": "[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}", "start_date": "2020-12-07T14:18:00Z", "end_date": "", "start_date_accuracy": "estimated", "end_date_accuracy": "estimated", "beginning_accuracy": "estimated", "ending_accuracy": "estimated", "road_name": "I-70 N", "direction": "northbound", "vehicle_impact": "all-lanes-open", "relationship": {"relationship_id": "[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}", "road_event_id": "[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}"}, "lanes": \\[\\], "road_number": "", "beginning_cross_street": "", "ending_cross_street": "", "event_status": "active", "types_of_work": \\[\\], "reduced_speed_limit": 25, "workers_present": false, "restrictions": \\[\\], "description": "Road constructions are going on", "creation_date": "2020-12-13T14:18:00Z", "update_date": "2020-12-16T17:18:00Z"}, "geometry": {"type": "LineString", "coordinates": \\[\\[-114\\.145065, 34\\.8380671\\], \\[-114\\.145065, 34\\.8380671\\]\\]}}\\]}'
#   test_wzdx = icone_translator.wzdx_creator(icone_obj, icone_translator.initialize_info())
#   assert re.match(wzdx_re,json.dumps(test_wzdx)) != None

# #--------------------------------------------------------------------------------Unit test for parse_polyline function--------------------------------------------------------------------------------
# def test_parse_polyline_valid_data() :
#     test_polyline= "34.8380671,-114.1450650,34.8380671,-114.1450650"
#     test_coordinates=icone_translator.parse_polyline(test_polyline)
#     valid_coordinates= [
#           [
#             -114.145065,
#             34.8380671
#           ],
#           [
#             -114.145065,
#             34.8380671
#           ]
#         ]
#     assert  test_coordinates == valid_coordinates

# def test_parse_polyline_null_parameter() :
#     test_polyline= None
#     test_coordinates=icone_translator.parse_polyline(test_polyline)
#     expected_coordinates= None
#     assert  test_coordinates == expected_coordinates

# def test_parse_polyline_invalid_data() :
#     test_polyline= 'invalid' 
#     test_coordinates=icone_translator.parse_polyline(test_polyline)
#     expected_coordinates= []
#     assert  test_coordinates == expected_coordinates

# def test_parse_polyline_invalid_coordinates():
#     test_polyline = 'a,b,c,d'
#     test_coordinates = icone_translator.parse_polyline(test_polyline)
#     expected_coordinates= []
#     assert  test_coordinates == expected_coordinates


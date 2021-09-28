import os
import uuid
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import time_machine
import xmltodict
from translator import icone_translator

# Unit testing code for icone_translator.py
# --------------------------------------------------------------------------------Unit test for parse_incident function--------------------------------------------------------------------------------


def test_parse_incident_from_street_success():
    test_var = """ <incident id="1245">
    <creationtime>2019-11-05T01:22:20Z</creationtime>
    <updatetime>2020-08-21T15:52:02Z</updatetime>
    <type>CONSTRUCTION</type>
    <description>19-1245: Roadwork between MP 40 and MP 48</description>
    <location>
      <street>I-75 N</street>
      <direction>ONE_DIRECTION</direction>
      <polyline>37.1571990,-84.1128540,37.1686478,-84.1238971,37.1913000,-84.1458610,37.2093480,-84.1752970,37.2168370,-84.2013030</polyline>
    </location>
    <starttime>2020-02-14T17:08:16Z</starttime>
    </incident>  """

    icone_obj = xmltodict.parse(test_var)
    test_feature = icone_translator.parse_incident(icone_obj['incident'])
    expected_feature = {
        "type": "Feature",
        "properties": {
            "road_event_id": "",
            "event_type": "work-zone",
            "data_source_id": "",
            "start_date": "2020-02-14T17:08:16Z",
            "end_date": "",
            "start_date_accuracy": "estimated",
            "end_date_accuracy": "estimated",
            "beginning_accuracy": "estimated",
            "ending_accuracy": "estimated",
            "road_names": ["I-75 N"],
            "direction": "northbound",
            "vehicle_impact": "all-lanes-open",
            "relationship": {},
            "lanes": [],
            "beginning_cross_street": "",
            "ending_cross_street": "",
            "event_status": "active",
            "types_of_work": [],
            "restrictions": [],
            "description": "19-1245: Roadwork between MP 40 and MP 48",
            "creation_date": "2019-11-05T01:22:20Z",
            "update_date": "2020-08-21T15:52:02Z"
        },
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [
                    -84.112854,
                    37.157199
                ],
                [
                    -84.1238971,
                    37.1686478
                ],
                [
                    -84.145861,
                    37.1913
                ],
                [
                    -84.175297,
                    37.209348
                ],
                [
                    -84.201303,
                    37.216837
                ]
            ]
        }
    }
    assert test_feature == expected_feature


def test_parse_incident_from_coordinates_success():
    test_var = """ <incident id="1245">
    <creationtime>2019-11-05T01:22:20Z</creationtime>
    <updatetime>2020-08-21T15:52:02Z</updatetime>
    <type>CONSTRUCTION</type>
    <description>19-1245: Roadwork between MP 40 and MP 48</description>
    <location>
      <street>I-75</street>
      <direction>ONE_DIRECTION</direction>
      <polyline>37.1571990,-84.1128540,37.1686478,-84.1238971,37.1913000,-84.1458610,37.2093480,-84.1752970,37.2168370,-84.2013030</polyline>
    </location>
    <starttime>2020-02-14T17:08:16Z</starttime>
    </incident>  """

    icone_obj = xmltodict.parse(test_var)
    test_feature = icone_translator.parse_incident(icone_obj['incident'])
    expected_feature = {
        "type": "Feature",
        "properties": {
            "road_event_id": "",
            "event_type": "work-zone",
            "data_source_id": "",
            "start_date": "2020-02-14T17:08:16Z",
            "end_date": "",
            "start_date_accuracy": "estimated",
            "end_date_accuracy": "estimated",
            "beginning_accuracy": "estimated",
            "ending_accuracy": "estimated",
            "road_names": ["I-75"],
            "direction": "westbound",
            "vehicle_impact": "all-lanes-open",
            "relationship": {},
            "lanes": [],
            "beginning_cross_street": "",
            "ending_cross_street": "",
            "event_status": "active",
            "types_of_work": [],
            "restrictions": [],
            "description": "19-1245: Roadwork between MP 40 and MP 48",
            "creation_date": "2019-11-05T01:22:20Z",
            "update_date": "2020-08-21T15:52:02Z"
        },
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [
                    -84.112854,
                    37.157199
                ],
                [
                    -84.1238971,
                    37.1686478
                ],
                [
                    -84.145861,
                    37.1913
                ],
                [
                    -84.175297,
                    37.209348
                ],
                [
                    -84.201303,
                    37.216837
                ]
            ]
        }
    }
    assert test_feature == expected_feature


def test_parse_incident_no_data():
    test_feature = icone_translator.parse_incident(None)
    expected_feature = None
    assert test_feature == expected_feature


def test_parse_incident_invalid_data():
    test_var = 'a,b,c,d'
    callback = MagicMock()
    test_feature = icone_translator.parse_incident(
        test_var, callback_function=callback)
    assert callback.called and test_feature == None


def test_parse_incident_no_direction():
    test_var = """ <incident id="U13631595_202012160845">
           <creationtime>2020-12-16T08:45:03Z</creationtime>
           <updatetime>2020-12-16T17:18:00Z</updatetime>
           <type>CONSTRUCTION</type>
           <description>Roadwork - Lane Closed, MERGE LEFT [Trafficade, iCone]</description>
           <location>
           <street>I-75</street>
             <direction>ONE_DIRECTION</direction>
             <polyline>34.8380671,-114.1450650,34.8380671,-114.1450650</polyline>
           </location>
           <starttime>2020-12-16T08:45:03Z</starttime>
           </incident> """

    icone_obj = xmltodict.parse(test_var)
    test_feature = icone_translator.parse_incident(icone_obj['incident'])
    assert test_feature == None


# --------------------------------------------------------------------------------Unit test for parse_polyline function--------------------------------------------------------------------------------
def test_parse_polyline_valid_data():
    test_polyline = "34.8380671,-114.1450650,34.8380671,-114.1450650"
    test_coordinates = icone_translator.parse_polyline(test_polyline)
    valid_coordinates = [
        [
            -114.145065,
            34.8380671
        ],
        [
            -114.145065,
            34.8380671
        ]
    ]
    assert test_coordinates == valid_coordinates


def test_parse_polyline_null_parameter():
    test_polyline = None
    test_coordinates = icone_translator.parse_polyline(test_polyline)
    expected_coordinates = None
    assert test_coordinates == expected_coordinates


def test_parse_polyline_invalid_data():
    test_polyline = 'invalid'
    test_coordinates = icone_translator.parse_polyline(test_polyline)
    expected_coordinates = []
    assert test_coordinates == expected_coordinates


def test_parse_polyline_invalid_coordinates():
    test_polyline = 'a,b,c,d'
    test_coordinates = icone_translator.parse_polyline(test_polyline)
    expected_coordinates = []
    assert test_coordinates == expected_coordinates


# --------------------------------------------------------------------------------Unit test for validate_incident function--------------------------------------------------------------------------------
def test_validate_incident_valid_data():
    test_valid_output = {
        '@id': 'U13631595_202012160845',
        'updatetime': '2020-12-16T17:18:00Z',
        'starttime': '2020-12-07T14:18:00Z',
        'description': 'Road constructions are going on',
        'creationtime': '2020-12-13T14:18:00Z',
        'location': {
            'polyline': '34.8380671,-114.1450650,34.8380671,-114.1450650',
            'street': 'I-70 N'
        }
    }
    assert icone_translator.validate_incident(test_valid_output) == True


def test_validate_incident_missing_required_field_description():
    test_valid_output = {
        '@id': 'U13631595_202012160845',
        'updatetime': '2020-12-16T17:18:00Z',
        'starttime': '2020-12-07T14:18:00Z',
        'creationtime': '2020-12-13T14:18:00Z',
        'location': {
            'polyline': '34.8380671,-114.1450650,34.8380671,-114.1450650'
        }
    }
    assert icone_translator.validate_incident(test_valid_output) == False


def test_validate_incident_invalid_start_time():
    test_valid_output = {
        '@id': 'U13631595_202012160845',
        'updatetime': '2020-12-16T17:18:00Z',
        'starttime': 'dsafsaf',
        'description': 'Road constructions are going on',
        'creationtime': '2020-12-13T14:18:00Z',
        'location': {
            'polyline': '34.8380671,-114.1450650,34.8380671,-114.1450650',
            'street': 'I-70 N'
        }
    }
    assert icone_translator.validate_incident(test_valid_output) == False


def test_validate_incident_invalid():
    test_valid_output = 'invalid output'
    assert icone_translator.validate_incident(test_valid_output) == False


def test_validate_incident_no_data():
    test_valid_output = None
    assert icone_translator.validate_incident(test_valid_output) == False


# --------------------------------------------------------------------------------Unit test for get_vehicle_impact function--------------------------------------------------------------------------------
def test_get_vehicle_impact_some_lanes_closed():
    test_description = "Roadwork - Lane Closed, MERGE LEFT [Trafficade, iCone]"
    test_vehicle_impact = icone_translator.get_vehicle_impact(test_description)
    expected_vehicle_impact = "some-lanes-closed"
    assert test_vehicle_impact == expected_vehicle_impact


def test_get_vehicle_impact_all_lanes_open():
    test_description = 'Road Ranger Emergency Personnel On-Scene. Move over - Caution [DBi, iCone]'
    test_vehicle_impact = icone_translator.get_vehicle_impact(test_description)
    expected_vehicle_impact = "all-lanes-open"
    assert test_vehicle_impact == expected_vehicle_impact


# --------------------------------------------------------------------------------Unit test for wzdx_creator function--------------------------------------------------------------------------------
@patch.dict(os.environ, {
    'contact_name': 'Ashley Nylen',
    'contact_email': 'ashley.nylen@state.co.us',
    'issuing_organization': 'CDOT'
})
@patch('uuid.uuid4')
def test_wzdx_creator(mockuuid):
    uuid.uuid4 = Mock()
    uuid.uuid4.side_effect = 'we234de'
    icone_obj = {'incidents': {'incident': [{
        '@id': 'U13631595_202012160845',
        'updatetime': '2020-12-16T17:18:00Z',
        'starttime': '2020-12-07T14:18:00Z',
        'creationtime': '2020-12-13T14:18:00Z',
        'description': 'Road constructions are going on',
        'location': {
            'polyline': '34.8380671,-114.1450650,34.8380671,-114.1450650',
            'street': 'I-70 N'
        }
    }]}}

    expected_wzdx = {
        'road_event_feed_info': {
            'feed_info_id': '104d7746-688c-44ed-b195-2ee948bf9dfa',
            'update_date': '2021-04-13T00:00:00Z',
            'publisher': 'CDOT',
            'contact_name': 'Ashley Nylen',
            'contact_email': 'ashley.nylen@state.co.us',
            'version': '3.1',
            'license': 'https://creativecommons.org/publicdomain/zero/1.0/',
            'data_sources': [{
                'data_source_id': 'w',
                'feed_info_id': '104d7746-688c-44ed-b195-2ee948bf9dfa',
                'organization_name': 'CDOT',
                'contact_name': 'Ashley Nylen',
                'contact_email': 'ashley.nylen@state.co.us',
                'update_date': '2021-04-13T00:00:00Z',
                'location_method': 'channel-device-method',
                'lrs_type': 'lrs_type'}]},
        'type': 'FeatureCollection',
        'features': [{
            'type': 'Feature',
            'properties': {

                'road_event_id': '2',
                'event_type': 'work-zone',
                'data_source_id': 'w',
                'start_date': '2020-12-07T14:18:00Z',
                'end_date': '',
                'start_date_accuracy': 'estimated',
                'end_date_accuracy': 'estimated',
                'beginning_accuracy': 'estimated',
                'ending_accuracy': 'estimated',
                'road_names': ['I-70 N'],
                'direction': 'northbound',
                'vehicle_impact': 'all-lanes-open',
                'relationship': {},
                'lanes': [],
                'beginning_cross_street': '',
                'ending_cross_street': '',
                'event_status': 'active',
                'types_of_work': [],
                'restrictions': [],
                'description': 'Road constructions are going on',
                'creation_date': '2020-12-13T14:18:00Z',
                'update_date': '2020-12-16T17:18:00Z'},
            'geometry': {
                'type': 'LineString',
                'coordinates': [[-114.145065, 34.8380671], [-114.145065, 34.8380671]]}}]}

    with time_machine.travel(datetime(2021, 4, 13, 0, 0, 0)):
        test_wzdx = icone_translator.wzdx_creator(icone_obj)

    assert expected_wzdx == test_wzdx


def test_wzdx_creator_empty_icone_object():
    icone_obj = None
    test_wzdx = icone_translator.wzdx_creator(icone_obj)
    assert test_wzdx == None


@patch.dict(os.environ, {
    'contact_name': 'Ashley Nylen',
    'contact_email': 'ashley.nylen@state.co.us',
    'issuing_organization': 'CDOT'
})
@patch('uuid.uuid4')
def test_wzdx_creator_no_info_object(mockuuid):
    uuid.uuid4 = Mock()
    uuid.uuid4.side_effect = 'we234de'
    icone_obj = {'incidents': {'incident': [{
        '@id': 'U13631595_202012160845',
        'updatetime': '2020-12-16T17:18:00Z',
        'starttime': '2020-12-07T14:18:00Z',
        'creationtime': '2020-12-13T14:18:00Z',
        'description': 'Road constructions are going on',
        'location': {
            'polyline': '34.8380671,-114.1450650,34.8380671,-114.1450650',
            'street': 'I-70 N'
        }
    }]}}
    expected_wzdx = {
        'road_event_feed_info': {
            'feed_info_id': '104d7746-688c-44ed-b195-2ee948bf9dfa',
            'update_date': '2021-04-13T00:00:00Z',
            'publisher': 'CDOT',
            'contact_name': 'Ashley Nylen',
            'contact_email': 'ashley.nylen@state.co.us',
            'version': '3.1',
            'license': 'https://creativecommons.org/publicdomain/zero/1.0/',
            'data_sources': [{
                'data_source_id': 'w',
                'feed_info_id': '104d7746-688c-44ed-b195-2ee948bf9dfa',
                'organization_name': 'CDOT',
                'contact_name': 'Ashley Nylen',
                'contact_email': 'ashley.nylen@state.co.us',
                'update_date': '2021-04-13T00:00:00Z',
                'location_method': 'channel-device-method',
                'lrs_type': 'lrs_type'}]},
        'type': 'FeatureCollection',
        'features': [{
            'type': 'Feature',
            'properties': {

                'road_event_id': '2',
                'event_type': 'work-zone',
                'data_source_id': 'w',
                'start_date': '2020-12-07T14:18:00Z',
                'end_date': '',
                'start_date_accuracy': 'estimated',
                'end_date_accuracy': 'estimated',
                'beginning_accuracy': 'estimated',
                'ending_accuracy': 'estimated',
                'road_names': ['I-70 N'],
                'direction': 'northbound',
                'vehicle_impact': 'all-lanes-open',
                'relationship': {},
                'lanes': [],
                'beginning_cross_street': '',
                'ending_cross_street': '',
                'event_status': 'active',
                'types_of_work': [],
                'restrictions': [],
                'description': 'Road constructions are going on',
                'creation_date': '2020-12-13T14:18:00Z',
                'update_date': '2020-12-16T17:18:00Z'},
            'geometry': {
                'type': 'LineString',
                'coordinates': [[-114.145065, 34.8380671], [-114.145065, 34.8380671]]}}]}
    with time_machine.travel(datetime(2021, 4, 13, 0, 0, 0)):
        test_wzdx = icone_translator.wzdx_creator(icone_obj)
    assert expected_wzdx == test_wzdx


def test_wzdx_creator_no_incidents():
    icone_obj = {'incidents': {'@timestamp': '2020-12-16T17:18:00Z'}}
    test_wzdx = icone_translator.wzdx_creator(icone_obj)
    assert test_wzdx == None


@patch.dict(os.environ, {
    'contact_name': 'Ashley Nylen',
    'contact_email': 'ashley.nylen@state.co.us',
    'issuing_organization': 'CDOT'
})
def test_wzdx_creator_invalid_incidents_no_description():
    icone_obj = {'incidents': {'incident': [{
        '@id': 'U13631595_202012160845',
        'updatetime': '2020-12-16T17:18:00Z',
        'starttime': '2020-12-07T14:18:00Z',
        'creationtime': '2020-12-13T14:18:00Z',
        'location': {
            'polyline': '34.8380671,-114.1450650,34.8380671,-114.1450650',
            'street': 'I-70 N'
        }
    }]}}
    test_wzdx = icone_translator.wzdx_creator(icone_obj)
    assert test_wzdx == None


def test_wzdx_creator_invalid_info_object():
    icone_obj = {'incidents': {'incident': [{
        '@id': 'U13631595_202012160845',
        'updatetime': '2020-12-16T17:18:00Z',
        'starttime': '2020-12-07T14:18:00Z',
        'creationtime': '2020-12-13T14:18:00Z',
        'location': {
            'polyline': '34.8380671,-114.1450650,34.8380671,-114.1450650',
            'street': 'I-70 N'
        }
    }]}}

    test_invalid_info_object = {
        'feed_info_id': "104d7746-e948bf9dfa",
        'metadata': {
            'wz_location_method': "channel-device-method",
            'lrs_type': "lrs_type",
            'contact_name': "Ashley Nylen",
            'contact_email': "ashley.nylen@state.co.us",
            'issuing_organization': "iCone",
        }
    }

    test_wzdx = icone_translator.wzdx_creator(
        icone_obj, test_invalid_info_object)
    assert test_wzdx == None


@patch.dict(os.environ, {
    'contact_name': 'Ashley Nylen',
    'contact_email': 'ashley.nylen@state.co.us',
    'issuing_organization': 'CDOT'
})
@patch('uuid.uuid4')
def test_wzdx_creator_valid_and_invalid(mockuuid):
    uuid.uuid4 = Mock()
    uuid.uuid4.side_effect = 'we234de'
    icone_obj = {'incidents': {'incident': [{
        '@id': 'U13631595_202012160845',
        'updatetime': '2020-12-16T17:18:00Z',
        'starttime': '2020-12-07T14:18:00Z',
        'creationtime': '2020-12-13T14:18:00Z',
        'description': 'Road constructions are going on',
        'location': {
            'polyline': '34.8380671,-114.1450650,34.8380671,-114.1450650',
            'street': 'I-70 N'
        }
    }, {
        '@id': 'U13631595_202012160845',
        'updatetime': '2020-12-16T17:18:00Z',
        'starttime': '2020-12-07T14:18:00Z',
        'creationtime': '2020-12-13T14:18:00Z',
        'location': {
            'polyline': '34.8380671,-114.1450650,34.8380671,-114.1450650',
            'street': 'I-70 N'
        }
    }]}}

    expected_wzdx = {'road_event_feed_info': {
        'feed_info_id': '104d7746-688c-44ed-b195-2ee948bf9dfa',
        'update_date': '2021-04-13T00:00:00Z',
        'publisher': 'CDOT',
        'contact_name':
        'Ashley Nylen',
        'contact_email':
        'ashley.nylen@state.co.us',
        'version': '3.1',
        'license': 'https://creativecommons.org/publicdomain/zero/1.0/',
        'data_sources': [
            {'data_source_id': 'w',
             'feed_info_id': '104d7746-688c-44ed-b195-2ee948bf9dfa',
             'organization_name': 'CDOT',
             'contact_name': 'Ashley Nylen',
             'contact_email': 'ashley.nylen@state.co.us',
             'update_date': '2021-04-13T00:00:00Z',
             'location_method': 'channel-device-method',
             'lrs_type': 'lrs_type'}
        ]
    },
        'type': 'FeatureCollection',
        'features': [
            {'type': 'Feature', 'properties': {
                'road_event_id': '2',
                'event_type':
                'work-zone',
                'data_source_id': 'w',
                'start_date': '2020-12-07T14:18:00Z',
                'end_date': '',
                'start_date_accuracy': 'estimated',
                'end_date_accuracy': 'estimated',
                'beginning_accuracy': 'estimated',
                'ending_accuracy': 'estimated',
                'road_names': ['I-70 N'],
                'direction': 'northbound',
                'vehicle_impact': 'all-lanes-open',
                'relationship': {}, 'lanes': [],
                'beginning_cross_street': '',
                'ending_cross_street': '',
                'event_status': 'active',
                'types_of_work': [],
                'restrictions': [],
                'description': 'Road constructions are going on',
                'creation_date': '2020-12-13T14:18:00Z',
                'update_date': '2020-12-16T17:18:00Z'},
                'geometry': {
                    'type': 'LineString',
                    'coordinates': [
                        [-114.145065, 34.8380671],
                        [-114.145065, 34.8380671]
                    ]
            }
            }
    ]
    }

    with time_machine.travel(datetime(2021, 4, 13, 0, 0, 0)):
        test_wzdx = icone_translator.wzdx_creator(icone_obj)
    assert expected_wzdx == test_wzdx
# --------------------------------------------------------------------------------unit test for parse_direction_from_street_name function--------------------------------------------------------------------------------


def test_parse_direction_from_street_name_southbound():
    test_road_name = 'I-75 S'
    output_direction = icone_translator.parse_direction_from_street_name(
        test_road_name)
    assert output_direction == 'southbound'


def test_parse_direction_from_street_name_northbound():
    test_road_name = 'I-75 NB'
    output_direction = icone_translator.parse_direction_from_street_name(
        test_road_name)
    assert output_direction == 'northbound'


def test_parse_direction_from_street_name_eastbound():
    test_road_name = 'I-75 EB'
    output_direction = icone_translator.parse_direction_from_street_name(
        test_road_name)
    assert output_direction == 'eastbound'


def test_parse_direction_from_street_name_westbound():
    test_road_name = 'I-75 W'
    output_direction = icone_translator.parse_direction_from_street_name(
        test_road_name)
    assert output_direction == 'westbound'

# --------------------------------------------------------------------------------unit test for parse_icone_sensor function--------------------------------------------------------------------------------


def test_parse_icone_sensor():
    valid_description = {'type': 'iCone', 'id': '#4', 'location': [41.3883260, -81.9707500], 'radar': {
        'average_speed': 63.52, 'std_dev_speed': 7.32, 'timestamp': '2020-08-21T15:55:00Z'}}
    test_sensor = {"@type": "iCone", "@id": "#4", "@latitude": "41.3883260", "@longitude": "-81.9707500", "radar": [{"@devID": "1645", "@intervalEnd": "2020-08-21T15:40:00Z", "@latitude": "41.3883258", "@longitude": "-81.9707325", "@numReads": "22", "@avgSpeed": "64.32", "@stDevSpeed": "6.1080"}, {"@devID": "1645", "@intervalEnd": "2020-08-21T15:45:00Z", "@latitude": "41.3883258", "@longitude": "-81.9707325", "@numReads": "43", "@avgSpeed": "63.66", "@stDevSpeed": "5.1282"}, {
        "@devID": "1645", "@intervalEnd": "2020-08-21T15:50:00Z", "@latitude": "41.3883258", "@longitude": "-81.9707325", "@numReads": "59", "@avgSpeed": "63.52", "@stDevSpeed": "7.9526"}, {"@devID": "1645", "@intervalEnd": "2020-08-21T15:55:00Z", "@latitude": "41.3883258", "@longitude": "-81.9707325", "@numReads": "18", "@avgSpeed": "62.22", "@stDevSpeed": "11.9760"}]}
    output_description = icone_translator.parse_icone_sensor(test_sensor)
    assert output_description == valid_description

    valid_description = {'type': 'iCone', 'id': '#4', 'location': [41.3883260, -81.9707500],
                         'radar': {'average_speed': 64.32, 'std_dev_speed': 6.11, 'timestamp': '2020-08-21T15:40:00Z'}}
    test_sensor = {"@type": "iCone", "@id": "#4", "@latitude": "41.3883260", "@longitude": "-81.9707500", "radar": [
        {"@devID": "1645", "@intervalEnd": "2020-08-21T15:40:00Z", "@latitude": "41.3883258",
         "@longitude": "-81.9707325", "@numReads": "22", "@avgSpeed": "64.32", "@stDevSpeed": "6.1080"}]}
    output_description = icone_translator.parse_icone_sensor(test_sensor)
    assert output_description == valid_description


# --------------------------------------------------------------------------------unit test for parse_pcms_sensor function--------------------------------------------------------------------------------
def test_parse_pcms_sensor():
    valid_description = {'type': 'PCMS', 'id': 'I-75 NB - MP 48.3', 'timestamp': '2020-08-21T15:48:25Z',
                         'location': [37.2182000, -84.2027000], 'messages': [' ROADWORK / 5 MILES / AHEAD']}
    test_sensor = {'@type': 'PCMS', '@id': 'I-75 NB - MP 48.3', '@latitude': '37.2182000', '@longitude': '-84.2027000', 'message': {
        '@verified': '2020-08-21T15:48:25Z', '@latitude': '37.2178100', '@longitude': '-84.2024390', '@text': ' ROADWORK / 5 MILES / AHEAD'}}
    output_description = icone_translator.parse_pcms_sensor(test_sensor)
    assert output_description == valid_description


# --------------------------------------------------------------------------------unit test for create_description function--------------------------------------------------------------------------------
def test_create_description():
    test_description = "19-1245: Roadwork between MP 48 and MP 40\n sensors: \n{\n  \"type\": \"iCone\",\n  \"id\": \"SB 1 - MP 40.8\",\n  \"location\": [\n    37.147808,\n    -84.111588\n  ]\n}\n{\n  \"type\": \"iCone\",\n  \"id\": \"SB 2 - MP 42.1\",\n  \"location\": [\n    37.166345,\n    -84.121425\n  ],\n  \"radar\": {\n    \"average_speed\": 67.63,\n    \"std_dev_speed\": 6.44,\n    \"timestamp\": \"2020-08-21T15:55:00Z\"\n  }\n}\n{\n  \"type\": \"iCone\",\n  \"id\": \"SB 3 - MP 44.0\",\n  \"location\": [\n    37.185815,\n    -84.140482\n  ],\n  \"radar\": {\n    \"average_speed\": 65.5,\n    \"std_dev_speed\": 6.59,\n    \"timestamp\": \"2020-08-21T15:50:00Z\"\n  }\n}\n{\n  \"type\": \"iCone\",\n  \"id\": \"SB 4 - MP 45.7\",\n  \"location\": [\n    37.201223,\n    -84.157346\n  ],\n  \"radar\": {\n    \"average_speed\": 65.94,\n    \"std_dev_speed\": 7.49,\n    \"timestamp\": \"2020-08-21T15:55:00Z\"\n  }\n}\n{\n  \"type\": \"iCone\",\n  \"id\": \"SB 5 - MP 47.5\",\n  \"location\": [\n    37.20667,\n    -84.169129\n  ],\n  \"radar\": {\n    \"average_speed\": 67.0,\n    \"std_dev_speed\": 6.21,\n    \"timestamp\": \"2020-08-21T15:45:00Z\"\n  }\n}\n{\n  \"type\": \"iCone\",\n  \"id\": \"SB 6 - MP 48.5\",\n  \"location\": [\n    37.219313,\n    -84.20466\n  ]\n}\n{\n  \"type\": \"iCone\",\n  \"id\": \"SB 7 - MP 49.5\",\n  \"location\": [\n    37.2299854,\n    -84.2221508\n  ],\n  \"radar\": {\n    \"average_speed\": 63.03,\n    \"std_dev_speed\": 9.19,\n    \"timestamp\": \"2020-08-21T15:55:00Z\"\n  }\n}\n{\n  \"type\": \"iCone\",\n  \"id\": \"SB 8 - MP 50.5\",\n  \"location\": [\n    37.237888,\n    -84.235918\n  ]\n}\n displays: \n{\n  \"type\": \"PCMS\",\n  \"id\": \"I-75 SB - MP 50\",\n  \"timestamp\": \"2020-08-21T15:52:27Z\",\n  \"location\": [\n    37.23397,\n    -84.2290798\n  ],\n  \"messages\": [\n    \" ROADWORK / 4 MILES / AHEAD // 19 MILES / OF WORK / MP 48-29\"\n  ]\n}\n{\n  \"type\": \"PCMS\",\n  \"id\": \"I-75 SB - MP 46\",\n  \"timestamp\": \"2020-08-21T15:48:32Z\",\n  \"location\": [\n    37.205992,\n    -84.167269\n  ],\n  \"messages\": [\n    \" ROADWORK / NEXT / 5 MILES // 19 MILES / OF WORK / MP 48-29\"\n  ]\n}"
    test_incident = """ <incident id="1246">
    <creationtime>2019-11-05T01:32:44Z</creationtime>
    <updatetime>2020-08-21T15:52:02Z</updatetime>
    <type>CONSTRUCTION</type>
    <description>19-1245: Roadwork between MP 48 and MP 40</description>
    <location>
      <street>I-75 S</street>
      <direction>ONE_DIRECTION</direction>
      <polyline>37.2066700,-84.1691290,37.2012230,-84.1573460,37.1858150,-84.1404820,37.1663450,-84.1214250,37.1478080,-84.1115880</polyline>
    </location>
    <starttime>2019-11-22T23:02:21Z</starttime>
    <sensor type="iCone" id="SB 1 - MP 40.8" latitude="37.1478080" longitude="-84.1115880" />
    <sensor type="iCone" id="SB 2 - MP 42.1" latitude="37.1663450" longitude="-84.1214250">
      <radar devID="1614" intervalEnd="2020-08-21T15:45:00Z" latitude="37.1663422" longitude="-84.1214254" numReads="67" avgSpeed="67.43" stDevSpeed="6.5561" />
      <radar devID="1614" intervalEnd="2020-08-21T15:50:00Z" latitude="37.1663422" longitude="-84.1214254" numReads="48" avgSpeed="68.54" stDevSpeed="6.2738" />
      <radar devID="1614" intervalEnd="2020-08-21T15:55:00Z" latitude="37.1663422" longitude="-84.1214254" numReads="38" avgSpeed="66.84" stDevSpeed="6.4339" />
    </sensor>
    <sensor type="iCone" id="SB 3 - MP 44.0" latitude="37.1858150" longitude="-84.1404820">
      <radar devID="1740" intervalEnd="2020-08-21T15:40:00Z" latitude="37.1857562" longitude="-84.1404956" numReads="9" avgSpeed="61.39" stDevSpeed="6.3463" />
      <radar devID="1740" intervalEnd="2020-08-21T15:45:00Z" latitude="37.1857562" longitude="-84.1404956" numReads="68" avgSpeed="65.51" stDevSpeed="6.5987" />
      <radar devID="1740" intervalEnd="2020-08-21T15:50:00Z" latitude="37.1857562" longitude="-84.1404956" numReads="33" avgSpeed="66.59" stDevSpeed="6.6288" />
    </sensor>
    <sensor type="iCone" id="SB 4 - MP 45.7" latitude="37.2012230" longitude="-84.1573460">
      <radar devID="1724" intervalEnd="2020-08-21T15:40:00Z" latitude="37.2012256" longitude="-84.1573747" numReads="21" avgSpeed="64.64" stDevSpeed="5.6432" />
      <radar devID="1724" intervalEnd="2020-08-21T15:45:00Z" latitude="37.2012256" longitude="-84.1573747" numReads="38" avgSpeed="69.21" stDevSpeed="6.9488" />
      <radar devID="1724" intervalEnd="2020-08-21T15:50:00Z" latitude="37.2012256" longitude="-84.1573747" numReads="62" avgSpeed="64.11" stDevSpeed="9.0186" />
      <radar devID="1724" intervalEnd="2020-08-21T15:55:00Z" latitude="37.2012256" longitude="-84.1573747" numReads="17" avgSpeed="66.91" stDevSpeed="5.3667" />
    </sensor>
    <sensor type="iCone" id="SB 5 - MP 47.5" latitude="37.2066700" longitude="-84.1691290">
      <radar devID="1735" intervalEnd="2020-08-21T15:45:00Z" latitude="37.2066724" longitude="-84.1691283" numReads="70" avgSpeed="67.00" stDevSpeed="6.2133" />   
    </sensor>
    <sensor type="iCone" id="SB 6 - MP 48.5" latitude="37.2193130" longitude="-84.2046600" />
    <sensor type="iCone" id="SB 7 - MP 49.5" latitude="37.2299854" longitude="-84.2221508">
      <radar devID="1719" intervalEnd="2020-08-21T15:40:00Z" numReads="19" avgSpeed="67.24" stDevSpeed="4.9229" />
      <radar devID="1719" intervalEnd="2020-08-21T15:45:00Z" numReads="38" avgSpeed="65.00" stDevSpeed="10.7934" />
      <radar devID="1719" intervalEnd="2020-08-21T15:50:00Z" numReads="62" avgSpeed="62.82" stDevSpeed="9.7647" />
      <radar devID="1719" intervalEnd="2020-08-21T15:55:00Z" numReads="41" avgSpeed="59.57" stDevSpeed="8.8250" />
    </sensor>
    <sensor type="iCone" id="SB 8 - MP 50.5" latitude="37.2378880" longitude="-84.2359180" />
    <display type="PCMS" id="I-75 SB - MP 50" latitude="37.2339700" longitude="-84.2290798">
      <message verified="2020-08-21T15:42:27Z" text=" ROADWORK / 4 MILES / AHEAD // 19 MILES / OF WORK / MP 48-29" />
      <message verified="2020-08-21T15:52:27Z" text=" ROADWORK / 4 MILES / AHEAD // 19 MILES / OF WORK / MP 48-29" />
    </display>
    <display type="PCMS" id="I-75 SB - MP 46" latitude="37.2059920" longitude="-84.1672690">
      <message verified="2020-08-21T15:48:32Z" latitude="37.2060070" longitude="-84.1673050" text=" ROADWORK / NEXT / 5 MILES // 19 MILES / OF WORK / MP 48-29" />
    </display>
  </incident>"""
    output_description = icone_translator.create_description(
        xmltodict.parse(test_incident)['incident'])
    assert output_description == test_description

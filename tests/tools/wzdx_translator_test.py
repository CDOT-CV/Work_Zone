import json
import os
import uuid
from unittest.mock import Mock, patch

from wzdx.tools import wzdx_translator
from tests.data.tools import wzdx_translator_data


# --------------------------------------------------------------------------------unit test for valid_info function--------------------------------------------------------------------------------
def test_valid_info_valid_info():
    test_info = {
        'feed_info_id': "104d7746-688c-44ed-b195-2ee948bf9dfa",
        'metadata': {
            'wz_location_method': "channel-device-method",
            'lrs_type': "lrs_type",
            'contact_name': "Ashley Nylen",
            'contact_email': "ashley.nylen@state.co.us",
            'issuing_organization': "iCone",
        }
    }
    test_validate_info = wzdx_translator.validate_info(test_info)
    assert test_validate_info == True


def test_valid_info_no_info():
    test_info = None
    test_validate_info = wzdx_translator.validate_info(test_info)
    assert test_validate_info == False


def test_valid_info_invalid_info_missing_required_fields_lrs_type():
    test_info = {
        'feed_info_id': "104d7746-688c-44ed-b195-2ee948bf9dfa",
        'metadata': {
            'wz_location_method': "channel-device-method",
            'contact_name': "Ashley Nylen",
            'contact_email': "ashley.nylen@state.co.us",
            'issuing_organization': "iCone",
        }
    }
    test_validate_info = wzdx_translator.validate_info(test_info)
    assert test_validate_info == False


def test_valid_info_invalid_info_invalid_feed_info_id():
    test_info = {
        'feed_info_id': "104d7746-e948bf9dfa",
        'metadata': {
            'wz_location_method': "channel-device-method",
            'lrs_type': "lrs_type",
            'contact_name': "Ashley Nylen",
            'contact_email': "ashley.nylen@state.co.us",
            'issuing_organization': "iCone",
        }
    }
    test_validate_info = wzdx_translator.validate_info(test_info)
    assert test_validate_info == False


# --------------------------------------------------------------------------------unit test for parse_xml function--------------------------------------------------------------------------------
def test_parse_xml():
    inputfile = './wzdx/sample_files/raw/icone/incident_short.xml'
    with open(inputfile, encoding='utf-8-sig') as f:
        xml_string = f.read()
        actual_icone_data = wzdx_translator.parse_xml_to_dict(xml_string)
        assert actual_icone_data == wzdx_translator_data.test_parse_xml_expected_icone_data


# --------------------------------------------------------------------------------unit test for validate_wzdx function--------------------------------------------------------------------------------
def test_validate_wzdx_valid_wzdx_data():
    test_schema = json.loads(
        open('wzdx/sample_files/validation_schema/wzdx_v3.1_feed.json').read())
    validate_write = wzdx_translator.validate_wzdx(
        wzdx_translator_data.test_validate_wzdx_valid_wzdx_data, test_schema)
    assert validate_write == True


def test_validate_wzdx_invalid_location_method_wzdx_data():
    test_schema = json.loads(
        open('wzdx/sample_files/validation_schema/wzdx_v3.1_feed.json').read())
    invalid_write = wzdx_translator.validate_wzdx(
        wzdx_translator_data.test_validate_wzdx_invalid_location_method, test_schema)
    assert invalid_write == False


def test_validate_wzdx_no_schema():
    test_schema = {}
    invalid_write = wzdx_translator.validate_wzdx(
        wzdx_translator_data.test_validate_wzdx_valid_wzdx_data, test_schema)
    assert invalid_write == False


def test_validate_wzdx_no_wzdx_data():
    test_wzdx_data = {}
    test_schema = json.loads(
        open('wzdx/sample_files/validation_schema/wzdx_v3.1_feed.json').read())
    validate_write = wzdx_translator.validate_wzdx(
        test_wzdx_data, test_schema)
    assert validate_write == False


# --------------------------------------------------------------------------------unit test for initialize_info function--------------------------------------------------------------------------------
@patch.dict(os.environ, {
    'contact_name': 'Ashley Nylen',
    'contact_email': 'ashley.nylen@state.co.us',
    'issuing_organization': 'CDOT'
})
def test_initialize_info():
    actual = wzdx_translator.initialize_info(
        "104d7746-688c-44ed-b195-2ee948bf9dfa")
    expected = {'feed_info_id': "104d7746-688c-44ed-b195-2ee948bf9dfa", 'metadata': {'wz_location_method': "channel-device-method",
                                                                                     'lrs_type': "lrs_type", 'contact_name': "Ashley Nylen", 'contact_email': "ashley.nylen@state.co.us", 'issuing_organization': "CDOT"}}
    assert actual == expected


# --------------------------------------------------------------------------------Unit test for add_ids_v3 function--------------------------------------------------------------------------------
@patch('uuid.uuid4')
def test_add_ids(mockuuid):
    uuid.uuid4 = Mock()
    uuid.uuid4.side_effect = ['we234de', '23wsg54h']
    input_message = {
        'feed_info': {
            'data_sources': [
                {
                    'data_source_id': 'u12s5grt'
                }
            ]
        },
        'features': [
            {
                'properties': {
                    'core_details': {
                        'data_source_id': "",
                        'relationship': {
                            'relationship_id': "",
                            'road_event_id': ""
                        }
                    }
                }
            }
        ]
    }
    actual = wzdx_translator.add_ids(input_message)
    expected = {
        'feed_info': {
            'data_sources': [
                {
                    'data_source_id': 'u12s5grt'
                }
            ]
        },
        'features': [
            {
                'properties': {
                    'core_details': {
                        'data_source_id': "u12s5grt",
                        'relationship': {
                            'relationship_id': "23wsg54h",
                            'road_event_id': "we234de"
                        }
                    }
                }
            }
        ]
    }

    assert actual == expected


@patch('uuid.uuid4')
def test_add_ids_invalid_message_type(mockuuid):
    uuid.uuid4 = Mock()
    uuid.uuid4.side_effect = ['we234de', '23wsg54h']
    input_message = 'invalid message'
    actual = wzdx_translator.add_ids(input_message)
    expected = None

    assert actual == expected


@patch('uuid.uuid4')
def test_add_ids_empty_message(mockuuid):
    uuid.uuid4 = Mock()
    uuid.uuid4.side_effect = ['we234de', '23wsg54h']
    input_message = None
    actual = wzdx_translator.add_ids(input_message)
    expected = None

    assert actual == expected


# --------------------------------------------------------------------------------Unit test for parse_polyline_from_linestring function--------------------------------------------------------------------------------
def test_parse_polyline_from_linestring_valid_data():
    test_polyline = "LINESTRING (-104.828415 37.735142, -104.830933 37.741074)"
    test_coordinates = wzdx_translator.parse_polyline_from_linestring(
        test_polyline)
    valid_coordinates = [
        [
            -104.828415,
            37.735142
        ],
        [
            -104.830933,
            37.741074
        ]
    ]
    assert test_coordinates == valid_coordinates


def test_parse_polyline_from_linestring_null_parameter():
    test_polyline = None
    test_coordinates = wzdx_translator.parse_polyline_from_linestring(
        test_polyline)
    expected_coordinates = None
    assert test_coordinates == expected_coordinates


def test_parse_polyline_from_linestring_invalid_data():
    test_polyline = 'invalid'
    test_coordinates = wzdx_translator.parse_polyline_from_linestring(
        test_polyline)
    expected_coordinates = []
    assert test_coordinates == expected_coordinates


def test_parse_polyline_from_linestring_invalid_coordinates():
    test_polyline = 'a,b,c,d'
    test_coordinates = wzdx_translator.parse_polyline_from_linestring(
        test_polyline)
    expected_coordinates = []
    assert test_coordinates == expected_coordinates


# --------------------------------------------------------------------------------unit test for parse_direction_from_street_name function--------------------------------------------------------------------------------
def test_parse_direction_from_street_name_southbound():
    test_road_name = 'I-75 S'
    output_direction = wzdx_translator.parse_direction_from_street_name(
        test_road_name)
    assert output_direction == 'southbound'


def test_parse_direction_from_street_name_northbound():
    test_road_name = 'I-75 NB'
    output_direction = wzdx_translator.parse_direction_from_street_name(
        test_road_name)
    assert output_direction == 'northbound'


def test_parse_direction_from_street_name_eastbound():
    test_road_name = 'I-75 EB'
    output_direction = wzdx_translator.parse_direction_from_street_name(
        test_road_name)
    assert output_direction == 'eastbound'


def test_parse_direction_from_street_name_westbound():
    test_road_name = 'I-75 W'
    output_direction = wzdx_translator.parse_direction_from_street_name(
        test_road_name)
    assert output_direction == 'westbound'

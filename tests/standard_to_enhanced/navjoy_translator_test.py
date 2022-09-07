import os
import unittest
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, Mock, patch

import time_machine
from wzdx.standard_to_enhanced import navjoy_translator


def init_datetime_mocks(mock_dts):
    for i in mock_dts:
        i.utcnow = MagicMock(return_value=datetime(
            2021, 4, 13, tzinfo=timezone.utc))
        i.now = MagicMock(return_value=datetime(
            2021, 4, 13))
        i.strptime = datetime.strptime


@unittest.mock.patch('wzdx.standard_to_enhanced.navjoy_translator.datetime')
@unittest.mock.patch('wzdx.tools.wzdx_translator.datetime')
def test_parse_reduction_zone_linestring(mock_dt, mock_dt_3):
    init_datetime_mocks([mock_dt, mock_dt_3])
    standard = {
        'rtdh_timestamp': 1638846301.4691865,
        'rtdh_message_id': 'e5bba2f6-bbd0-4a61-8d64-b7c33657d35a',
        'event': {
            'type': '',
            'source': {
                'id': 'Form568-44819108-703c-4d6d-ae0d-7dca7319e5b0',
                'last_updated_timestamp': 1638871501469
            },
            'geometry': [
                [-104.82230842595187, 39.73946349406594],
                [-104.79432762150851, 39.73959547447038]
            ],
            'header': {
                'description': 'Maintenance for lane expansion',
                'justification': 'Lane expansion - maintenance work',
                'reduced_speed_limit': 45,
                'start_timestamp': 1630290600000,
                'end_timestamp': 1630290600000
            },
            'detail': {
                'road_name': '287',
                'road_number': '287',
                'direction': 'eastbound'
            }
        }
    }

    test_feature = navjoy_translator.parse_reduction_zone(standard)

    expected_feature = {
        'id': 'Form568-44819108-703c-4d6d-ae0d-7dca7319e5b0',
        "type": "Feature",
        "properties": {
            "core_details": {
                "data_source_id": '',
                "event_type": "work-zone",
                "road_names": ["287"],
                "direction": "eastbound",
                "description": "Maintenance for lane expansion. Lane expansion - maintenance work",
                "update_date": "2021-12-07T10:05:01Z"
            },
            "start_date": "2021-08-30T02:30:00Z",
            "end_date": "2021-08-30T02:30:00Z",
            "start_date_accuracy": "estimated",
            "end_date_accuracy": "estimated",
            "beginning_accuracy": "estimated",
            "ending_accuracy": "estimated",
            "vehicle_impact": "all-lanes-open",
            "event_status": "completed",
            "reduced_speed_limit": 45,
            'types_of_work': [{'type_name': 'surface-work',
                               'is_architectural_change': True}],
        },
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [
                    -104.82230842595187,
                    39.73946349406594
                ],
                [
                    -104.79432762150851,
                    39.73959547447038
                ],
            ]
        }
    }
    assert test_feature == expected_feature


def test_parse_reduction_zone_no_data():
    test_feature = navjoy_translator.parse_reduction_zone(None)
    expected_feature = None
    assert test_feature == expected_feature


def test_parse_reduction_zone_invalid_data():
    test_var = 'a,b,c,d'
    test_feature = navjoy_translator.parse_reduction_zone(test_var)
    assert test_feature == None


# --------------------------------------------------------------------------------Unit test for get_vehicle_impact function--------------------------------------------------------------------------------
def test_get_vehicle_impact_some_lanes_closed():
    test_description = "Right Lane Closure"
    test_vehicle_impact = navjoy_translator.get_vehicle_impact(
        test_description)
    expected_vehicle_impact = "some-lanes-closed"
    assert test_vehicle_impact == expected_vehicle_impact


def test_get_vehicle_impact_all_lanes_closed():
    test_description = 'All Lanes Closed'
    test_vehicle_impact = navjoy_translator.get_vehicle_impact(
        test_description)
    expected_vehicle_impact = "all-lanes-closed"
    assert test_vehicle_impact == expected_vehicle_impact


def test_get_vehicle_impact_all_lanes_open():
    test_description = 'Everything is fine'
    test_vehicle_impact = navjoy_translator.get_vehicle_impact(
        test_description)
    expected_vehicle_impact = "all-lanes-open"
    assert test_vehicle_impact == expected_vehicle_impact


# --------------------------------------------------------------------------------Unit test for wzdx_creator function--------------------------------------------------------------------------------
@patch.dict(os.environ, {
    'contact_name': 'Ashley Nylen',
    'contact_email': 'ashley.nylen@state.co.us',
    'issuing_organization': 'CDOT'
})
@patch('uuid.uuid4')
@unittest.mock.patch('wzdx.standard_to_enhanced.navjoy_translator.datetime')
@unittest.mock.patch('wzdx.tools.wzdx_translator.datetime')
def test_wzdx_creator(mock_dt, mock_dt_3, mockuuid):
    init_datetime_mocks([mock_dt, mock_dt_3])
    uuid.uuid4 = Mock()
    uuid.uuid4.side_effect = 'we234de'

    standard = {
        'rtdh_timestamp': 1638846301.4691865,
        'rtdh_message_id': 'e5bba2f6-bbd0-4a61-8d64-b7c33657d35a',
        'event': {
            'type': '',
            'source': {
                'id': 'Form568-44819108-703c-4d6d-ae0d-7dca7319e5b0',
                'last_updated_timestamp': 1638871501469
            },
            'geometry': [
                [-104.82230842595187, 39.73946349406594],
                [-104.79432762150851, 39.73959547447038]
            ],
            'header': {
                'description': 'Maintenance for lane expansion',
                'justification': 'Lane expansion - maintenance work',
                'reduced_speed_limit': 45,
                'start_timestamp': 1630290600000,
                'end_timestamp': 1630290600000
            },
            'detail': {
                'road_name': '287',
                'road_number': '287',
                'direction': 'eastbound'
            }
        }
    }

    expected_wzdx = {
        'road_event_feed_info': {
            'update_date': '2021-04-13T00:00:00Z',
            'publisher': 'CDOT',
            'contact_name': 'Ashley Nylen',
            'contact_email': 'ashley.nylen@state.co.us',
            'version': '4.0',
            "update_frequency": 300,
            'license': 'https://creativecommons.org/publicdomain/zero/1.0/',
            'data_sources': [
                {
                    'data_source_id': 'w',
                    'organization_name': 'CDOT',
                    'contact_name': 'Ashley Nylen',
                    'contact_email': 'ashley.nylen@state.co.us',
                    'update_date': '2021-04-13T00:00:00Z',
                    "update_frequency": 300,
                }
            ]
        },
        'type': 'FeatureCollection',
        'features': [
            {
                'id': 'Form568-44819108-703c-4d6d-ae0d-7dca7319e5b0',
                'type': 'Feature',
                'properties': {
                    'core_details': {
                        'data_source_id': 'w',
                        'event_type': 'work-zone',
                        'road_names': ['287'],
                        'direction': 'eastbound',
                        'description': 'Maintenance for lane expansion. Lane expansion - maintenance work',
                        'update_date': "2021-12-07T10:05:01Z"
                    },
                    'reduced_speed_limit': 45,
                    'start_date': "2021-08-30T02:30:00Z",
                    'end_date': "2021-08-30T02:30:00Z",
                    'start_date_accuracy': 'estimated',
                    'end_date_accuracy': 'estimated',
                    'beginning_accuracy': 'estimated',
                    'ending_accuracy': 'estimated',
                    'vehicle_impact': 'all-lanes-open',
                    'event_status': 'planned',
                    'types_of_work': [
                        {
                            'type_name': 'surface-work',
                            'is_architectural_change': True
                        }
                    ]
                },
                'geometry': {
                    'type': 'LineString',
                    'coordinates': [
                        [-104.82230842595187, 39.73946349406594],
                        [-104.79432762150851, 39.73959547447038]
                    ]
                },
            }
        ]
    }

    with time_machine.travel(datetime(2021, 4, 13, 0, 0, 0)):
        test_wzdx = navjoy_translator.wzdx_creator(standard)
    print(test_wzdx)
    assert expected_wzdx == test_wzdx


def test_wzdx_creator_empty_object():
    obj = None
    test_wzdx = navjoy_translator.wzdx_creator(obj)
    assert test_wzdx == None


def test_wzdx_creator_no_incidents():
    obj = []
    test_wzdx = navjoy_translator.wzdx_creator(obj)
    assert test_wzdx == None


def test_wzdx_creator_invalid_info_object():
    standard = {'rtdh_timestamp': 1638846301.4691865, 'rtdh_message_id': 'e5bba2f6-bbd0-4a61-8d64-b7c33657d35a', 'event': {'type': '', 'source': {'id': 'Form568-44819108-703c-4d6d-ae0d-7dca7319e5b0', 'last_updated_timestamp': 1638871501469}, 'geometry': [[-104.82230842595187, 39.73946349406594],
                                                                                                                                                                                                                                                               [-104.79432762150851, 39.73959547447038]], 'header': {'description': 'Maintenance for lane expansion', 'justification': 'Lane expansion - maintenance work', 'start_timestamp': 1630290600000, 'end_timestamp': 1630290600000}, 'detail': {'road_name': '287', 'road_number': '287', 'direction': 'eastbound'}}}

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

    test_wzdx = navjoy_translator.wzdx_creator(
        standard, test_invalid_info_object)
    assert test_wzdx == None


# ----------------------------------------- get_types_of_work -----------------------------------------
def test_get_types_of_work_restriping():
    field = 'Restriping and crack seal operations.'
    expected = [{'type_name': 'minor-road-defect-repair',
                              'is_architectural_change': False},
                {'type_name': 'painting',
                 'is_architectural_change': False}]
    actual = navjoy_translator.get_types_of_work(field)

    assert actual == expected


def test_get_types_of_work_none():
    field = None
    expected = None
    actual = navjoy_translator.get_types_of_work(field)

    assert actual == expected


def test_get_types_of_work_empty():
    field = ''
    expected = None
    actual = navjoy_translator.get_types_of_work(field)

    assert actual == expected

import os
import unittest
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, Mock, patch

import time_machine
from wzdx.standard_to_enhanced import planned_events_translator


def init_datetime_mocks(mock_dts):
    for i in mock_dts:
        i.utcnow = MagicMock(return_value=datetime(
            2021, 4, 13, tzinfo=timezone.utc))
        i.now = MagicMock(return_value=datetime(
            2021, 4, 13))
        i.strptime = datetime.strptime


@unittest.mock.patch('wzdx.standard_to_enhanced.navjoy_translator.datetime')
@unittest.mock.patch('wzdx.tools.wzdx_translator.datetime')
def test_parse_work_zone_linestring(mock_dt, mock_dt_3):
    init_datetime_mocks([mock_dt, mock_dt_3])
    standard = {
        "rtdh_timestamp": 1642036259.3099449,
        "rtdh_message_id": "42fe21b8-102b-43e8-8668-23c55334a201",
        "event": {
            "type": 'work-zone',
            "source": {
                "id": "OpenTMS-Event1689408506",
                "creation_timestamp": 1635531964000,
                "last_updated_timestamp": 1635532501835
            },
            "geometry": [
                [
                    -108.279106,
                    39.195663
                ],
                [
                    -108.218549,
                    39.302392
                ]
            ],
            "header": {
                "description": "Between Exit 49: CO 65; Grand Mesa (5 miles east of the Palisade area) and US 6 (Debeque) from Mile Point 50 to Mile Point 60. Road closed expect delays due to bridge construction. Until May 1, 2022 at about 12:26PM MDT.",
                "start_timestamp": 1635531964000,
                "end_timestamp": 1651429564000
            },
            "detail": {
                "road_name": "I-70E",
                "road_number": "I-70E",
                "direction": "westbound"
            },
            "additional_info": {
                "lanes": [
                    {
                        "order": 1,
                        "type": "shoulder",
                        "status": "open"
                    },
                    {
                        "order": 2,
                        "type": "general",
                        "status": "closed"
                    },
                    {
                        "order": 3,
                        "type": "general",
                        "status": "closed"
                    },
                    {
                        "order": 4,
                        "type": "shoulder",
                        "status": "open"
                    }
                ],
                "restrictions": [],
                "beginning_milepost": 50.0,
                "ending_milepost": 60.0,
                "types_of_work": [{
                    "type_name": "below-road-work",
                    "is_architectural_change": True
                }]
            }
        }
    }

    test_feature = planned_events_translator.parse_work_zone(standard)

    expected_feature = {
        "id": "OpenTMS-Event1689408506",
        "type": "Feature",
        "properties": {
            "core_details": {
              "data_source_id": "",
              "event_type": "work-zone",
              "road_names": [
                  "I-70E"
              ],
                "direction": "westbound",
                "relationship": {},
                "description": "Between Exit 49: CO 65; Grand Mesa (5 miles east of the Palisade area) and US 6 (Debeque) from Mile Point 50 to Mile Point 60. Road closed expect delays due to bridge construction. Until May 1, 2022 at about 12:26PM MDT.",
                "creation_date": "2021-10-29T18:26:04Z",
                "update_date": "2021-10-29T18:35:01Z",
            },
            "start_date": "2021-10-29T18:26:04Z",
            "end_date": "2022-05-01T18:26:04Z",
            "location_method": "channel-device-method",
            "start_date_accuracy": "estimated",
            "end_date_accuracy": "estimated",
            "beginning_accuracy": "estimated",
            "ending_accuracy": "estimated",
            "vehicle_impact": "some-lanes-closed",
            "beginning_milepost": 50.0,
            "ending_milepost": 60.0,
            "lanes": [
                {
                    "order": 1,
                    "type": "shoulder",
                    "status": "open"
                },
                {
                    "order": 2,
                    "type": "general",
                    "status": "closed"
                },
                {
                    "order": 3,
                    "type": "general",
                    "status": "closed"
                },
                {
                    "order": 4,
                    "type": "shoulder",
                    "status": "open"
                }
            ],
            "event_status": "active"
        },
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [
                    -108.279106,
                    39.195663
                ],
                [
                    -108.218549,
                    39.302392
                ]
            ]
        }
    }
    assert test_feature == expected_feature


def test_parse_work_zone_no_data():
    test_feature = planned_events_translator.parse_work_zone(None)
    expected_feature = None
    assert test_feature == expected_feature


def test_parse_work_zone_invalid_data():
    test_var = 'a,b,c,d'
    test_feature = planned_events_translator.parse_work_zone(test_var)
    assert test_feature == None


# --------------------------------------------------------------------------------Unit test for get_vehicle_impact function--------------------------------------------------------------------------------
def test_get_vehicle_impact_some_lanes_closed():
    lanes = [{
        "order": 1,
        "type": "shoulder",
        "status": "open"
    },
        {
        "order": 2,
        "type": "general",
        "status": "closed"
    },
        {
        "order": 3,
        "type": "general",
        "status": "closed"
    },
        {
        "order": 4,
        "type": "shoulder",
        "status": "open"
    }]
    test_vehicle_impact = planned_events_translator.get_vehicle_impact(
        lanes)
    expected_vehicle_impact = "some-lanes-closed"
    assert test_vehicle_impact == expected_vehicle_impact


def test_get_vehicle_impact_all_lanes_closed():
    lanes = [{
        "order": 1,
        "type": "shoulder",
        "status": "closed"
    },
        {
        "order": 2,
        "type": "general",
        "status": "closed"
    },
        {
        "order": 3,
        "type": "general",
        "status": "closed"
    },
        {
        "order": 4,
        "type": "shoulder",
        "status": "closed"
    }]
    test_vehicle_impact = planned_events_translator.get_vehicle_impact(
        lanes)
    expected_vehicle_impact = "all-lanes-closed"
    assert test_vehicle_impact == expected_vehicle_impact


def test_get_vehicle_impact_all_lanes_open():
    lanes = [{
        "order": 1,
        "type": "shoulder",
        "status": "open"
    },
        {
        "order": 2,
        "type": "general",
        "status": "open"
    },
        {
        "order": 3,
        "type": "general",
        "status": "open"
    },
        {
        "order": 4,
        "type": "shoulder",
        "status": "open"
    }]
    test_vehicle_impact = planned_events_translator.get_vehicle_impact(
        lanes)
    expected_vehicle_impact = "all-lanes-open"
    assert test_vehicle_impact == expected_vehicle_impact


# --------------------------------------------------------------------------------Unit test for wzdx_creator function--------------------------------------------------------------------------------


@patch.dict(os.environ, {
    'contact_name': 'Ashley Nylen',
    'contact_email': 'ashley.nylen@state.co.us',
    'issuing_organization': 'CDOT'
})
# first is for data source id, second is for a default id that is not used in this example, and the third is the road_event_id
@patch.object(uuid, 'uuid4', side_effect=['w', '', '3'])
@unittest.mock.patch('wzdx.standard_to_enhanced.navjoy_translator.datetime')
@unittest.mock.patch('wzdx.tools.wzdx_translator.datetime')
def test_wzdx_creator(mock_dt, mock_dt_3, _):
    init_datetime_mocks([mock_dt, mock_dt_3])

    standard = {
        "rtdh_timestamp": 1642036259.3099449,
        "rtdh_message_id": "42fe21b8-102b-43e8-8668-23c55334a201",
        "event": {
            "type": "work-zone",
            "types_of_lanes": {
                "type_name": "below-road-work",
                "is_architectural_change": True
            },
            "source": {
                "id": "OpenTMS-Event1689408506",
                "creation_timestamp": 1635531964000,
                "last_updated_timestamp": 1635532501835
            },
            "geometry": [
                [
                    -108.279106,
                    39.195663
                ],
                [
                    -108.218549,
                    39.302392
                ]
            ],
            "header": {
                "description": "Between Exit 49: CO 65; Grand Mesa (5 miles east of the Palisade area) and US 6 (Debeque) from Mile Point 50 to Mile Point 60. Road closed expect delays due to bridge construction. Until May 1, 2022 at about 12:26PM MDT.",
                "start_timestamp": 1635531964000,
                "end_timestamp": 1651429564000
            },
            "detail": {
                "road_name": "I-70E",
                "road_number": "I-70E",
                "direction": "westbound"
            },
            "additional_info": {
                "lanes": [
                    {
                        "order": 1,
                        "type": "shoulder",
                        "status": "open"
                    },
                    {
                        "order": 2,
                        "type": "general",
                        "status": "closed"
                    },
                    {
                        "order": 3,
                        "type": "general",
                        "status": "closed"
                    },
                    {
                        "order": 4,
                        "type": "shoulder",
                        "status": "open"
                    }
                ],
                "restrictions": [],
                "beginning_milepost": 50.0,
                "ending_milepost": 60.0
            }
        }
    }

    expected_wzdx = {
        "road_event_feed_info": {
            "feed_info_id": "49253be7-0c6a-4a65-8113-450f9041f989",
            "update_date": "2021-04-13T00:00:00Z",
            "publisher": "CDOT",
            "contact_name": "Ashley Nylen",
            "contact_email": "ashley.nylen@state.co.us",
            "version": "4.0",
            "license": "https://creativecommons.org/publicdomain/zero/1.0/",
            "data_sources": [
                {
                    "data_source_id": "w",
                    "feed_info_id": "49253be7-0c6a-4a65-8113-450f9041f989",
                    "organization_name": "CDOT",
                    "contact_name": "Ashley Nylen",
                    "contact_email": "ashley.nylen@state.co.us",
                    "update_date": "2021-04-13T00:00:00Z",
                    "location_method": "channel-device-method",
                    "lrs_type": "lrs_type"
                }
            ]
        },
        "type": "FeatureCollection",
        "features": [
            {
                "id": "OpenTMS-Event1689408506",
                "type": "Feature",
                "properties": {
                    "core_details": {
                        "data_source_id": "w",
                        "event_type": "work-zone",
                        "road_names": [
                            "I-70E"
                        ],
                        "direction": "westbound",
                        "relationship": {},
                        "description": "Between Exit 49: CO 65; Grand Mesa (5 miles east of the Palisade area) and US 6 (Debeque) from Mile Point 50 to Mile Point 60. Road closed expect delays due to bridge construction. Until May 1, 2022 at about 12:26PM MDT.",
                        'creation_date': "2021-10-29T18:26:04Z",
                        'update_date': "2021-10-29T18:35:01Z",
                        "road_event_id": "3"
                    },
                    "start_date": "2021-10-29T18:26:04Z",
                    "end_date": "2022-05-01T18:26:04Z",
                    "location_method": "channel-device-method",
                    "beginning_milepost": 50.0,
                    "ending_milepost": 60.0,
                    "start_date_accuracy": "estimated",
                    "end_date_accuracy": "estimated",
                    "beginning_accuracy": "estimated",
                    "ending_accuracy": "estimated",
                    "vehicle_impact": "some-lanes-closed",
                    "lanes": [
                        {
                            "order": 1,
                            "type": "shoulder",
                            "status": "open"
                        },
                        {
                            "order": 2,
                            "type": "general",
                            "status": "closed"
                        },
                        {
                            "order": 3,
                            "type": "general",
                            "status": "closed"
                        },
                        {
                            "order": 4,
                            "type": "shoulder",
                            "status": "open"
                        }
                    ],
                    "event_status": "planned"
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [
                            -108.279106,
                            39.195663
                        ],
                        [
                            -108.218549,
                            39.302392
                        ]
                    ]
                }
            }
        ]
    }

    with time_machine.travel(datetime(2021, 4, 13, 0, 0, 0)):
        test_wzdx = planned_events_translator.wzdx_creator(standard)
    print(test_wzdx)
    assert expected_wzdx == test_wzdx


def test_wzdx_creator_empty_object():
    obj = None
    test_wzdx = planned_events_translator.wzdx_creator(obj)
    assert test_wzdx == None


def test_wzdx_creator_no_incidents():
    obj = []
    test_wzdx = planned_events_translator.wzdx_creator(obj)
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

    test_wzdx = planned_events_translator.wzdx_creator(
        standard, test_invalid_info_object)
    assert test_wzdx == None

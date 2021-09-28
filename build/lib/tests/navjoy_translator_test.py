import os
import unittest
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, Mock, patch

import time_machine
from translator import navjoy_translator

# Unit testing code for navjoy_translator.py
# --------------------------------------------------------------------------------Unit test for parse_incident function--------------------------------------------------------------------------------

# utc_time_zone = ZoneInfo("America/Los_Angeles")


def init_datetime_mocks(mock_dts):
    for i in mock_dts:
        i.utcnow = MagicMock(return_value=datetime(
            2021, 4, 13, tzinfo=timezone.utc))
        i.now = MagicMock(return_value=datetime(
            2021, 4, 13))
        i.strptime = datetime.strptime


@unittest.mock.patch('translator.navjoy_translator.datetime')
@unittest.mock.patch('translator.tools.date_tools.datetime')
@unittest.mock.patch('translator.tools.wzdx_translator.datetime')
def test_parse_reduction_zone_linestring(mock_dt, mock_dt_2, mock_dt_3):
    init_datetime_mocks([mock_dt, mock_dt_2, mock_dt_3])
    event = {
        "sys_gUid": "Form568-cb0fdaf0-c27a-4bef-aabd-442615dfb2d6",
        "data": {
            "descriptionForProject": "Bridge Repairs",
            "srzmap": [
                {
                    "type": "LineString",
                    "coordinates": [
                        [
                            [
                                -104.65225365171561,
                                40.39393671703483
                            ],
                            [
                                -104.65228583822379,
                                40.39342193227279
                            ],
                            [
                                -104.64946415434012,
                                40.39348730198451
                            ],
                            [
                                -104.64953925619254,
                                40.394108311080984
                            ],
                            [
                                -104.65225365171561,
                                40.39393671703483
                            ]
                        ]
                    ],
                },
            ],
            "streetNameFrom": "US-34",
            "directionOfTraffic": " East/West ",
            "requestedTemporarySpeed": "45",
            "workStartDate": "2021-08-09T13:00:00.000Z",
            "workEndDate": "2021-09-24T23:00:00.000Z",
            "reductionJustification": "Crews roadside.",
        }
    }

    test_feature = navjoy_translator.parse_reduction_zone(
        event, 'eastbound')

    expected_feature = {
        "type": "Feature",
        "properties": {
            "road_event_id": None,
            "event_type": "work-zone",
            "data_source_id": None,
            "start_date": "2021-08-09T13:00:00Z",
            "end_date": "2021-09-24T23:00:00Z",
            "start_date_accuracy": "estimated",
            "end_date_accuracy": "estimated",
            "beginning_accuracy": "estimated",
            "ending_accuracy": "estimated",
            "road_names": ["US-34"],
            "direction": "eastbound",
            "vehicle_impact": "all-lanes-open",
            "event_status": "planned",
            "reduced_speed_limit": 45,
            "description": "Bridge Repairs. Crews roadside.",
            "creation_date": "2021-04-13T00:00:00Z",
            "update_date": "2021-04-13T00:00:00Z"
        },
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [
                    -104.65225365171561,
                    40.39393671703483
                ],
                [
                    -104.65228583822379,
                    40.39342193227279
                ],
                [
                    -104.64946415434012,
                    40.39348730198451
                ],
                [
                    -104.64953925619254,
                    40.394108311080984
                ],
                [
                    -104.65225365171561,
                    40.39393671703483
                ]
            ]
        }
    }
    assert test_feature == expected_feature


@unittest.mock.patch('translator.navjoy_translator.datetime')
@unittest.mock.patch('translator.tools.date_tools.datetime')
@unittest.mock.patch('translator.tools.wzdx_translator.datetime')
def test_parse_reduction_zone_polygon(mock_dt, mock_dt_2, mock_dt_3):
    init_datetime_mocks([mock_dt, mock_dt_2, mock_dt_3])
    event = {
        "sys_gUid": "Form568-cb0fdaf0-c27a-4bef-aabd-442615dfb2d6",
        "data": {
            "descriptionForProject": "Bridge Repairs",
            "srzmap": [
                {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [
                                -103.17130040113868,
                                40.625392709715676
                            ],
                            [
                                -103.17889641706886,
                                40.61979008921054
                            ],
                            [
                                -103.17567776625098,
                                40.61724921108253
                            ],
                            [
                                -103.17396115248145,
                                40.616206771586256
                            ],
                            [
                                -103.16709469740333,
                                40.62167939747747
                            ],
                            [
                                -103.16851090376319,
                                40.62477383867882
                            ],
                            [
                                -103.17130040113868,
                                40.625392709715676
                            ]
                        ]
                    ],
                },
            ],
            "streetNameFrom": "US-34",
            "directionOfTraffic": " East/West ",
            "requestedTemporarySpeed": "45",
            "workStartDate": "2021-08-09T13:00:00.000Z",
            "workEndDate": "2021-09-24T23:00:00.000Z",
            "reductionJustification": "Crews roadside.",
        }
    }

    test_feature = navjoy_translator.parse_reduction_zone(
        event, 'eastbound')

    expected_feature = {
        "type": "Feature",
        "properties": {
            "road_event_id": None,
            "event_type": "work-zone",
            "data_source_id": None,
            "start_date": "2021-08-09T13:00:00Z",
            "end_date": "2021-09-24T23:00:00Z",
            "start_date_accuracy": "estimated",
            "end_date_accuracy": "estimated",
            "beginning_accuracy": "estimated",
            "ending_accuracy": "estimated",
            "road_names": ["US-34"],
            "direction": "eastbound",
            "vehicle_impact": "all-lanes-open",
            "event_status": "planned",
            "reduced_speed_limit": 45,
            "description": "Bridge Repairs. Crews roadside.",
            "creation_date": "2021-04-13T00:00:00Z",
            "update_date": "2021-04-13T00:00:00Z"
        },
        "geometry": {
            "type": "MultiPoint",
            "coordinates": [
                [
                    -103.17728709165992,
                    40.61851965014654
                ],
                [
                    -103.17481945936622,
                    40.61672799133439
                ]
            ]
        }
    }
    assert test_feature == expected_feature


def test_parse_reduction_zone_no_data():
    test_feature = navjoy_translator.parse_reduction_zone(None, None)
    expected_feature = None
    assert test_feature == expected_feature


def test_parse_reduction_zone_invalid_data():
    test_var = 'a,b,c,d'
    callback = MagicMock()
    test_feature = navjoy_translator.parse_reduction_zone(
        test_var, 'eastbound', callback_function=callback)
    assert callback.called and test_feature == None


# --------------------------------------------------------------------------------Unit test for validate_closure function--------------------------------------------------------------------------------
def test_validate_closure_valid_data():
    event = {
        "sys_gUid": "Form568-cb0fdaf0-c27a-4bef-aabd-442615dfb2d6",
        "data": {
            "descriptionForProject": "Bridge Repairs",
            "srzmap": [
                {
                    "type": "LineString",
                    "coordinates": [
                        [
                            [
                                -103.17130040113868,
                                40.625392709715676
                            ],
                            [
                                -103.17889641706886,
                                40.61979008921054
                            ]
                        ]
                    ],
                },
            ],
            "streetNameFrom": "US-34",
            "directionOfTraffic": " East/West ",
            "requestedTemporarySpeed": "45",
            "workStartDate": "2021-08-09T13:00:00.000Z",
            "workEndDate": "2021-09-24T23:00:00.000Z",
            "reductionJustification": "Crews roadside.",
        }
    }
    assert navjoy_translator.validate_closure(event) == True


def test_validate_closure_missing_required_field_description():
    event = {
        "sys_gUid": "Form568-cb0fdaf0-c27a-4bef-aabd-442615dfb2d6",
        "data": {
            "srzmap": [
                {
                    "type": "LineString",
                    "coordinates": [
                        [
                            [
                                -103.17130040113868,
                                40.625392709715676
                            ],
                            [
                                -103.17889641706886,
                                40.61979008921054
                            ]
                        ]
                    ],
                },
            ],
            "streetNameFrom": "US-34",
            "directionOfTraffic": " East/West ",
            "requestedTemporarySpeed": "45",
            "workStartDate": "2021-08-09T13:00:00.000Z",
            "workEndDate": "2021-09-24T23:00:00.000Z",
            "reductionJustification": "Crews roadside.",
        }
    }
    assert navjoy_translator.validate_closure(event) == False


def test_validate_closure_invalid_start_time():
    event = {
        "sys_gUid": "Form568-cb0fdaf0-c27a-4bef-aabd-442615dfb2d6",
        "data": {
            "descriptionForProject": "Bridge Repairs",
            "srzmap": [
                {
                    "type": "LineString",
                    "coordinates": [
                        [
                            [
                                -103.17130040113868,
                                40.625392709715676
                            ],
                            [
                                -103.17889641706886,
                                40.61979008921054
                            ]
                        ]
                    ],
                },
            ],
            "streetNameFrom": "US-34",
            "directionOfTraffic": " East/West ",
            "requestedTemporarySpeed": "45",
            "workStartDate": 1713004011,
            "workEndDate": "2021-09-24T23:00:00.000Z",
            "reductionJustification": "Crews roadside.",
        }
    }
    assert navjoy_translator.validate_closure(event) == False


def test_validate_closure_invalid():
    event = 'invalid output'
    assert navjoy_translator.validate_closure(event) == False


def test_validate_closure_no_data():
    event = None
    assert navjoy_translator.validate_closure(event) == False


def test_validate_closure_no_coordinates():
    event = {
        "sys_gUid": "Form568-cb0fdaf0-c27a-4bef-aabd-442615dfb2d6",
        "data": {
            "descriptionForProject": "Bridge Repairs",
            "srzmap": [
                {
                    "type": "Point",
                    "coordinates":
                        [
                            -103.17130040113868,
                            40.625392709715676
                        ],
                },
            ],
            "streetNameFrom": "US-34",
            "directionOfTraffic": " East/West ",
            "requestedTemporarySpeed": "45",
            "workStartDate": "2021-08-09T13:00:00.000Z",
            "workEndDate": "2021-09-24T23:00:00.000Z",
            "reductionJustification": "Crews roadside.",
        }
    }
    assert navjoy_translator.validate_closure(event) == False


def test_validate_closure_no_polygon_or_linestring():
    event = {
        "sys_gUid": "Form568-cb0fdaf0-c27a-4bef-aabd-442615dfb2d6",
        "data": {
            "descriptionForProject": "Bridge Repairs",
            "srzmap": [],
            "streetNameFrom": "US-34",
            "directionOfTraffic": " East/West ",
            "requestedTemporarySpeed": "45",
            "workStartDate": "2021-08-09T13:00:00.000Z",
            "workEndDate": "2021-09-24T23:00:00.000Z",
            "reductionJustification": "Crews roadside.",
        }
    }
    assert navjoy_translator.validate_closure(event) == False


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
@unittest.mock.patch('translator.navjoy_translator.datetime')
@unittest.mock.patch('translator.tools.date_tools.datetime')
@unittest.mock.patch('translator.tools.wzdx_translator.datetime')
def test_wzdx_creator(mock_dt, mock_dt_2, mock_dt_3, mockuuid):
    init_datetime_mocks([mock_dt, mock_dt_2, mock_dt_3])
    uuid.uuid4 = Mock()
    uuid.uuid4.side_effect = 'we234de'
    obj = [
        {
            "sys_gUid": "Form568-cb0fdaf0-c27a-4bef-aabd-442615dfb2d6",
            "data": {
                "descriptionForProject": "Bridge Repairs",
                "srzmap": [
                    {
                        "type": "LineString",
                        "coordinates": [
                            [
                                [
                                    -104.65225365171561,
                                    40.39393671703483
                                ],
                                [
                                    -104.65228583822379,
                                    40.39342193227279
                                ],
                                [
                                    -104.64946415434012,
                                    40.39348730198451
                                ],
                                [
                                    -104.64953925619254,
                                    40.394108311080984
                                ],
                                [
                                    -104.65225365171561,
                                    40.39393671703483
                                ]
                            ]
                        ],
                    },
                ],
                "streetNameFrom": "US-34",
                "directionOfTraffic": " East/West ",
                "requestedTemporarySpeed": "45",
                "workStartDate": "2021-08-09T13:00:00.000Z",
                "workEndDate": "2021-09-24T23:00:00.000Z",
                "reductionJustification": "Crews roadside.",
            }
        }
    ]

    expected_wzdx = {
        'road_event_feed_info': {
            'feed_info_id': '2ed141dc-b998-4f7a-8395-9ae9dc7df2f8',
            'update_date': '2021-04-13T00:00:00Z',
            'publisher': 'CDOT',
            'contact_name': 'Ashley Nylen',
            'contact_email': 'ashley.nylen@state.co.us',
            'version': '3.1',
            'license': 'https://creativecommons.org/publicdomain/zero/1.0/',
            'data_sources': [
                {
                    'data_source_id': 'w',
                    'feed_info_id': '2ed141dc-b998-4f7a-8395-9ae9dc7df2f8',
                    'organization_name': 'CDOT',
                    'contact_name': 'Ashley Nylen',
                    'contact_email': 'ashley.nylen@state.co.us',
                    'update_date': '2021-04-13T00:00:00Z',
                    'location_method': 'channel-device-method',
                    'lrs_type': 'lrs_type'
                }
            ]
        },
        'type': 'FeatureCollection',
        'features': [
            {
                "type": "Feature",
                "properties": {
                    "road_event_id": '2',
                    "event_type": "work-zone",
                    "data_source_id": 'w',
                    "start_date": "2021-08-09T13:00:00Z",
                    "end_date": "2021-09-24T23:00:00Z",
                    "start_date_accuracy": "estimated",
                    "end_date_accuracy": "estimated",
                    "beginning_accuracy": "estimated",
                    "ending_accuracy": "estimated",
                    "road_names": ["US-34"],
                    "direction": "eastbound",
                    "vehicle_impact": "all-lanes-open",
                    "event_status": "planned",
                    "reduced_speed_limit": 45,
                    "description": "Bridge Repairs. Crews roadside.",
                    "creation_date": "2021-04-13T00:00:00Z",
                    "update_date": "2021-04-13T00:00:00Z"
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [
                            -104.65225365171561,
                            40.39393671703483
                        ],
                        [
                            -104.65228583822379,
                            40.39342193227279
                        ],
                        [
                            -104.64946415434012,
                            40.39348730198451
                        ],
                        [
                            -104.64953925619254,
                            40.394108311080984
                        ],
                        [
                            -104.65225365171561,
                            40.39393671703483
                        ]
                    ]
                }
            },
            {
                "type": "Feature",
                "properties": {
                    "road_event_id": '3',
                    "event_type": "work-zone",
                    "data_source_id": 'w',
                    "start_date": "2021-08-09T13:00:00Z",
                    "end_date": "2021-09-24T23:00:00Z",
                    "start_date_accuracy": "estimated",
                    "end_date_accuracy": "estimated",
                    "beginning_accuracy": "estimated",
                    "ending_accuracy": "estimated",
                    "road_names": ["US-34"],
                    "direction": "westbound",
                    "vehicle_impact": "all-lanes-open",
                    "event_status": "planned",
                    "reduced_speed_limit": 45,
                    "description": "Bridge Repairs. Crews roadside.",
                    "creation_date": "2021-04-13T00:00:00Z",
                    "update_date": "2021-04-13T00:00:00Z"
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [
                            -104.65225365171561,
                            40.39393671703483
                        ],
                        [
                            -104.65228583822379,
                            40.39342193227279
                        ],
                        [
                            -104.64946415434012,
                            40.39348730198451
                        ],
                        [
                            -104.64953925619254,
                            40.394108311080984
                        ],
                        [
                            -104.65225365171561,
                            40.39393671703483
                        ]
                    ]
                }
            }
        ]
    }

    with time_machine.travel(datetime(2021, 4, 13, 0, 0, 0)):
        test_wzdx = navjoy_translator.wzdx_creator(obj)

    assert expected_wzdx == test_wzdx


def test_wzdx_creator_empty_object():
    obj = None
    test_wzdx = navjoy_translator.wzdx_creator(obj)
    assert test_wzdx == None


def test_wzdx_creator_no_incidents():
    obj = []
    test_wzdx = navjoy_translator.wzdx_creator(obj)
    assert test_wzdx == None


@patch.dict(os.environ, {
    'contact_name': 'Ashley Nylen',
    'contact_email': 'ashley.nylen@state.co.us',
    'issuing_organization': 'CDOT'
})
def test_wzdx_creator_invalid_incidents_no_description():
    event = {
        "sys_gUid": "Form568-cb0fdaf0-c27a-4bef-aabd-442615dfb2d6",
        "data": {
            # No description
            "srzmap": [
                {
                    "type": "LineString",
                    "coordinates": [
                        [
                            [
                                -103.17130040113868,
                                40.625392709715676
                            ],
                            [
                                -103.17889641706886,
                                40.61979008921054
                            ]
                        ]
                    ],
                },
            ],
            "streetNameFrom": "US-34",
            "directionOfTraffic": " East/West ",
            "requestedTemporarySpeed": "45",
            "workStartDate": "2021-08-09T13:00:00.000Z",
            "workEndDate": "2021-09-24T23:00:00.000Z",
            "reductionJustification": "Crews roadside.",
        }
    }
    test_wzdx = navjoy_translator.wzdx_creator(event, 'eastbound')
    assert test_wzdx == None


def test_wzdx_creator_invalid_info_object():
    event = {
        "sys_gUid": "Form568-cb0fdaf0-c27a-4bef-aabd-442615dfb2d6",
        "data": {
            "descriptionForProject": "Bridge Repairs",
            "srzmap": [
                {
                    "type": "LineString",
                    "coordinates": [
                        [
                            [
                                -103.17130040113868,
                                40.625392709715676
                            ],
                            [
                                -103.17889641706886,
                                40.61979008921054
                            ]
                        ]
                    ],
                },
            ],
            "streetNameFrom": "US-34",
            "directionOfTraffic": " East/West ",
            "requestedTemporarySpeed": "45",
            "workStartDate": "2021-08-09T13:00:00.000Z",
            "workEndDate": "2021-09-24T23:00:00.000Z",
            "reductionJustification": "Crews roadside.",
        }
    }

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
        event, 'eastbound', test_invalid_info_object)
    assert test_wzdx == None


@patch.dict(os.environ, {
    'contact_name': 'Ashley Nylen',
    'contact_email': 'ashley.nylen@state.co.us',
    'issuing_organization': 'CDOT'
})
@patch('uuid.uuid4')
@unittest.mock.patch('translator.navjoy_translator.datetime')
@unittest.mock.patch('translator.tools.date_tools.datetime')
@unittest.mock.patch('translator.tools.wzdx_translator.datetime')
def test_wzdx_creator_valid_and_invalid(mock_dt, mock_dt_2, mock_dt_3, mockuuid):
    init_datetime_mocks([mock_dt, mock_dt_2, mock_dt_3])
    uuid.uuid4 = Mock()
    uuid.uuid4.side_effect = 'we234de'
    obj = [
        {
            "sys_gUid": "Form568-cb0fdaf0-c27a-4bef-aabd-442615dfb2d6",
            "data": {
                "descriptionForProject": "Bridge Repairs",
                "srzmap": [
                    {
                        "type": "LineString",
                        "coordinates": [
                            [
                                [
                                    -104.65225365171561,
                                    40.39393671703483
                                ],
                                [
                                    -104.65228583822379,
                                    40.39342193227279
                                ],
                                [
                                    -104.64946415434012,
                                    40.39348730198451
                                ],
                                [
                                    -104.64953925619254,
                                    40.394108311080984
                                ],
                                [
                                    -104.65225365171561,
                                    40.39393671703483
                                ]
                            ]
                        ],
                    },
                ],
                "streetNameFrom": "US-34",
                "directionOfTraffic": " East/West ",
                "requestedTemporarySpeed": "45",
                "workStartDate": "2021-08-09T13:00:00.000Z",
                "workEndDate": "2021-09-24T23:00:00.000Z",
                "reductionJustification": "Crews roadside.",
            }
        },
        {
            "sys_gUid": "Form568-cb0fdaf0-c27a-4bef-aabd-442615dfb2d6",
            "data": {
                # No description
                "srzmap": [
                    {
                        "type": "LineString",
                        "coordinates": [
                            [
                                [
                                    -104.65225365171561,
                                    40.39393671703483
                                ],
                                [
                                    -104.65228583822379,
                                    40.39342193227279
                                ]
                            ]
                        ],
                    },
                ],
                "streetNameFrom": "US-34",
                "directionOfTraffic": " East/West ",
                "requestedTemporarySpeed": "45",
                "workStartDate": "2021-08-09T13:00:00.000Z",
                "workEndDate": "2021-09-24T23:00:00.000Z",
                "reductionJustification": "Crews roadside.",
            }
        }
    ]

    expected_wzdx = {
        'road_event_feed_info': {
            'feed_info_id': '2ed141dc-b998-4f7a-8395-9ae9dc7df2f8',
            'update_date': '2021-04-13T00:00:00Z',
            'publisher': 'CDOT',
            'contact_name': 'Ashley Nylen',
            'contact_email': 'ashley.nylen@state.co.us',
            'version': '3.1',
            'license': 'https://creativecommons.org/publicdomain/zero/1.0/',
            'data_sources': [
                {
                    'data_source_id': 'w',
                    'feed_info_id': '2ed141dc-b998-4f7a-8395-9ae9dc7df2f8',
                    'organization_name': 'CDOT',
                    'contact_name': 'Ashley Nylen',
                    'contact_email': 'ashley.nylen@state.co.us',
                    'update_date': '2021-04-13T00:00:00Z',
                    'location_method': 'channel-device-method',
                    'lrs_type': 'lrs_type'
                }
            ]
        },
        'type': 'FeatureCollection',
        'features': [
            {
                "type": "Feature",
                "properties": {
                    "road_event_id": '2',
                    "event_type": "work-zone",
                    "data_source_id": 'w',
                    "start_date": "2021-08-09T13:00:00Z",
                    "end_date": "2021-09-24T23:00:00Z",
                    "start_date_accuracy": "estimated",
                    "end_date_accuracy": "estimated",
                    "beginning_accuracy": "estimated",
                    "ending_accuracy": "estimated",
                    "road_names": ["US-34"],
                    "direction": "eastbound",
                    "vehicle_impact": "all-lanes-open",
                    "event_status": "planned",
                    "reduced_speed_limit": 45,
                    "description": "Bridge Repairs. Crews roadside.",
                    "creation_date": "2021-04-13T00:00:00Z",
                    "update_date": "2021-04-13T00:00:00Z"
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [
                            -104.65225365171561,
                            40.39393671703483
                        ],
                        [
                            -104.65228583822379,
                            40.39342193227279
                        ],
                        [
                            -104.64946415434012,
                            40.39348730198451
                        ],
                        [
                            -104.64953925619254,
                            40.394108311080984
                        ],
                        [
                            -104.65225365171561,
                            40.39393671703483
                        ]
                    ]
                }
            },
            {
                "type": "Feature",
                "properties": {
                    "road_event_id": '3',
                    "event_type": "work-zone",
                    "data_source_id": 'w',
                    "start_date": "2021-08-09T13:00:00Z",
                    "end_date": "2021-09-24T23:00:00Z",
                    "start_date_accuracy": "estimated",
                    "end_date_accuracy": "estimated",
                    "beginning_accuracy": "estimated",
                    "ending_accuracy": "estimated",
                    "road_names": ["US-34"],
                    "direction": "westbound",
                    "vehicle_impact": "all-lanes-open",
                    "event_status": "planned",
                    "reduced_speed_limit": 45,
                    "description": "Bridge Repairs. Crews roadside.",
                    "creation_date": "2021-04-13T00:00:00Z",
                    "update_date": "2021-04-13T00:00:00Z"
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [
                            -104.65225365171561,
                            40.39393671703483
                        ],
                        [
                            -104.65228583822379,
                            40.39342193227279
                        ],
                        [
                            -104.64946415434012,
                            40.39348730198451
                        ],
                        [
                            -104.64953925619254,
                            40.394108311080984
                        ],
                        [
                            -104.65225365171561,
                            40.39393671703483
                        ]
                    ]
                }
            }
        ]
    }

    with time_machine.travel(datetime(2021, 4, 13, 0, 0, 0)):
        test_wzdx = navjoy_translator.wzdx_creator(obj)
    assert expected_wzdx == test_wzdx


# ----------------------------------------- get_directions_from_string -----------------------------------------
def test_get_directions_from_string_valid():
    directions_string = ' East/West '
    expected = ['eastbound', 'westbound']
    actual = navjoy_translator.get_directions_from_string(directions_string)

    assert actual == expected


def test_get_directions_from_string_invalid():
    directions_string = ' Easasdt/dWest '
    expected = []
    actual = navjoy_translator.get_directions_from_string(directions_string)

    assert actual == expected


def test_get_directions_from_string_none():
    directions_string = None
    expected = []
    actual = navjoy_translator.get_directions_from_string(directions_string)

    assert actual == expected


def test_get_directions_from_string_empty_string():
    directions_string = ''
    expected = []
    actual = navjoy_translator.get_directions_from_string(directions_string)

    assert actual == expected

# ----------------------------------------- get_linestring_index -----------------------------------------


def test_get_linestring_index_valid():
    map = [
        {
            "type": "LineString",
            "coordinates": [
                [
                    [
                        -103.17130040113868,
                        40.625392709715676
                    ],
                    [
                        -103.17889641706886,
                        40.61979008921054
                    ]
                ]
            ],
        },
    ]
    expected = 0
    actual = navjoy_translator.get_linestring_index(map)

    assert actual == expected


def test_get_linestring_no_linestring():
    map = [
        {
            "type": "Polygon",
            "coordinates": [
                [
                    [
                        -103.17130040113868,
                        40.625392709715676
                    ],
                    [
                        -103.17889641706886,
                        40.61979008921054
                    ]
                ]
            ],
        },
    ]
    expected = None
    actual = navjoy_translator.get_linestring_index(map)

    assert actual == expected

# ----------------------------------------- get_polygon_index -----------------------------------------


def test_get_polygon_index_valid():
    map = [
        {
            "type": "Polygon",
            "coordinates": [
                [
                    [
                        -103.17130040113868,
                        40.625392709715676
                    ],
                    [
                        -103.17889641706886,
                        40.61979008921054
                    ]
                ]
            ],
        },
    ]
    expected = 0
    actual = navjoy_translator.get_polygon_index(map)

    assert actual == expected


def test_get_polygon_no_polygon():
    map = [
        {
            "type": "Linestring",
            "coordinates": [
                [
                    [
                        -103.17130040113868,
                        40.625392709715676
                    ],
                    [
                        -103.17889641706886,
                        40.61979008921054
                    ]
                ]
            ],
        },
    ]
    expected = None
    actual = navjoy_translator.get_polygon_index(map)

    assert actual == expected


# ----------------------------------------- get_types_of_work -----------------------------------------
def test_get_types_of_work_restriping():
    field = 'Restriping and crack seal operations.'
    expected = [{'type_name': 'surface-work',
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

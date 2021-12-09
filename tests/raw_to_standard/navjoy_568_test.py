from wzdx.raw_to_standard import navjoy_568
from tests.raw_to_standard import navjoy_translator_test_expected_results as expected_results
import uuid
import json
from unittest.mock import MagicMock, Mock, patch
from datetime import datetime
import time_machine
import time


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
            "direction": "eastbound",
            "requestedTemporarySpeed": "45",
            "workStartDate": "2021-08-09T13:00:00.000Z",
            "workEndDate": "2021-09-24T23:00:00.000Z",
            "reductionJustification": "Crews roadside.",
        }
    }
    assert navjoy_568.validate_closure(event) == True


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
    assert navjoy_568.validate_closure(event) == False


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
    assert navjoy_568.validate_closure(event) == False


def test_validate_closure_invalid():
    event = 'invalid output'
    assert navjoy_568.validate_closure(event) == False


def test_validate_closure_no_data():
    event = None
    assert navjoy_568.validate_closure(event) == False


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
    assert navjoy_568.validate_closure(event) == False


# ----------------------------------------- get_directions_from_string -----------------------------------------
def test_get_directions_from_string_valid():
    directions_string = ' East/West '
    expected = ['eastbound', 'westbound']
    actual = navjoy_568.get_directions_from_string(directions_string)

    assert actual == expected


def test_get_directions_from_string_invalid():
    directions_string = ' Easasdt/dWest '
    expected = []
    actual = navjoy_568.get_directions_from_string(directions_string)

    assert actual == expected


def test_get_directions_from_string_none():
    directions_string = None
    expected = []
    actual = navjoy_568.get_directions_from_string(directions_string)

    assert actual == expected


def test_get_directions_from_string_empty_string():
    directions_string = ''
    expected = []
    actual = navjoy_568.get_directions_from_string(directions_string)

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
    actual = navjoy_568.get_linestring_index(map)

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
    actual = navjoy_568.get_linestring_index(map)

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
    actual = navjoy_568.get_polygon_index(map)

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
    actual = navjoy_568.get_polygon_index(map)

    assert actual == expected


def test_expand_speed_zone_1():
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
            'currentPostedSpeed': None,
            'mileMarkerEnd': None,
            'mileMarkerStart': None,
        }
    }

    actual = navjoy_568.expand_speed_zone(event)

    assert expected_results.test_expand_speed_zone_1_expected == actual


def test_expand_speed_zone_2():
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
            "reductionJustification": "Crews roadside.",

            "streetNameFrom2": "US-34",
            "directionOfTraffic2": " East/West ",
            "requestedTemporarySpeed2": "45",
            "workStartDate2": "2021-08-09T13:00:00.000Z",
            "workEndDate2": "2021-09-24T23:00:00.000Z",
            'currentPostedSpeed2': None,
            'mileMarkerEnd2': None,
            'mileMarkerStart2': None,
        }
    }

    actual = navjoy_568.expand_speed_zone(event)

    assert expected_results.test_expand_speed_zone_2_expected == actual


# I hate how long this test is, but this is what is has to be to test all 4 at the same time
def test_expand_speed_zone_2_3_4():
    event = {
        "sys_gUid": "Form568-cb0fdaf0-c27a-4bef-aabd-442615dfb2d6",
        "data": {
            "srzmap": [
            ],
            "reductionJustification": "Crews roadside.",
            "streetNameFrom": "US-34",
            "directionOfTraffic": " East/West ",
            "requestedTemporarySpeed": "1",
            "workStartDate": "2021-08-09T13:00:00.000Z",
            "workEndDate": "2021-09-24T23:00:00.000Z",
            'currentPostedSpeed': None,
            'mileMarkerEnd': None,
            'mileMarkerStart': None,

            "streetNameFrom2": "US-34",
            "directionOfTraffic2": " East/West ",
            "requestedTemporarySpeed2": "2",
            "workStartDate2": "2021-08-09T13:00:00.000Z",
            "workEndDate2": "2021-09-24T23:00:00.000Z",
            'currentPostedSpeed2': None,
            'mileMarkerEnd2': None,
            'mileMarkerStart2': None,

            "streetNameFrom3": "US-34",
            "directionOfTraffic3": " East/West ",
            "requestedTemporarySpeed3": "3",
            "workStartDate3": "2021-08-09T13:00:00.000Z",
            "workEndDate3": "2021-09-24T23:00:00.000Z",
            'currentPostedSpeed3': None,
            'mileMarkerEnd3': None,
            'mileMarkerStart3': None,

            "streetNameFrom4": "US-34",
            "directionOfTraffic4": " East/West ",
            "requestedTemporarySpeed4": "4",
            "workStartDate4": "2021-08-09T13:00:00.000Z",
            "workEndDate4": "2021-09-24T23:00:00.000Z",
            'currentPostedSpeed4': None,
            'mileMarkerEnd4': None,
            'mileMarkerStart4': None,
        }
    }

    actual = navjoy_568.expand_speed_zone(event)

    assert expected_results.test_expand_speed_zone_2_3_4_expected == actual


@patch('uuid.uuid4')
def test_generate_standard_messages_from_string(mockuuid):
    uuid.uuid4 = Mock()
    uuid.uuid4.side_effect = ['we234de', '23wsg54h', '7fa1dfas', '23h327j']
    xml_string = """[
    {
        "sys_gUid": "Form568-6ab4408e-d9c1-4ac0-ab1d-b16feb17f18d",
        "data": {
            "srzmap": [
                {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [
                                -104.67900571959923,
                                40.42358701413087
                            ],
                            [
                                -104.6784049047799,
                                40.42358701413087
                            ],
                            [
                                -104.67841563361596,
                                40.422517055735916
                            ],
                            [
                                -104.67902717727135,
                                40.42254155879033
                            ],
                            [
                                -104.67900571959923,
                                40.42358701413087
                            ]
                        ]
                    ],
                    "className": "Form568"
                },
                {
                    "type": "Point",
                    "coordinates": [
                        -104.67878764081412,
                        40.42327902840428
                    ],
                    "className": "text"
                }
            ],
            "cdotEngineeringRegionNumber": "4",
            "methodOfHandlingTraffic": [],
            "professionalEngineerStamp/Certification": [],
            "permits": [],
            "cdotSection/DepartmentName": "LA Projects",
            "cdotPatrolNumber/Id": "1",
            "subAccountNumber": "48976-A",
            "mpaCode": "789465",
            "descriptionForProject": "Bridge Repair and replacement.",
            "streetNameFrom": "US-85",
            "mileMarkerStart": "47.25",
            "mileMarkerEnd": "47.30",
            "directionOfTraffic": " North/South",
            "currentPostedSpeed": "45",
            "requestedTemporarySpeed": "35",
            "reductionJustification": "Repairing and replacing the bridge. Crews will be roadside, various alternating single lane closures.",
            "document": [],
            "approval": {
                "description": "",
                "value": "Approved"
            },
            "signature": {
                "url": "https://assetgovprod.s3-us-west-2.amazonaws.com/Documents/Signature/Files/signature--938878001",
                "date": "2021-05-11T16:25:45.352Z",
                "name": "Jonathan Woodworth"
            },
            "workStartDate": "2021-08-02T12:00:00.000Z",
            "workEndDate": "2021-10-30T00:00:00.000Z",
            "cdotProjectEngineerName": {
                "sys_gUid": "User-905f1bf6-05fb-4354-beb8-8f095203f7d8",
                "firstName": "Bryce",
                "lastName": "Reeves",
                "title": "Traffic Design and LA Projects Manager"
            },
            "requestorName": {
                "sys_gUid": "User-905f1bf6-05fb-4354-beb8-8f095203f7d8",
                "username": "bryce.reeves@state.co.us",
                "firstName": "Bryce",
                "lastName": "Reeves",
                "agencyuser": "CDOT Region 4",
                "roleName": "CDOT Projects Requestor",
                "email": "bryce.reeves@state.co.us",
                "Name": "CDOT Region 4",
                "title": "Traffic Design and LA Projects Manager"
            },
            "taskChecklist": [
                "Is the Required Information Tab Complete?",
                "Are the requester and CDOT Engineer details accurate?",
                "Are the speed reduction details and the SRZ polygon accurate?",
                "Is the requested speed reduction valid based on the criteria shown in the Authority tab?"
            ]
        }
    },
    {
        "sys_gUid": "Form568-2f560979-b6e9-4d28-a6e1-6120066ee992",
        "data": {
            "srzmap": [
                {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [
                                -104.68031879637711,
                                40.418367644368814
                            ],
                            [
                                -104.67920299742691,
                                40.418367644368814
                            ],
                            [
                                -104.67928882811539,
                                40.40980683657896
                            ],
                            [
                                -104.68074794981949,
                                40.40980683657896
                            ],
                            [
                                -104.68031879637711,
                                40.418367644368814
                            ]
                        ]
                    ],
                    "className": "Form568"
                },
                {
                    "type": "Point",
                    "coordinates": [
                        -104.67991855002329,
                        40.415730628325946
                    ],
                    "className": "text"
                }
            ],
            "cdotEngineeringRegionNumber": "4",
            "methodOfHandlingTraffic": [],
            "professionalEngineerStamp/Certification": [],
            "permits": [],
            "cdotSection/DepartmentName": "Traffic and LA Projects",
            "cdotPatrolNumber/Id": "1",
            "subAccountNumber": "1458-A",
            "mpaCode": "124578",
            "descriptionForProject": "Restriping operations.",
            "streetNameFrom": "US-85",
            "mileMarkerStart": "48",
            "mileMarkerEnd": "50",
            "directionOfTraffic": " North/South",
            "currentPostedSpeed": "45",
            "requestedTemporarySpeed": "35",
            "workStartDate": "2021-06-07T13:00:00.000Z",
            "workEndDate": "2021-06-25T23:00:00.000Z",
            "reductionJustification": "Crews will be roadside restriping in various alternating lane closures.",
            "document": [],
            "approval": {
                "description": "",
                "value": "Approved"
            },
            "cdotProjectEngineerName": {
                "sys_gUid": "User-905f1bf6-05fb-4354-beb8-8f095203f7d8",
                "firstName": "Bryce",
                "lastName": "Reeves",
                "title": "Traffic Design and LA Projects Manager"
            },
            "requestorName": {
                "sys_gUid": "User-905f1bf6-05fb-4354-beb8-8f095203f7d8",
                "username": "bryce.reeves@state.co.us",
                "firstName": "Bryce",
                "lastName": "Reeves",
                "agencyuser": "CDOT Region 4",
                "roleName": "CDOT Projects Requestor",
                "email": "bryce.reeves@state.co.us",
                "Name": "CDOT Region 4",
                "title": "Traffic Design and LA Projects Manager"
            },
            "taskChecklist": [
                "Is the Required Information Tab Complete?",
                "Are the requester and CDOT Engineer details accurate?",
                "Are the speed reduction details and the SRZ polygon accurate?",
                "Is the requested speed reduction valid based on the criteria shown in the Authority tab?"
            ],
            "signature": {
                "url": "https://assetgovprod.s3-us-west-2.amazonaws.com/Documents/Signature/Files/signature--938878001",
                "date": "2021-05-11T16:16:35.783Z",
                "name": "Jonathan Woodworth"
            }
        }
    }
    ]"""
    actual_standard = json.loads(json.dumps(navjoy_568.generate_standard_messages_from_string(
        xml_string)))
    for i in actual_standard:
        del i['rtdh_timestamp']
        del i['event']['source']['last_updated_timestamp']
    expected = expected_results.test_generate_standard_messages_from_string_expected
    for i in expected:
        del i['rtdh_timestamp']
        del i['event']['source']['last_updated_timestamp']
    # actual_standard = [dict(x) for x in actual_standard]
    assert actual_standard == expected

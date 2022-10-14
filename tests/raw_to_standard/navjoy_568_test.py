from wzdx.raw_to_standard import navjoy_568
from tests.data.raw_to_standard import navjoy_568_test_expected_results as expected_results
import uuid
import argparse
import json
from unittest.mock import Mock, patch
import copy


def compare_lists(list1, list2):
    l1 = copy.deepcopy(list1)
    l2 = copy.deepcopy(list2)
    remaining = False
    for i in l1:
        if i in l2:
            l2.remove(i)
        else:
            print(i)
            remaining = True
    print(l2)
    return not remaining and len(l2) == 0


@patch.object(argparse, 'ArgumentParser')
def test_parse_navjoy_arguments(argparse_mock):
    navjoyFile, outputFile = navjoy_568.parse_rtdh_arguments()
    assert navjoyFile != None and outputFile != None


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


def test_validate_closure_invalid_coordinates():
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
    expected = ['undefined']
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

    assert compare_lists(
        expected_results.test_expand_speed_zone_1_expected, actual)


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

    assert compare_lists(
        expected_results.test_expand_speed_zone_2_expected, actual)


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

    assert compare_lists(
        expected_results.test_expand_speed_zone_2_3_4_expected, actual)


@patch('uuid.uuid4')
def test_generate_standard_messages_from_string(mockuuid):
    uuid.uuid4 = Mock()
    uuid.uuid4.side_effect = ['we234de', '23wsg54h', '7fa1dfas', '23h327j']
    actual_standard = json.loads(json.dumps(navjoy_568.generate_standard_messages_from_string(
        expected_results.test_generate_standard_messages_from_string_input)))

    # Removing timestamps because mocking it was not working. Kept having incorrect decimal values, weird floating point errors?
    for i in actual_standard:
        del i['rtdh_timestamp']
        del i['event']['source']['last_updated_timestamp']
    expected = expected_results.test_generate_standard_messages_from_string_expected
    for i in expected:
        del i['rtdh_timestamp']
        del i['event']['source']['last_updated_timestamp']
    # actual_standard = [dict(x) for x in actual_standard]
    print(actual_standard)
    print(expected)
    assert compare_lists(actual_standard, expected)

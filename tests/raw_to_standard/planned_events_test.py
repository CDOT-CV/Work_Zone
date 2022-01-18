from wzdx.raw_to_standard import planned_events
from tests.raw_to_standard import planned_events_test_expected_results as expected_results
import uuid
import json
from unittest.mock import MagicMock, Mock, patch
from datetime import datetime
import time_machine
import time


# --------------------------------------------------------------------------------Unit test for validate_closure function--------------------------------------------------------------------------------
def test_validate_closure_valid_data():
    event = {
        "type": "Feature",
        "geometry": {
            "srid": 4326,
            "type": "MultiPoint",
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
        },
        "properties": {
            "clearTime": "2022-05-01T18:26:04.000+00:00",
            "startMarker": 50.0,
            "type": "Bridge Construction",
            "laneImpacts": [
                {
                    "direction": "east",
                    "laneCount": 2,
                    "laneClosures": "6000",
                    "closedLaneTypes": [
                        "left lane",
                        "right lane"
                    ]
                },
                {
                    "direction": "west",
                    "laneCount": 2,
                    "laneClosures": "0",
                    "closedLaneTypes": []
                }
            ],
            "routeName": "I-70E",
            "isOversizedLoadsProhibited": True,
            "lastUpdated": "2021-10-29T18:35:01.835+00:00",
            "schedule": [
                {
                    "startTime": "2021-10-29T18:26:04.000Z",
                    "endTime": "2022-05-01T18:26:04.000Z"
                }
            ],
            "endMarker": 60.0,
            "startTime": "2021-10-29T18:26:04.000+00:00",
            "id": "OpenTMS-Event1689408506",
            "travelerInformationMessage": "Between Exit 49: CO 65; Grand Mesa (5 miles east of the Palisade area) and US 6 (Debeque) from Mile Point 50 to Mile Point 60. Road closed expect delays due to bridge construction. Until May 1, 2022 at about 12:26PM MDT.",
            "direction": "east"
        },
        "attributes": {}
    }
    assert planned_events.validate_closure(event) == True


def test_validate_closure_missing_required_field_description():
    event = {
        "type": "Feature",
        "geometry": {
            "srid": 4326,
            "type": "MultiPoint",
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
        },
        "properties": {
            "clearTime": "2022-05-01T18:26:04.000+00:00",
            "startMarker": 50.0,
            "type": "Bridge Construction",
            "laneImpacts": [
                {
                    "direction": "east",
                    "laneCount": 2,
                    "laneClosures": "6000",
                    "closedLaneTypes": [
                        "left lane",
                        "right lane"
                    ]
                },
                {
                    "direction": "west",
                    "laneCount": 2,
                    "laneClosures": "0",
                    "closedLaneTypes": []
                }
            ],
            "routeName": "I-70E",
            "isOversizedLoadsProhibited": True,
            "lastUpdated": "2021-10-29T18:35:01.835+00:00",
            "schedule": [
                {
                    "startTime": "2021-10-29T18:26:04.000Z",
                    "endTime": "2022-05-01T18:26:04.000Z"
                }
            ],
            "endMarker": 60.0,
            "startTime": "2021-10-29T18:26:04.000+00:00",
            "id": "OpenTMS-Event1689408506",
            "direction": "east"
        },
        "attributes": {}
    }
    assert planned_events.validate_closure(event) == False


def test_validate_closure_invalid_start_time():
    event = {
        "type": "Feature",
        "geometry": {
            "srid": 4326,
            "type": "MultiPoint",
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
        },
        "properties": {
            "clearTime": "2022-05-01T18:26:04.000+00:00",
            "startMarker": 50.0,
            "type": "Bridge Construction",
            "laneImpacts": [
                {
                    "direction": "east",
                    "laneCount": 2,
                    "laneClosures": "6000",
                    "closedLaneTypes": [
                        "left lane",
                        "right lane"
                    ]
                },
                {
                    "direction": "west",
                    "laneCount": 2,
                    "laneClosures": "0",
                    "closedLaneTypes": []
                }
            ],
            "routeName": "I-70E",
            "isOversizedLoadsProhibited": True,
            "lastUpdated": "2021-10-29T18:35:01.835+00:00",
            "schedule": [
                {
                    "startTime": "2021-10-29T18:26:04.000Z",
                    "endTime": "2022-05-01T18:26:04.000Z"
                }
            ],
            "endMarker": 60.0,
            "startTime": 1713004011,
            "id": "OpenTMS-Event1689408506",
            "direction": "east"
        },
        "attributes": {}
    }

    assert planned_events.validate_closure(event) == False


def test_validate_closure_invalid():
    event = 'invalid output'
    assert planned_events.validate_closure(event) == False


def test_validate_closure_no_data():
    event = None
    assert planned_events.validate_closure(event) == False


def test_validate_closure_no_coordinates():
    event = {
        "type": "Feature",
        "geometry": {
            "srid": 4326,
            "type": "MultiPoint",
        },
        "properties": {
            "clearTime": "2022-05-01T18:26:04.000+00:00",
            "startMarker": 50.0,
            "type": "Bridge Construction",
            "laneImpacts": [
                {
                    "direction": "east",
                    "laneCount": 2,
                    "laneClosures": "6000",
                    "closedLaneTypes": [
                        "left lane",
                        "right lane"
                    ]
                },
                {
                    "direction": "west",
                    "laneCount": 2,
                    "laneClosures": "0",
                    "closedLaneTypes": []
                }
            ],
            "routeName": "I-70E",
            "isOversizedLoadsProhibited": True,
            "lastUpdated": "2021-10-29T18:35:01.835+00:00",
            "schedule": [
                {
                    "startTime": "2021-10-29T18:26:04.000Z",
                    "endTime": "2022-05-01T18:26:04.000Z"
                }
            ],
            "endMarker": 60.0,
            "startTime": 1713004011,
            "id": "OpenTMS-Event1689408506",
            "direction": "east"
        },
        "attributes": {}
    }
    assert planned_events.validate_closure(event) == False


# ----------------------------------------- get_directions_from_string -----------------------------------------
def test_map_direction_string_valid():
    directions_string = 'east'
    expected = 'eastbound'
    actual = planned_events.map_direction_string(directions_string)

    assert actual == expected


def test_map_directions_from_string_invalid():
    directions_string = 'Easasdt'
    expected = None
    actual = planned_events.map_direction_string(directions_string)

    assert actual == expected


def test_map_directions_from_string_none():
    directions_string = None
    expected = None
    actual = planned_events.map_direction_string(directions_string)

    assert actual == expected


def test_map_directions_from_string_empty_string():
    directions_string = ''
    expected = None
    actual = planned_events.map_direction_string(directions_string)

    assert actual == expected


def test_expand_event_directions_1():
    event = {
        "properties": {
            "laneImpacts": [
                {
                    "direction": "east",
                    "laneCount": 2,
                    "laneClosures": "6000",
                    "closedLaneTypes": [
                        "left lane",
                        "right lane"
                    ]
                },
                {
                    "direction": "west",
                    "laneCount": 2,
                    "laneClosures": "0",
                    "closedLaneTypes": []
                }
            ],
            "direction": "east"
        }
    }

    actual = planned_events.expand_event_directions(event)
    print(actual)

    assert expected_results.test_expand_speed_zone_1_expected == actual


def test_expand_event_directions_2():
    event = {
        "type": "Feature",
        "geometry": {
            "srid": 4326,
            "type": "MultiPoint",
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
        },
        "properties": {
            "clearTime": "2022-05-01T18:26:04.000+00:00",
            "startMarker": 50.0,
            "type": "Bridge Construction",
            "laneImpacts": [
                {
                    "direction": "east",
                    "laneCount": 2,
                    "laneClosures": "6000",
                    "closedLaneTypes": [
                        "left lane",
                        "right lane"
                    ]
                }
            ],
            "routeName": "I-70E",
            "isOversizedLoadsProhibited": True,
            "lastUpdated": "2021-10-29T18:35:01.835+00:00",
            "schedule": [
                {
                    "startTime": "2021-10-29T18:26:04.000Z",
                    "endTime": "2022-05-01T18:26:04.000Z"
                }
            ],
            "endMarker": 60.0,
            "startTime": "2021-10-29T18:26:04.000+00:00",
            "id": "OpenTMS-Event1689408506",
            "travelerInformationMessage": "Between Exit 49: CO 65; Grand Mesa (5 miles east of the Palisade area) and US 6 (Debeque) from Mile Point 50 to Mile Point 60. Road closed expect delays due to bridge construction. Until May 1, 2022 at about 12:26PM MDT.",
            "direction": "east"
        },
        "attributes": {}
    }

    actual = planned_events.expand_event_directions(event)

    assert expected_results.test_expand_speed_zone_2_expected == actual


@patch('uuid.uuid4')
def test_generate_standard_messages_from_string(mockuuid):
    uuid.uuid4 = Mock()
    uuid.uuid4.side_effect = ['we234de', '23wsg54h']
    xml_string = """
    {
        "type": "Feature",
        "geometry": {
            "srid": 4326,
            "type": "MultiPoint",
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
        },
        "properties": {
            "clearTime": "2022-05-01T18:26:04.000+00:00",
            "startMarker": 50.0,
            "type": "Bridge Construction",
            "laneImpacts": [
                {
                    "direction": "east",
                    "laneCount": 2,
                    "laneClosures": "6000",
                    "closedLaneTypes": [
                        "left lane",
                        "right lane"
                    ]
                },
                {
                    "direction": "west",
                    "laneCount": 2,
                    "laneClosures": "0",
                    "closedLaneTypes": []
                }
            ],
            "routeName": "I-70E",
            "isOversizedLoadsProhibited": true,
            "lastUpdated": "2021-10-29T18:35:01.835+00:00",
            "schedule": [
                {
                    "startTime": "2021-10-29T18:26:04.000Z",
                    "endTime": "2022-05-01T18:26:04.000Z"
                }
            ],
            "endMarker": 60.0,
            "startTime": "2021-10-29T18:26:04.000+00:00",
            "id": "OpenTMS-Event1689408506",
            "travelerInformationMessage": "Between Exit 49: CO 65; Grand Mesa (5 miles east of the Palisade area) and US 6 (Debeque) from Mile Point 50 to Mile Point 60. Road closed expect delays due to bridge construction. Until May 1, 2022 at about 12:26PM MDT.",
            "direction": "east"
        },
        "attributes": {}
    }
    """
    actual_standard = json.loads(json.dumps(planned_events.generate_standard_messages_from_string(
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


def test_get_lanes_list():
    lane_closures_hex = '6000'
    num_lanes = 2
    closedLaneTypes = ["left lane", "right lane"]

    expected = [{
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
    assert planned_events.get_lanes_list(
        lane_closures_hex, num_lanes, closedLaneTypes) == expected


def test_get_lanes_list():
    lane_closures_hex = 'F001'
    num_lanes = 3
    closedLaneTypes = ["left shoulder", "left lane",
                       "center lane", "right lane", "right shoulder"]

    expected = [
        {'order': 1, 'type': 'shoulder', 'status': 'closed'},
        {'order': 2, 'type': 'general', 'status': 'closed'},
        {'order': 3, 'type': 'general', 'status': 'closed'},
        {'order': 4, 'type': 'general', 'status': 'closed'},
        {'order': 5, 'type': 'shoulder', 'status': 'closed'}]
    print(planned_events.get_lanes_list(
        lane_closures_hex, num_lanes, closedLaneTypes))
    assert planned_events.get_lanes_list(
        lane_closures_hex, num_lanes, closedLaneTypes) == expected

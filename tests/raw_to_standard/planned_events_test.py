from wzdx.raw_to_standard import planned_events
from tests.raw_to_standard import planned_events_test_expected_results as expected_results
import uuid
import json
from unittest.mock import MagicMock, patch


# --------------------------------------------------------------------------------Unit test for validate_closure function--------------------------------------------------------------------------------
def test_validate_closure_valid_data():
    assert planned_events.validate_closure(
        expected_results.test_validate_closure_valid_data_input) == True


def test_validate_closure_missing_required_field_description():
    assert planned_events.validate_closure(
        expected_results.test_validate_closure_missing_required_field_description_input) == False


def test_validate_closure_invalid_start_time():
    assert planned_events.validate_closure(
        expected_results.test_validate_closure_invalid_start_time_input) == False


def test_validate_closure_invalid():
    event = 'invalid output'
    assert planned_events.validate_closure(event) == False


def test_validate_closure_no_data():
    event = None
    assert planned_events.validate_closure(event) == False


def test_validate_closure_no_coordinates():
    assert planned_events.validate_closure(
        expected_results.test_validate_closure_no_coordinates_input) == False


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


@patch.object(uuid, 'uuid4', side_effect=['we234de', '23wsg54h'])
def test_generate_standard_messages_from_string(_):
    actual_standard = json.loads(json.dumps(planned_events.generate_standard_messages_from_string(
        expected_results.test_generate_standard_messages_from_string_input)))
    for i in actual_standard:
        del i['rtdh_timestamp']
        del i['event']['source']['last_updated_timestamp']
    expected = expected_results.test_generate_standard_messages_from_string_expected
    for i in expected:
        del i['rtdh_timestamp']
        del i['event']['source']['last_updated_timestamp']
    # actual_standard = [dict(x) for x in actual_standard]
    print(actual_standard)
    assert actual_standard == expected


def test_get_lanes_list_1():
    lane_closures_hex = '6000'
    num_lanes = 2
    closedLaneTypes = ["left lane", "right lane"]

    expected = [
        {
            "order": 1,
            "type": "general",
            "status": "closed"
        },
        {
            "order": 2,
            "type": "general",
            "status": "closed"
        }
    ]
    assert planned_events.get_lanes_list(
        lane_closures_hex, num_lanes, closedLaneTypes) == expected


def test_get_lanes_list_2():
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


def test_is_incident_true_true():
    msg = {
        "properties": {
            "id": "OpenTMS-Incident2028603626",
            "type": "Emergency Roadwork"
        }
    }
    # is_incident, is_wz
    expected = (True, True)
    actual = planned_events.is_incident_wz(msg)
    assert actual == expected


def test_is_incident_true_false():
    msg = {
        "properties": {
            "id": "OpenTMS-Incident2028603626",
            "type": "Chain Law Code 18"
        }
    }
    expected = (True, False)
    actual = planned_events.is_incident_wz(msg)
    assert actual == expected


def test_is_incident_false_false():
    msg = {
        "properties": {
            "id": "OpenTMS-Event2702170538",
            "type": "Chain Law Code 18"
        }
    }
    expected = (False, False)
    actual = planned_events.is_incident_wz(msg)
    assert actual == expected


@patch.object(planned_events, 'create_rtdh_standard_msg')
def test_generate_rtdh_standard_message_from_raw_single_incident_valid(mocked_create_rtdh_standard_msg):
    planned_events.create_rtdh_standard_msg = MagicMock(return_value=True)

    msg = {
        "properties": {
            "id": "OpenTMS-Incident2028603626",
            "type": "Emergency Roadwork"
        }
    }
    actual = planned_events.generate_rtdh_standard_message_from_raw_single(msg)
    assert actual != {}


@patch.object(planned_events, 'create_rtdh_standard_msg')
def test_generate_rtdh_standard_message_from_raw_single_incident_invalid(mocked_create_rtdh_standard_msg):
    planned_events.create_rtdh_standard_msg = MagicMock(return_value=True)

    msg = {
        "properties": {
            "id": "OpenTMS-Incident2028603626",
            "type": "Chain Law Code 18"
        }
    }
    actual = planned_events.generate_rtdh_standard_message_from_raw_single(msg)
    assert actual == {}


def test_is_incident_wz_true_1():
    msg = {}
    msg['properties'] = {}
    msg['properties']['id'] = 'OpenTMS-Incident2028603626'
    msg['properties']['type'] = 'Maintenance Operations'

    actual = planned_events.is_incident_wz(msg)

    assert actual == (True, True)


def test_is_incident_wz_false_1():
    msg = {}
    msg['properties'] = {}
    msg['properties']['id'] = 'OpenTMS-Incident2028603626'
    msg['properties']['type'] = 'Crash Unknown'

    actual = planned_events.is_incident_wz(msg)

    assert actual == (True, False)


def test_is_incident_wz_false_2():
    msg = {}
    msg['properties'] = {}
    msg['properties']['id'] = 'OpenTMS-Event2843552682'
    msg['properties']['type'] = 'Road Construction'

    actual = planned_events.is_incident_wz(msg)

    assert actual == (False, False)

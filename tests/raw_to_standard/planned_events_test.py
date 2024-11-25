import math
from wzdx.raw_to_standard import planned_events
from tests.data.raw_to_standard import (
    description_arsenal,
    planned_events_test_expected_results as expected_results,
)
from wzdx.tools import cdot_geospatial_api, geospatial_tools
import uuid
import argparse
import json
from unittest.mock import MagicMock, patch


@patch.object(argparse, "ArgumentParser")
def test_parse_navjoy_arguments(argparse_mock):
    navjoyFile, outputFile = planned_events.parse_rtdh_arguments()
    assert navjoyFile != None and outputFile != None


# --------------------------------------------------------------------------------Unit test for validate_closure function--------------------------------------------------------------------------------


def test_validate_closure_valid_data():
    assert (
        planned_events.validate_closure(
            expected_results.test_validate_closure_valid_data_input
        )
        == True
    )


def test_validate_closure_missing_required_field_description():
    assert (
        planned_events.validate_closure(
            expected_results.test_validate_closure_missing_required_field_description_input
        )
        == False
    )


def test_validate_closure_invalid_start_time():
    assert (
        planned_events.validate_closure(
            expected_results.test_validate_closure_invalid_start_time_input
        )
        == False
    )


def test_validate_closure_invalid():
    event = "invalid output"
    assert planned_events.validate_closure(event) == False


def test_validate_closure_no_data():
    event = None
    assert planned_events.validate_closure(event) == False


def test_validate_closure_no_coordinates():
    assert (
        planned_events.validate_closure(
            expected_results.test_validate_closure_no_coordinates_input
        )
        == False
    )


# ----------------------------------------- get_directions_from_string -----------------------------------------
def test_map_direction_string_valid():
    directions_string = "east"
    actual = planned_events.map_direction_string(directions_string)

    assert actual == "eastbound"


def test_map_directions_from_string_invalid():
    directions_string = "Easasdt"
    actual = planned_events.map_direction_string(directions_string)

    assert actual == "undefined"


def test_map_directions_from_string_none():
    directions_string = None
    actual = planned_events.map_direction_string(directions_string)

    assert actual == "undefined"


def test_map_directions_from_string_empty_string():
    directions_string = ""
    actual = planned_events.map_direction_string(directions_string)

    assert actual == "undefined"


def test_expand_event_directions_1():
    event = {
        "properties": {
            "laneImpacts": [
                {
                    "direction": "east",
                    "laneCount": 2,
                    "laneClosures": "6000",
                    "closedLaneTypes": ["left lane", "right lane"],
                },
                {
                    "direction": "west",
                    "laneCount": 2,
                    "laneClosures": "0",
                    "closedLaneTypes": [],
                },
            ],
            "direction": "east",
        }
    }

    actual = planned_events.expand_event_directions(event)

    assert expected_results.test_expand_speed_zone_1_expected == actual


def test_expand_event_directions_2():
    event = {
        "type": "Feature",
        "geometry": {
            "srid": 4326,
            "type": "MultiPoint",
            "coordinates": [[-108.279106, 39.195663], [-108.218549, 39.302392]],
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
                    "closedLaneTypes": ["left lane", "right lane"],
                }
            ],
            "routeName": "I-70E",
            "isOversizedLoadsProhibited": True,
            "lastUpdated": "2021-10-29T18:35:01.835+00:00",
            "schedule": [
                {
                    "startTime": "2021-10-29T18:26:04.000Z",
                    "endTime": "2022-05-01T18:26:04.000Z",
                }
            ],
            "endMarker": 60.0,
            "startTime": "2021-10-29T18:26:04.000+00:00",
            "id": "OpenTMS-Event1689408506",
            "travelerInformationMessage": "Between Exit 49: CO 65; Grand Mesa (5 miles east of the Palisade area) and US 6 (Debeque) from Mile Point 50 to Mile Point 60. Road closed expect delays due to bridge construction. Until May 1, 2022 at about 12:26PM MDT.",
            "direction": "east",
        },
        "attributes": {},
    }

    actual = planned_events.expand_event_directions(event)

    assert expected_results.test_expand_speed_zone_2_expected == actual


@patch.object(uuid, "uuid4", side_effect=["we234de", "23wsg54h"])
def test_generate_standard_messages_from_string(_):
    actual_standard = json.loads(
        json.dumps(
            planned_events.generate_standard_messages_from_string(
                cdot_geospatial_api.GeospatialApi(),
                expected_results.test_generate_standard_messages_from_string_input,
            )
        )
    )
    for i in actual_standard:
        del i["rtdh_timestamp"]
        del i["event"]["source"]["last_updated_timestamp"]
    expected = expected_results.test_generate_standard_messages_from_string_expected
    for i in expected:
        del i["rtdh_timestamp"]
        del i["event"]["source"]["last_updated_timestamp"]
    # actual_standard = [dict(x) for x in actual_standard]
    assert actual_standard == expected


def test_get_lanes_list_1():
    lane_closures_hex = "6000"
    num_lanes = 2
    closedLaneTypes = ["left lane", "right lane"]

    expected = [
        {"order": 1, "type": "general", "status": "closed"},
        {"order": 2, "type": "general", "status": "closed"},
    ]
    assert (
        planned_events.get_lanes_list(lane_closures_hex, num_lanes, closedLaneTypes)
        == expected
    )


def test_get_lanes_list_2():
    lane_closures_hex = "F001"
    num_lanes = 3
    closedLaneTypes = [
        "left shoulder",
        "left lane",
        "center lane",
        "right lane",
        "right shoulder",
    ]

    expected = [
        {"order": 1, "type": "shoulder", "status": "closed"},
        {"order": 2, "type": "general", "status": "closed"},
        {"order": 3, "type": "general", "status": "closed"},
        {"order": 4, "type": "general", "status": "closed"},
        {"order": 5, "type": "shoulder", "status": "closed"},
    ]
    assert (
        planned_events.get_lanes_list(lane_closures_hex, num_lanes, closedLaneTypes)
        == expected
    )


def test_is_incident_true_true():
    msg = {
        "properties": {"id": "OpenTMS-Incident2028603626", "type": "Emergency Roadwork"}
    }
    # is_incident, is_wz
    expected = (True, True)
    actual = planned_events.is_incident_wz(msg)
    assert actual == expected


def test_is_incident_true_false():
    msg = {
        "properties": {"id": "OpenTMS-Incident2028603626", "type": "Chain Law Code 18"}
    }
    expected = (True, False)
    actual = planned_events.is_incident_wz(msg)
    assert actual == expected


def test_is_incident_false_false():
    msg = {"properties": {"id": "OpenTMS-Event2702170538", "type": "Chain Law Code 18"}}
    expected = (False, False)
    actual = planned_events.is_incident_wz(msg)
    assert actual == expected


@patch.object(planned_events, "create_rtdh_standard_msg")
def test_generate_rtdh_standard_message_from_raw_single_incident_valid(
    mocked_create_rtdh_standard_msg,
):
    planned_events.create_rtdh_standard_msg = MagicMock(return_value=True)

    msg = {
        "properties": {"id": "OpenTMS-Incident2028603626", "type": "Emergency Roadwork"}
    }
    actual = planned_events.generate_rtdh_standard_message_from_raw_single(
        cdot_geospatial_api.GeospatialApi(), msg
    )
    assert actual != {}


@patch.object(planned_events, "create_rtdh_standard_msg")
def test_generate_rtdh_standard_message_from_raw_single_incident_invalid(
    mocked_create_rtdh_standard_msg,
):
    planned_events.create_rtdh_standard_msg = MagicMock(return_value=True)

    msg = {
        "properties": {"id": "OpenTMS-Incident2028603626", "type": "Chain Law Code 18"}
    }
    actual = planned_events.generate_rtdh_standard_message_from_raw_single(
        cdot_geospatial_api.GeospatialApi(), msg
    )
    assert actual == {}


def test_is_incident_wz_true_1():
    msg = {}
    msg["properties"] = {}
    msg["properties"]["id"] = "OpenTMS-Incident2028603626"
    msg["properties"]["type"] = "Maintenance Operations"

    actual = planned_events.is_incident_wz(msg)

    assert actual == (True, True)


def test_is_incident_wz_false_1():
    msg = {}
    msg["properties"] = {}
    msg["properties"]["id"] = "OpenTMS-Incident2028603626"
    msg["properties"]["type"] = "Crash Unknown"

    actual = planned_events.is_incident_wz(msg)

    assert actual == (True, False)


def test_is_incident_wz_false_2():
    msg = {}
    msg["properties"] = {}
    msg["properties"]["id"] = "OpenTMS-Event2843552682"
    msg["properties"]["type"] = "Road Construction"

    actual = planned_events.is_incident_wz(msg)

    assert actual == (False, False)


class MockGeospatialApi:
    def __init__(
        self, getCachedRequest=lambda x: None, setCachedRequest=lambda x, y: None
    ):
        self.getCachedRequest = getCachedRequest
        self.setCachedRequest = setCachedRequest

    def get_route_and_measure(self, latLng, heading=None, tolerance=10000):
        return [
            {
                "Route": "route",
                "Measure": 0,
                "MMin": 0,
                "MMax": 1,
                "Distance": 1,
            },
            {
                "Route": "route",
                "Measure": 1,
                "MMin": 0,
                "MMax": 1,
                "Distance": 1,
            },
        ]

    def get_route_between_measures(self, arg1, arg2, arg3, compressed):
        return [[2, 3], [0, 1]]


@patch.object(
    cdot_geospatial_api,
    "GeospatialApi",
    side_effect=lambda: MockGeospatialApi(),
)
@patch.object(
    geospatial_tools,
    "get_road_direction_from_coordinates",
    side_effect=["southbound", "northbound"],
)
def test_get_improved_geometry(mock1, mock2):
    coordinates = [[4, 5], [6, 7]]
    event_status = "active"
    id = "id"

    expected = [[0, 1], [2, 3]]

    route_details = {"Route": "Route", "Measure": "Measure"}

    actual = planned_events.get_improved_geometry(
        cdot_geospatial_api.GeospatialApi(),
        coordinates,
        event_status,
        route_details,
        route_details,
        id,
    )

    assert actual == expected

    assert set(tuple(x) for x in actual) == set(tuple(x) for x in expected)


# Go through all descriptions from production_sample.json, and verify that a valid route name is returned
# There are 2 invalid descriptions in the list, which are expected to be empty
def test_get_cross_streets_from_description_all():
    descriptions = description_arsenal.planned_event_descriptions
    roads = description_arsenal.planned_events_roads
    for description in descriptions:
        print(description)  # This makes it easy to debug if the test fails
        v1, v2 = planned_events.get_cross_streets_from_description(description)
        if description in description_arsenal.invalid_descriptions:
            assert v1 == ""
            assert v2 == ""
        else:
            assert v1 in roads
            assert v2 in roads


def test_get_mileposts_from_description_all():
    descriptions = description_arsenal.planned_event_descriptions
    for description in descriptions:
        print(description)  # This makes it easy to debug if the test fails
        m1, m2 = planned_events.get_mileposts_from_description(description)
        print(m1, m2)
        if description in description_arsenal.invalid_descriptions:
            assert m1 is None
            assert m2 is None
        else:
            assert m1 is not None
            assert m2 is not None
            assert isinstance(m1, float)
            assert isinstance(m2, float)
            assert not math.isnan(m1)
            assert not math.isnan(m2)

import os
import unittest
import uuid
import argparse
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import time_machine
from wzdx.standard_to_wzdx import planned_events_translator
from wzdx.tools import wzdx_translator

from tests.data.standard_to_wzdx import planned_events_translator_data


@patch.object(argparse, "ArgumentParser")
def test_parse_planned_events_arguments(argparse_mock):
    plannedEventsFile, outputFile = (
        planned_events_translator.parse_planned_events_arguments()
    )
    assert plannedEventsFile != None and outputFile != None


def init_datetime_mocks(mock_dts):
    for i in mock_dts:
        i.utcnow = MagicMock(return_value=datetime(2021, 4, 13, tzinfo=timezone.utc))
        i.now = MagicMock(return_value=datetime(2021, 4, 13))
        i.strptime = datetime.strptime


@patch.dict(
    os.environ,
    {
        "contact_name": "Heather Pickering-Hilgers",
        "contact_email": "heather.pickeringhilgers@state.co.us",
        "publisher": "CDOT",
        "NAMESPACE_UUID": "3f0bce7b-1e59-4be0-80cd-b5f1f3801708",
    },
)
@unittest.mock.patch("wzdx.standard_to_wzdx.navjoy_translator.datetime")
@unittest.mock.patch("wzdx.tools.wzdx_translator.datetime")
def test_parse_work_zone_multipoint(mock_dt, mock_dt_3):
    init_datetime_mocks([mock_dt, mock_dt_3])
    standard = planned_events_translator_data.test_parse_work_zone_multipoint_standard
    expected_feature = (
        planned_events_translator_data.test_parse_work_zone_multipoint_expected
    )

    test_feature = planned_events_translator.parse_work_zone(standard)
    test_feature = wzdx_translator.remove_unnecessary_fields_feature(test_feature)

    assert test_feature == expected_feature


def test_parse_work_zone_no_data():
    test_feature = planned_events_translator.parse_work_zone(None)
    expected_feature = None
    assert test_feature == expected_feature


def test_parse_work_zone_invalid_data():
    test_var = "a,b,c,d"
    test_feature = planned_events_translator.parse_work_zone(test_var)
    assert test_feature == None


# --------------------------------------------------------------------------------Unit test for get_vehicle_impact function--------------------------------------------------------------------------------
def test_get_vehicle_impact_some_lanes_closed():
    lanes = [
        {"order": 1, "type": "shoulder", "status": "open"},
        {"order": 2, "type": "general", "status": "closed"},
        {"order": 3, "type": "general", "status": "closed"},
        {"order": 4, "type": "shoulder", "status": "open"},
    ]
    test_vehicle_impact = planned_events_translator.get_vehicle_impact(
        lanes, "description"
    )
    expected_vehicle_impact = "some-lanes-closed"
    assert test_vehicle_impact == expected_vehicle_impact


def test_get_vehicle_impact_all_lanes_closed():
    lanes = [
        {"order": 1, "type": "shoulder", "status": "closed"},
        {"order": 2, "type": "general", "status": "closed"},
        {"order": 3, "type": "general", "status": "closed"},
        {"order": 4, "type": "shoulder", "status": "closed"},
    ]
    test_vehicle_impact = planned_events_translator.get_vehicle_impact(
        lanes, "description"
    )
    expected_vehicle_impact = "all-lanes-closed"
    assert test_vehicle_impact == expected_vehicle_impact


def test_get_vehicle_impact_all_lanes_open():
    lanes = [
        {"order": 1, "type": "shoulder", "status": "open"},
        {"order": 2, "type": "general", "status": "open"},
        {"order": 3, "type": "general", "status": "open"},
        {"order": 4, "type": "shoulder", "status": "open"},
    ]
    test_vehicle_impact = planned_events_translator.get_vehicle_impact(
        lanes, "description"
    )
    expected_vehicle_impact = "all-lanes-open"
    assert test_vehicle_impact == expected_vehicle_impact


def test_get_vehicle_impact_alternating_description_valid():
    lanes = [
        {"order": 1, "type": "shoulder", "status": "open"},
        {"order": 2, "type": "general", "status": "closed"},
        {"order": 3, "type": "general", "status": "open"},
        {"order": 4, "type": "shoulder", "status": "closed"},
    ]
    test_vehicle_impact = planned_events_translator.get_vehicle_impact(
        lanes,
        "Between Utopia Place and CO 14 (Laporte) from Mile Point 354.5 to Mile Point 355.7. Paving operations. Alternating traffic. "
        "Starting June 5, 2025 at 7:00AM MDT until June 5, 2025 at about 5:00PM MDT. Full schedule below: \u2022 June 5, 7:00AM - "
        "June 5, 5:00PM Comment: Delays of up to 15 minutes can be anticipated. The speed limit will be reduced to 40 mph through the "
        "work zone. More project information is available at 970-632-7440 or sherry@sawpr.com.",
    )
    expected_vehicle_impact = "alternating-one-way"
    assert test_vehicle_impact == expected_vehicle_impact


def test_get_vehicle_impact_alternating_comment_invalid():
    lanes = [
        {"order": 1, "type": "shoulder", "status": "open"},
        {"order": 2, "type": "general", "status": "closed"},
        {"order": 3, "type": "general", "status": "open"},
        {"order": 4, "type": "shoulder", "status": "closed"},
    ]
    test_vehicle_impact = planned_events_translator.get_vehicle_impact(
        lanes,
        "Between 3300 Road and Pleasure Park Road (1 to 4 miles west of Hotchkiss) from Mile Point 18.9 to Mile Point 15.6. "
        "Road construction. Starting June 5, 2025 at 6:01AM MDT until June 5, 2025 at about 6:00PM MDT. Full schedule below: "
        "\u2022 June 5, 6:01AM - June 5, 6:00PM Comment: Shoulder widening will start on the north side. Crews continue pipe "
        "installation and waterline work between Mile Point 15-16 in both the eastbound and westbound direction. Alternating "
        "single lane traffic under flagger control will be implemented throughout the work zone and delays are expected during "
        "peak commuter times. Motorists should expect delays through the work zone. There will be one lane alternating traffic "
        "during the majority of the project and shoulder closures as needed and periodic traffic stops in order to move equipment.",
    )
    expected_vehicle_impact = "some-lanes-closed"
    assert test_vehicle_impact == expected_vehicle_impact


# --------------------------------------------------------------------------------Unit test for wzdx_creator function--------------------------------------------------------------------------------
@patch.dict(
    os.environ,
    {
        "contact_name": "Heather Pickering-Hilgers",
        "contact_email": "heather.pickeringhilgers@state.co.us",
        "publisher": "CDOT",
        "NAMESPACE_UUID": "3f0bce7b-1e59-4be0-80cd-b5f1f3801708",
    },
)
# first is for data source id, second is for a default id that is not used in this example, and the third is the road_event_id
@patch.object(uuid, "uuid4", side_effect=["w", "", "3"])
@unittest.mock.patch("wzdx.standard_to_wzdx.navjoy_translator.datetime")
@unittest.mock.patch("wzdx.tools.wzdx_translator.datetime")
def test_wzdx_creator(mock_dt, mock_dt_3, _):
    init_datetime_mocks([mock_dt, mock_dt_3])

    standard = planned_events_translator_data.test_wzdx_creator_standard

    expected_wzdx = planned_events_translator_data.test_wzdx_creator_expected

    with time_machine.travel(datetime(2021, 4, 13, 0, 0, 0)):
        test_wzdx = planned_events_translator.wzdx_creator(standard)
    test_wzdx = wzdx_translator.remove_unnecessary_fields(test_wzdx)
    assert expected_wzdx == test_wzdx


@patch.dict(
    os.environ,
    {
        "contact_name": "Heather Pickering-Hilgers",
        "contact_email": "heather.pickeringhilgers@state.co.us",
        "publisher": "CDOT",
        "NAMESPACE_UUID": "3f0bce7b-1e59-4be0-80cd-b5f1f3801708",
    },
)
# first is for data source id, second is for a default id that is not used in this example, and the third is the road_event_id
@patch.object(uuid, "uuid4", side_effect=["w", "", "3", "4", "5"])
@unittest.mock.patch("wzdx.standard_to_wzdx.navjoy_translator.datetime")
@unittest.mock.patch("wzdx.tools.wzdx_translator.datetime")
def test_wzdx_creator_road_restriction(mock_dt, mock_dt_3, _):
    init_datetime_mocks([mock_dt, mock_dt_3])

    standard = (
        planned_events_translator_data.test_wzdx_creator_standard_road_restriction
    )

    expected_wzdx = (
        planned_events_translator_data.test_wzdx_creator_expected_road_restriction
    )

    with time_machine.travel(datetime(2021, 4, 13, 0, 0, 0)):
        test_wzdx = planned_events_translator.wzdx_creator(standard)

    test_wzdx = wzdx_translator.remove_unnecessary_fields(test_wzdx)
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
    standard = {
        "rtdh_timestamp": 1638846301.4691865,
        "rtdh_message_id": "e5bba2f6-bbd0-4a61-8d64-b7c33657d35a",
        "event": {
            "type": "",
            "source": {
                "id": "Form568-44819108-703c-4d6d-ae0d-7dca7319e5b0",
                "last_updated_timestamp": 1638871501469,
            },
            "geometry": [
                [-104.82230842595187, 39.73946349406594],
                [-104.79432762150851, 39.73959547447038],
            ],
            "header": {
                "description": "Maintenance for lane expansion",
                "justification": "Lane expansion - maintenance work",
                "start_timestamp": 1630290600000,
                "end_timestamp": 1630290600000,
            },
            "detail": {
                "road_name": "287",
                "road_number": "287",
                "direction": "eastbound",
            },
        },
    }

    test_invalid_info_object = {
        "contact_name": "Heather Pickering-Hilgers",
        "contact_email": "heather.pickeringhilgers@state.co.us",
        "publisher": "iCone",
    }

    test_wzdx = planned_events_translator.wzdx_creator(
        standard, test_invalid_info_object
    )
    assert test_wzdx == None

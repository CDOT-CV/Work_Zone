import os
import unittest
import uuid
import argparse
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import time_machine
from wzdx.standard_to_cwz import planned_events_translator
from wzdx.tools import wzdx_translator

from tests.data.standard_to_cwz import planned_events_translator_data


@patch.object(argparse, "ArgumentParser")
def test_parse_planned_events_arguments(argparse_mock):
    plannedEventsFile, outputFile = (
        planned_events_translator.parse_planned_events_arguments()
    )
    assert plannedEventsFile is not None and outputFile is not None


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
@unittest.mock.patch("wzdx.tools.cwz_translator.datetime")
def test_parse_work_zone_multipoint(mock_dt):
    init_datetime_mocks([mock_dt])
    standard = planned_events_translator_data.test_parse_work_zone_linestring_standard
    expected_feature = (
        planned_events_translator_data.test_parse_work_zone_linestring_expected
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
    assert test_feature is None


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
@unittest.mock.patch("wzdx.tools.cwz_translator.datetime")
def test_cwz_creator(mock_dt, _):
    init_datetime_mocks([mock_dt])

    standard = planned_events_translator_data.test_cwz_creator_standard

    expected_cwz = planned_events_translator_data.test_cwz_creator_expected

    with time_machine.travel(datetime(2021, 4, 13, 0, 0, 0)):
        test_cwz = planned_events_translator.cwz_creator(standard)
    test_cwz = wzdx_translator.remove_unnecessary_fields(test_cwz)
    assert expected_cwz == test_cwz


def test_cwz_creator_empty_object():
    obj = None
    test_cwz = planned_events_translator.cwz_creator(obj)
    assert test_cwz is None


def test_cwz_creator_no_incidents():
    obj = []
    test_cwz = planned_events_translator.cwz_creator(obj)
    assert test_cwz is None


def test_cwz_creator_invalid_info_object():
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

    test_cwz = planned_events_translator.cwz_creator(standard, test_invalid_info_object)
    assert test_cwz is None

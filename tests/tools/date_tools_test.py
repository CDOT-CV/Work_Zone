from datetime import datetime, timedelta, timezone

import time_machine
from translator.tools import date_tools


# --------------------------------------------------------------------------------unit test for parse_datetime_from_unix function--------------------------------------------------------------------------------
def test_parse_datetime_from_unix_valid():
    time = 1609398000
    expected = datetime(2020, 12, 31, 7, tzinfo=timezone.utc)
    actual = date_tools.parse_datetime_from_unix(time)
    assert actual == expected


def test_parse_datetime_from_unix_decimal():
    time = 1615866698.393723
    expected = datetime(2021, 3, 16, 3, 51, 38, tzinfo=timezone.utc)
    actual = date_tools.parse_datetime_from_unix(time)
    assert (actual - expected) < timedelta(seconds=1)


def test_parse_datetime_from_unix_string():
    time = '1609398000'
    expected = datetime(2020, 12, 31, 7, tzinfo=timezone.utc)
    actual = date_tools.parse_datetime_from_unix(time)
    assert actual == expected


def test_parse_datetime_from_unix_invalid_none():
    time = None
    expected = None
    actual = date_tools.parse_datetime_from_unix(time)
    assert actual == expected


def test_parse_datetime_from_unix_invalid_dict():
    time = {}
    expected = None
    actual = date_tools.parse_datetime_from_unix(time)
    assert actual == expected


# --------------------------------------------------------------------------------unit test for parse_datetime_from_iso_string function--------------------------------------------------------------------------------
def test_parse_datetime_from_iso_string_valid():
    time_string = "2020-12-31T07:00:00Z"
    expected = datetime(2020, 12, 31, 7, tzinfo=timezone.utc)
    actual = date_tools.parse_datetime_from_iso_string(time_string)
    assert actual == expected


def test_parse_datetime_from_iso_string_with_decimal():
    time_string = "2020-12-31T07:00:00.123Z"
    expected = datetime(2020, 12, 31, 7, 0, 0, 123000, tzinfo=timezone.utc)
    actual = date_tools.parse_datetime_from_iso_string(time_string)
    assert actual == expected


def test_parse_datetime_from_iso_string_invalid_none():
    time_string = None
    actual = date_tools.parse_datetime_from_iso_string(time_string)
    assert actual == None


def test_parse_datetime_from_iso_string_invalid_num():
    time_string = 12
    actual = date_tools.parse_datetime_from_iso_string(time_string)
    assert actual == None


# --------------------------------------------------------------------------------unit test for get_iso_string_from_datetime function--------------------------------------------------------------------------------
def test_get_iso_string_from_datetime_valid():
    time = datetime(2020, 12, 31, 7, tzinfo=timezone.utc)
    expected = "2020-12-31T07:00:00Z"
    actual = date_tools.get_iso_string_from_datetime(time)
    assert actual == expected


def test_get_iso_string_from_datetime_invalid_none():
    time_string = None
    actual = date_tools.get_iso_string_from_datetime(time_string)
    assert actual == None


def test_get_iso_string_from_datetime_invalid_string():
    time_string = "2020-12-31T07:00:00Z"
    actual = date_tools.get_iso_string_from_datetime(time_string)
    assert actual == None


# --------------------------------------------------------------------------------Unit test for get_event_status function--------------------------------------------------------------------------------
def test_get_event_status_active():
    test_starttime_string = datetime(2020, 1, 1)
    test_endtime_string = None
    with time_machine.travel(datetime(2022, 1, 1)):
        test_event_status = date_tools.get_event_status(
            test_starttime_string, test_endtime_string)
    valid_event_status = "active"
    assert test_event_status == valid_event_status


def test_get_event_status_planned():
    test_starttime_string = datetime(2021, 1, 1)
    test_endtime_string = None
    with time_machine.travel(datetime(2020, 1, 1)):
        test_event_status = date_tools.get_event_status(
            test_starttime_string, test_endtime_string)
    valid_event_status = "planned"
    assert test_event_status == valid_event_status


def test_get_event_status_pending():
    test_starttime_string = datetime(2021, 1, 14)
    test_endtime_string = None
    with time_machine.travel(datetime(2021, 1, 1)):
        test_event_status = date_tools.get_event_status(
            test_starttime_string, test_endtime_string)
    valid_event_status = "pending"
    assert test_event_status == valid_event_status


def test_get_event_status_completed():
    test_starttime_string = datetime(2020, 1, 1)
    test_endtime_string = datetime(2021, 1, 1)
    with time_machine.travel(datetime(2022, 1, 1)):
        test_event_status = date_tools.get_event_status(
            test_starttime_string, test_endtime_string)
    valid_event_status = "completed"
    assert test_event_status == valid_event_status


def test_get_event_status_none():
    test_starttime_string = None
    test_endtime_string = None
    test_event_status = date_tools.get_event_status(
        test_starttime_string, test_endtime_string)
    valid_event_status = None
    assert test_event_status == valid_event_status


def test_get_event_status_string():
    test_starttime_string = "2020-12-31T07:00:00.123Z"
    test_endtime_string = None
    test_event_status = date_tools.get_event_status(
        test_starttime_string, test_endtime_string)
    valid_event_status = None
    assert test_event_status == valid_event_status

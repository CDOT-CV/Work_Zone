from translator.tools import date_tools

# --------------------------------------------------------------------------------unit test for reformat_datetime function--------------------------------------------------------------------------------


def test_parse_datetime_from_unix():
    time = 1609398000
    actual = date_tools.parse_datetime_from_unix(time)
    assert actual != None


def test_parse_datetime_from_unix():
    time = 1615866698.393723
    actual = date_tools.parse_datetime_from_unix(time)
    assert actual != None


# def test_reformat_datetime_null_time():
#     test_time = None
#     actual_time = date_tools.reformat_datetime(test_time)
#     expected_time = None
#     assert actual_time == expected_time


# def test_reformat_datetime_invalid_time():
#     test_time = "16093s98000z"
#     actual_time = date_tools.reformat_datetime(test_time)
#     expected_time = None
#     assert actual_time == expected_time


def test_parse_datetime_from_iso_string_valid():
    time_string = "2020-12-31T07:00:00Z"
    actual = date_tools.parse_datetime_from_iso_string(time_string)
    assert actual != None


def test_parse_datetime_from_iso_string_with_deccimal():
    time_string = "2020-12-31T07:00:00.123Z"
    actual = date_tools.parse_datetime_from_iso_string(time_string)
    assert actual != None

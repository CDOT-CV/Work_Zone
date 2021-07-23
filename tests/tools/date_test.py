from translator.tools import date

# --------------------------------------------------------------------------------unit test for reformat_datetime function--------------------------------------------------------------------------------


def test_reformat_datetime_valid_timeformat():
    test_time = 1609398000
    actual_time = date.reformat_datetime(test_time)
    expected_time = "2020-12-31T07:00:00Z"
    assert actual_time == expected_time


def test_reformat_datetime_null_time():
    test_time = None
    actual_time = date.reformat_datetime(test_time)
    expected_time = None
    assert actual_time == expected_time


def test_reformat_datetime_invalid_time():
    test_time = "16093s98000z"
    actual_time = date.reformat_datetime(test_time)
    expected_time = None
    assert actual_time == expected_time

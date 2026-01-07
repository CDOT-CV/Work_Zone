import datetime as dt
import logging
from datetime import datetime, timedelta, timezone

from dateutil import parser

ISO_8601_FORMAT_STRING = "%Y-%m-%dT%H:%M:%SZ"


def get_unix_from_iso_string(time_string):
    return date_to_unix(parse_datetime_from_iso_string(time_string))


def get_iso_string_from_unix(time_string):
    return get_iso_string_from_datetime(parse_datetime_from_unix(time_string))


def get_iso_string_from_datetime(date):
    # This is added for unit test mocking (dt.datetime instead of just datetime)
    if not date or type(date) is not dt.datetime:
        return None
    return date.astimezone(timezone.utc).strftime(ISO_8601_FORMAT_STRING)


def parse_datetime_from_iso_string(time_string):
    """Parse ISO string to datetime. Handles many different datetime formats"""
    if not time_string or type(time_string) is not str:
        return None

    try:
        return parser.parse(time_string)
    except ValueError:
        logging.warning("invalid datetime string: " + time_string)
        return None


def parse_datetime_from_unix(time):
    if not time:
        return None

    if type(time) is str:
        try:
            return datetime_from_unix(float(time))
        except ValueError:
            return None
    elif type(time) is int or type(time) is float:
        return datetime_from_unix(time)


def datetime_from_unix(time):
    # Maximum unix value of 32536850399 due to windows 32-bit signed integer (max valid date is 3001, 1, 19, 21, 59, 59)
    if time > 32536850399:
        return datetime.fromtimestamp(time / 1000, tz=timezone.utc)
    else:
        return datetime.fromtimestamp(time, tz=timezone.utc)


def date_to_unix(time: datetime):
    if not time or type(time) is not datetime:
        return None

    return round(time.timestamp() * 1000)


# function to get event status from start and end datetimes
def get_event_status(start_time, end_time):
    if not start_time or type(start_time) is not dt.datetime:
        return None

    event_status = "active"

    current_time = datetime.now()

    # check if datetime is time zone aware. If it is, get utc time
    if (
        start_time.tzinfo is not None
        and start_time.tzinfo.utcoffset(start_time) is not None
    ):
        current_time = datetime.now(timezone.utc)

    future_date_after_2weeks = current_time + timedelta(days=14)
    past_date_2weeks_ago = current_time - timedelta(days=14)

    if current_time < start_time:
        if start_time < future_date_after_2weeks:
            event_status = "pending"
        else:
            event_status = "planned"
    elif end_time and type(end_time) is dt.datetime and end_time < current_time:
        if end_time > past_date_2weeks_ago:
            event_status = "completed_recently"
        else:
            event_status = "completed"
    return event_status


def get_current_ts_millis():
    return datetime.now(timezone.utc).timestamp()

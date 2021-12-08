from datetime import datetime, timedelta, timezone
import datetime as dt
import logging
from dateutil import parser
import unittest


ISO_8601_FORMAT_STRING = "%Y-%m-%dT%H:%M:%SZ"


def get_unix_from_iso_string(time_string):
    return date_to_unix(parse_datetime_from_iso_string(time_string))


def get_iso_string_from_unix(time_string):
    return get_iso_string_from_datetime(parse_datetime_from_unix(time_string))


def get_iso_string_from_datetime(date):
    # This is added for unit test mocking (dt.datetime instead of just datetime)
    if (not date or type(date) != dt.datetime):
        return None
    return date.astimezone(timezone.utc).strftime(ISO_8601_FORMAT_STRING)


def parse_datetime_from_iso_string(time_string):
    """Parse ISO string to datetime. Handles many differnet datetime formats"""
    if not time_string or type(time_string) != str:
        return None

    try:
        return parser.parse(time_string)
    except ValueError:
        logging.warning("invalid datetime string: " + time_string)
        return None


def parse_datetime_from_unix(time):
    if not time:
        return None

    if type(time) == str:
        try:
            return datetime_from_unix(float(time))
        except ValueError:
            return None
    elif type(time) == int or type(time) == float:
        return datetime_from_unix(time)


def datetime_from_unix(time):
    try:
        # Fails for milliseconds
        return datetime.fromtimestamp(time, tz=timezone.utc)
    except:
        try:
            return datetime.fromtimestamp(time/1000, tz=timezone.utc)
        except:
            return None


def date_to_unix(time: datetime):
    if not time or type(time) != datetime:
        return None

    return round(time.timestamp() * 1000)


# function to get event status from start and end datetimes
def get_event_status(start_time, end_time):
    if not start_time or type(start_time) != dt.datetime:
        return None

    event_status = "active"

    current_time = datetime.now()

    # check if datetime is time zone aware. If it is, get utc time
    if start_time.tzinfo is not None and start_time.tzinfo.utcoffset(start_time) is not None:
        current_time = datetime.utcnow().astimezone(timezone.utc)

    future_date_after_2weeks = current_time + \
        timedelta(days=14)

    if current_time < start_time:
        if start_time < future_date_after_2weeks:
            event_status = "pending"
        else:
            event_status = "planned"
    elif end_time and type(end_time) == dt.datetime and end_time < current_time:
        event_status = "completed"
    return event_status

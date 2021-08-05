import re
from datetime import datetime, timezone
import logging


ISO_8601_FORMAT_STRING = "%Y-%m-%dT%H:%M:%SZ"


# convert UNIX timestamp to ISO timestamp
def reformat_datetime(datetime_string):
    if not datetime_string:
        return None
    elif type(datetime_string) == str:
        if re.match('^-?([0-9]*[.])?[0-9]+$', datetime_string):
            datetime_string = float(datetime_string)
        else:
            return None
    time = datetime.fromtimestamp(datetime_string)
    wzdx_format_datetime = time.astimezone(
        timezone.utc).strftime(ISO_8601_FORMAT_STRING)
    return wzdx_format_datetime


def get_iso_string_from_datetime(date):
    if not date or type(date) != datetime:
        return None
    return date.astimezone(timezone.utc).strftime(ISO_8601_FORMAT_STRING)


def parse_datetime_from_iso_string(time_string):
    if not time_string or type(time_string) != str:
        return None

    try:
        return datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        try:
            return datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            logging.warning("invalid datetime string: " + time_string)
            return None


def parse_datetime_from_unix(time):
    if not time:
        return None

    if type(time) == str:
        if re.match('^-?([0-9]*[.])?[0-9]+$', time):
            return datetime.fromtimestamp(float(time))
        else:
            return None
    elif type(time) == int or type(time) == float:
        return datetime.fromtimestamp(time)
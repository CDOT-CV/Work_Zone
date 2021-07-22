from datetime import datetime, timezone
import re


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
        timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return wzdx_format_datetime

import datetime
import xmltodict


def rfc_to_unix(date_string):
    return (int(datetime.datetime.strptime(
        date_string,
        '%Y-%m-%dT%H:%M:%SZ').timestamp())
        if date_string is not None
        else None)


def iso_to_posix(s: str) -> int:
    d = datetime.datetime.fromisoformat(s)
    p = d.timestamp()
    return int(p)


def to_dict(element):
    d = xmltodict.parse(element)
    return d


def int_or_none(param):
    try:
        return int(param)
    except TypeError:
        return None

    return None


def float_or_none(param):
    try:
        return float(param)
    except TypeError:
        return None

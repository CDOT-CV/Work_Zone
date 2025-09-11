import logging
import os
import random
import string
import uuid
from collections import OrderedDict
from datetime import datetime, timezone

from wzdx.models.enums import Direction, EventType
from ..sample_files.validation_schema import work_zone_feed_v42

import jsonschema
import xmltodict


def initialize_feature_properties():
    properties = {}
    properties["core_details"] = {
        "event_type": None,
        "data_source_id": None,
        "road_names": None,
        "direction": None,
        "related_road_events": [],
        "name": None,
        "description": None,
        "creation_date": None,
        "update_date": None,
    }
    properties["start_date"] = None
    properties["end_date"] = None
    properties["is_start_date_verified"] = None
    properties["is_end_date_verified"] = None
    properties["is_start_position_verified"] = None
    properties["is_end_position_verified"] = None
    properties["location_method"] = None
    properties["work_zone_type"] = None
    properties["vehicle_impact"] = None
    properties["lanes"] = None
    properties["beginning_cross_street"] = None
    properties["ending_cross_street"] = None
    properties["beginning_mile_post"] = None
    properties["ending_mile_post"] = None
    properties["types_of_work"] = None
    properties["worker_presence"] = None
    properties["reduced_speed_limit_kph"] = None
    properties["restrictions"] = None

    return properties


def validate_info(info):

    if (not info) or (type(info) is not dict and type(info) is not OrderedDict):
        logging.warning("invalid type")
        return False

    contact_name = info.get("contact_name")
    contact_email = info.get("contact_email")
    publisher = info.get("publisher")
    required_fields = [contact_name, contact_email, publisher]
    for field in required_fields:
        if not field:
            logging.warning(
                "invalid supplementary information object. Not all required fields are present"
            )
            return False

    return True


def parse_xml_to_dict(xml_string):
    d = xmltodict.parse(xml_string)
    return d


def validate_wzdx(wzdx_obj, wzdx_schema=work_zone_feed_v42.wzdx_v42_schema_string):
    if not wzdx_schema or not wzdx_obj:
        return False
    try:
        jsonschema.validate(instance=wzdx_obj, schema=wzdx_schema)
    except jsonschema.ValidationError as e:
        logging.error(RuntimeError(str(e)))
        return False
    return True


def initialize_info():
    info = {}
    info["contact_name"] = os.getenv("contact_name", "Heather Pickering-Hilgers")
    info["contact_email"] = os.getenv(
        "contact_email", "heather.pickeringhilgers@state.co.us"
    )
    info["publisher"] = os.getenv("publisher", "CDOT")

    return info


# Add ids to message
# This function may fail if some optional fields are not present (lanes, types_of_work, relationship, ...)
def add_ids(message: dict, event_type=EventType.WORK_ZONE):
    if not message or type(message) is not dict:
        return None

    if event_type == EventType.WORK_ZONE:
        data_source_id = (
            message.get("feed_info").get("data_sources")[0].get("data_source_id")
        )
    else:
        logging.warning("Unsupported event type for add_ids: %s", event_type)
        return None

    road_event_length = len(message.get("features"))
    road_event_ids = []
    for i in range(road_event_length):
        road_event_ids.append(str(uuid.uuid4()))

    for i in range(road_event_length):
        feature = message.get("features")[i]
        id = road_event_ids[i]
        feature["properties"]["core_details"]["data_source_id"] = data_source_id
        if feature["properties"]["core_details"].get("relationship"):
            feature["properties"]["core_details"]["relationship"]["relationship_id"] = (
                str(uuid.uuid4())
            )
            feature["properties"]["core_details"]["relationship"]["road_event_id"] = (
                feature.get("id", id)
            )
    return message


def initialize_wzdx_object(info: dict):
    wzd = {}
    wzd["feed_info"] = {}
    wzd["feed_info"]["publisher"] = info.get("publisher")
    wzd["feed_info"]["version"] = "4.2"
    wzd["feed_info"]["license"] = "https://creativecommons.org/publicdomain/zero/1.0/"

    data_source = {}
    data_source["data_source_id"] = str(uuid.uuid4())
    data_source["organization_name"] = info.get("publisher")
    data_source["update_date"] = datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    data_source["update_frequency"] = info.get("datafeed_frequency_update", 300)
    data_source["contact_name"] = info.get("contact_name")
    data_source["contact_email"] = info.get("contact_email")
    wzd["feed_info"]["data_sources"] = [data_source]

    wzd["feed_info"]["update_date"] = datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    wzd["feed_info"]["update_frequency"] = info.get("datafeed_frequency_update", 300)
    wzd["feed_info"]["contact_name"] = info.get("contact_name")
    wzd["feed_info"]["contact_email"] = info.get("contact_email")

    wzd["type"] = "FeatureCollection"

    wzd["features"] = []

    return wzd


def initialize_wzdx_object_restriction(info: dict):
    wzd = {}
    wzd["feed_info"] = {}
    # hardcode
    wzd["feed_info"]["update_date"] = datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    wzd["feed_info"]["publisher"] = info.get("publisher")
    wzd["feed_info"]["contact_name"] = info.get("contact_name")
    wzd["feed_info"]["contact_email"] = info.get("contact_email")
    if info.get("datafeed_frequency_update", False):
        wzd["feed_info"]["update_frequency"] = info[
            "datafeed_frequency_update"
        ]  # Verify data type
    wzd["feed_info"]["version"] = "4.0"
    wzd["feed_info"]["license"] = "https://creativecommons.org/publicdomain/zero/1.0/"

    data_source = {}
    data_source["data_source_id"] = str(uuid.uuid4())
    data_source["organization_name"] = info.get("publisher")
    data_source["contact_name"] = info.get("contact_name")
    data_source["contact_email"] = info.get("contact_email")
    if info.get("datafeed_frequency_update", False):
        data_source["update_frequency"] = info.get("datafeed_frequency_update")
    data_source["update_date"] = datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    wzd["feed_info"]["data_sources"] = [data_source]

    wzd["type"] = "FeatureCollection"
    sub_identifier = "".join(
        random.SystemRandom().choice(string.ascii_uppercase + string.digits)
        for _ in range(6)
    )  # Create random 6 character digit/letter string
    id = str(uuid.uuid4())
    ids = {}
    ids["sub_identifier"] = sub_identifier
    ids["id"] = id

    wzd["features"] = []

    return wzd


def string_to_number(field):
    try:
        return int(field)
    except ValueError:
        try:
            return float(field)
        except ValueError:
            return None


# function to parse direction from street name
def parse_direction_from_street_name(street: str) -> Direction:
    if not street or type(street) is not str:
        return None
    street_char = street[-1]
    street_chars = street[-2:]
    if street_char == "N" or street_chars == "NB":
        return Direction.NORTHBOUND
    elif street_char == "S" or street_chars == "SB":
        return Direction.SOUTHBOUND
    elif street_char == "W" or street_chars == "WB":
        return Direction.WESTBOUND
    elif street_char == "E" or street_chars == "EB":
        return Direction.EASTBOUND
    else:
        return Direction.UNKNOWN


# function to remove direction from street name
def remove_direction_from_street_name(street):
    SINGLE_CHARACTER_DIRECTIONS = ["N", "E", "S", "W"]
    MULTIPLE_CHARACTER_DIRECTIONS = ["NB", "EB", "SB", "WB"]

    if not street or type(street) is not str:
        return None
    street_char = street[-1]
    street_chars = street[-2:]
    if street_char in SINGLE_CHARACTER_DIRECTIONS:
        street = street[:-1]
    if street_chars in MULTIPLE_CHARACTER_DIRECTIONS:
        street = street[:-2]

    return street

import logging
import os
import uuid
from collections import OrderedDict
from datetime import datetime, timezone

from ..sample_files.validation_schema import connected_work_zone_feed_v10

import jsonschema


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
    properties["impacted_cds_curb_zones"] = None
    properties["lanes"] = None
    properties["beginning_cross_street"] = None
    properties["ending_cross_street"] = None
    properties["beginning_reference_post"] = None
    properties["ending_reference_post"] = None
    properties["reference_post_unit"] = None
    properties["types_of_work"] = None
    properties["worker_presence"] = None
    properties["reduced_speed_limit_kph"] = None
    properties["restrictions"] = None

    return properties


def validate_info(info):
    if (not info) or (type(info) is not dict and type(info) is not OrderedDict):
        logging.warning(
            "Unable to validate info object if not of type dict or OrderedDict. Type: %s",
            type(info),
        )
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


def validate_feed(
    obj, schema=connected_work_zone_feed_v10.connected_work_zone_feed_v10_schema_string
):
    if not schema or not obj:
        return False
    try:
        jsonschema.validate(instance=obj, schema=schema)
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
# This function may fail if some optional fields are not present (lanes, types_of_work, ...)
def add_ids(message):
    if not message or type(message) is not dict:
        return None

    data_source_id = (
        message.get("feed_info").get("data_sources")[0].get("data_source_id")
    )

    road_event_length = len(message.get("features"))
    road_event_ids = []
    for i in range(road_event_length):
        road_event_ids.append(str(uuid.uuid4()))

    for i in range(road_event_length):
        feature = message.get("features")[i]
        feature["properties"]["core_details"]["data_source_id"] = data_source_id
    return message


def initialize_feed_object(info):
    wzd = {}
    wzd["feed_info"] = {}
    wzd["feed_info"]["publisher"] = info.get("publisher")
    wzd["feed_info"]["version"] = "1.0"
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

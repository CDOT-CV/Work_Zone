import json
import os
import uuid
from unittest.mock import Mock, patch

from wzdx.tools import cwz_translator
from tests.data.tools import cwz_translator_data


# --------------------------------------------------------------------------------unit test for valid_info function--------------------------------------------------------------------------------
def test_valid_info_valid_info():
    test_info = {
        "contact_name": "Heather Pickering-Hilgers",
        "contact_email": "heather.pickeringhilgers@state.co.us",
        "publisher": "iCone",
    }
    test_validate_info = cwz_translator.validate_info(test_info)
    assert test_validate_info is True


def test_valid_info_no_info():
    test_info = None
    test_validate_info = cwz_translator.validate_info(test_info)
    assert test_validate_info is False


def test_valid_info_invalid_info_missing_required_fields_contact_name():
    test_info = {
        "contact_email": "heather.pickeringhilgers@state.co.us",
        "publisher": "iCone",
    }
    test_validate_info = cwz_translator.validate_info(test_info)
    assert test_validate_info is False


# --------------------------------------------------------------------------------unit test for validate_cwz function--------------------------------------------------------------------------------
def test_validate_cwz_valid_cwz_data():
    test_schema = json.loads(
        open("wzdx/sample_files/validation_schema/work_zone_feed_v42.json").read()
    )
    validate_write = cwz_translator.validate_feed(
        cwz_translator_data.test_validate_cwz_valid_cwz_data, test_schema
    )
    assert validate_write is True


def test_validate_cwz_invalid_location_method_cwz_data():
    test_schema = json.loads(
        open("wzdx/sample_files/validation_schema/work_zone_feed_v42.json").read()
    )
    invalid_write = cwz_translator.validate_feed(
        cwz_translator_data.test_validate_cwz_invalid_location_method, test_schema
    )
    assert invalid_write is False


def test_validate_cwz_no_schema():
    test_schema = {}
    invalid_write = cwz_translator.validate_feed(
        cwz_translator_data.test_validate_cwz_valid_cwz_data, test_schema
    )
    assert invalid_write is False


def test_validate_cwz_no_cwz_data():
    test_cwz_data = {}
    test_schema = json.loads(
        open("wzdx/sample_files/validation_schema/work_zone_feed_v42.json").read()
    )
    validate_write = cwz_translator.validate_feed(test_cwz_data, test_schema)
    assert validate_write is False


# --------------------------------------------------------------------------------unit test for initialize_info function--------------------------------------------------------------------------------
@patch.dict(
    os.environ,
    {
        "contact_name": "Heather Pickering-Hilgers",
        "contact_email": "heather.pickeringhilgers@state.co.us",
        "publisher": "CDOT",
    },
)
def test_initialize_info():
    actual = cwz_translator.initialize_info()
    expected = {
        "contact_name": "Heather Pickering-Hilgers",
        "contact_email": "heather.pickeringhilgers@state.co.us",
        "publisher": "CDOT",
    }
    assert actual == expected


# --------------------------------------------------------------------------------Unit test for add_ids_v3 function--------------------------------------------------------------------------------
@patch("uuid.uuid4")
def test_add_ids(mock_uuid):
    uuid.uuid4 = Mock()
    uuid.uuid4.side_effect = ["we234de", "23wsg54h"]
    input_message = {
        "feed_info": {"data_sources": [{"data_source_id": "u12s5grt"}]},
        "features": [
            {
                "properties": {
                    "core_details": {
                        "data_source_id": "",
                    }
                }
            }
        ],
    }
    actual = cwz_translator.add_ids(input_message)
    expected = {
        "feed_info": {"data_sources": [{"data_source_id": "u12s5grt"}]},
        "features": [
            {
                "properties": {
                    "core_details": {
                        "data_source_id": "u12s5grt",
                    }
                }
            }
        ],
    }

    assert actual == expected


@patch("uuid.uuid4")
def test_add_ids_invalid_message_type(mock_uuid):
    uuid.uuid4 = Mock()
    uuid.uuid4.side_effect = ["we234de"]
    input_message = "invalid message"
    actual = cwz_translator.add_ids(input_message)
    expected = None

    assert actual == expected


@patch("uuid.uuid4")
def test_add_ids_empty_message(mock_uuid):
    uuid.uuid4 = Mock()
    uuid.uuid4.side_effect = ["we234de"]
    input_message = None
    actual = cwz_translator.add_ids(input_message)
    expected = None

    assert actual == expected

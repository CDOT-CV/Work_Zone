from pydantic import TypeAdapter
from wzdx.models.field_device_feed.device_feed import DeviceFeed
import json


def test_deserialization():
    """Test deserialization and serialization of field device feed"""
    # Load and deserialize JSON
    with open("./tests/data/models/field_device_feed_icone_raw.json") as f:
        json_string = f.read()

    adapter = TypeAdapter(list[DeviceFeed])
    device_feed_list: list[DeviceFeed] = adapter.validate_json(json_string)

    # Validate structure
    assert len(device_feed_list) == 1, "Expected exactly one device feed"
    device_feed = device_feed_list[0]
    assert len(device_feed.features) > 0, "Expected at least one feature"

    # Validate first feature properties
    first_feature = device_feed.features[0]
    assert first_feature.id is not None, "Feature should have an ID"
    assert first_feature.properties.core_details.device_status is not None
    assert first_feature.properties.core_details.update_date is not None

    # Load expected output
    with open("./tests/data/models/field_device_feed_icone_final.json") as f:
        expected_object = json.load(f)

    # Compare serialized output with expected
    actual_output = device_feed.model_dump(
        by_alias=True, exclude_none=True, mode="json"
    )
    assert actual_output == expected_object, "Serialized output should match expected"


def test_roundtrip_serialization():
    """Test that serialize -> deserialize produces identical results"""
    # Load original data
    with open("./tests/data/models/field_device_feed_icone_raw.json") as f:
        json_string = f.read()

    adapter = TypeAdapter(list[DeviceFeed])

    # First deserialization
    device_feed_list_1 = adapter.validate_json(json_string)

    # Serialize and deserialize again
    json_output = adapter.dump_json(
        device_feed_list_1, by_alias=True, exclude_none=True
    )
    device_feed_list_2 = adapter.validate_json(json_output)

    # Should be identical
    assert (
        device_feed_list_1 == device_feed_list_2
    ), "Roundtrip serialization should be stable"

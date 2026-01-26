from pydantic import TypeAdapter
from wzdx.models.field_device_feed.device_feed import DeviceFeed
import json

def test_deserialization():
    # Deserialize from JSON string
    json_string = open("./tests/data/models/field_device_feed_icone_raw.json").read()

    adapter = TypeAdapter(list[DeviceFeed])
    device_feed_list: list[DeviceFeed] = adapter.validate_json(json_string)

    # Serialize to JSON
    json_output = adapter.dump_json(device_feed_list, by_alias=True, exclude_none=True)

    # Access properties
    if device_feed_list and len(device_feed_list) > 0:
        device_feed = device_feed_list[0]
        for feature in device_feed.features:
            print(f"Device ID: {feature.id}")
            print(f"Status: {feature.properties.core_details.device_status}")
            print(
                f"Update Date: {feature.properties.core_details.update_date}, {type(feature.properties.core_details.update_date)}"
            )

        print("JSON Output", json_output)

    expected_object = json.load(
        open("./tests/data/models/field_device_feed_icone_final.json")
    )

    assert (
        device_feed_list[0].model_dump(by_alias=True, exclude_none=True, mode="json")
        == expected_object
    )

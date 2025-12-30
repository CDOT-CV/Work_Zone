from pydantic import TypeAdapter
from wzdx.models.field_device_feed.device_feed import DeviceFeed


def test_deserialization():
    # Deserialize from JSON string
    json_string = """
    [
    {
        "feed_info": {
            "update_date": "2025-12-18T20:34:51.1500000Z",
            "publisher": "iCone Products LLC",
            "contact_email": "support@iconeproducts.com",
            "version": "4.2",
            "data_sources": [
                {
                    "data_source_id": "67899A97-0F3E-4683-B169-75C09C3B8F67",
                    "update_date": "2025-12-18T20:34:51.1500000Z",
                    "organization_name": "iCone Products LLC",
                    "contact_email": "support@iconeproducts.com"
                }
            ],
            "custom": {
                "oldest_feature": "2025-12-17T20:34:51.0300000Z",
                "oldest_location": "2025-12-17T20:34:51.0300000Z",
                "username": "cdotfeeds",
                "active_only": false,
                "require_location": false,
                "allow_custom_enums": true,
                "include_custom": true,
                "force_spec_required": false
            }
        },
        "type": "FeatureCollection",
        "features": [
            {
                "id": "E595E296-B1DE-4911-9454-1F2D54AC2EBD",
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        -104.7752009,
                        39.4983242
                    ]
                },
                "properties": {
                    "core_details": {
                        "device_type": "arrow-board",
                        "data_source_id": "67899A97-0F3E-4683-B169-75C09C3B8F67",
                        "device_status": "ok",
                        "update_date": "2025-12-18T20:30:27Z",
                        "has_automatic_location": true,
                        "description": "Roadwork - Caution"
                    },
                    "pattern": "four-corners-flashing",
                    "custom": {
                        "start_date": "2025-12-16T16:16:08",
                        "waze_incident": {
                            "type": "CONSTRUCTION",
                            "description": "Roadwork - Caution"
                        }
                    }
                }
            },
            {
                "id": "0E1E3B5B-D06E-4390-ABB3-C89091E246F0",
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        -106.0079266,
                        39.6531149
                    ]
                },
                "properties": {
                    "core_details": {
                        "device_type": "location-marker",
                        "data_source_id": "67899A97-0F3E-4683-B169-75C09C3B8F67",
                        "device_status": "ok",
                        "update_date": "2025-12-18T20:19:13Z",
                        "has_automatic_location": true,
                        "description": "Roadwork Active"
                    },
                    "marked_locations": [
                        {
                            "type": "work-truck-with-lights-flashing"
                        }
                    ],
                    "custom": {
                        "isActive": true,
                        "start_date": "2025-12-18T20:08:16.1200000",
                        "waze_incident": {
                            "type": "HAZARD",
                            "description": "Roadwork Active"
                        }
                    }
                }
            }
        ]
    }
    ]
    """

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

    expected_object = {
        "feed_info": {
            "update_date": "2025-12-18T20:34:51.150000Z",
            "publisher": "iCone Products LLC",
            "contact_email": "support@iconeproducts.com",
            "version": "4.2",
            "data_sources": [
                {
                    "data_source_id": "67899A97-0F3E-4683-B169-75C09C3B8F67",
                    "update_date": "2025-12-18T20:34:51.150000Z",
                    "organization_name": "iCone Products LLC",
                    "contact_email": "support@iconeproducts.com",
                }
            ],
        },
        "type": "FeatureCollection",
        "features": [
            {
                "id": "E595E296-B1DE-4911-9454-1F2D54AC2EBD",
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [-104.7752009, 39.4983242],
                },
                "properties": {
                    "core_details": {
                        "device_type": "arrow-board",
                        "data_source_id": "67899A97-0F3E-4683-B169-75C09C3B8F67",
                        "device_status": "ok",
                        "update_date": "2025-12-18T20:30:27Z",
                        "has_automatic_location": True,
                        "description": "Roadwork - Caution",
                    },
                    "pattern": "four-corners-flashing",
                },
            },
            {
                "id": "0E1E3B5B-D06E-4390-ABB3-C89091E246F0",
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [-106.0079266, 39.6531149],
                },
                "properties": {
                    "core_details": {
                        "device_type": "location-marker",
                        "data_source_id": "67899A97-0F3E-4683-B169-75C09C3B8F67",
                        "device_status": "ok",
                        "update_date": "2025-12-18T20:19:13Z",
                        "has_automatic_location": True,
                        "description": "Roadwork Active",
                    },
                    "marked_locations": [{"type": "work-truck-with-lights-flashing"}],
                },
            },
        ],
    }

    assert (
        device_feed_list[0].model_dump(by_alias=True, exclude_none=True, mode="json")
        == expected_object
    )

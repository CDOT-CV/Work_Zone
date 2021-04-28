from unittest import mock
from translator.source_code import combine_wzdx
from unittest.mock import MagicMock


# --------------------------------------------------------------------------------Unit test for combine_wzdx function--------------------------------------------------------------------------------
def test_combine_wzdx():
    test_cotrip_data = {
        "road_event_feed_info": {
            "data_sources": [
                {
                    "data_source_id": "e9403a90-e033-44d1-969e-c4ac62f26b1d"
                }
            ]
        },

        "features": [
            {
                "properties": {
                    "vehicle_impact": "unknown"
                }
            }
        ]
    }

    test_icone_data = {
        "road_event_feed_info": {
            "data_sources": [
                {
                    "data_source_id": "123dhthu-j234-o2687hvvct-o12"
                }
            ]
        }
    }

    icone_feature = {
        "properties": {
            "vehicle_impact": "all-lanes-open"
        }
    }

    expected_combined_wzdx = {
        "road_event_feed_info": {
            "data_sources": [
                {
                    "data_source_id": "e9403a90-e033-44d1-969e-c4ac62f26b1d"
                },

                {
                    "data_source_id": "123dhthu-j234-o2687hvvct-o12"
                }
            ]
        },

        "features": [
            {
                "properties": {
                    "vehicle_impact": "all-lanes-open"
                }
            }
        ]
    }

    actual = combine_wzdx.combine_wzdx(
        test_cotrip_data, test_icone_data, icone_feature)

    assert expected_combined_wzdx == actual

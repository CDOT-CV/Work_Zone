
from os import path
from translator.source_code import combine_wzdx
from shapely.geometry.polygon import Polygon
from shapely.geometry import Point
from unittest.mock import MagicMock, patch, call, Mock

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

# --------------------------------------------------------------------------------Unit test for iterate_feature function--------------------------------------------------------------------------------


@patch.object(combine_wzdx, 'isPointInPolygon')
def test_iterate_feature(mocked_combine_wzdx):
    combine_wzdx.isPointInPolygon = MagicMock(return_value=True)

    test_wzdx_message = {
        "features": [
            {
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [
                            -104.48011,
                            37.007645
                        ],
                        [
                            -104.480103,
                            37.008034
                        ]
                    ]
                }
            }
        ]
    }

    expected = {
        "geometry": {
            "type": "LineString",
                    "coordinates": [
                        [
                            -104.48011,
                            37.007645
                        ],
                        [
                            -104.480103,
                            37.008034
                        ]
                    ]
        }
    }

    actual = combine_wzdx.iterate_feature('polygon', test_wzdx_message)

    assert actual == expected

# --------------------------------------------------------------------------------Unit test for generate_polygon function--------------------------------------------------------------------------------


# def test_generate_polygon():
#     test_geomatry =

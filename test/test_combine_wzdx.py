
from os import path

from shapely.geometry import polygon
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


@patch.object(combine_wzdx, 'isPointInPolygon')
def test_iterate_feature_no_match_feature(mocked_combine_wzdx):
    combine_wzdx.isPointInPolygon = MagicMock(return_value=False)

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

    expected = None

    actual = combine_wzdx.iterate_feature('polygon', test_wzdx_message)

    assert actual == expected

# --------------------------------------------------------------------------------Unit test for generate_polygon function--------------------------------------------------------------------------------


def test_generate_polygon():
    test_geometry = [
        [
            -104.48011,
            37.007645
        ],
        [
            -104.480103,
            37.008034
        ]
    ]

    test_polygon_width = 100

    expected = Polygon([[37.00765150000295, -104.48067172189111], [37.008040500002515, -104.48066472475348], [37.008027497338986, -
                       104.4795412753422], [37.007638497338576, -104.47954827820456], [37.00765150000295, -104.48067172189111]])

    actual = combine_wzdx.generate_polygon(test_geometry, test_polygon_width)
    assert actual == expected


def test_generate_polygon_no_geometry():
    test_geometry = []
    test_polygon_width = 100
    expected = None
    actual = combine_wzdx.generate_polygon(test_geometry, test_polygon_width)
    assert actual == expected

# --------------------------------------------------------------------------------Unit test for isPointInPolygon function--------------------------------------------------------------------------------


def test_isPointInPolygon_not_inpolygon():
    test_point = Point(37.007644, -104.48011)
    test_polygon = Polygon([[37.00765150000295, -104.48067172189111], [37.008040500002515, -104.48066472475348], [37.008027497338986, -
                                                                                                                  104.4795412753422], [37.007638497338576, -104.47954827820456], [37.00765150000295, -104.48067172189111]])
    actual = combine_wzdx.isPointInPolygon(test_point, test_polygon)

    assert actual == False


def test_isPointInPolygon():
    test_point = Point(37.008034, -104.480103)
    test_polygon = Polygon([[37.00765150000295, -104.48067172189111], [37.008040500002515, -104.48066472475348], [37.00844573771368, -104.48065159550085], [
                           37.008422259629015, -104.47952840467188], [37.008027497338986, -104.4795412753422], [37.007638497338576, -104.47954827820456], [37.00765150000295, -104.48067172189111]])
    actual = combine_wzdx.isPointInPolygon(test_point, test_polygon)

    assert actual == True


def test_isPointInPolygon_no_point():
    test_point = None
    test_polygon = Polygon([[37.00765150000295, -104.48067172189111], [37.008040500002515, -104.48066472475348], [37.008027497338986, -
                                                                                                                  104.4795412753422], [37.007638497338576, -104.47954827820456], [37.00765150000295, -104.48067172189111]])
    actual = combine_wzdx.isPointInPolygon(test_point, test_polygon)

    assert actual == None


def test_isPointInPolygon_no_polygon():
    test_point = Point(-104.48011, 37.007900)
    test_polygon = None
    actual = combine_wzdx.isPointInPolygon(test_point, test_polygon)

    assert actual == None

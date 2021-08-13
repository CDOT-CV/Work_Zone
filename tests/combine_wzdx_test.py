from unittest.mock import MagicMock, patch

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from translator import combine_wzdx
from translator.tools import polygon_tools

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
        },
        "features": [
            {
                "properties": {
                    "vehicle_impact": "all-lanes-open"
                }
            }
        ]
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
        test_cotrip_data, 0, test_icone_data, 0)

    assert expected_combined_wzdx == actual

# --------------------------------------------------------------------------------Unit test for duplicate_features_and_combine function--------------------------------------------------------------------------------


def test_find_overlapping_features_and_combine():
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
                },
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

    # First feature is duplicate, second is not
    test_icone_data = {
        "road_event_feed_info": {
            "data_sources": [
                {
                    "data_source_id": "123dhthu-j234-o2687hvvct-o12"
                }
            ]
        },
        "features": [
            {
                "properties": {
                    "vehicle_impact": "all-lanes-open"
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [
                            -104.480108,
                            37.007900
                        ],
                    ]
                }
            },
            {
                "properties": {
                    "vehicle_impact": "all-lanes-closed"
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [
                            -104.490108,
                            37.007900
                        ],
                    ]
                }
            }
        ]
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
                },
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

    actual = combine_wzdx.find_overlapping_features_and_combine(
        test_icone_data, test_cotrip_data)

    assert expected_combined_wzdx == actual


def test_find_overlapping_features_and_combine_no_duplicates():
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
                },
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

    test_icone_data = {
        "road_event_feed_info": {
            "data_sources": [
                {
                    "data_source_id": "123dhthu-j234-o2687hvvct-o12"
                }
            ]
        },
        "features": [
            {
                "properties": {
                    "vehicle_impact": "all-lanes-open"
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [
                            -104.490108,
                            37.007900
                        ],
                    ]
                }
            }
        ]
    }

    expected_combined_wzdx = None

    actual = combine_wzdx.find_overlapping_features_and_combine(
        test_icone_data, test_cotrip_data)

    assert expected_combined_wzdx == actual

# --------------------------------------------------------------------------------Unit test for iterate_feature function--------------------------------------------------------------------------------


@patch.object(polygon_tools, 'isPointInPolygon')
def test_iterate_feature(mocked_combine_wzdx):
    polygon_tools.isPointInPolygon = MagicMock(return_value=True)

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
            },
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

    expected = [0, 1]

    actual = combine_wzdx.iterate_feature('polygon', test_wzdx_message)

    assert actual == expected


@patch.object(polygon_tools, 'isPointInPolygon')
def test_iterate_feature_no_match_feature(mocked_combine_wzdx):
    polygon_tools.isPointInPolygon = MagicMock(return_value=False)

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

    expected = []

    actual = combine_wzdx.iterate_feature('polygon', test_wzdx_message)

    assert actual == expected

# --------------------------------------------------------------------------------Unit test for generate_buffer_polygon_from_linestring function--------------------------------------------------------------------------------


def closeTo(num1, num2, tolerance):
    return abs(num1 - num2) < tolerance


def test_generate_buffer_polygon_from_linestring():
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

    actual = polygon_tools.generate_buffer_polygon_from_linestring(
        test_geometry, test_polygon_width)

    expected_boundary = expected.boundary.coords
    actual_boundary = actual.boundary.coords
    for index, expected_coord in enumerate(expected_boundary):
        for index_2, val in enumerate(expected_coord):
            # within 1 cm
            assert closeTo(val, actual_boundary[index][index_2], 0.000001)


def test_generate_buffer_polygon_from_linestring_no_geometry():
    test_geometry = []
    test_polygon_width = 100
    expected = None
    actual = polygon_tools.generate_buffer_polygon_from_linestring(
        test_geometry, test_polygon_width)
    assert actual == expected

# --------------------------------------------------------------------------------Unit test for isPointInPolygon function--------------------------------------------------------------------------------


def test_isPointInPolygon_not_inpolygon():
    test_point = Point(37.007644, -104.48011)
    test_polygon = Polygon([[37.00765150000295, -104.48067172189111], [37.008040500002515, -104.48066472475348], [37.008027497338986, -
                                                                                                                  104.4795412753422], [37.007638497338576, -104.47954827820456], [37.00765150000295, -104.48067172189111]])
    actual = polygon_tools.isPointInPolygon(test_point, test_polygon)

    assert actual == False


def test_isPointInPolygon():
    test_point = Point(37.008034, -104.480103)
    test_polygon = Polygon([[37.00765150000295, -104.48067172189111], [37.008040500002515, -104.48066472475348], [37.00844573771368, -104.48065159550085], [
                           37.008422259629015, -104.47952840467188], [37.008027497338986, -104.4795412753422], [37.007638497338576, -104.47954827820456], [37.00765150000295, -104.48067172189111]])
    actual = polygon_tools.isPointInPolygon(test_point, test_polygon)

    assert actual == True


def test_isPointInPolygon_no_point():
    test_point = None
    test_polygon = Polygon([[37.00765150000295, -104.48067172189111], [37.008040500002515, -104.48066472475348], [37.008027497338986, -
                                                                                                                  104.4795412753422], [37.007638497338576, -104.47954827820456], [37.00765150000295, -104.48067172189111]])
    actual = polygon_tools.isPointInPolygon(test_point, test_polygon)

    assert actual == None


def test_isPointInPolygon_no_polygon():
    test_point = Point(-104.48011, 37.007900)
    test_polygon = None
    actual = polygon_tools.isPointInPolygon(test_point, test_polygon)

    assert actual == None

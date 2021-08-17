from translator.tools import polygon_tools


# --------------------------------------------------------------------------------Unit test for get_road_direction function--------------------------------------------------------------------------------
def test_get_road_direction_no_direction():
    test_coordinates = [
        [
            -114.145065,
            34.8380671
        ],
        [
            -114.145065,
            34.8380671
        ]
    ]
    test_direction = polygon_tools.get_road_direction_from_coordinates(
        test_coordinates)
    valid_direction = None
    assert test_direction == valid_direction


def test_get_road_direction_empty_string():
    test_coordinates = ''
    test_direction = polygon_tools.get_road_direction_from_coordinates(
        test_coordinates)
    valid_direction = None
    assert test_direction == valid_direction


def test_get_road_direction_empty_coordinates():
    test_coordinates = []
    test_direction = polygon_tools.get_road_direction_from_coordinates(
        test_coordinates)
    valid_direction = None
    assert test_direction == valid_direction


def test_get_road_direction_null_coordinates():
    test_coordinates = None
    test_direction = polygon_tools.get_road_direction_from_coordinates(
        test_coordinates)
    valid_direction = None
    assert test_direction == valid_direction


def test_get_road_direction_northbound_direction():
    test_coordinates = [
        [
            -114.145065,
            34.8380671
        ],
        [
            -114.145065,
            38.8380671
        ]
    ]
    test_direction = polygon_tools.get_road_direction_from_coordinates(
        test_coordinates)
    valid_direction = 'northbound'
    assert test_direction == valid_direction


def test_get_road_direction_eastbound_direction():
    test_coordinates = [
        [
            -114.145065,
            34.8380671
        ],
        [
            -104.145065,
            34.8380671
        ]
    ]
    test_direction = polygon_tools.get_road_direction_from_coordinates(
        test_coordinates)
    valid_direction = 'eastbound'
    assert test_direction == valid_direction


def test_get_road_direction_westbound_direction():
    test_coordinates = [
        [
            -114.145065,
            34.8380671
        ],
        [
            -124.145065,
            34.8380671
        ]
    ]
    test_direction = polygon_tools.get_road_direction_from_coordinates(
        test_coordinates)
    valid_direction = 'westbound'
    assert test_direction == valid_direction


def test_polygon_to_polyline():
    coordinates = [[
        -105.02536913607729,
        39.7766424440161
    ],
        [
        -105.02503117774141,
        39.77663419842862
    ],
        [
        -105.0250819152026,
        39.771948514459645
    ],
        [
        -105.02539573365735,
        39.77195057599695
    ],
        [
        -105.02536913607729,
        39.7766424440161
    ]]
    polyline = polygon_tools.polygon_to_polyline_corners(coordinates)
    assert polyline != None


# --------------------------------------------- polygon_to_polyline_center ---------------------------------------------
def test_polygon_to_polyline_center_valid():
    coordinates = [[0, 0], [0, 1], [10, 1], [10, 0], [0, 0]]
    expected = [[10, 0.5], [0, 0.5]]
    actual = polygon_tools.polygon_to_polyline_center(coordinates)
    assert actual == expected


def test_polygon_to_polyline_center_invalid_3_points():
    coordinates = [[0, 0], [0, 1], [0, 0]]
    expected = None
    actual = polygon_tools.polygon_to_polyline_center(coordinates)
    assert actual == expected


def test_polygon_to_polyline_center_invalid_none():
    coordinates = None
    expected = None
    actual = polygon_tools.polygon_to_polyline_center(coordinates)
    assert actual == expected


def test_polygon_to_polyline_center_invalid_string():
    coordinates = "[[0, 0], [0, 1], [0, 0]]"
    expected = None
    actual = polygon_tools.polygon_to_polyline_center(coordinates)
    assert actual == expected

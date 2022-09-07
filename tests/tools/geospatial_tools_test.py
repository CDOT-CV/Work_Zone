from wzdx.tools import geospatial_tools


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
    test_direction = geospatial_tools.get_road_direction_from_coordinates(
        test_coordinates)
    valid_direction = None
    assert test_direction == valid_direction


def test_get_road_direction_empty_string():
    test_coordinates = ''
    test_direction = geospatial_tools.get_road_direction_from_coordinates(
        test_coordinates)
    valid_direction = None
    assert test_direction == valid_direction


def test_get_road_direction_empty_coordinates():
    test_coordinates = []
    test_direction = geospatial_tools.get_road_direction_from_coordinates(
        test_coordinates)
    valid_direction = None
    assert test_direction == valid_direction


def test_get_road_direction_null_coordinates():
    test_coordinates = None
    test_direction = geospatial_tools.get_road_direction_from_coordinates(
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
    test_direction = geospatial_tools.get_road_direction_from_coordinates(
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
    test_direction = geospatial_tools.get_road_direction_from_coordinates(
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
    test_direction = geospatial_tools.get_road_direction_from_coordinates(
        test_coordinates)
    valid_direction = 'westbound'
    assert test_direction == valid_direction


def test_get_heading_from_coordinates_north():
    coordinates = [[0, 0], [0, 1]]
    actual = geospatial_tools.get_heading_from_coordinates(coordinates) % 360
    expected = 0
    assert abs(actual - expected) < 0.1


def test_get_heading_from_coordinates_east():
    coordinates = [[0, 0], [1, 0]]
    actual = geospatial_tools.get_heading_from_coordinates(coordinates) % 360
    expected = 90
    assert abs(actual - expected) < 0.1


def test_get_heading_from_coordinates_south():
    coordinates = [[0, 0], [0, -1]]
    actual = geospatial_tools.get_heading_from_coordinates(coordinates) % 360
    expected = 180
    assert abs(actual - expected) < 0.1


def test_get_heading_from_coordinates_west():
    coordinates = [[0, 0], [-1, 0]]
    actual = geospatial_tools.get_heading_from_coordinates(coordinates) % 360
    expected = 270
    assert abs(actual - expected) < 0.1


def test_get_direction_from_bearing_all():
    for i in range(-45, 45):
        assert geospatial_tools.get_direction_from_bearing(i) == 'northbound'
    for i in range(-360, -315):
        assert geospatial_tools.get_direction_from_bearing(i) == 'northbound'
    for i in range(45, 135):
        assert geospatial_tools.get_direction_from_bearing(i) == 'eastbound'
    for i in range(-315, -225):
        assert geospatial_tools.get_direction_from_bearing(i) == 'eastbound'
    for i in range(135, 225):
        assert geospatial_tools.get_direction_from_bearing(i) == 'southbound'
    for i in range(-225, -135):
        assert geospatial_tools.get_direction_from_bearing(i) == 'southbound'
    for i in range(225, 315):
        assert geospatial_tools.get_direction_from_bearing(i) == 'westbound'
    for i in range(-135, -45):
        assert geospatial_tools.get_direction_from_bearing(i) == 'westbound'


def test_get_closest_direction_from_bearing_all_northbound():
    for i in range(-90, 90):  # skips 90
        print(i)
        assert geospatial_tools.get_closest_direction_from_bearing(
            i, 'northbound') == 'northbound'
    for i in range(270, 361):  # skips 361
        print(i)
        assert geospatial_tools.get_closest_direction_from_bearing(
            i, 'northbound') == 'northbound'
    for i in range(-360, -270):  # skips -270
        print(i)
        assert geospatial_tools.get_closest_direction_from_bearing(
            i, 'northbound') == 'northbound'


def test_get_closest_direction_from_bearing_all_southbound():
    for i in range(90, 269):  # skips 270
        print(i)
        assert geospatial_tools.get_closest_direction_from_bearing(
            i, 'northbound') == 'southbound'
    for i in range(-269, -90):  # skips -90
        print(i)
        assert geospatial_tools.get_closest_direction_from_bearing(
            i, 'northbound') == 'southbound'

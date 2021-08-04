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
    test_direction = polygon_tools.get_road_direction_from_coordinates(test_coordinates)
    valid_direction = None
    assert test_direction == valid_direction


def test_get_road_direction_empty_string():
    test_coordinates = ''
    test_direction = polygon_tools.get_road_direction_from_coordinates(test_coordinates)
    valid_direction = None
    assert test_direction == valid_direction


def test_get_road_direction_empty_coordinates():
    test_coordinates = []
    test_direction = polygon_tools.get_road_direction_from_coordinates(test_coordinates)
    valid_direction = None
    assert test_direction == valid_direction


def test_get_road_direction_null_coordinates():
    test_coordinates = None
    test_direction = polygon_tools.get_road_direction_from_coordinates(test_coordinates)
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
    test_direction = polygon_tools.get_road_direction_from_coordinates(test_coordinates)
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
    test_direction = polygon_tools.get_road_direction_from_coordinates(test_coordinates)
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
    test_direction = polygon_tools.get_road_direction_from_coordinates(test_coordinates)
    valid_direction = 'westbound'
    assert test_direction == valid_direction
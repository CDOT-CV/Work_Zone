from wzdx.tools import polygon_tools


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

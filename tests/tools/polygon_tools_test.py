from wzdx.tools import polygon_tools, geospatial_tools
import unittest
from shapely.geometry.polygon import Polygon


def test_generate_buffer_polygon_from_linestring():
    polyline = [
        [-105.02518638968468, 39.776638166930375],
        [-105.02523601055145, 39.771953483109826],
    ]
    expected = [
        [39.77663632624975, -105.02489458690503],
        [39.77195164242777, -105.0249442275526],
        [39.77195532305836, -105.02552779356584],
        [39.77664000687735, -105.02547819247987],
        [39.77663632624975, -105.02489458690503],
    ]
    width = 50
    polygon = polygon_tools.generate_buffer_polygon_from_linestring(polyline, width)
    polygon_points = polygon_tools.polygon_to_list(polygon)
    testCase = unittest.TestCase()

    # Validate against previous result
    for i, point in enumerate(expected):
        testCase.assertAlmostEqual(point[0], polygon_points[i][0], places=10)
        testCase.assertAlmostEqual(point[1], polygon_points[i][1], places=10)

    # Validate width
    testCase.assertAlmostEqual(
        geospatial_tools.getDist(
            polyline[0], (polygon_points[0][1], polygon_points[0][0])
        ),
        width / 2,
        places=0,
    )


def test_polygon_to_list():
    expected = [[0, 0], [0, 1], [10, 1], [10, 0], [0, 0]]
    polygon = Polygon(expected)
    actual = polygon_tools.polygon_to_list(polygon)
    assert actual == expected


def test_list_to_polygon():
    coordinates = [[0, 0], [0, 1], [10, 1], [10, 0], [0, 0]]
    expected = Polygon(coordinates)
    actual = polygon_tools.list_to_polygon(coordinates)
    assert actual == expected


def test_is_point_in_polygon_true():
    polygon = [[0, 0], [0, 1], [10, 1], [10, 0], [0, 0]]
    point = [5, 0.5]
    actual = polygon_tools.is_point_in_polygon(point, polygon)
    assert actual == True


def test_is_point_in_polygon_false():
    polygon = [[0, 0], [0, 1], [10, 1], [10, 0], [0, 0]]
    point = [10.5, 0.5]
    actual = polygon_tools.is_point_in_polygon(point, polygon)
    assert actual == False


def test_average_coordinates():
    expected = [0.5, 1.5]
    actual = polygon_tools.average_coordinates([0, 0], [1, 3])
    assert actual == expected


def test_average_symmetric_polygon_to_centerline():
    coordinates = [[0, 0], [0, 1], [10, 1], [10, 0], [0, 0]]
    expected = [[0, 0.5], [10, 0.5]]
    actual = polygon_tools.average_symmetric_polygon_to_centerline(coordinates)
    assert actual == expected


def test_rotate_polygon():
    polygon = [[0, 1], [2, 3], [3, 4], [4, 5]]
    expected = [[4, 5], [0, 1], [2, 3], [3, 4]]
    actual = polygon_tools.rotate(polygon, 1)
    assert actual == expected


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

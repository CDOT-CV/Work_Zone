from wzdx.tools import cdot_geospatial_api


def test_get_routes_list():
    assert cdot_geospatial_api.GeospatialApi().get_routes_list()


def test_get_route_details():
    expected = {"Route": "070A", "MMin": 0, "MMax": 449.589}
    assert cdot_geospatial_api.GeospatialApi().get_route_details("070A") == expected


def test_get_route_and_measure():
    expected = {
        "Route": "159A",
        "MMin": 0.0,
        "MMax": 33.84,
        "Measure": 17.597,
        "Distance": 0.89,
    }
    pos = (37.1957245, -105.428146)
    assert cdot_geospatial_api.GeospatialApi().get_route_and_measure(pos) == expected


def test_get_route_and_measure_heading():
    expected = {
        "Route": "159A",
        "MMin": 0.0,
        "MMax": 33.84,
        "Measure": 17.597,
        "Distance": 0.89,
        "Direction": "-",
    }
    pos = (37.1957245, -105.428146)
    assert (
        cdot_geospatial_api.GeospatialApi().get_route_and_measure(pos, 225) == expected
    )


def test_get_point_at_measure():
    expected = (37.06983954800006, -105.52087752399996)
    actual = cdot_geospatial_api.GeospatialApi().get_point_at_measure("159A", 5)
    assert (
        abs(actual[0] - expected[0]) < 0.0001 and abs(actual[1] - expected[1]) < 0.0001
    )


def test_get_route_geometry_ahead():
    actual = cdot_geospatial_api.GeospatialApi().get_route_geometry_ahead(
        "159A", 5, 225, 5
    )
    assert len(actual["coordinates"]) == 20


def test_get_route_geometry_ahead_mMax():
    actual = cdot_geospatial_api.GeospatialApi().get_route_geometry_ahead(
        "159A", 5, 45, 5, mMin=5, mMax=7
    )
    assert len(actual["coordinates"]) == 7


def test_get_route_geometry_ahead_mMin():
    actual = cdot_geospatial_api.GeospatialApi().get_route_geometry_ahead(
        "159A", 5, 45, 5, mMin=8, mMax=10
    )
    assert len(actual["coordinates"]) == 6


# --------------------------------------------------------------------------------unit test for parse_datetime_from_unix function--------------------------------------------------------------------------------
def test_get_route_between_measures():
    routeId = "070A"
    startMeasure = 50
    endMeasure = 60
    actual = cdot_geospatial_api.GeospatialApi().get_route_between_measures(
        routeId, startMeasure, endMeasure, compressed=False
    )
    assert len(actual) == 221


def test_get_route_between_measures():
    routeId = "070A"
    startMeasure = 50
    endMeasure = 60
    actual = cdot_geospatial_api.GeospatialApi().get_route_between_measures(
        routeId, startMeasure, endMeasure, compressed=True, adjustRoute=False
    )
    assert len(actual) == 108


def test_get_route_between_measures_allow_reversal():
    routeId = "070A"
    startMeasure = 60
    endMeasure = 50
    actual = cdot_geospatial_api.GeospatialApi().get_route_between_measures(
        routeId, startMeasure, endMeasure, compressed=True
    )
    assert len(actual) == 81

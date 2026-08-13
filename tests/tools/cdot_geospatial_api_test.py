from unittest.mock import MagicMock

import pytest

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
    print(cdot_geospatial_api.GeospatialApi().get_routes_list())
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


def test_get_route_between_measures_compressed():
    routeId = "070A"
    startMeasure = 50
    endMeasure = 60
    actual = cdot_geospatial_api.GeospatialApi().get_route_between_measures(
        routeId, startMeasure, endMeasure, compressed=True, adjustRoute=False
    )
    assert len(actual) == 108


def test_get_route_between_measures_compressed_allow_reversal():
    routeId = "070A"
    startMeasure = 60
    endMeasure = 50
    actual = cdot_geospatial_api.GeospatialApi().get_route_between_measures(
        routeId, startMeasure, endMeasure, compressed=True
    )
    assert len(actual) == 81


def test_make_cached_web_request_retries_with_backup_url_and_format():
    api = cdot_geospatial_api.GeospatialApi(
        BASE_URL="https://primary.example/arcgis/rest/services/LRS/Routes/MapServer/exts/LrsServerRounded",
        BASE_URL_FORMAT="json",
        BACKUP_BASE_URL="https://backup.example/arcgis/rest/services/LRS/Routes/MapServer/exts/LrsServerRounded",
        BACKUP_BASE_URL_FORMAT="pjson",
    )
    api._make_web_request = MagicMock(
        side_effect=[RuntimeError("boom"), '{"status": "ok"}']
    )

    actual = api._make_cached_web_request(
        "https://primary.example/arcgis/rest/services/LRS/Routes/MapServer/exts/LrsServerRounded/Route?routeId=070A&f=json",
        timeout=5,
    )

    assert actual == {"status": "ok"}
    assert api._make_web_request.call_count == 2
    assert api._make_web_request.call_args_list[0].args[0].endswith("f=json")
    assert api._make_web_request.call_args_list[1].args[0].startswith(
        "https://backup.example"
    )
    assert "f=pjson" in api._make_web_request.call_args_list[1].args[0]


def test_make_cached_web_request_keeps_format_when_backup_format_matches():
    api = cdot_geospatial_api.GeospatialApi(
        BASE_URL="https://primary.example/arcgis/rest/services/LRS/Routes/MapServer/exts/LrsServerRounded",
        BASE_URL_FORMAT="json",
        BACKUP_BASE_URL="https://backup.example/arcgis/rest/services/LRS/Routes/MapServer/exts/LrsServerRounded",
        BACKUP_BASE_URL_FORMAT="json",
    )
    api._make_web_request = MagicMock(
        side_effect=[RuntimeError("boom"), '{"status": "ok"}']
    )

    api._make_cached_web_request(
        "https://primary.example/arcgis/rest/services/LRS/Routes/MapServer/exts/LrsServerRounded/Route?routeId=070A&f=json",
        timeout=5,
    )

    assert api._make_web_request.call_count == 2
    assert api._make_web_request.call_args_list[1].args[0].startswith(
        "https://backup.example"
    )
    assert api._make_web_request.call_args_list[1].args[0].endswith("f=json")


def test_make_cached_web_request_no_retries_without_backup_url():
    api = cdot_geospatial_api.GeospatialApi(
        BASE_URL="https://primary.example/arcgis/rest/services/LRS/Routes/MapServer/exts/LrsServerRounded",
        BASE_URL_FORMAT="json",
    )
    api._make_web_request = MagicMock(
        side_effect=[RuntimeError("boom"), '{"status": "ok"}']
    )

    actual = api._make_cached_web_request(
        "https://primary.example/arcgis/rest/services/LRS/Routes/MapServer/exts/LrsServerRounded/Route?routeId=070A&f=json",
        timeout=5,
    )

    assert actual == None
    assert api._make_web_request.call_count == 1
    assert api._make_web_request.call_args_list[0].args[0].endswith("f=json")

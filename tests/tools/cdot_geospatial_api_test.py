from datetime import datetime, timedelta, timezone

import math
from unittest import expectedFailure
from wzdx.tools import cdot_geospatial_api


# --------------------------------------------------------------------------------unit test for parse_datetime_from_unix function--------------------------------------------------------------------------------
def test_get_route_between_measures():
    routeId = "070A"
    startMeasure = 50
    endMeasure = 60
    actual = cdot_geospatial_api.get_route_between_measures(
        routeId, startMeasure, endMeasure, compressed=False)
    assert len(actual) == 221


def test_get_route_between_measures():
    routeId = "070A"
    startMeasure = 50
    endMeasure = 60
    actual = cdot_geospatial_api.get_route_between_measures(
        routeId, startMeasure, endMeasure, compressed=True)
    assert len(actual) == 108

import datetime
from unittest.mock import MagicMock, patch

import time_machine

from wzdx.experimental_combination import attenuator
from wzdx.tools import cdot_geospatial_api, combination
import json
import os
import os.path


def test_validate_directionality_valid():
    geotab = {"avl_location": {"position": {"bearing": 0}}}
    planned_event = {
        "features": [{"properties": {"core_details": {"direction": "northbound"}}}]
    }

    actual = attenuator.validate_directionality(geotab, planned_event)

    assert actual == True


def test_validate_directionality_invalid():
    geotab = {"avl_location": {"position": {"bearing": 180}}}
    planned_event = {
        "features": [{"properties": {"core_details": {"direction": "northbound"}}}]
    }

    actual = attenuator.validate_directionality(geotab, planned_event)

    assert actual == False


def test_get_combined_events_valid():
    geotab_msgs = json.loads(
        open(
            "./tests/data/experimental_combination/geotab/geotab_msgs_single.json"
        ).read()
    )
    wzdx_msgs = [json.loads(open("./tests/data/wzdx.json").read())]

    with time_machine.travel(
        datetime.datetime(2022, 7, 27, 20, 0, 0, 0, tzinfo=datetime.timezone.utc)
    ):
        combined_events = attenuator.get_combined_events(geotab_msgs, wzdx_msgs)

    assert len(combined_events) == 1
    assert len(combined_events[0]["features"][0]["geometry"]["coordinates"]) > 2


def test_get_combined_events_valid_multiple():
    geotab_msgs = json.loads(
        open(
            "./tests/data/experimental_combination/geotab/geotab_msgs_double.json"
        ).read()
    )
    wzdx_msgs = [json.loads(open("./tests/data/wzdx.json").read())]

    with time_machine.travel(
        datetime.datetime(2022, 7, 27, 20, 0, 0, 0, tzinfo=datetime.timezone.utc)
    ):
        combined_events = attenuator.get_combined_events(geotab_msgs, wzdx_msgs)

    assert len(combined_events) == 1
    assert len(combined_events[0]["features"][0]["geometry"]["coordinates"]) > 2


def test_identify_overlapping_features_valid():
    geotab_msgs = json.loads(
        open(
            "./tests/data/experimental_combination/geotab/geotab_msgs_overlapping.json"
        ).read()
    )
    wzdx_msgs = [
        json.loads(
            open(
                "./tests/data/experimental_combination/geotab/wzdx_overlapping.json"
            ).read()
        )
    ]

    with time_machine.travel(
        datetime.datetime(2022, 2, 14, 21, 41, 33, 0, tzinfo=datetime.timezone.utc)
    ):
        features = attenuator.identify_overlapping_features(geotab_msgs, wzdx_msgs)
    assert len(features) == 1


@patch.object(attenuator, "get_geometry_for_distance_ahead")
def test_combine_with_wzdx_reversed(atten_patch):
    attenuator.get_geometry_for_distance_ahead = MagicMock(return_value=([], 0, 1))
    geotab_avl = json.loads(
        open(
            "./tests/data/experimental_combination/geotab/geotab_msgs_overlapping.json"
        ).read()
    )[0]
    wzdx = json.loads(
        open(
            "./tests/data/experimental_combination/geotab/wzdx_overlapping.json"
        ).read()
    )

    with time_machine.travel(
        datetime.datetime(2022, 7, 27, 14, 22, 31, 0, tzinfo=datetime.timezone.utc)
    ):
        actual = attenuator.combine_geotab_with_wzdx(geotab_avl, wzdx)

    expected = json.loads(
        open("./tests/data/experimental_combination/geotab/wzdx_combined.json").read()
    )
    print(attenuator.get_geometry_for_distance_ahead.call_args)
    attenuator.get_geometry_for_distance_ahead.assert_called_with(
        2.5,
        {
            "Route": "159A",
            "Measure": 17.597,
            "MMin": 0.0,
            "MMax": 33.84,
            "Distance": 0.89,
        },
        215,
        17.597,
        25.358,
    )
    print(actual)
    assert actual == expected


class MockGeospatialApi:
    def __init__(
        self, getCachedRequest=lambda x: None, setCachedRequest=lambda x, y: None
    ):
        self.getCachedRequest = getCachedRequest
        self.setCachedRequest = setCachedRequest

    def get_route_geometry_ahead(
        self,
        routeId,
        startMeasure,
        heading,
        distanceAhead,
        compressed=False,
        routeDetails=None,
        mmin=None,
        mmax=None,
    ):
        return {"coordinates": "a", "start_measure": "b", "end_measure": "c"}


@patch.object(
    cdot_geospatial_api,
    "GeospatialApi",
    side_effect=lambda: MockGeospatialApi(),
)
def test_get_geometry_for_distance_ahead(cdot_patch):
    # cdot_geospatial_api.get_route_geometry_ahead = MagicMock(
    #     return_value={'coordinates': 'a', 'start_measure': 'b', 'end_measure': 'c'})
    actual = attenuator.get_geometry_for_distance_ahead(
        0, {"Route": 0, "Measure": 0}, 0, 0, 0
    )
    expected = ("a", "b", "c")
    assert actual == expected


def test_get_distance_ahead_normal():
    actual = attenuator.get_distance_ahead_miles(25, 30 * 60)
    assert actual == 12.5


def test_get_distance_ahead_normal_2():
    actual = attenuator.get_distance_ahead_miles(10, 30 * 60)
    assert actual == 5


def test_get_distance_ahead_default():
    actual = attenuator.get_distance_ahead_miles(0, 30 * 60)
    assert actual == 2.5


def test_main():
    outputPath = "./tests/data/output/wzdx_attenuator_combined.json"
    try:
        os.remove(outputPath)
    except Exception:
        pass

    with time_machine.travel(
        datetime.datetime(2022, 7, 22, 20, 0, 0, 0, tzinfo=datetime.timezone.utc)
    ):
        attenuator.main(outputPath=outputPath)
    assert os.path.isfile(outputPath)
    assert len(json.loads(open(outputPath).read())) == 1


@patch.object(combination, "get_route_details_for_wzdx")
def test_get_combined_events_no_requests(combination_patch):
    geotab_msgs = json.loads(
        open(
            "./tests/data/experimental_combination/geotab/geotab_msgs_single.json"
        ).read()
    )
    wzdx_msgs = [
        json.loads(
            open(
                "./tests/data/experimental_combination/geotab/wzdx_preprocessed.json"
            ).read()
        )
    ]

    with time_machine.travel(
        datetime.datetime(2022, 7, 27, 20, 0, 0, 0, tzinfo=datetime.timezone.utc)
    ):
        attenuator.get_combined_events(geotab_msgs, wzdx_msgs)

    combination_patch.get_route_details_for_wzdx.assert_not_called()

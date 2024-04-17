import datetime
from unittest.mock import MagicMock, patch

import time_machine

from wzdx.experimental_combination import attenuator
from wzdx.tools import cdot_geospatial_api
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
    geotab_msgs = json.loads(open("./tests/data/geotab_msgs_single.json").read())
    wzdx_msgs = [json.loads(open("./tests/data/wzdx.json").read())]

    with time_machine.travel(
        datetime.datetime(2022, 7, 27, 20, 0, 0, 0, tzinfo=datetime.timezone.utc)
    ):
        combined_events = attenuator.get_combined_events(geotab_msgs, wzdx_msgs)

    assert len(combined_events) == 1
    assert len(combined_events[0]["features"][0]["geometry"]["coordinates"]) > 2


def test_get_combined_events_valid_multiple():
    geotab_msgs = json.loads(open("./tests/data/geotab_msgs_double.json").read())
    wzdx_msgs = [json.loads(open("./tests/data/wzdx.json").read())]

    with time_machine.travel(
        datetime.datetime(2022, 7, 27, 20, 0, 0, 0, tzinfo=datetime.timezone.utc)
    ):
        combined_events = attenuator.get_combined_events(geotab_msgs, wzdx_msgs)

    assert len(combined_events) == 1
    assert len(combined_events[0]["features"][0]["geometry"]["coordinates"]) > 2


# def test_identify_overlapping_features_valid():
#     geotab_msgs = [
#         {
#             "avl_location": {
#                 "position": {
#                     "latitude": 39.739928,
#                     "longitude": -104.593591,
#                     "bearing": 45,
#                     "speed": 5,
#                     "odometer": None,
#                 },
#                 "source": {"collection_timestamp": "2022-07-28T21:05:53Z"},
#             },
#             "rtdh_message_id": "110e5ecc-cd7f-48dc-8e59-ac6ef49fc1d0",
#             "rtdh_timestamp": "2022-07-28T21:05:53Z",
#         }
#     ]
#     wzdx_msgs = [
#         {
#             "features": [
#                 {
#                     "id": 42,
#                     "properties": {
#                         "core_details": {"direction": "northbound"},
#                         "start_date": "2022-07-28T21:00:00Z",
#                         "end_date": "2022-07-29T21:00:00Z",
#                     },
#                     "geometry": {
#                         "coordinates": [
#                             [-104.599491, 39.740070],
#                             [-104.584285, 39.739899],
#                         ]
#                     },
#                 }
#             ]
#         }
#     ]

#     features = attenuator.identify_overlapping_features(geotab_msgs, wzdx_msgs)
#     assert len(features) == 1


# @patch.object(attenuator, "get_geometry_for_distance_ahead")
# def test_combine_with_wzdx_reversed(atten_patch):
#     attenuator.get_geometry_for_distance_ahead = MagicMock(return_value=([], 0, 1))
#     geotab_avl = {
#         "route_details_start": {"Route": "025A", "Measure": 1},
#         "avl_location": {
#             "position": {
#                 "speed": 1,
#                 "bearing": 2,
#             },
#             "vehicle": {"id": "a"},
#             "source": {
#                 "collection_timestamp": {
#                     "timestamp": "2022-07-28T21:05:53Z",
#                 }
#             },
#         },
#         "rtdh_message_id": "110e5ecc-cd7f-48dc-8e59-ac6ef49fc1d0",
#         "rtdh_timestamp": "2022-07-28T21:05:53Z",
#     }
#     wzdx = {
#         "feed_info": {"data_sources": [{}]},
#         "route_details_start": {
#             "Route": "025A_DEC",
#             "Measure": 10,
#         },
#         "route_details_end": {
#             "Route": "025A_DEC",
#             "Measure": 5,
#         },
#         "features": [
#             {
#                 "properties": {
#                     "core_details": {"description": ""},
#                     "start_date": "2022-07-28T21:00:00Z",
#                     "end_date": "2022-07-29T21:00:00Z",
#                 },
#                 "geometry": {},
#             }
#         ],
#     }
#     actual = attenuator.combine_geotab_with_wzdx(geotab_avl, wzdx)

#     expected = {
#         "properties": {
#             "beginning_milepost": 0,
#             "ending_milepost": 1,
#         },
#         "geometry": {
#             "coordinates": [],
#         },
#     }
#     print(attenuator.get_geometry_for_distance_ahead.call_args)
#     attenuator.get_geometry_for_distance_ahead.assert_called_with(0, {}, 2, 5, 10)
#     print(actual)
#     assert actual == expected


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


# def test_main():
#     outputPath = "./tests/data/output/wzdx_attenuator_combined.json"
#     try:
#         os.remove(outputPath)
#     except Exception:
#         pass

#     with time_machine.travel(
#         datetime.datetime(2022, 7, 22, 20, 0, 0, 0, tzinfo=datetime.timezone.utc)
#     ):
#         attenuator.main(outputPath=outputPath)
#     assert os.path.isfile(outputPath)
#     assert len(json.loads(open(outputPath).read())) == 1

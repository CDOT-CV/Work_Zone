from unittest.mock import MagicMock, patch

from wzdx.experimental_combination import attenuator
from wzdx.tools import cdot_geospatial_api
import json


def test_validate_directionality_valid():
    geotab = {'avl_location': {'position': {'bearing': 0}}}
    planned_event = {'features': [
        {'properties': {'core_details': {'direction': 'northbound'}}}]}

    actual = attenuator.validate_directionality(geotab, planned_event)

    assert actual == True


def test_validate_directionality_invalid():
    geotab = {'avl_location': {'position': {'bearing': 180}}}
    planned_event = {'features': [
        {'properties': {'core_details': {'direction': 'northbound'}}}]}

    actual = attenuator.validate_directionality(geotab, planned_event)

    assert actual == False


def test_get_combined_events_valid():
    geotab_msgs = json.loads(open('./tests/data/geotab_msgs_1.json').read())
    wzdx_msgs = [json.loads(open('./tests/data/wzdx_1.json').read())]
    combined_events = attenuator.get_combined_events(
        geotab_msgs, wzdx_msgs)

    assert len(combined_events) == 1


def test_get_combined_events_valid_multiple():
    geotab_msgs = json.loads(open('./tests/data/geotab_msgs_2.json').read())
    wzdx_msgs = [json.loads(open('./tests/data/wzdx_1.json').read())]

    combined_events = attenuator.get_combined_events(
        geotab_msgs, wzdx_msgs)

    assert len(combined_events) == 1


def test_identify_overlapping_features_valid():
    geotab_msgs = [
        {
            "avl_location": {
                "position": {
                    "latitude": 39.739928,
                    "longitude": -104.593591,
                    "bearing": 45,
                    "speed": 5,
                    "odometer": None
                },
            },
            "rtdh_message_id": "110e5ecc-cd7f-48dc-8e59-ac6ef49fc1d0",
            "rtdh_timestamp": "2022-07-28T21:05:53Z"
        }]
    wzdx_msgs = [
        {
            'features': [
                {
                    'id': 42,
                    'geometry': {
                        'coordinates': [
                            [-104.599491, 39.740070],
                            [-104.584285, 39.739899]
                        ]}
                }
            ]
        }
    ]

    features = attenuator.identify_overlapping_features(geotab_msgs, wzdx_msgs)
    assert len(features) == 1


@patch.object(attenuator, 'get_geometry_for_distance_ahead')
def test_combine_with_wzdx_ordered(atten_patch):
    attenuator.get_geometry_for_distance_ahead = MagicMock(
        return_value=([], 0, 1))
    wzdx_feature = {'properties': {}, 'geometry': {}}
    route_details = {}
    distance_ahead = 0
    bearing = 0
    event_start_marker = 5
    event_end_marker = 10
    actual = attenuator.combine_with_wzdx(
        wzdx_feature, route_details, distance_ahead, bearing, event_start_marker, event_end_marker)

    expected = {'properties': {
        'beginning_milepost': 0,
        'ending_milepost': 1,
    },
        'geometry': {
        'coordinates': [],
    }}

    attenuator.get_geometry_for_distance_ahead.assert_called_with(
        distance_ahead, route_details, bearing, event_start_marker, event_end_marker)

    assert actual == expected


@patch.object(attenuator, 'get_geometry_for_distance_ahead')
def test_combine_with_wzdx_reversed(atten_patch):
    attenuator.get_geometry_for_distance_ahead = MagicMock(
        return_value=([], 0, 1))
    wzdx_feature = {'properties': {}, 'geometry': {}}
    route_details = {}
    distance_ahead = 0
    bearing = 0
    event_start_marker = 10
    event_end_marker = 5
    actual = attenuator.combine_with_wzdx(
        wzdx_feature, route_details, distance_ahead, bearing, event_start_marker, event_end_marker)

    expected = {'properties': {
        'beginning_milepost': 0,
        'ending_milepost': 1,
    }, 'geometry': {
        'coordinates': [],
    }}

    attenuator.get_geometry_for_distance_ahead.assert_called_with(
        distance_ahead, route_details, bearing, event_end_marker, event_start_marker)

    assert actual == expected


@patch.object(cdot_geospatial_api, 'get_route_geometry_ahead', side_effect=[{'coordinates': 'a', 'start_measure': 'b', 'end_measure': 'c'}])
def test_get_geometry_for_distance_ahead(cdot_patch):
    # cdot_geospatial_api.get_route_geometry_ahead = MagicMock(
    #     return_value={'coordinates': 'a', 'start_measure': 'b', 'end_measure': 'c'})
    actual = attenuator.get_geometry_for_distance_ahead(
        0, {'Route': 0, 'Measure': 0}, 0, 0, 0)
    expected = ('a', 'b', 'c')
    assert actual == expected


def test_get_distance_ahead_normal():
    actual = attenuator.get_distance_ahead_miles(25, 30*60)
    assert actual == 12.5


def test_get_distance_ahead_normal_2():
    actual = attenuator.get_distance_ahead_miles(10, 30*60)
    assert actual == 5


def test_get_distance_ahead_default():
    actual = attenuator.get_distance_ahead_miles(0, 30*60)
    assert actual == 2.5

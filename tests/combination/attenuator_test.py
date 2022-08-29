from unittest.mock import MagicMock, patch

from wzdx.combination import attenuator
from wzdx.tools import polygon_tools


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


@patch.object(attenuator, 'get_geometry_for_distance_ahead')
def test_combine_with_planned_event_ordered(atten_patch):
    attenuator.get_geometry_for_distance_ahead = MagicMock(
        return_value=([], 0, 1))
    planned_event_wzdx_feature = {'properties': {}, 'geometry': {}}
    route_details = {}
    distance_ahead = 0
    bearing = 0
    event_start_marker = 5
    event_end_marker = 10
    attenuator.combine_with_planned_event(
        planned_event_wzdx_feature, route_details, distance_ahead, bearing, event_start_marker, event_end_marker)

    attenuator.get_geometry_for_distance_ahead.assert_called_with(
        distance_ahead, route_details, bearing, event_start_marker, event_end_marker)


@patch.object(attenuator, 'get_geometry_for_distance_ahead')
def test_combine_with_planned_event_reversed(atten_patch):
    attenuator.get_geometry_for_distance_ahead = MagicMock(
        return_value=([], 0, 1))
    planned_event_wzdx_feature = {'properties': {}, 'geometry': {}}
    route_details = {}
    distance_ahead = 0
    bearing = 0
    event_start_marker = 10
    event_end_marker = 5
    attenuator.combine_with_planned_event(
        planned_event_wzdx_feature, route_details, distance_ahead, bearing, event_start_marker, event_end_marker)

    attenuator.get_geometry_for_distance_ahead.assert_called_with(
        distance_ahead, route_details, bearing, event_end_marker, event_start_marker)


def test_get_distance_ahead_normal():
    actual = attenuator.get_distance_ahead(25, 30*60)
    assert actual == 12.5


def test_get_distance_ahead_normal_2():
    actual = attenuator.get_distance_ahead(10, 30*60)
    assert actual == 5


def test_get_distance_ahead_default():
    actual = attenuator.get_distance_ahead(0, 30*60)
    assert actual == 2.5

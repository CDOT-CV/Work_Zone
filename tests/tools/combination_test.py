from unittest.mock import Mock, patch
from wzdx.tools import combination, cdot_geospatial_api
import json


def test_validate_directionality_wzdx():
    wzdx_1 = {
        "features": [{"properties": {"core_details": {"direction": "northbound"}}}]
    }

    wzdx_2 = {
        "features": [{"properties": {"core_details": {"direction": "northbound"}}}]
    }
    actual = combination.validate_directionality_wzdx(wzdx_1, wzdx_2)
    assert actual == True

    wzdx_2 = {
        "features": [{"properties": {"core_details": {"direction": "southbound"}}}]
    }
    actual = combination.validate_directionality_wzdx(wzdx_1, wzdx_2)
    assert actual == False


def test_does_route_overlap_invalid():
    obj1 = {"route_details_start": None, "route_details_end": None}
    obj2 = {"route_details_start": None, "route_details_end": None}
    actual = combination.does_route_overlap(obj1, obj2)
    assert actual == None
    actual = combination.does_route_overlap(obj2, obj1)
    assert actual == None

    obj1 = {"route_details_start": {"Measure": 1}, "route_details_end": None}
    obj2 = {"route_details_start": None, "route_details_end": None}
    actual = combination.does_route_overlap(obj1, obj2)
    assert actual == None
    actual = combination.does_route_overlap(obj2, obj1)
    assert actual == None

    obj1 = {"route_details_start": {"Measure": 1}, "route_details_end": {"Measure": 2}}
    obj2 = {"route_details_start": None, "route_details_end": None}
    actual = combination.does_route_overlap(obj1, obj2)
    assert actual == None
    actual = combination.does_route_overlap(obj2, obj1)
    assert actual == None

    obj1 = {"route_details_start": None, "route_details_end": {"Measure": 2}}
    obj2 = {"route_details_start": None, "route_details_end": None}
    actual = combination.does_route_overlap(obj1, obj2)
    assert actual == None
    actual = combination.does_route_overlap(obj2, obj1)
    assert actual == None


def test_does_route_overlap_2():
    # -------------------- Valid Equal --------------------
    obj1 = {"route_details_start": {"Measure": 1}, "route_details_end": None}
    obj2 = {"route_details_start": {"Measure": 1}, "route_details_end": None}
    actual = combination.does_route_overlap(obj1, obj2)
    assert actual == True
    actual = combination.does_route_overlap(obj2, obj1)
    assert actual == True

    obj1 = {"route_details_start": {"Measure": 1}, "route_details_end": None}
    obj2 = {"route_details_start": None, "route_details_end": {"Measure": 1}}
    actual = combination.does_route_overlap(obj1, obj2)
    assert actual == True
    actual = combination.does_route_overlap(obj2, obj1)
    assert actual == True

    obj1 = {"route_details_start": None, "route_details_end": {"Measure": 1}}
    obj2 = {"route_details_start": None, "route_details_end": {"Measure": 1}}
    actual = combination.does_route_overlap(obj1, obj2)
    assert actual == True
    actual = combination.does_route_overlap(obj2, obj1)
    assert actual == True

    # -------------------- Valid Edge of Range --------------------
    obj1 = {"route_details_start": {"Measure": 1}, "route_details_end": None}
    obj2 = {"route_details_start": {"Measure": 1.24}, "route_details_end": None}
    actual = combination.does_route_overlap(obj1, obj2)
    assert actual == True
    actual = combination.does_route_overlap(obj2, obj1)
    assert actual == True

    obj1 = {"route_details_start": {"Measure": 1}, "route_details_end": None}
    obj2 = {"route_details_start": None, "route_details_end": {"Measure": 1.24}}
    actual = combination.does_route_overlap(obj1, obj2)
    assert actual == True
    actual = combination.does_route_overlap(obj2, obj1)
    assert actual == True

    obj1 = {"route_details_start": {"Measure": 1.24}, "route_details_end": None}
    obj2 = {"route_details_start": None, "route_details_end": {"Measure": 1}}
    actual = combination.does_route_overlap(obj1, obj2)
    assert actual == True
    actual = combination.does_route_overlap(obj2, obj1)
    assert actual == True

    obj1 = {"route_details_start": None, "route_details_end": {"Measure": 1}}
    obj2 = {"route_details_start": None, "route_details_end": {"Measure": 1.24}}
    actual = combination.does_route_overlap(obj1, obj2)
    assert actual == True
    actual = combination.does_route_overlap(obj2, obj1)
    assert actual == True

    # -------------------- Invalid Edge of Range --------------------
    obj1 = {"route_details_start": {"Measure": 1}, "route_details_end": None}
    obj2 = {"route_details_start": {"Measure": 1.26}, "route_details_end": None}
    actual = combination.does_route_overlap(obj1, obj2)
    assert actual == False
    actual = combination.does_route_overlap(obj2, obj1)
    assert actual == False

    obj1 = {"route_details_start": {"Measure": 1}, "route_details_end": None}
    obj2 = {"route_details_start": None, "route_details_end": {"Measure": 1.26}}
    actual = combination.does_route_overlap(obj1, obj2)
    assert actual == False
    actual = combination.does_route_overlap(obj2, obj1)
    assert actual == False

    obj1 = {"route_details_start": {"Measure": 1.26}, "route_details_end": None}
    obj2 = {"route_details_start": None, "route_details_end": {"Measure": 1}}
    actual = combination.does_route_overlap(obj1, obj2)
    assert actual == False
    actual = combination.does_route_overlap(obj2, obj1)
    assert actual == False

    obj1 = {"route_details_start": None, "route_details_end": {"Measure": 1}}
    obj2 = {"route_details_start": None, "route_details_end": {"Measure": 1.26}}
    actual = combination.does_route_overlap(obj1, obj2)
    assert actual == False
    actual = combination.does_route_overlap(obj2, obj1)
    assert actual == False


def test_does_route_overlap_3():
    # -------------------- Valid --------------------
    obj1 = {"route_details_start": {"Measure": 1}, "route_details_end": {"Measure": 2}}
    obj2 = {"route_details_start": {"Measure": 1}, "route_details_end": None}
    actual = combination.does_route_overlap(obj1, obj2)
    assert actual == True
    actual = combination.does_route_overlap(obj2, obj1)
    assert actual == True

    obj1 = {"route_details_start": {"Measure": 1}, "route_details_end": {"Measure": 2}}
    obj2 = {"route_details_start": None, "route_details_end": {"Measure": 1}}
    actual = combination.does_route_overlap(obj1, obj2)
    assert actual == True
    actual = combination.does_route_overlap(obj2, obj1)
    assert actual == True

    obj1 = {"route_details_start": {"Measure": 1}, "route_details_end": {"Measure": 2}}
    obj2 = {"route_details_start": {"Measure": 1.5}, "route_details_end": None}
    actual = combination.does_route_overlap(obj1, obj2)
    assert actual == True
    actual = combination.does_route_overlap(obj2, obj1)
    assert actual == True

    obj1 = {"route_details_start": {"Measure": 1}, "route_details_end": {"Measure": 2}}
    obj2 = {"route_details_start": None, "route_details_end": {"Measure": 1.5}}
    actual = combination.does_route_overlap(obj1, obj2)
    assert actual == True
    actual = combination.does_route_overlap(obj2, obj1)
    assert actual == True

    # -------------------- Invalid --------------------
    obj1 = {"route_details_start": {"Measure": 1}, "route_details_end": {"Measure": 2}}
    obj2 = {"route_details_start": {"Measure": 2.5}, "route_details_end": None}
    actual = combination.does_route_overlap(obj1, obj2)
    assert actual == False
    actual = combination.does_route_overlap(obj2, obj1)
    assert actual == False

    obj1 = {"route_details_start": {"Measure": 1}, "route_details_end": {"Measure": 2}}
    obj2 = {"route_details_start": None, "route_details_end": {"Measure": 2.5}}
    actual = combination.does_route_overlap(obj1, obj2)
    assert actual == False
    actual = combination.does_route_overlap(obj2, obj1)
    assert actual == False

    obj1 = {"route_details_start": {"Measure": 1}, "route_details_end": {"Measure": 2}}
    obj2 = {"route_details_start": {"Measure": 0.5}, "route_details_end": None}
    actual = combination.does_route_overlap(obj1, obj2)
    assert actual == False
    actual = combination.does_route_overlap(obj2, obj1)
    assert actual == False

    obj1 = {"route_details_start": {"Measure": 1}, "route_details_end": {"Measure": 2}}
    obj2 = {"route_details_start": None, "route_details_end": {"Measure": 0.5}}
    actual = combination.does_route_overlap(obj1, obj2)
    assert actual == False
    actual = combination.does_route_overlap(obj2, obj1)
    assert actual == False


def test_does_route_overlap_4():
    obj1 = {"route_details_start": {"Measure": 1}, "route_details_end": {"Measure": 2}}

    obj2 = {
        "route_details_start": {"Measure": 1.01},
        "route_details_end": {"Measure": 1.99},
    }
    actual = combination.does_route_overlap(obj1, obj2)
    assert actual == True
    actual = combination.does_route_overlap(obj2, obj1)
    assert actual == True

    obj2 = {
        "route_details_start": {"Measure": 0},
        "route_details_end": {"Measure": 1.5},
    }
    actual = combination.does_route_overlap(obj1, obj2)
    assert actual == True
    actual = combination.does_route_overlap(obj2, obj1)
    assert actual == True

    obj2 = {
        "route_details_start": {"Measure": 1.5},
        "route_details_end": {"Measure": 3},
    }
    actual = combination.does_route_overlap(obj1, obj2)
    assert actual == True
    actual = combination.does_route_overlap(obj2, obj1)
    assert actual == True

    obj2 = {"route_details_start": {"Measure": 0}, "route_details_end": {"Measure": 3}}
    actual = combination.does_route_overlap(obj1, obj2)
    assert actual == True
    actual = combination.does_route_overlap(obj2, obj1)
    assert actual == True

    obj2 = {
        "route_details_start": {"Measure": 0},
        "route_details_end": {"Measure": 0.99},
    }
    actual = combination.does_route_overlap(obj1, obj2)
    assert actual == False
    actual = combination.does_route_overlap(obj2, obj1)
    assert actual == False

    obj2 = {
        "route_details_start": {"Measure": 2.01},
        "route_details_end": {"Measure": 3},
    }
    actual = combination.does_route_overlap(obj1, obj2)
    assert actual == False
    actual = combination.does_route_overlap(obj2, obj1)
    assert actual == False


class MockGeospatialApi:
    def __init__(
        self, getCachedRequest=lambda x: None, setCachedRequest=lambda x, y: None
    ):
        self.getCachedRequest = getCachedRequest
        self.setCachedRequest = setCachedRequest

    def get_route_and_measure(self, arg):
        return "route_and_measure"


@patch.object(
    cdot_geospatial_api,
    "GeospatialApi",
    side_effect=lambda: MockGeospatialApi(),
)
def test_get_route_details(mock_geospatial_api):
    coords = [0, 1]
    expected = "route_and_measure"
    actual = combination.get_route_details(*coords)
    assert actual == expected


@patch.object(
    combination,
    "get_route_details",
    side_effect=["route_details_start", "route_details_end"],
)
def test_add_route_details_overwrite_false(mock_get_route_details):
    wzdx = {
        "features": [
            {
                "geometry": {"coordinates": [[0, 1], [2, 3]]},
                "route_details_start": "start",
                "route_details_end": "end",
            }
        ]
    }
    expected = ("route_details_start", "route_details_end")
    actual = combination.add_route_details([wzdx])
    assert (
        actual[0]["route_details_start"],
        actual[0]["route_details_end"],
    ) == expected


@patch.object(
    combination,
    "get_route_details",
    side_effect=["route_details_start", "route_details_end"],
)
def test_add_route_details_overwrite_true(mock_get_route_details):
    wzdx = {
        "features": [
            {
                "geometry": {"coordinates": [[0, 1], [2, 3]]},
                "route_details_start": "start",
                "route_details_end": "end",
            }
        ]
    }
    expected = ("route_details_start", "route_details_end")
    actual = combination.add_route_details([wzdx], overwrite=True)
    assert (
        actual[0]["route_details_start"],
        actual[0]["route_details_end"],
    ) == expected


@patch.object(combination, "get_route_details", side_effect=[{}, {}])
def test_add_route_details_keepInvalid_true(mock_get_route_details):
    wzdx = {"features": [{"geometry": {"coordinates": [[0, 1], [2, 3]]}}]}
    actual = combination.add_route_details([wzdx])
    assert len(actual) == 1


@patch.object(combination, "get_route_details", side_effect=[{}, {}])
def test_add_route_details_keepInvalid_false(mock_get_route_details):
    wzdx = {"features": [{"geometry": {"coordinates": [[0, 1], [2, 3]]}}]}
    actual = combination.add_route_details([wzdx], keepInvalid=False)
    assert len(actual) == 0


@patch.object(
    combination,
    "get_route_details",
    side_effect=["route_details_start", "route_details_end"],
)
def test_get_route_details_for_wzdx(mock_get_route_details):
    wzdx = {"geometry": {"coordinates": [[0, 1], [2, 3]]}}
    expected = ("route_details_start", "route_details_end")
    actual = combination.get_route_details_for_wzdx(wzdx)
    assert actual == expected


@patch.object(
    combination,
    "get_route_details_for_wzdx",
    side_effect=[
        ({"Route": "route_1", "Measure": 1}, {"Route": "route_1", "Measure": 2}),
        ({"Route": "route_1", "Measure": 1.5}, {"Route": "route_1", "Measure": 2.5}),
    ],
)
def test_identify_overlapping_features_wzdx_valid(mock_get_route_details_for_wzdx):
    wzdx_1 = {
        "features": [
            {
                "properties": {
                    "core_details": {"direction": "northbound"},
                    "start_date": "2024-01-01T00:00:00Z",
                    "end_date": "2024-01-02T00:00:00Z",
                },
                "id": "a",
            }
        ]
    }

    wzdx_2 = {
        "features": [
            {
                "properties": {
                    "core_details": {"direction": "northbound"},
                    "start_date": "2024-01-01T00:00:00Z",
                    "end_date": "2024-01-02T00:00:00Z",
                },
                "id": "a",
            }
        ]
    }
    actual = combination.identify_overlapping_features_wzdx([wzdx_1], [wzdx_2])
    assert len(actual) == 1


@patch.object(
    combination,
    "get_route_details_for_wzdx",
    side_effect=[
        ({"Route": "route_1", "Measure": 1}, {"Route": "route_1", "Measure": 2}),
        ({"Route": "route_1", "Measure": 1}, {"Route": "route_1", "Measure": 2}),
        ({"Route": "route_1", "Measure": 1.5}, {"Route": "route_1", "Measure": 2.5}),
        ({"Route": "route_1", "Measure": 1.5}, {"Route": "route_1", "Measure": 2.5}),
    ],
)
def test_identify_overlapping_features_wzdx_valid_multiple(
    mock_get_route_details_for_wzdx,
):
    wzdx_0 = {
        "features": [
            {
                "properties": {
                    "core_details": {"direction": "northbound"},
                    "start_date": "2024-01-01T00:00:00Z",
                    "end_date": "2024-01-02T00:00:00Z",
                },
                "id": "a",
            }
        ]
    }
    wzdx_1 = {
        "features": [
            {
                "properties": {
                    "core_details": {"direction": "northbound"},
                    "start_date": "2024-01-01T00:00:00Z",
                    "end_date": "2024-01-05T00:00:00Z",
                },
                "id": "a",
            }
        ]
    }

    wzdx_2 = {
        "features": [
            {
                "properties": {
                    "core_details": {"direction": "northbound"},
                    "start_date": "2024-01-01T01:00:00Z",
                    "end_date": "2024-01-06T00:00:00Z",
                },
                "id": "a",
            }
        ]
    }
    wzdx_3 = {
        "features": [
            {
                "properties": {
                    "core_details": {"direction": "northbound"},
                    "start_date": "2024-01-01T22:00:00Z",
                    "end_date": "2024-01-07T00:00:00Z",
                },
                "id": "a",
            }
        ]
    }
    actual = combination.identify_overlapping_features_wzdx(
        [wzdx_0, wzdx_1], [wzdx_2, wzdx_3]
    )
    assert len(actual) == 2 * 2


@patch.object(combination, "get_route_details_for_wzdx", side_effect=[])
def test_identify_overlapping_features_wzdx_valid_with_routes(
    mock_get_route_details_for_wzdx,
):
    wzdx_1 = {
        "features": [
            {
                "properties": {
                    "core_details": {"direction": "northbound"},
                    "route_details_start": {"Route": "route_1", "Measure": 1},
                    "route_details_end": {"Route": "route_1", "Measure": 2},
                    "start_date": "2024-01-01T00:00:00Z",
                    "end_date": "2024-01-02T00:00:00Z",
                },
                "id": "a",
            }
        ]
    }

    wzdx_2 = {
        "features": [
            {
                "properties": {
                    "core_details": {"direction": "northbound"},
                    "route_details_start": {"Route": "route_1", "Measure": 1.5},
                    "route_details_end": {"Route": "route_1", "Measure": 2.5},
                    "start_date": "2023-12-29T00:00:00Z",
                    "end_date": "2024-01-01T01:00:00Z",
                },
                "id": "a",
            }
        ]
    }
    actual = combination.identify_overlapping_features_wzdx([wzdx_1], [wzdx_2])
    assert len(actual) == 1


@patch.object(
    combination,
    "get_route_details_for_wzdx",
    side_effect=[
        ({"Route": "route_1", "Measure": 1}, {"Route": "route_1", "Measure": 2}),
        ({"Route": "route_1", "Measure": 1.5}, {"Route": "route_1", "Measure": 2.5}),
    ],
)
def test_identify_overlapping_features_wzdx_invalid_direction(
    mock_get_route_details_for_wzdx,
):
    wzdx_1 = {
        "features": [
            {"properties": {"core_details": {"direction": "northbound"}}, "id": "a"}
        ]
    }

    wzdx_2 = {
        "features": [
            {"properties": {"core_details": {"direction": "southbound"}}, "id": "a"}
        ]
    }
    actual = combination.identify_overlapping_features_wzdx([wzdx_1], [wzdx_2])
    assert len(actual) == 0


@patch.object(
    combination,
    "get_route_details_for_wzdx",
    side_effect=[
        ({"Route": "route_1", "Measure": 1}, {"Route": "route_1", "Measure": 2}),
        ({"Route": "route_1", "Measure": 2.1}, {"Route": "route_1", "Measure": 2.5}),
    ],
)
def test_identify_overlapping_features_wzdx_invalid_overlap(
    mock_get_route_details_for_wzdx,
):
    wzdx_1 = {
        "features": [
            {"properties": {"core_details": {"direction": "northbound"}}, "id": "a"}
        ]
    }

    wzdx_2 = {
        "features": [
            {"properties": {"core_details": {"direction": "northbound"}}, "id": "a"}
        ]
    }
    actual = combination.identify_overlapping_features_wzdx([wzdx_1], [wzdx_2])
    assert len(actual) == 0


@patch.object(
    combination,
    "get_route_details_for_wzdx",
    side_effect=[
        ({"Route": "route_1", "Measure": 1}, {"Route": "route_1", "Measure": 2}),
        ({"Route": "route_1", "Measure": 1.5}, {"Route": "route_2", "Measure": 2.5}),
    ],
)
def test_identify_overlapping_features_wzdx_invalid_route_mismatch_1(
    mock_get_route_details_for_wzdx,
):
    wzdx_1 = {
        "features": [
            {"properties": {"core_details": {"direction": "northbound"}}, "id": "a"}
        ]
    }

    wzdx_2 = {
        "features": [
            {"properties": {"core_details": {"direction": "northbound"}}, "id": "a"}
        ]
    }
    actual = combination.identify_overlapping_features_wzdx([wzdx_1], [wzdx_2])
    assert len(actual) == 0


@patch.object(
    combination,
    "get_route_details_for_wzdx",
    side_effect=[
        ({"Route": "route_1", "Measure": 1}, {"Route": "route_2", "Measure": 2}),
        ({"Route": "route_1", "Measure": 1.5}, {"Route": "route_2", "Measure": 2.5}),
    ],
)
def test_identify_overlapping_features_wzdx_invalid_route_mismatch_2(
    mock_get_route_details_for_wzdx,
):
    wzdx_1 = {
        "features": [
            {"properties": {"core_details": {"direction": "northbound"}}, "id": "a"}
        ]
    }

    wzdx_2 = {
        "features": [
            {"properties": {"core_details": {"direction": "northbound"}}, "id": "a"}
        ]
    }
    actual = combination.identify_overlapping_features_wzdx([wzdx_1], [wzdx_2])
    assert len(actual) == 0


@patch.object(
    combination,
    "get_route_details_for_wzdx",
    side_effect=[
        ({"Route": "route_1", "Measure": 1}, {"Route": "route_1", "Measure": 2}),
        ({"Route": "route_2", "Measure": 1.5}, {"Route": "route_2", "Measure": 2.5}),
    ],
)
def test_identify_overlapping_features_wzdx_invalid_route_mismatch_3(
    mock_get_route_details_for_wzdx,
):
    wzdx_1 = {
        "features": [
            {"properties": {"core_details": {"direction": "northbound"}}, "id": "a"}
        ]
    }

    wzdx_2 = {
        "features": [
            {"properties": {"core_details": {"direction": "northbound"}}, "id": "a"}
        ]
    }
    actual = combination.identify_overlapping_features_wzdx([wzdx_1], [wzdx_2])
    assert len(actual) == 0


@patch.object(
    combination,
    "get_route_details_for_wzdx",
    side_effect=[
        (None, {"Route": "route_1", "Measure": 2}),
        (None, {"Route": "route_2", "Measure": 2.5}),
    ],
)
def test_identify_overlapping_features_wzdx_invalid_route_none(
    mock_get_route_details_for_wzdx,
):
    wzdx_1 = {
        "features": [
            {"properties": {"core_details": {"direction": "northbound"}}, "id": "a"}
        ]
    }

    wzdx_2 = {
        "features": [
            {"properties": {"core_details": {"direction": "northbound"}}, "id": "a"}
        ]
    }
    actual = combination.identify_overlapping_features_wzdx([wzdx_1], [wzdx_2])
    assert len(actual) == 0

from wzdx.experimental_combination import icone
import json
import time_machine
import datetime


def test_get_direction_from_route_details():
    route_details = {"Direction": "a"}
    expected = "a"

    actual = icone.get_direction_from_route_details(route_details)

    assert actual == expected


def test_get_direction():
    street = "I-25N"
    coords = [
        [-106.07316970825195, 39.190971392168045],
        [-106.07331991195677, 39.18659739731203],
    ]
    route_details = {"Direction": "northbound"}

    expected = "northbound"
    actual = icone.get_direction(street, [])
    assert actual == expected

    expected = "southbound"
    actual = icone.get_direction("", coords)
    assert actual == expected

    expected = "northbound"
    actual = icone.get_direction("", [], route_details)
    assert actual == expected

    expected = "northbound"
    actual = icone.get_direction(street, coords, route_details)
    assert actual == expected


def test_get_combined_events_valid():
    icone_msgs = [
        json.loads(
            open(
                "./tests/data/experimental_combination/icone/icone_standard_hwy-159.json"
            ).read()
        )
    ]
    wzdx = [
        json.loads(
            open(
                "./tests/data/experimental_combination/icone/wzdx_combination_hwy-159.json"
            ).read()
        )
    ]

    with time_machine.travel(
        datetime.datetime(2022, 7, 27, 22, 0, 0, 0, tzinfo=datetime.timezone.utc)
    ):
        expected = icone.get_combined_events(icone_msgs, wzdx)
    assert len(expected) == 1


def test_get_combined_events_invalid():
    icone_msgs = [
        json.loads(
            open(
                "./tests/data/experimental_combination/icone/icone_standard_hwy-159.json"
            ).read()
        )
    ]
    wzdx = [
        json.loads(
            open(
                "./tests/data/experimental_combination/icone/wzdx_combination_nowhere.json"
            ).read()
        )
    ]

    with time_machine.travel(
        datetime.datetime(2022, 7, 27, 20, 0, 0, 0, tzinfo=datetime.timezone.utc)
    ):
        expected = icone.get_combined_events(icone_msgs, wzdx)
    assert len(expected) == 0


def test_get_combined_events_invalid_different_routes():
    icone_msgs = [
        json.loads(
            open(
                "./tests/data/experimental_combination/icone/icone_standard_hwy-159.json"
            ).read()
        )
    ]
    wzdx = [
        json.loads(
            open(
                "./tests/data/experimental_combination/icone/wzdx_combination_co-9.json"
            ).read()
        )
    ]

    with time_machine.travel(
        datetime.datetime(2022, 7, 27, 20, 0, 0, 0, tzinfo=datetime.timezone.utc)
    ):
        expected = icone.get_combined_events(icone_msgs, wzdx)
    assert len(expected) == 0


def test_get_combined_events_invalid_no_routes():
    icone_msgs = [
        json.loads(
            open(
                "./tests/data/experimental_combination/icone/icone_standard_nowhere.json"
            ).read()
        )
    ]
    wzdx = [
        json.loads(
            open(
                "./tests/data/experimental_combination/icone/wzdx_combination_nowhere_2.json"
            ).read()
        )
    ]

    with time_machine.travel(
        datetime.datetime(2022, 7, 27, 20, 0, 0, 0, tzinfo=datetime.timezone.utc)
    ):
        expected = icone.get_combined_events(icone_msgs, wzdx)
    assert len(expected) == 0

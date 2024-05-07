from wzdx.experimental_combination import navjoy
import json
import os
import os.path
import datetime
import time_machine


def test_get_combined_events_valid():
    navjoy_msgs = [
        json.loads(
            open("./tests/data/experimental_combination/navjoy/wzdx_navjoy.json").read()
        )
    ]
    wzdx = [
        json.loads(
            open("./tests/data/experimental_combination/navjoy/wzdx.json").read()
        )
    ]

    with time_machine.travel(
        datetime.datetime(2022, 7, 27, 20, 0, 0, 0, tzinfo=datetime.timezone.utc)
    ):
        expected = navjoy.get_combined_events(navjoy_msgs, wzdx)
    assert len(expected) == 1
    assert (
        expected[0]["features"][0]["properties"]["reduced_speed_limit_kph"]
        == navjoy_msgs[0]["features"][0]["properties"]["reduced_speed_limit_kph"]
    )


def test_main():
    outputPath = "./tests/data/output/wzdx_navjoy_combined.json"
    try:
        os.remove(outputPath)
    except Exception:
        pass
    navjoy.main(outputPath=outputPath)
    assert os.path.isfile(outputPath)
    assert len(json.loads(open(outputPath).read())) == 1

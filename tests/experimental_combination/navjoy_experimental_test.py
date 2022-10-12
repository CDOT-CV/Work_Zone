from wzdx.experimental_combination import navjoy
import json


def test_get_combined_events_valid():
    navjoy_msgs = [json.loads(
        open('./tests/data/experimental_combination/navjoy/wzdx_navjoy_1.json').read())]
    wzdx = [json.loads(
        open('./tests/data/experimental_combination/navjoy/wzdx_1.json').read())]

    expected = navjoy.get_combined_events(navjoy_msgs, wzdx)
    assert len(expected) == 1
    print(expected[0]['features'])
    assert expected[0]['features'][0]['properties']['reduced_speed_limit_kph'] == navjoy_msgs[0]['features'][0]['properties']['reduced_speed_limit_kph']

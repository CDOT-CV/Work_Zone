import json
from datetime import datetime
import logging

from ..tools import combination

ISO_8601_FORMAT_STRING = "%Y-%m-%dT%H:%M:%SZ"


def main():
    with open('./wzdx/sample_files/raw/geotab_avl/geotab_all.json') as f:
        geotab_avl = json.loads(f.read())
    with open('./wzdx/sample_files/enhanced/wzdxs/wzdx_all.json') as f:
        wzdx = json.loads(f.read())

    combined_events = get_combined_events(geotab_avl, wzdx)

    with open('./wzdx/sample_files/enhanced/wzdxs/wzdx_combined.json', 'w+') as f:
        f.write(json.dumps(combined_events, indent=2))


def get_combined_events(navjoy_wzdx_msgs, wzdx_msgs):
    combined_events = []
    for i in combination.identify_overlapping_features_wzdx(navjoy_wzdx_msgs, wzdx_msgs):
        feature = combine_navjoy_with_wzdx(*i)
        wzdx = i[1]
        wzdx['features'] = [feature]
        combined_events.append(wzdx)
    return combined_events


def combine_navjoy_with_wzdx(navjoy_wzdx, wzdx_wzdx):
    combined_event = wzdx_wzdx

    combined_event['features'][0]['properties']['reduced_speed_limit_kph'] = navjoy_wzdx['features'][0]['properties']['reduced_speed_limit_kph']

    for i in ['route_details_start', 'route_details_end']:
        if i in combined_event:
            del combined_event[i]
    return combined_event


if __name__ == "__main__":
    main()

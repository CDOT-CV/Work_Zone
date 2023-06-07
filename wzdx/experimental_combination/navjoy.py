import json

from ..tools import combination, date_tools, wzdx_translator
from datetime import datetime, timedelta

ISO_8601_FORMAT_STRING = "%Y-%m-%dT%H:%M:%SZ"


def main(outputPath='./tests/data/output/wzdx_navjoy_combined.json'):
    with open('./wzdx/sample_files/enhanced/navjoy/wzdx_2022_11_3.json') as f:
        navjoy = [json.loads(f.read())]
        navjoy[0]['features'][0]['properties']['start_date'] = date_tools.get_iso_string_from_datetime(
            datetime.now() - timedelta(days=1))
        navjoy[0]['features'][0]['properties']['end_date'] = date_tools.get_iso_string_from_datetime(
            datetime.now() + timedelta(days=1))
    with open('./wzdx/sample_files/enhanced/planned_events/wzdx_2022_11_3.json') as f:
        wzdx = [json.loads(f.read())]
        wzdx[0]['features'][0]['properties']['start_date'] = date_tools.get_iso_string_from_datetime(
            datetime.now() - timedelta(days=2))
        wzdx[0]['features'][0]['properties']['end_date'] = date_tools.get_iso_string_from_datetime(
            datetime.now() + timedelta(days=2))

    combined_events = get_combined_events(navjoy, wzdx)

    with open(outputPath, 'w+') as f:
        f.write(json.dumps(combined_events, indent=2))


def get_combined_events(navjoy_wzdx_msgs, wzdx_msgs):
    combined_events = []
    active_navjoy_wzdx_msgs = wzdx_translator.filter_active_wzdx(
        navjoy_wzdx_msgs)
    active_wzdx_msgs = wzdx_translator.filter_active_wzdx(wzdx_msgs)
    for i in combination.identify_overlapping_features_wzdx(active_navjoy_wzdx_msgs, active_wzdx_msgs):
        navjoy_msg, wzdx_msg = i
        event_status = wzdx_translator.get_event_status(
            wzdx_msg['features'][0])
        if event_status in ['active']:
            combined = combine_navjoy_with_wzdx(navjoy_msg, wzdx_msg)
            wzdx_msg['features'] = combined['features']
            combined_events.append(wzdx_msg)
    return combined_events


def combine_navjoy_with_wzdx(navjoy_wzdx, wzdx_wzdx):
    combined_event = wzdx_wzdx

    combined_feature = combined_event['features'][0]

    combined_feature['properties']['reduced_speed_limit_kph'] = navjoy_wzdx['features'][0]['properties']['reduced_speed_limit_kph']
    combined_feature['properties']['core_details'][
        'description'] += f" Moving area updated by Geotab ATMA {combined_event['id']}"

    # add fields for traceability
    combined_feature['properties']['experimental_source_type'] = 'geotab'
    combined_feature['properties']['experimental_source_id'] = combined_event['id']
    combined_feature['properties']['navjoy_id'] = combined_event['id']
    combined_feature['properties']['navjoy_message'] = geotab_avl

    for i in ['route_details_start', 'route_details_end']:
        if i in combined_event:
            del combined_event[i]
    return combined_event


if __name__ == "__main__":
    main()

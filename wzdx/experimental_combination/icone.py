import json
from datetime import datetime
import logging
from datetime import datetime, timedelta
import glob

from ..tools import combination, wzdx_translator, geospatial_tools, date_tools

ISO_8601_FORMAT_STRING = "%Y-%m-%dT%H:%M:%SZ"
START_TIME_THRESHOLD_MILLISECONDS = 1000 * 60 * 60 * 24 * 31  # 31 days
END_TIME_THRESHOLD_MILLISECONDS = 1000 * 60 * 60 * 24 * 31  # 31 days


def main(outputPath='./tests/data/output/wzdx_icone_combined.json'):
    icone = [json.loads(open(f_name).read()) for f_name in glob.glob(
        './icone_arrow_boards/2023_05_16_standard/*.json')]
    wzdx_full = json.loads(
        open('./icone_arrow_boards/2023_05_16_standard/wzdx.geojson').read())
    wzdx = [{
        'feed_info': wzdx_full['feed_info'],
        'type': "FeatureCollection",
        'features': [i]
    } for i in wzdx_full['features']]
    outputPath = './icone_arrow_boards/2023_05_16_standard/wzdx_experimental.geojson'
    # with open('./wzdx/sample_files/standard/icone/standard_icone_combination.json') as f:
    #     icone = json.loads(f.read())
    #     icone[0]['event']['header']['start_timestamp'] = date_tools.date_to_unix(
    #         datetime.now())
    # with open('./wzdx/sample_files/enhanced/attenuator/attenuator_combination_wzdx.json') as f:
    #     wzdx = json.loads(f.read())
    #     wzdx[0]['features'][0]['properties']['start_date'] = date_tools.get_iso_string_from_datetime(
    #         datetime.now() - timedelta(days=1))
    #     wzdx[0]['features'][0]['properties']['end_date'] = date_tools.get_iso_string_from_datetime(
    #         datetime.now() + timedelta(days=1))

    combined_events = get_combined_events(icone, wzdx)

    with open(outputPath, 'w+') as f:
        f.write(json.dumps(combined_events, indent=2))


def get_direction_from_route_details(route_details):
    return route_details.get('Direction')


def get_direction(street, coords, route_details=None):
    direction = wzdx_translator.parse_direction_from_street_name(street)
    if not direction and route_details:
        direction = get_direction_from_route_details(route_details)
    if not direction:
        direction = geospatial_tools.get_road_direction_from_coordinates(
            coords)
    return direction


def get_combined_events(icone_standard_msgs, wzdx_msgs):
    combined_events = []
    
    filtered_wzdx_msgs = wzdx_translator.filter_wzdx_by_event_status(wzdx_msgs, ['pending', 'completed_recently'])
    
    for i in identify_overlapping_features_icone(icone_standard_msgs, filtered_wzdx_msgs):
        icone_msg, wzdx_msg = i
        event_status = wzdx_translator.get_event_status(
            wzdx_msg['features'][0])
        if event_status in ['pending', 'completed_recently']:
            wzdx = combine_icone_with_wzdx(icone_msg, wzdx_msg, event_status)
            if wzdx:
                combined_events.append(wzdx)
    return combined_events


def combine_icone_with_wzdx(icone_standard, wzdx_wzdx, event_status):
    combined_event = wzdx_wzdx
    updated = False

    if event_status == "pending":
        combined_event['features'][0]['properties']['start_date'] = date_tools.get_iso_string_from_unix(
            icone_standard['event']['header']['start_timestamp'])
    elif event_status == "completed_recently":
        combined_event['features'][0]['properties']['end_date'] = date_tools.get_iso_string_from_unix(
            icone_standard['event']['header']['start_timestamp'] + 60*60)
        combined_event['features'][0]['properties']['core_details']['description'] += ' ' + \
            icone_standard['event']['header']['description']

    if updated:
        update_date = date_tools.get_iso_string_from_datetime(datetime.now())
        combined_event['features'][0]['properties']['core_details']['update_date'] = update_date
        combined_event['feed_info']['data_sources'][0]['update_date'] = update_date

        combined_event['features'][0]['properties']['experimental_source_type'] = 'icone'
        combined_event['features'][0]['properties']['experimental_source_id'] = icone_standard['rtdh_message_id']
        combined_event['features'][0]['properties']['icone_id'] = icone_standard['event']['source']['id']
        combined_event['features'][0]['properties']['icone_message'] = icone_standard

        for i in ['route_details_start', 'route_details_end']:
            if i in combined_event:
                del combined_event[i]
        return combined_event
    else:
        return None


def get_route_details_for_icone(coordinates):
    route_details_start = combination.get_route_details(
        coordinates[0][1], coordinates[0][0])

    if len(coordinates) == 1 or (len(coordinates) == 2 and coordinates[0] == coordinates[1]):
        route_details_end = None
    else:
        route_details_end = combination.get_route_details(
            coordinates[-1][1], coordinates[-1][0])

    return route_details_start, route_details_end


def validate_directionality_wzdx_icone(icone, wzdx):
    direction_1 = icone['event']['detail']['direction']
    direction_2 = wzdx['features'][0]['properties']['core_details']['direction']

    return direction_1 in [None, 'unknown', 'undefined'] or direction_1 == direction_2


# Filter out iCone and WZDx messages which are not within the time interval
def validate_dates(icone, wzdx):
    wzdx_start_date = date_tools.get_unix_from_iso_string(
        wzdx['features'][0]['properties']['start_date'])
    wzdx_end_date = date_tools.get_unix_from_iso_string(
        wzdx['features'][0]['properties']['end_date'])
    icone_start_date = icone['event']['header']['start_timestamp']
    icone_end_date = icone['event']['header']['end_timestamp']
    return (wzdx_start_date - icone_start_date < START_TIME_THRESHOLD_MILLISECONDS
            and icone_end_date - wzdx_end_date < END_TIME_THRESHOLD_MILLISECONDS)


def identify_overlapping_features_icone(icone_standard_msgs, wzdx_msgs):
    icone_routes = {}
    wzdx_routes = {}
    matching_routes = []

    # Step 1: Add route info to iCone messages
    for icone in icone_standard_msgs:
        icone['route_details_start'] = icone['event'].get('additional_info', {}).get(
            'route_details_start')
        icone['route_details_end'] = icone['event'].get('additional_info', {}).get(
            'route_details_end')
        route_details_start, route_details_end = get_route_details_for_icone(
            icone['event']['geometry'])

        if not route_details_start:
            logging.debug(
                f"Invalid route details for iCone: {icone['event']['source']['id']}")
            continue
        icone['route_details_start'] = route_details_start
        icone['route_details_end'] = route_details_end

        if icone['route_details_end'] and route_details_start['Route'] != route_details_end['Route']:
            logging.debug(
                f"Mismatched routes for iCone feature {icone['event']['source']['id']}")
            continue

        if route_details_start['Route'] in icone_routes:
            icone_routes[route_details_start['Route']].append(icone)
        else:
            icone_routes[route_details_start['Route']] = [icone]

    # Step 2: Add route info to WZDx messages
    for wzdx in wzdx_msgs:
        wzdx['route_details_start'] = wzdx['features'][0]['properties'].get(
            'route_details_start')
        wzdx['route_details_end'] = wzdx['features'][0]['properties'].get(
            'route_details_end')
        if not wzdx.get('route_details_start') or not wzdx.get('route_details_end'):
            route_details_start, route_details_end = combination.get_route_details_for_wzdx(
                wzdx['features'][0])

            if not route_details_start or not route_details_end:
                logging.debug(
                    f"Missing WZDx route details {wzdx['features'][0]['id']}")
                continue
            wzdx['route_details_start'] = route_details_start
            wzdx['route_details_end'] = route_details_end
        else:
            route_details_start = wzdx['route_details_start']
            route_details_end = wzdx['route_details_end']

        if route_details_start['Route'] != route_details_end['Route']:
            logging.debug(
                f"Mismatched routes for feature {wzdx['features'][0]['id']}")
            continue

        if route_details_start['Route'] in wzdx_routes:
            wzdx_routes[route_details_start['Route']].append(wzdx)
        else:
            wzdx_routes[route_details_start['Route']] = [wzdx]

    if not icone_routes:
        logging.debug('No routes found for icone')
        return []
    if not wzdx_routes:
        logging.debug('No routes found for wzdx')
        return []

    # Step 3: Identify overlapping events
    for wzdx_route_id, wzdx_matched_msgs in wzdx_routes.items():
        matching_icone_routes = icone_routes.get(wzdx_route_id, [])

        for match_icone in matching_icone_routes:
            for match_wzdx in wzdx_matched_msgs:
                # require routes to overlap, directionality to match, and dates to match
                if (combination.does_route_overlap(match_icone, match_wzdx)
                        and validate_directionality_wzdx_icone(match_icone, match_wzdx)
                        and validate_dates(match_icone, match_wzdx)):

                    matching_routes.append((match_icone, match_wzdx))

    return matching_routes


if __name__ == "__main__":
    main()

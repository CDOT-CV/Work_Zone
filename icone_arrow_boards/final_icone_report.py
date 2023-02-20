import xmltodict
from wzdx.tools import cdot_geospatial_api
import os
from datetime import datetime, timedelta
import json


###################################################################
############ THIS SCRIPT IS INTENDED TO RUN FROM THE ROOT DIRECTORY 
############ IT WAS MOVED FOR ORGANIZATION PURPOSES
###################################################################

def parse_xml_to_dict(xml_string):
    d = xmltodict.parse(xml_string)
    return d


IDS = ['13632527', '13632530', '13632531', '13632528']
ROUTE_ID = "025A"
MILE_MARKER_RANGE = (253.6, 270.24)
CACHED_LOCATIONS = {}
CACHE_THRESHOLD = 3


def check_within_range(min, max, val):
    return min <= val <= max


def check_geofence(lat, lng):
    lng = lng + 0.006
    rounded_lat = round(lat, CACHE_THRESHOLD)
    rounded_lng = round(lng, CACHE_THRESHOLD)
    cache_key = f"{rounded_lat}_{rounded_lng}"
    if cache_key in CACHED_LOCATIONS:
        route_details = CACHED_LOCATIONS[cache_key]
    else:
        route_details = cdot_geospatial_api.get_route_and_measure((lat, lng))
        CACHED_LOCATIONS[cache_key] = route_details
    route = route_details.get('Route')
    mile = route_details.get('Measure')
    return route == ROUTE_ID and check_within_range(*MILE_MARKER_RANGE, mile), mile, route


def check_id(id):
    # print(id)
    return id in IDS


INITIAL_PATH = "./icone_arrow_boards"
files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(INITIAL_PATH)
         for f in filenames if os.path.splitext(f)[1] == '.xml']


# matches = []
segments = []
start_time = None
end_time = None
prevID = None
prevTs = None

for file_path in files:
    # print(file_path)
    fileName = file_path.split('/')[-1]
    ts = datetime.strptime(fileName.split(
        '.')[0].split('_')[-1], "%Y%m%d-%H%M%S")
    icone = xmltodict.parse(open(file_path).read())
    incidents = icone.get('incidents', {}).get('incident', [])

    icone_matches = []
    if type(incidents) == list:
        for incident in incidents:
            id = incident['@id'][1:9]
            if check_id(id):
                coordinates = [float(i) for i in incident.get(
                    'location', {}).get('polyline').split(',')]
                valid, mile_marker, route = check_geofence(
                    coordinates[0], coordinates[1])
                # if not valid:
                #     continue
                update_time = incident['updatetime']
                try:
                    state = incident['display']['status']['@state']
                except:
                    state = [i['@state']
                             for i in incident['display']['status']]
                update_time = incident['updatetime']
                msg = {'id': id, 'update_time': update_time, 'state': state,
                       'lat': coordinates[0], 'lng': coordinates[1], 'mile_marker': mile_marker, "route": route}
                icone_matches.append(msg)
    else:
        incident = incidents
        id = incident['@id'][1:9]
        if check_id(id):
            coordinates = [float(i) for i in incident.get(
                'location', {}).get('polyline').split(',')]
            valid, mile_marker, route = check_geofence(
                coordinates[0], coordinates[1])
            # if not valid:
            #     continue

            update_time = incident['updatetime']
            try:
                state = incident['display']['status']['@state']
            except:
                state = [i['@state']
                         for i in incident['display']['status']]
            update_time = incident['updatetime']
            msg = {'id': id, 'update_time': update_time, 'state': state,
                   'lat': coordinates[0], 'lng': coordinates[1], 'mile_marker': mile_marker, "route": route}
            icone_matches.append(msg)
    # print(icone_matches)
    # matches.append(icone_matches)

    if icone_matches:
        icone = icone_matches[0]
        if len(icone_matches) > 1:
            print("MISSED MATCHES:", len(icone_matches))
        # for icone in icone_matches:
        if not start_time:
            start_time = ts
        end_time = ts

        if prevID and prevTs and ts - prevTs < timedelta(hours=3):
            # print("APPENDING")
            segments[-1]['end_time'] = ts.strftime("%Y-%m-%dT%H:%M:%SZ")
            # segments[-1]['coordinates'].append(
            #     [icone['lng'], icone['lat']])
            if state not in segments[-1]['states']:
                segments[-1]['states'].append(state)
            if icone['mile_marker'] < segments[-1]['mm_min']:
                segments[-1]['mm_min'] = icone['mile_marker']
            elif icone['mile_marker'] > segments[-1]['mm_max']:
                segments[-1]['mm_max'] = icone['mile_marker']

        else:
            # print(icone['id'], prevID)
            # print("CREATING")
            segments.append({'start_time': ts.strftime("%Y-%m-%dT%H:%M:%SZ"), 'end_time': ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                            'id': icone['id'], 'states': [state],
                             'mm_min': icone['mile_marker'], 'mm_max': icone['mile_marker'], 'route': icone['route'],
                             'coordinates': [[float(coordinates[1]), float(coordinates[0])]]
                             })

        # else:
        #     if prevID and ts - prevTs < timedelta(hours=1):
        #         segments[-1]['end_time'] = ts.strftime("%Y-%m-%dT%H:%M:%SZ")
        #     prevID = None
        #     prevTs = None
        #     continue
        prevID = icone['id']
        prevTs = ts
    else:
        if prevID and ts - prevTs < timedelta(hours=1):
            segments[-1]['end_time'] = ts.strftime("%Y-%m-%dT%H:%M:%SZ")
        prevID = None
        prevTs = None


open('final_icone_report.json', 'w').write(
    json.dumps(segments, indent=2, default=str))
# open('final_icone_report_matches.json', 'w').write(
#     json.dumps(matches, indent=2, default=str))

# print(cdot_geospatial_api.get_route_and_measure((40.310253, -104.980264)))

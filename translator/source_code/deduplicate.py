import json
import math
import copy


def wzdx_input():
    icone_input = open('../sample files/Output Message/icone_wzdx_translated.geojson', 'r').read()
    cotrip_input = open('../sample files/Output Message/cotrip_wzdx_translated.geojson', 'r').read()
    return json.loads(icone_input), json.loads(cotrip_input)


def find_duplicate(icone_message_set, cotrip_message_set):
    deduplicated_feed = copy.deepcopy(cotrip_message_set)
    deduplicated_feed['features'] = []
    
    icone_message_map = {}
    for icone_message in icone_message_set['features']:
        icone_message_map[icone_message['properties']['road_event_id']] = icone_message  

    for cotrip_message in cotrip_message_set['features'] :
        add_cotrip = True

        for icone_message in icone_message_set['features']:
            cotrip_lat_long = cotrip_message['geometry']['coordinates'][0]
            icone_lat_long = icone_message['geometry']['coordinates'][0]
            distance = getDist((cotrip_lat_long[0], cotrip_lat_long[1]), (icone_lat_long[0], icone_lat_long[1]))

            if distance < 100:
                add_cotrip = False
                del icone_message_map[icone_message['properties']['road_event_id']] 
                deduplicated_feed['features'].append(icone_message)
                break

        if add_cotrip:
            deduplicated_feed['features'].append(cotrip_message)
    for id in icone_message_map:
        deduplicated_feed['features'].append(icone_message_map[id])
    return deduplicated_feed


def combine_duplicate_messages(icone_obj, cotrip_obj):
    print('duplicate message found')
    return cotrip_obj



def getDist(origin, destination):
    if not origin or not destination:
        return None

    lat1, lon1 = origin  # lat/lon of origin
    lat2, lon2 = destination  # lat/lon of dest

    radius = 6371.0*1000  # meters

    dlat = math.radians(lat2-lat1)  # in radians
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d

with open('deduplicated_wzdx_field', 'w+') as f:
    icone, cotrip = wzdx_input()
    f.write(json.dumps(find_duplicate(cotrip, icone), indent=2))
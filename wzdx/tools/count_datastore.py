from google.cloud import datastore
import json
import datetime
import pytz

import date_tools


_datastore_client = datastore.Client(project='cdot-rtdh-prod')


def get_current_planned_events():
    query = _datastore_client.query(
        namespace='rtdh_cache_latest', kind='RTDHCache')
    query.add_filter('label', '=', 'CacheWZDxPlannedEventsStandard')
    query.add_filter('condition_1', '=', True)
    # query.add_filter('timestamp', '>', datetime.datetime.utcnow(
    # ) - datetime.timedelta(minutes=QUERY_INTERVAL_MINUTES))

    resp = query.fetch()
    resp = list(resp)
    return [json.loads(i['value']) for i in resp]


total_total = 0
total = 0
active_count = 0
planned_count = 0
for i in get_current_planned_events():
    total_total += 1
    if date_tools.parse_datetime_from_iso_string(i['road_event_feed_info']['update_date']) > (datetime.datetime.utcnow().replace(tzinfo=pytz.utc) - datetime.timedelta(days=1)):
        continue
    total += 1
    if i['features'][0]['properties']['event_status'] == "active":
        active_count += 1
    if i['features'][0]['properties']['event_status'] == "planned" or i['features'][0]['properties']['event_status'] == "pending":
        planned_count += 1

print(total_total, total, active_count, planned_count)

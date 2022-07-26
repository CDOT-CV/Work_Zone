import datetime
from google.cloud import datastore
import json


_datastore_client = datastore.Client(project="cdot-rtdh-prod")


def get_planned_events():
    query = _datastore_client.query(
        namespace='rtdh_cache_latest', kind='RTDHCache')
    query.add_filter('label', '=', 'CachePlannedEventsStandard')
    query.add_filter('condition_1', '=', True)
    resp = query.fetch()
    resp = list(resp)
    return resp


def get_recent_planned_events():
    planned_events = get_planned_events()
    prev_time = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc) - datetime.timedelta(days=31)
    recent_planned_events = [
        i for i in planned_events if i['timestamp'] > prev_time]
    return recent_planned_events


with open(f'planned_events_{datetime.datetime.now().strftime("%Y%m%d-%H%M%S")}.json', 'w+', newline='') as f:
    planned_events = get_recent_planned_events()
    f.write(json.dumps([json.loads(i['value'])
            for i in planned_events], indent=2, default=str))

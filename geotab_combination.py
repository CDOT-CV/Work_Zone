#!/usr/bin/env python

# Copyright 2020 Google LLC. This software is provided as is, without
# warranty or representation for any use or purpose. Your use of it is
# subject to your agreement with Google.

from google.cloud import bigquery
import settings
import logging
import flask
import datetime
import requests
import uuid
from wzdx.tools import cdot_geospatial_api
from wzdx.combination import attenuator
import json

app = flask.Flask(__name__)

# Set Logging Object and Functionality
logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)-8s [%(filename)s:%(lineno)d] %(message)s')
l = logging.getLogger(__name__)


ISO_8601_FORMAT_STRING = "%Y-%m-%dT%H:%M:%SZ"
GEOTAB_AUTOMATED_ATTENUATOR_IDS = settings.GEOTAB_AUTOMATED_ATTENUATOR_IDS.split(
    ';')
# General Variables
# d0c2feba6d38df6fdd284d370cbd69636f337d48

# _publisher_client = pubsub_v1.PublisherClient()
# _storage_client = storage.Client()
# _datastore_client = datastore.Client(project=settings.PROJECT)
_bigquery_client = bigquery.Client(project=f'cdot-adap-prod')
try:
    QUERY_INTERVAL_MINUTES = int(settings.QUERY_INTERVAL_MINUTES)
except:
    QUERY_INTERVAL_MINUTES = 5

#######################
# METHODS
#######################


def get_api_response(url, api_key):
    # format URL with username, password, and file path
    formatted_url = url.format(api_key=api_key)

    content = requests.get(formatted_url).content.decode("utf-8")
    # l.info(f"API Response content length: {len(content)}")

    return json.loads(content)


def get_current_planned_events():
    return get_api_response(settings.WZDX_REST_ENDPOINT_PROD, settings.WZDX_REST_API_KEY_PROD)

    # query = _datastore_client.query(
    #     namespace='rtdh_cache_latest', kind='RTDHCache')
    # query.add_filter('label', '=', 'CacheWZDxPlannedEventsStandard')
    # query.add_filter('condition_1', '=', True)
    # # query.add_filter('timestamp', '>', datetime.datetime.utcnow(
    # # ) - datetime.timedelta(minutes=QUERY_INTERVAL_MINUTES))

    # resp = query.fetch()
    # resp = list(resp)
    # return [json.loads(i['value']) for i in resp]


def get_route_info_planned_event(planned_event):
    start = cdot_geospatial_api.get_route_and_measure(
        planned_event['geometry']['coordinates'][0])
    end = cdot_geospatial_api.get_route_and_measure(
        planned_event['geometry']['coordinates'][1])
    if start['Route'] != end['Route'] or start['Measure'] == end['Measure']:
        return None
    else:
        return {
            'route': start['Route'],
            'start_measure': start['Measure'],
            'end_measure': end['Measure']
        }


def get_route_info_geotab(geotab):
    start = cdot_geospatial_api.get_route_and_measure(
        geotab['geometry']['coordinates'][0])
    end = cdot_geospatial_api.get_route_and_measure(
        geotab['geometry']['coordinates'][1])
    if start['Route'] != end['Route'] or start['Measure'] == end['Measure']:
        return None
    else:
        return {
            'route': start['Route'],
            'start_measure': start['Measure'],
            'end_measure': end['Measure']
        }


def create_geotab_query(attenuator_ids):
    queries = []
    now = datetime.datetime.utcnow()
    start = now
    if now.hour == 0 and now.minute < QUERY_INTERVAL_MINUTES:
        start1 = now - \
            datetime.timedelta(minutes=QUERY_INTERVAL_MINUTES)
        end1 = start1.replace(minute=59, second=59, microsecond=99999)
        start2 = now.replace(minute=0, second=0, microsecond=0)
        end2 = now
        queries.append({'year': start1.year, 'month': start1.month, 'day': start1.day, 'startTimestamp': start1.strftime(
            ISO_8601_FORMAT_STRING), 'endTimestamp': end1.strftime(ISO_8601_FORMAT_STRING)})
        queries.append({'year': start2.year, 'month': start2.month, 'day': start2.day, 'startTimestamp': start2.strftime(
            ISO_8601_FORMAT_STRING), 'endTimestamp': end2.strftime(ISO_8601_FORMAT_STRING)})
    else:
        start = now - \
            datetime.timedelta(minutes=QUERY_INTERVAL_MINUTES)
        queries.append({'year': now.year, 'month': now.month, 'day': now.day, 'startTimestamp': start.strftime(
            ISO_8601_FORMAT_STRING), 'endTimestamp': now.strftime(ISO_8601_FORMAT_STRING)})
    query_where_format = '(year = {year} and month = {month} and day = {day} and rtdh_timestamp BETWEEN TIMESTAMP("{startTimestamp}") and TIMESTAMP("{endTimestamp}"))'
    query_where = ' or '.join([query_where_format.format(
        **query_params) for query_params in queries])
    query_ids = ' or '.join(
        [f'avl_location.vehicle.id2 = "{id}"' for id in attenuator_ids])
    query_str = f'''
        SELECT *
        FROM `cdot-adap-prod.raw_from_rtdh_standard.geotab_avl_standard_v3` 
        where ({query_where}) 
    '''
    # and ({query_ids})
    l.debug(query_str)
    return query_str


def get_query_results(query_str):
    query_job = _bigquery_client.query(query_str)
    return list(query_job)


def get_recent_geotab(attenuator_ids):
    query_str = create_geotab_query(attenuator_ids)
    return [{'avl_location': i['avl_location'], 'rtdh_message_id': i['rtdh_message_id'], 'rtdh_timestamp': i['rtdh_timestamp'].strftime(ISO_8601_FORMAT_STRING)} for i in get_query_results(query_str)]


def main():
    now = datetime.datetime.now()
    # This is pretty dumb, but it converts all of the timestamps for formatted ones.

    geotab_msgs = get_recent_geotab(GEOTAB_AUTOMATED_ATTENUATOR_IDS)
    l.info(f"Grabbed matching geotab messages: {len(geotab_msgs)}")

    with open(f'testing_results/geotab_{now.strftime("%Y%m%d-%H%M%S")}.json', 'w+', newline='') as f:
        f.write(json.dumps(geotab_msgs, indent=2, default=str))
    return
    l.info(f"Grabbed attenuator messages: {len(geotab_msgs)}")
    if geotab_msgs:
        planned_events = get_current_planned_events()
        l.info(f"Geotab messages found, planned events: {len(planned_events)}")
        with open(f'testing_results/planned_events_{now.strftime("%Y%m%d-%H%M%S")}.json', 'w+', newline='') as f:
            f.write(json.dumps(planned_events, indent=2, default=str))
        l.info(f"Grabbed planned events wzdx messages: {len(planned_events)}")
        combined_events = attenuator.get_combined_events(
            geotab_msgs, planned_events)
        l.info(f"Generated combined events: {len(combined_events)}")

        with open(f'testing_results/wzdx_{now.strftime("%Y%m%d-%H%M%S")}.json', 'w+', newline='') as f:
            f.write(json.dumps(combined_events, indent=2, default=str))


if __name__ == "__main__":
    main()
    # app.run(debug=True)

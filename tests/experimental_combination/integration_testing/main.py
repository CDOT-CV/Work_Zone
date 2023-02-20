#!/usr/bin/env python

# Copyright 2020 Google LLC. This software is provided as is, without
# warranty or representation for any use or purpose. Your use of it is
# subject to your agreement with Google.

from google.cloud import storage, datastore, bigquery
from . import settings
import logging
import datetime
import uuid
from wzdx.experimental_combination import icone, navjoy, attenuator
from wzdx.tools import combination
import json
import copy
from . import get_geotab
from . import get_icone as get_icone_standard
from . import get_navjoy as get_navjoy_enhanced

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
_storage_client = storage.Client()
_datastore_client = datastore.Client(
    project=f'cdot-rtdh-prod')  # settings.PROJECT
_bigquery_client = bigquery.Client(project=f'cdot-adap-prod')
try:
    QUERY_INTERVAL_MINUTES = int(settings.QUERY_INTERVAL_MINUTES)
except:
    QUERY_INTERVAL_MINUTES = 5

#######################
# METHODS
#######################


def get_wzdx():
    return [json.loads(open('./tests/data/wzdx.json').read())]

    query = _datastore_client.query(
        namespace='rtdh_cache_latest', kind='RTDHCache')
    query.add_filter('label', '=', 'CacheWZDxPlannedEventsStandard')
    query.add_filter('condition_1', '=', True)
    resp = query.fetch()
    resp = list(resp)
    return [json.loads(i['value']) for i in resp]


def get_icone():
    return get_icone_standard.main()

    query = _datastore_client.query(
        namespace='rtdh_cache_latest', kind='RTDHCache')
    query.add_filter('label', '=', 'CacheIconeStandard')
    resp = query.fetch()
    resp = list(resp)
    return resp


def get_navjoy():
    return get_navjoy_enhanced.main()

    query = _datastore_client.query(
        namespace='rtdh_cache_latest', kind='RTDHCache')
    query.add_filter('label', '=', 'CacheWZDxNavjoy')
    resp = query.fetch()
    resp = list(resp)
    return resp


# Write API GET request response to PubSub topic
def write_raw_pubsub(messages, topic):
    open('wzdx_experimental.json', 'w').write(
        json.dumps(messages, default=str))
    return

    topic_path = _publisher_client.topic_path(settings.PROJECT, topic)

    # Loop through all elements and print each element to PubSub
    for msg in messages:
        _publisher_client.publish(
            topic_path, json.dumps(msg, default=str).encode())

    l.info(
        f"Published all {str(len(messages))} messages to PubSub topic {topic}")


# Upload to GCS
def upload_blob(bucket, name, content):
    bucket = _storage_client.bucket(bucket)
    blob = bucket.blob(name)
    blob.upload_from_string(content)


def combine_experimental_feed(wzdx, wzdx_exp):
    output = {}
    for i in wzdx:
        id = i['features'][0]['id']
        output[id] = i

    for i in wzdx_exp:
        id = i['features'][0]['id']
        output[id] = i

    return list(output.values())


def get_experimental_icone(wzdx):
    icone_msgs = [json.loads(
        open('./tests/data/icone_standard.json').read())]
    # icone_msgs = get_icone()
    open('wzdx_icone.json', 'w').write(json.dumps(icone_msgs, default=str))
    return icone.get_combined_events(icone_msgs, wzdx)


def get_experimental_navjoy(wzdx):
    navjoy_wzdx_msgs = get_navjoy()
    open('wzdx_navjoy.json', 'w').write(
        json.dumps(navjoy_wzdx_msgs, default=str))
    return navjoy.get_combined_events(navjoy_wzdx_msgs, wzdx)


def get_experimental_atma(wzdx):
    geotab_msgs = json.loads(open('./tests/data/geotab_msgs_single.json').read())
    # geotab_msgs = get_geotab.get_recent_geotab(
    #     GEOTAB_AUTOMATED_ATTENUATOR_IDS, QUERY_INTERVAL_MINUTES, _bigquery_client)
    # l.info(f"Grabbed attenuator messages: {len(geotab_msgs)}")
    open('wzdx_geotab.json', 'w').write(json.dumps(geotab_msgs, default=str))
    if geotab_msgs:
        l.info(f"Grabbed planned events wzdx messages: {len(wzdx)}")
        combined_events = attenuator.get_combined_events(
            geotab_msgs, wzdx)
        l.info(f"Generated combined events: {len(combined_events)}")
        return combined_events
    return None


def add_wzdx_route_info(wzdx_msgs):
    updated_wzdx = []
    for wzdx in wzdx_msgs:
        feature = wzdx['features'][0]
        route_details_start, route_details_end = combination.get_route_details_for_wzdx(
            feature)
        feature['route_details_start'] = route_details_start
        feature['route_details_end'] = route_details_end
        wzdx['features'][0] = feature
        updated_wzdx.append(wzdx)
    return updated_wzdx


#######################
# Main Control Flow
#######################
def cron():
    l.info("Setting Environment Variables...")
    l.info(f"Environment Variable: Project = {settings.PROJECT}")
    l.info(f"Environment Variable: Region = {settings.REGION}")
    l.info(
        f"Environment Variable: QUERY_INTERVAL_MINUTES = {settings.QUERY_INTERVAL_MINUTES}")
    l.info(
        f"Environment Variable: EXPERIMENTAL_TOPIC = {settings.EXPERIMENTAL_TOPIC}")
    l.info(
        f"Environment Variable: GEOTAB_AUTOMATED_ATTENUATOR_IDS = {settings.GEOTAB_AUTOMATED_ATTENUATOR_IDS}")

    # Retrieve and generate WZDx experimental feed. Order matters, could overwrite data. Put most important last
    wzdx_experimental = get_wzdx()
    # wzdx_experimental = wzdx_experimental[:100]
    wzdx_experimental = add_wzdx_route_info(wzdx_experimental)
    open('wzdx.json', 'w').write(json.dumps(wzdx_experimental))
    print(len(wzdx_experimental))

    # iCone
    wzdx_exp_icone = get_experimental_icone(wzdx_experimental)
    open('wzdx_experimental_icone.json', 'w').write(
        json.dumps(wzdx_exp_icone))
    wzdx_experimental = combine_experimental_feed(
        wzdx_experimental, wzdx_exp_icone)
    print(len(wzdx_experimental))

    # Navjoy 568
    wzdx_exp_navjoy = get_experimental_navjoy(wzdx_experimental)
    open('wzdx_experimental_navjoy.json', 'w').write(
        json.dumps(wzdx_exp_navjoy))
    wzdx_experimental = combine_experimental_feed(
        wzdx_experimental, wzdx_exp_navjoy)
    print(len(wzdx_experimental))

    # ATMA/GeoTab
    wzdx_exp_atma = get_experimental_atma(wzdx_experimental)
    open('wzdx_experimental_geotab.json', 'w').write(
        json.dumps(wzdx_exp_atma))
    wzdx_experimental = combine_experimental_feed(
        wzdx_experimental, wzdx_exp_atma)
    print(len(wzdx_experimental))

    write_raw_pubsub(wzdx_experimental, topic=settings.EXPERIMENTAL_TOPIC)


if __name__ == "__main__":
    cron()

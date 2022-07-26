#!/usr/bin/env python

# Copyright 2020 Google LLC. This software is provided as is, without
# warranty or representation for any use or purpose. Your use of it is
# subject to your agreement with Google.

from google.cloud import datastore
import settings
import logging
import flask
import datetime
from wzdx.tools import date_tools
import json

app = flask.Flask(__name__)

# Set Logging Object and Functionality
logging.basicConfig(level=logging.INFO,
                    format='%(levelname)-8s [%(filename)s:%(lineno)d] %(message)s')
l = logging.getLogger(__name__)


ISO_8601_FORMAT_STRING = "%Y-%m-%dT%H:%M:%SZ"
# General Variables
# d0c2feba6d38df6fdd284d370cbd69636f337d48

_datastore_client = datastore.Client(project='cdot-rtdh-prod')


#######################
# METHODS
#######################
def get_planned_events():
    query = _datastore_client.query(
        namespace='rtdh_cache_latest', kind='RTDHCache')
    query.add_filter('label', '=', 'CachePlannedEventsStandard')
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


def get_incidents():
    query = _datastore_client.query(
        namespace='rtdh_cache_latest', kind='RTDHCache')
    query.add_filter('label', '=', 'CacheIncidentsStandard')
    resp = query.fetch()
    resp = list(resp)
    return resp


def get_recent_incidents():
    incidents = get_incidents()
    prev_time = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc) - datetime.timedelta(days=31)
    recent_incidents = [
        i for i in incidents if i['timestamp'] > prev_time]
    return recent_incidents


def get_wzdx_planned_events():
    query = _datastore_client.query(
        namespace='rtdh_cache_latest', kind='RTDHCache')
    query.add_filter('label', '=', 'CacheWZDxPlannedEventsStandard')
    query.add_filter('condition_1', '=', True)

    resp = query.fetch()
    resp = list(resp)
    return resp


def get_recent_wzdx_planned_events():
    wzdx = get_wzdx_planned_events()
    prev_time = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc) - datetime.timedelta(days=31)
    recent_wzdx = [
        i for i in wzdx if i['timestamp'] > prev_time]
    return recent_wzdx


def get_updated_planned_events(planned_events, wzdx):
    updated_planned_events = []
    update_times = {}
    for i in wzdx:
        msg = json.loads(i['value'])
        id = msg['features'][0]['id'].split('_')[0]
        update_date = date_tools.parse_datetime_from_iso_string(
            msg['features'][0]['properties']['core_details']['update_date'])
        event_status = msg['features'][0]['properties']['event_status']
        if id not in update_times:
            update_times[id] = (update_date, event_status)
        else:
            prev_date = update_times[id][0]
            if update_date > prev_date:
                update_times[id] = (update_date, event_status)

    yesterday = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc) - datetime.timedelta(hours=23)
    for i in planned_events:
        msg = json.loads(i['value'])
        id = msg['properties']['id']
        update_date = date_tools.parse_datetime_from_iso_string(
            msg['properties']['lastUpdated'])
        start_date = date_tools.parse_datetime_from_iso_string(
            msg['properties']['startTime'])
        end_date = date_tools.parse_datetime_from_iso_string(
            msg['properties'].get('clearTime'))
        event_status = date_tools.get_event_status(start_date, end_date)

        wzdx_update_date, wzdx_event_status = update_times.get(
            id, (None, None))
        if wzdx_event_status and event_status != wzdx_event_status:
            updated_planned_events.append(i)
        elif wzdx_update_date:
            wzdx_update_date = wzdx_update_date.replace(
                tzinfo=datetime.timezone.utc)
            # account for minor differences in timestamps
            # Find updated messages, where update_date in raw is greater than wzdx
            logging.info(id)
            logging.info(wzdx_update_date, yesterday)

            if update_date > (wzdx_update_date + datetime.timedelta(seconds=1)):
                updated_planned_events.append(i)
            # Update messages at least once per day
            elif wzdx_update_date < yesterday:
                updated_planned_events.append(i)
        else:
            # not found, should create
            updated_planned_events.append(i)
    return updated_planned_events

# Write API GET request response to PubSub topic


#######################
# Main Control Flow
#######################
# @app.route('/cron/wzdx-planned-events', methods=['GET'])
def main():
    # Prevent executions outside of App Engine Cron.
    if flask.request.headers.get('X-AppEngine-Cron') != 'true':
        flask.abort(400)

    l.info("Setting Environment Variables...")
    l.info(f"Environment Variable: Project = {settings.PROJECT}")
    l.info(f"Environment Variable: Region = {settings.REGION}")
    l.info(f"Environment Variable: Raw Topic ID = {settings.TOPIC}")

    request_timestamp = (flask.request.date
                         if flask.request.date is not None
                         else datetime.datetime.now(datetime.timezone.utc))

    recent_planned_events = get_planned_events()
    l.info(f"Grabbed planned events: {len(recent_planned_events)}")
    wzdx_planned_events = get_wzdx_planned_events()
    l.info(f"Grabbed WZDx planned events: {len(wzdx_planned_events)}")

    entries = get_updated_planned_events(
        recent_planned_events, wzdx_planned_events)
    entries += get_recent_incidents()

    with open(f'planned_events_app_engine{datetime.datetime.now().strftime("%Y%m%d-%H%M%S")}.json', 'w+', newline='') as f:
        f.write(json.dumps(json.loads(entries, indent=2, default=str)))

    # blob_name = '{}/{}/{}.xml'.format(
    #     'wzdx_planned_events',
    #     request_timestamp.strftime('year=%Y/month=%m/day=%d/time=%H:%M:%SZ'),
    #     uuid.uuid4())
    # upload_blob(settings.BUCKET, blob_name, json.dumps(entries, default=str))
    # l.info(f"Upload raw data to GCS.")

    # write_raw_pubsub(entries)

    l.info(f"Open TMS Planned Events API Called at: {request_timestamp}")

    return ((f"Open TMS Planned Events API Called - Data Written to PubSub. {request_timestamp}"), 200)


if __name__ == "__main__":
    main()
    # app.run(debug=True)

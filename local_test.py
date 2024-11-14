import json
import time
import uuid
from wzdx.raw_to_standard import planned_events
from wzdx.standard_to_enhanced.planned_events_translator import wzdx_creator
import logging
import datetime
import pytz


from wzdx.tools import cdot_geospatial_api
from google.cloud import datastore

CACHED_REQUESTS = {}

PROCESS_WARNING_TIME = 30

planned_events_list = json.load(
    open("./wzdx/sample_files/raw/planned_events/all_events_2024_11_08.json")
)
datastore_client = datastore.Client(
    project="cdot-rtdh-test", namespace="geospatial_caching"
)
wzdx_info = {
    # pipeline_options.wzdx_contact_name,
    "contact_name": "Heather Pickering-Hilgers",
    # pipeline_options.wzdx_contact_email,
    "contact_email": "heather.pickeringhilgers@state.co.us",
    "publisher": "CDOT",
}


def getCachedRequest(url: str) -> str:
    return CACHED_REQUESTS.get(url)
    # try:
    #     key = datastore_client.key("cachedRequest", url)
    #     task = datastore_client.get(key)

    #     # Check if entity doesn't exist or is older than 14 days
    #     if task is None or task["timestamp"] < datetime.datetime.now(
    #         pytz.utc
    #     ) - datetime.timedelta(days=14):
    #         return None
    #     return task.get("response")
    # except Exception as e:
    #     logging.error("Error getting cached request for key %s: %s", url, e)
    #     return None


def setCachedRequest(url: str, response: str) -> None:
    CACHED_REQUESTS[url] = response
    # key = datastore_client.key("cachedRequest", url)
    # task = datastore.Entity(key=key, exclude_from_indexes=["response"])
    # task.update({"response": response, "timestamp": datetime.datetime.now(pytz.utc)})
    # datastore_client.put(task)


geospatial_api = cdot_geospatial_api.GeospatialApi(
    setCachedRequest=setCachedRequest,
    getCachedRequest=getCachedRequest,
)

messages = []

for i, raw_msg in enumerate(planned_events_list):
    if i % 10 == 0:
        print(i)
    start = time.time()
    id = f"{raw_msg.get('properties', {}).get('id', uuid.uuid4())}_{uuid.uuid4()}"
    events = planned_events.expand_event_directions(raw_msg)

    split = time.time()
    if (split - start) > PROCESS_WARNING_TIME:
        logging.warning(
            f"sid: {id}, step: split___, delta: {split - start}, delta_full: {split - start}"
        )
    for i, elem in enumerate(events):
        new_dict = planned_events.generate_rtdh_standard_message_from_raw_single(
            geospatial_api, elem
        )
        standard = time.time()
        if (standard - split) > PROCESS_WARNING_TIME:
            logging.warning(
                f"sid: {id}, index: {i}, step: standard, delta: {standard - split}, delta_full: {standard - start}"
            )
        split = time.time()

        # Avoiding non-relevant workzones, which are returned as {}
        if not new_dict:
            logging.debug(f"sid: {id}, index: {i}, step: standard-empty")
            split = time.time()
            continue
        if not new_dict["event"]["additional_info"].get("condition_1"):
            new_dict["event"]["additional_info"]["condition_1"] = True

        wzdx = wzdx_creator(new_dict, info={})
        # if not wzdx:
        #     print(f"wzdx_creator failed: {new_dict["rtdh_message_id"]}")
        #     continue
        wzdx["condition_1"] = new_dict["event"]["additional_info"]["condition_1"]
        enhanced = time.time()
        if (enhanced - standard) > PROCESS_WARNING_TIME:
            logging.warning(
                f"sid: {id}, index: {i}, step: enhanced, delta: {enhanced - standard}, delta_full: {enhanced - start}"
            )

        messages.append(wzdx)
        split = time.time()
    if not events:
        # not sure if this is necessary
        continue

json.dump(messages, open("./enhanced_2024_11_08_replay_2.json", "w"), indent=2)
# messages = json.load(open("./enhanced_2024_11_08_replay.json"))

active_messages = [
    message
    for message in messages
    if message["features"][0]["properties"]["condition_1"]
]
json.dump(active_messages, open("./active_2024_11_08.json", "w"), indent=2)


enhanced = []
skipped = 0
good = 0
updated = 0
short = 0
# enhanced messages without matching route ids
for message in active_messages:
    start_details = message["features"][0]["properties"].get("route_details_start", {})
    end_details = message["features"][0]["properties"].get("route_details_end", {})
    if len(message["features"][0]["geometry"]["coordinates"]) == 2:
        short += 1
        print(message["features"][0]["id"], start_details, end_details)
        continue
    if not start_details or not end_details:
        skipped += 1
        # enhanced.append(message)
    elif start_details["Route"] != end_details["Route"]:
        updated += 1
        print(message["features"][0]["id"])
        print(start_details["Route"], end_details["Route"])
    else:
        good += 1
        # enhanced.append(message)
print(short, skipped, good, updated)

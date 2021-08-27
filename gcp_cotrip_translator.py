import json
import logging
import os

import json
from google.cloud import pubsub_v1
from datetime import datetime, timedelta

from translator import cotrip_translator
from translator.tools import gcp_tools, wzdx_translator


def pull_recent_messages():
    project_id = "cdot-rtdh-prod"
    #subscription_id = "salesforce-events-standard-oim-wzdx-integration"
    #subscription_id = "cotrip-events-standard-oim-wzdx-integration"
    subscription_id = "cotrip-alerts-standard-oim-wzdx-integration"
    # subscription_id = "cotrip-alerts-raw-oim-wzdx-integration"
    subscriber = pubsub_v1.SubscriberClient()
    timeout = 60
    NUM_MESSAGES = 10

    bucket_name = 'data_salesforce'

    subscription_path = subscriber.subscription_path(
        project_id, subscription_id)
    # streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    print('--------------------------------------------------------------')
    print(f"Listening for messages on {subscription_path}..\n")

    time_7_days_ago = datetime.now() - timedelta(days=7)
    # Wrap subscriber in a 'with' block to automatically call close() when done.

    messages = []

    with subscriber:

        response = subscriber.pull(
            request={
                "subscription": subscription_path,
                "max_messages": 5
            }
        )

        for msg in response.received_messages:
            print("Received message:", msg.message.data)

            # destination_blob_name = project_id + '_' + subscription_id + '_' + datetime.now().strftime("%Y%m%d-%H%M%S-%f")
            # blob = bucket.blob(destination_blob_name)
            # blob.upload_from_string(msg.message.data.decode('utf-8'))
            messages.append(json.loads(msg.message.data.decode('utf-8')))

        ack_ids = [msg.ack_id for msg in response.received_messages]


def main(event):
    try:
        cotrip_messages = pull_recent_messages()
    except ValueError as e:
        logging.error(
            'Unable to retrive COtrip events from RTDH')
        return 'failed to get data from RTDH. Exiting Application!', 500

    for message in cotrip_messages:
        wzdx_obj = cotrip_translator.wzdx_creator(
            message, unsupported_message_callback=gcp_tools.unsupported_messages_callback)

        wzdx_schema = gcp_tools.get_wzdx_schema(
            'translator/sample files/validation_schema/wzdx_v3.1_feed.json')

        if not wzdx_translator.validate_wzdx(wzdx_obj, wzdx_schema):
            logging.error(
                'validation error more message are printed above. output file is not created because the message failed validation.')
            # return 'WZDx message failed validation. Exiting Application !', 500
        print("Generated WZDx message")

        gcp_tools.publish_wzdx_message(wzdx_obj)

    return "Success"

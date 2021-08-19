import json
import logging
import os

import requests
from flask import abort
from google.cloud import pubsub_v1

from translator import navjoy_translator
from translator.tools import wzdx_translator

# from google.cloud import error_reporting
# client = error_reporting.Client()


# def main(request):
#     print("Running Translator")
#     directions = navjoy_translator.get_directions_from_string(" East/West ")
#     print(directions)

#     return


def get_new_568_data():
    response = requests.get(os.environ['navjoy_568_endpoint'])
    return response.content()


def main(request):
    try:
        navjoy_obj = json.loads(get_new_568_data())
    except ValueError as e:
        logging.error(
            'Unable to retrive Navjoy 568 data from API endpoint')
        return abort(500)
    wzdx_obj = navjoy_translator.wzdx_creator(
        navjoy_obj, unsupported_message_callback=unsupported_messages_callback)

    location_schema = 'translator/sample files/validation_schema/wzdx_v3.1_feed.json'
    wzdx_schema = json.loads(open(location_schema).read())

    if not wzdx_translator.validate_wzdx(wzdx_obj, wzdx_schema):
        logging.error(
            'validation error more message are printed above. output file is not created because the message failed validation.')
        return abort(500)
    print("Generated WZDx message")

    publish_message(wzdx_obj)

    return "Success"


def publish_message(obj):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(
        os.environ['project_id'], os.environ['wzdx_topic_id'])
    future = publisher.publish(topic_path, str.encode(json.dumps(
        obj, indent=2)), origin='navjoy 568 translator cloud function')
    print(future.result())


def unsupported_messages_callback(message):
    project_id = os.environ.get('project_id')
    unsupported_messages_topic_id = os.environ.get(
        'unsupported_messages_topic_id')
    if not project_id or not unsupported_messages_topic_id:
        return False
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(
        project_id, unsupported_messages_topic_id)
    # publish unsupported messages into pub/sub topic
    try:
        future = publisher.publish(topic_path, str.encode(formatMessage(
            message)), origin='navjoy 568 translator cloud function')
    except Exception as e:
        logging.error('failed to publish unsupported message to project_id: {:s}, topic_id: {:s}, error_message: {:s}'.format(
            project_id, unsupported_messages_topic_id, str(e)))
        return False
    print(future.result())
    return True


def formatMessage(message) -> str:
    message_type = [dict, list, tuple, str, int, float, bool, type(None)]
    if type(message) in message_type:
        msg = json.dumps(message, indent=2)
    else:
        msg = str(message)
    return msg

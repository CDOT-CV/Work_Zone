import json
import logging
import os
import jsonschema

from google.cloud import pubsub_v1


def publish_wzdx_message(obj):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(
        os.environ['project_id'], os.environ['wzdx_topic_id'])
    future = publisher.publish(topic_path, str.encode(json.dumps(
        obj, indent=2)), origin=os.environ['publish_source'])
    print(future.result())


def unsupported_messages_callback(message):
    project_id = os.environ['project_id']
    unsupported_messages_topic_id = os.environ[
        'unsupported_messages_topic_id']
    if not project_id or not unsupported_messages_topic_id:
        return False
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(
        project_id, unsupported_messages_topic_id)
    # publish unsupported messages into pub/sub topic
    try:
        future = publisher.publish(topic_path, str.encode(formatMessage(
            message)), origin=os.environ['publish_source'])
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

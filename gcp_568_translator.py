import json
import logging
import os

import requests

from translator import navjoy_translator
from translator.tools import gcp_tools, wzdx_translator


def get_new_568_data():
    response = requests.get(os.environ['navjoy_568_endpoint'])
    return response.content.decode("utf-8")


def main(request, context):
    try:
        navjoy_obj = json.loads(get_new_568_data())
    except ValueError as e:
        logging.error(
            'Unable to retrive Navjoy 568 data from API endpoint')
        return 'failed to get data from REST API. Exiting Application!', 500
    wzdx_obj = navjoy_translator.wzdx_creator(
        navjoy_obj, unsupported_message_callback=gcp_tools.unsupported_messages_callback)

    wzdx_schema = gcp_tools.get_wzdx_schema(
        'translator/sample files/validation_schema/wzdx_v3.1_feed.json')

    if not wzdx_translator.validate_wzdx(wzdx_obj, wzdx_schema):
        logging.error(
            'validation error more message are printed above. output file is not created because the message failed validation.')
        return 'WZDx message failed validation. Exiting Application !', 500
    print("Generated WZDx message")

    gcp_tools.publish_wzdx_message(wzdx_obj)

    return "Success"

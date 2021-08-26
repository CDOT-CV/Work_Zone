import json
import logging
import os
import urllib

import xmltodict
from google.cloud import secretmanager

from translator import icone_translator
from translator.tools import gcp_tools, wzdx_translator


def get_ftp_url():
    server = os.environ['ftp_server_address']
    port = os.environ['ftp_port']
    user, password = get_ftp_credentials()
    if not user or not password:
        return None
    filepath = os.environ['ftp_icone_file_path']
    ftpString = 'ftp://{0}:{1}@{2}:{3}/{4}'
    ftpUrl = ftpString.format(user, password, server, port, filepath)
    return ftpUrl


def main(event, context):
    try:
        ftp_url = get_ftp_url()
        if not ftp_url:
            logging.error(RuntimeError(
                'failed to get ftp url. Exiting Application!'))
            return 'failed to get ftp url. Exiting Application!', 500

        icone_data = get_ftp_file(ftp_url)
    except:
        logging.error(RuntimeError(
            'failed to get ftp file. Exiting Application!'))
        return 'failed to get ftp file. Exiting Application!', 500
    icone_obj = parse_xml(icone_data)

    wzdx_obj = icone_translator.wzdx_creator(
        icone_obj, unsupported_message_callback=gcp_tools.unsupported_messages_callback)

    wzdx_schema = gcp_tools.get_wzdx_schema(
        'translator/sample files/validation_schema/wzdx_v3.1_feed.json')
    if not wzdx_translator.validate_wzdx(wzdx_obj, wzdx_schema):
        logging.error(RuntimeError(
            'WZDx message failed validation. Exiting Application !'))
        return 'WZDx message failed validation. Exiting Application !', 500

    gcp_tools.publish_wzdx_message(wzdx_obj)

    return "Success"


def get_ftp_file(url):
    return urllib.request.urlopen(url).read().decode('utf-8-sig')


def parse_xml(xml_string):
    return xmltodict.parse(xml_string)


def get_ftp_credentials():
    secret_client = secretmanager.SecretManagerServiceClient()
    username_secret_name = os.environ.get('icone_ftp_username_secret_name')
    password_secret_name = os.environ.get('icone_ftp_password_secret_name')
    project_id = os.environ.get('project_id')

    if not username_secret_name or not password_secret_name or not project_id:
        return None, None
    request = {
        "name": f"projects/{project_id}/secrets/{username_secret_name}/versions/latest"}
    try:
        response = secret_client.access_secret_version(request)
    except:
        logging.error(RuntimeError(
            'unable to get username from secret. Either the secret does not exist or there are no permissions!'))
        return None, None
    username = response.payload.data.decode("UTF-8")

    request = {
        "name": f"projects/{project_id}/secrets/{password_secret_name}/versions/latest"}
    try:
        response = secret_client.access_secret_version(request)
    except:
        logging.error(RuntimeError(
            'unable to get password from secret. Either the secret does not exist or there are no permissions!'))
        return None, None
    password = response.payload.data.decode("UTF-8")

    return username, password

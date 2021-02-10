import sys
sys.path.append('..')
from translator.GCP_cloud_function.cloud_function import main, icone_translator
from unittest.mock import MagicMock, patch
import urllib.request as request
from contextlib import closing
from google.cloud import pubsub_v1
import os


# import icone_translator
# from gcloud import storage
# import json
# import xmltodict
# import shutil
# import urllib.request as request
# from contextlib import closing
# from google.cloud import pubsub_v1
# import os
# from google.cloud import secretmanager
#
#
#
# server = os.environ['ftp_server_address']
# port = os.environ['ftp_port']
# user=os.environ['icone_ftp_username']
# password=os.environ['icone_ftp_password']
# #user,password=get_ftp_credentials()
# filepath = os.environ['ftp_icone_file_path']
#
#
# ftpString = 'ftp://{0}:{1}@{2}:{3}/{4}'
# ftpUrl = ftpString.format(user, password, server, port, filepath)
#
#
# def translate_newest_icone_to_wzdx(event, context):
#
#
#   icone_data=get_ftp_file(ftpUrl)
#   icone_obj=parse_xml(icone_data)
#
#   wzdx_obj=icone_translator.wzdx_creator(icone_obj)
#   wzdx_schema=get_wzdx_schema('wzdx_schema.json')
#   #this will throw an exception if validation fails
#   icone_translator.validate_wzdx(wzdx_obj,wzdx_schema)
#   print(json.dumps(wzdx_obj))
#
#   publisher = pubsub_v1.PublisherClient()
#   topic_path = publisher.topic_path(os.environ['project_id'], os.environ['wzdx_topic_id'])
#   future=publisher.publish(topic_path,str.encode(json.dumps(wzdx_obj, indent=2)),origin='auto_icone_translator_ftp cloud function')
#   print(future.result())
#   return

# def test_translate_newest_icone_to_wzdx():
#     get_ftp_file=MagicMock(return_value)

@patch('urllib.request')
def test_get_ftp_file(request):
    test_url='fake url'
    test_output=main.get_ftp_file(test_url)
    request.urlopen.assert_called_with(test_url)
    assert True

@patch('pubsub_v1')
@patch('icone_translator')
def test_translate_newest_icone_to_wzdx(icone,pubsub):
    get_ftp_url=MagicMock(return_value='')
    get_ftp_file=MagicMock(return_value='')
    parse_xml=MagicMock(return_value='')
    #icone_translator = MagicMock()
    icone.wzdx_creator= MagicMock(return_value='WZDx')
    icone.validate_wzdx= MagicMock(return_value='')
    os.environ['project_id']='project_id'
    os.environ['wzdx_topic_id']='wzdx_topic_id'
    main.translate_newest_icone_to_wzdx(None,None)
    assert True
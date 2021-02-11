import sys
sys.path.append('..')
sys.path.append('./translator/GCP_cloud_function/cloud_function')
import main, icone_translator
# import translator
#from translator.GCP_cloud_function.cloud_function import icone_translator
from unittest.mock import MagicMock, patch
import urllib.request as request
from contextlib import closing
from google.cloud import pubsub_v1
import os
import json

@patch('urllib.request')
def test_get_ftp_file(request):
    test_url='fake url'
    test_output=main.get_ftp_file(test_url)
    request.urlopen.assert_called_with(test_url)
    assert True


@patch('google.cloud.pubsub_v1.PublisherClient')
@patch.object(icone_translator,'wzdx_creator')
@patch.object(icone_translator,'validate_wzdx')
@patch(main)
def test_translate_newest_icone_to_wzdx(test_main, validate_wzdx, wzdx_creator, pubsub):
    #import main as temp_main
    temp_main.get_ftp_url=MagicMock(return_value='')
    temp_main.get_ftp_file=MagicMock(return_value='')
    temp_main.parse_xml=MagicMock(return_value='')
    temp_main.get_wzdx_schema=MagicMock(return_value='')
    icone_translator.wzdx_creator= MagicMock(return_value='WZDx')
    icone_translator.validate_wzdx= MagicMock(return_value='')
    os.environ['project_id']='project_id'
    os.environ['wzdx_topic_id']='wzdx_topic_id'
    temp_main.translate_newest_icone_to_wzdx(None,None)
    publisher=pubsub().publish
    publisher.assert_called_with(pubsub().topic_path('project_id', 'wzdx_topic_id'),str.encode(json.dumps('WZDx', indent=2)),origin='auto_icone_translator_ftp cloud function')
    assert True

def test_get_ftp_url():
    import main
    os.environ['ftp_server_address']='www.icone.com'
    os.environ['ftp_port']='4425'
    os.environ['icone_ftp_username']='username'
    os.environ['icone_ftp_password']='password'
    # user,password=get_ftp_credentials()
    os.environ['ftp_icone_file_path']='test_filepath'
    test_ftp_url='ftp://username:password@www.icone.com:4425/test_filepath'
    actual=main.get_ftp_url()
    assert actual==test_ftp_url


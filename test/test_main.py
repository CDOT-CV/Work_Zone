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

@patch('urllib.request')
def test_get_ftp_file(request):
    test_url='fake url'
    test_output=main.get_ftp_file(test_url)
    request.urlopen.assert_called_with(test_url)
    assert True


@patch('google.cloud.pubsub_v1.PublisherClient')
@patch.object(icone_translator,'wzdx_creator')
@patch.object(icone_translator,'validate_wzdx')
def test_translate_newest_icone_to_wzdx(validate_wzdx, wzdx_creator, pubsub):
    #from translator.GCP_cloud_function.cloud_function import icone_translator
    main.get_ftp_url=MagicMock(return_value='')
    main.get_ftp_file=MagicMock(return_value='')
    main.parse_xml=MagicMock(return_value='')
    main.get_wzdx_schema=MagicMock(return_value='')
    #icone_translator = MagicMock()
    icone_translator.wzdx_creator= MagicMock(return_value='WZDx')
    icone_translator.validate_wzdx= MagicMock(return_value='')
    os.environ['project_id']='project_id'
    os.environ['wzdx_topic_id']='wzdx_topic_id'
    #from translator.GCP_cloud_function.cloud_function import main
    main.translate_newest_icone_to_wzdx(None,None)
    publisher=pubsub().publish
    publisher.assert_called_with('')
    assert True
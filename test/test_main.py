import sys
from collections import OrderedDict
sys.path.append('..')
sys.path.append('./translator/GCP_cloud_function/cloud_function')
from unittest.mock import MagicMock, patch, call, Mock
sys.modules['icone_translator'] =Mock()
import main
import icone_translator
import os
import json


@patch('urllib.request')
def test_get_ftp_file(request):
    test_url='fake url'
    test_output=main.get_ftp_file(test_url)
    request.urlopen.assert_called_with(test_url)
    assert True


@patch('google.cloud.pubsub_v1.PublisherClient')
@patch.object(main, 'get_ftp_url')
@patch.object(main, 'get_ftp_file')
@patch.object(main, 'parse_xml')
@patch.object(main, 'get_wzdx_schema')
def test_translate_newest_icone_to_wzdx(get_wzdx_schema, parse_xml, get_ftp_file, get_ftp_url, pubsub):
#the intent of this magic mock fuction is that we give a valid input ,that publishes data
    main.get_ftp_url=MagicMock(return_value='')
    main.get_ftp_file=MagicMock(return_value='')
    main.parse_xml=MagicMock(return_value='')
    main.get_wzdx_schema=MagicMock(return_value='')
    icone_translator.wzdx_creator= MagicMock(return_value='WZDx')
    icone_translator.validate_wzdx= MagicMock(return_value=True)
    os.environ['project_id']='project_id'
    os.environ['wzdx_topic_id']='wzdx_topic_id'
    main.translate_newest_icone_to_wzdx(None,None)
    publisher=pubsub().publish
    publisher.assert_called_with(pubsub().topic_path('project_id', 'wzdx_topic_id'),str.encode(json.dumps('WZDx', indent=2)),origin='auto_icone_translator_ftp cloud function')



@patch.object(main, 'get_ftp_credentials')
def test_get_ftp_url(ftp_credentials):
    credentials='username', 'password'
    main.get_ftp_credentials=MagicMock(return_value=credentials)
    os.environ['ftp_server_address']='www.icone.com'
    os.environ['ftp_port']='4425'
    os.environ['icone_ftp_username']='username'
    os.environ['icone_ftp_password']='password'
    os.environ['ftp_icone_file_path']='test_filepath'
    test_ftp_url='ftp://username:password@www.icone.com:4425/test_filepath'
    actual=main.get_ftp_url()
    assert actual==test_ftp_url

def test_parse_xml():
    test_parse_xml_string= """<incident id="U13631595_202012160845">
        <updatetime>2020-12-16T17:18:00Z</updatetime>
        <type>CONSTRUCTION</type>
         <type> Hazard </type>
          <polyline>34.8380671,-114.1450650,34.8380671,-114.1450650</polyline>
        </incident>"""

    test_valid_output= {"incident": OrderedDict({'@id': 'U13631595_202012160845', 'updatetime': '2020-12-16T17:18:00Z', 'type': ['CONSTRUCTION', 'Hazard'], 'polyline': '34.8380671,-114.1450650,34.8380671,-114.1450650' })}
    actual_output= main.parse_xml(test_parse_xml_string)
    assert actual_output == test_valid_output


@patch('google.cloud.secretmanager.SecretManagerServiceClient')
def test_get_ftp_credentials(secret):
    os.environ['icone_ftp_username_secret_name']='secret_username'
    os.environ['icone_ftp_password_secret_name']='secret_password'
    os.environ['project_id'] = 'project_id'
    main.get_ftp_credentials()
    valid_secret_user_request={"name": "projects/project_id/secrets/secret_username/versions/latest"}
    valid_secret_pass_request = {"name": "projects/project_id/secrets/secret_password/versions/latest"}
    requests=[call(valid_secret_user_request),call().payload.data.decode("UTF-8"), call(valid_secret_pass_request), call().payload.data.decode("UTF-8")]
    secret_client=secret().access_secret_version
    secret_client.assert_has_calls(requests)


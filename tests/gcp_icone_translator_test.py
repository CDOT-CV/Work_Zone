from collections import OrderedDict
import gcp_icone_translator
import pytest
import json
import os
import sys
from unittest.mock import MagicMock, patch, Mock
from translator import icone_translator
from translator.tools import wzdx_translator, gcp_tools


# --------------------------------------------------------------------------------unit test for get_ftp_file function--------------------------------------------------------------------------------
@patch('urllib.request')
def test_get_ftp_file(request):
    test_url = 'fake url'
    test_output = gcp_icone_translator.get_ftp_file(test_url)
    request.urlopen.assert_called_with(test_url)


# --------------------------------------------------------------------------------unit test for main function--------------------------------------------------------------------------------
@patch('google.cloud.pubsub_v1.PublisherClient')
@patch.object(gcp_icone_translator, 'get_ftp_url')
@patch.object(gcp_icone_translator, 'get_ftp_file')
@patch.object(gcp_icone_translator, 'parse_xml')
@patch.object(gcp_tools, 'get_wzdx_schema')
@patch.object(icone_translator, 'wzdx_creator')
@patch.object(wzdx_translator, 'validate_wzdx')
@patch.dict(os.environ, {
    'project_id': 'project_id',
    'wzdx_topic_id': 'wzdx_topic_id',
    'publish_source': 'publish_source'
})
def test_main_success(validate_wzdx, wzdx_creator, get_wzdx_schema, parse_xml, get_ftp_file, get_ftp_url, pubsub):
    # the intent of this magic mock fuction is that we give a valid input ,that publishes data
    gcp_icone_translator.get_ftp_url = MagicMock(return_value='url')
    gcp_icone_translator.get_ftp_file = MagicMock(return_value='')
    gcp_icone_translator.parse_xml = MagicMock(return_value='')
    gcp_tools.get_wzdx_schema = MagicMock(return_value='')
    icone_translator.wzdx_creator = MagicMock(return_value='WZDx')
    wzdx_translator.validate_wzdx = MagicMock(
        return_value=True)

    gcp_icone_translator.main(None, None)
    publisher = pubsub().publish
    publisher.assert_called_with(pubsub().topic_path('project_id', 'wzdx_topic_id'), str.encode(
        json.dumps('WZDx', indent=2)), origin='publish_source')


@patch('google.cloud.pubsub_v1.PublisherClient')
@patch.object(gcp_icone_translator, 'get_ftp_url')
@patch.object(gcp_icone_translator, 'get_ftp_file')
@patch.object(gcp_icone_translator, 'parse_xml')
@patch.object(gcp_tools, 'get_wzdx_schema')
@patch.object(icone_translator, 'wzdx_creator')
@patch.object(wzdx_translator, 'validate_wzdx')
@patch.dict(os.environ, {
    'project_id': 'project_id',
    'wzdx_topic_id': 'wzdx_topic_id',
    'publish_source': 'publish_source'
})
def test_main_validation_failed(validate_wzdx, wzdx_creator, get_wzdx_schema, parse_xml, get_ftp_file, get_ftp_url, pubsub):
    # the intent of this magic mock fuction is that we give a valid input ,that publishes data
    gcp_icone_translator.get_ftp_url = MagicMock(return_value='url')
    gcp_icone_translator.get_ftp_file = MagicMock(return_value='')
    gcp_icone_translator.parse_xml = MagicMock(return_value='')
    gcp_tools.get_wzdx_schema = MagicMock(return_value='')
    icone_translator.wzdx_creator = MagicMock(return_value='WZDx')
    wzdx_translator.validate_wzdx = MagicMock(
        return_value=False)

    gcp_icone_translator.main(None, None)
    publisher = pubsub().publish
    publisher.assert_not_called()


@patch('google.cloud.pubsub_v1.PublisherClient')
@patch.object(gcp_icone_translator, 'get_ftp_url')
@patch.object(gcp_icone_translator, 'get_ftp_file')
@patch.object(gcp_icone_translator, 'parse_xml')
@patch.object(gcp_tools, 'get_wzdx_schema')
@patch.dict(os.environ, {
    'project_id': 'project_id',
    'wzdx_topic_id': 'wzdx_topic_id',
})
def test_main_no_ftp_url(get_wzdx_schema, parse_xml, get_ftp_file, get_ftp_url, pubsub):
    # the intent of this magic mock fuction is that we give a valid input ,that publishes data
    gcp_icone_translator.get_ftp_url = MagicMock(return_value=None)
    gcp_icone_translator.main(None, None)
    publisher = pubsub().publish
    publisher.assert_not_called()


@patch('google.cloud.pubsub_v1.PublisherClient')
@patch.object(gcp_icone_translator, 'get_ftp_url')
@patch.object(gcp_icone_translator, 'get_ftp_file')
@patch.object(gcp_icone_translator, 'parse_xml')
@patch.object(gcp_tools, 'get_wzdx_schema')
@patch.dict(os.environ, {
    'project_id': 'project_id',
    'wzdx_topic_id': 'wzdx_topic_id',
})
def test_main_invalid_ftp_url(get_wzdx_schema, parse_xml, get_ftp_file, get_ftp_url, pubsub):
    # the intent of this magic mock fuction is that we give a valid input ,that publishes data
    gcp_icone_translator.get_ftp_url = MagicMock(return_value='url')
    gcp_icone_translator.get_ftp_file = MagicMock(
        side_effect=ValueError('malformed URL'))
    gcp_icone_translator.main(None, None)
    publisher = pubsub().publish
    publisher.assert_not_called()

# --------------------------------------------------------------------------------unit test for get_ftp_url function--------------------------------------------------------------------------------


@patch.dict(os.environ, {
    'ftp_server_address': 'www.icone.com',
    'ftp_port': '4425',
    'icone_ftp_username': 'username',
    'icone_ftp_password': 'password',
    'ftp_icone_file_path': 'test_filepath',
})
@patch.object(gcp_icone_translator, 'get_ftp_credentials')
def test_get_ftp_url(ftp_credentials):
    credentials = 'username', 'password'
    gcp_icone_translator.get_ftp_credentials = MagicMock(
        return_value=credentials)
    test_ftp_url = 'ftp://username:password@www.icone.com:4425/test_filepath'
    actual = gcp_icone_translator.get_ftp_url()
    assert actual == test_ftp_url


@patch.object(gcp_icone_translator, 'get_ftp_credentials')
@patch.dict(os.environ, {})
def test_get_ftp_url_missing_environment_variable(ftp_credentials):
    credentials = 'username', 'password'
    gcp_icone_translator.get_ftp_credentials = MagicMock(
        return_value=credentials)
    with pytest.raises(KeyError):
        gcp_icone_translator.get_ftp_url()

# --------------------------------------------------------------------------------unit test for parse_xml function--------------------------------------------------------------------------------


def test_parse_xml():
    test_parse_xml_string = """<incident id="U13631595_202012160845">
        <updatetime>2020-12-16T17:18:00Z</updatetime>
        <type>CONSTRUCTION</type>
         <type> Hazard </type>
          <polyline>34.8380671,-114.1450650,34.8380671,-114.1450650</polyline>
        </incident>"""
    test_valid_output = {"incident": OrderedDict({'@id': 'U13631595_202012160845', 'updatetime': '2020-12-16T17:18:00Z', 'type': [
                                                 'CONSTRUCTION', 'Hazard'], 'polyline': '34.8380671,-114.1450650,34.8380671,-114.1450650'})}
    actual_output = gcp_icone_translator.parse_xml(test_parse_xml_string)
    assert actual_output == test_valid_output

# --------------------------------------------------------------------------------unit test for get_ftp_credentials function--------------------------------------------------------------------------------


@patch.dict(os.environ, {
    'icone_ftp_username_secret_name': 'secret_username',
    'icone_ftp_password_secret_name': 'secret_password',
    'project_id': 'project_id'})
@patch('google.cloud.secretmanager.SecretManagerServiceClient')
def test_get_ftp_credentials(secret):
    secret().access_secret_version = fake_secret_client
    actual = gcp_icone_translator.get_ftp_credentials()
    valid_username = 'username'
    valid_password = 'password'
    expected = (valid_username, valid_password)
    assert actual == expected


@patch.dict(os.environ, {})
@patch('google.cloud.secretmanager.SecretManagerServiceClient')
def test_get_ftp_credentials_no_env_vars(secret):
    secret().access_secret_version = fake_secret_client
    actual = gcp_icone_translator.get_ftp_credentials()
    assert actual == (None, None)


@patch.dict(os.environ, {
    'icone_ftp_username_secret_name': 'secret_username',
    'icone_ftp_password_secret_name': 'fail',
    'project_id': 'project_id'})
@patch('google.cloud.secretmanager.SecretManagerServiceClient')
def test_get_ftp_secrets_password_does_not_exist(secret):
    secret().access_secret_version = fake_secret_client
    actual = gcp_icone_translator.get_ftp_credentials()

    assert actual == (None, None)


@patch.dict(os.environ, {
    'icone_ftp_username_secret_name': 'fail',
    'icone_ftp_password_secret_name': 'secret_password',
    'project_id': 'project_id'})
@patch('google.cloud.secretmanager.SecretManagerServiceClient')
def test_get_ftp_secrets_username_does_not_exist(secret):
    secret().access_secret_version = fake_secret_client
    actual = gcp_icone_translator.get_ftp_credentials()

    assert actual == (None, None)


valid_secret_user_request = {
    "name": "projects/project_id/secrets/secret_username/versions/latest"}
valid_secret_pass_request = {
    "name": "projects/project_id/secrets/secret_password/versions/latest"}


def fake_secret_client(request):
    if request == valid_secret_user_request:
        username = MagicMock()
        username.payload.data = b'username'
        return username

    elif request == valid_secret_pass_request:
        password = MagicMock()
        password.payload.data = b'password'
        return password

    else:
        raise RuntimeError('secret does not exist!')

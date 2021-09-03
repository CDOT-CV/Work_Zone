import json
import pytest
import os
from unittest.mock import patch
from translator.tools import gcp_tools


# --------------------------------------------------------------------------------unit test for unsupported_messages_callback function--------------------------------------------------------------------------------
@patch('google.cloud.pubsub_v1.PublisherClient')
@patch.dict(os.environ, {'project_id': 'project_id',
                         'unsupported_messages_topic_id': 'unsupported_messages_topic_id',
                         'publish_source': 'publish_source'})
def test_unsupported_messages_callback_dict(pubsub):
    output = gcp_tools.unsupported_messages_callback(
        {'messages': 'unsupported_messages'})
    publisher = pubsub().publish
    publisher.assert_called_with(pubsub().topic_path('project_id', 'unsupported_messages_topic_id'), str.encode(
        json.dumps({'messages': 'unsupported_messages'}, indent=2)), origin='publish_source')


@patch('google.cloud.pubsub_v1.PublisherClient')
@patch.dict(os.environ, {'project_id': 'project_id',
                         'unsupported_messages_topic_id': 'unsupported_messages_topic_id',
                         'publish_source': 'publish_source'})
def test_unsupported_messages_callback_string(pubsub):
    output = gcp_tools.unsupported_messages_callback(
        'unsupported_messages')
    publisher = pubsub().publish
    publisher.assert_called_with(pubsub().topic_path('project_id', 'unsupported_messages_topic_id'), str.encode(
        json.dumps('unsupported_messages')), origin='publish_source')


# --------------------------------------------------------------------------------unit test for formatMessage function--------------------------------------------------------------------------------
def test_formatMessage_dict_type():
    test_message = {'type': 'PCMS',
                    'id': 'I-75 NB - MP 48.3',
                    'timestamp': '2020-08-21T15:48:25Z'}

    actual = gcp_tools.formatMessage(test_message)
    expected_output = '{\n  "type": "PCMS",\n  "id": "I-75 NB - MP 48.3",\n  "timestamp": "2020-08-21T15:48:25Z"\n}'
    assert actual == expected_output


def test_formatMessage_string_type():
    test_message = 'string_type_message'
    actual = gcp_tools.formatMessage(test_message)
    expected_output = '"string_type_message"'
    assert actual == expected_output


def test_formatMessage_list_type():
    test_message = ['message', 'type', 'list', 12345]
    actual = gcp_tools.formatMessage(test_message)
    expected_output = '[\n  "message",\n  "type",\n  "list",\n  12345\n]'
    assert actual == expected_output


def test_formatMessage_None_type():
    test_message = None
    actual = gcp_tools.formatMessage(test_message)
    expected_output = 'null'
    assert actual == expected_output


def test_formatMessage_int_type():
    test_message = 12345
    actual = gcp_tools.formatMessage(test_message)
    expected_output = '12345'
    assert actual == expected_output


def test_formatMessage_float_type():
    test_message = 12345.67
    actual = gcp_tools.formatMessage(test_message)
    expected_output = '12345.67'
    assert actual == expected_output


def test_formatMessage_byte_string():
    test_message = b'byte_string_message'
    actual = gcp_tools.formatMessage(test_message)
    expected_output = "b'byte_string_message'"
    assert actual == expected_output


# --------------------------------------------------------------------------------unit test for get_wzdx_schema function--------------------------------------------------------------------------------
def test_get_wzdx_schema():
    expected_schema = json.loads(
        open('translator/sample files/validation_schema/wzdx_v3.1_feed.json').read())
    actual = gcp_tools.get_wzdx_schema(
        'translator/sample files/validation_schema/wzdx_v3.1_feed.json')
    assert actual == expected_schema


def test_get_wzdx_schema_invalid_data():
    with pytest.raises(RuntimeError) as runtimeErr:
        gcp_tools.get_wzdx_schema('tests/docs/invalid_schema.json')
    assert 'invalid schema: not valid json' in str(runtimeErr.value)


def test_get_wzdx_schema_not_exist():
    with pytest.raises(RuntimeError) as runtimeErr:
        gcp_tools.get_wzdx_schema('not_exist.json')
    assert 'invalid schema: file does not exist' in str(runtimeErr.value)

import json
import os
from unittest.mock import MagicMock, patch

import gcp_568_translator
from translator import navjoy_translator
from translator.tools import wzdx_translator, gcp_tools


# --------------------------------------------------------------------------------unit test for main function--------------------------------------------------------------------------------
@patch('google.cloud.pubsub_v1.PublisherClient')
@patch.object(gcp_568_translator, 'get_new_568_data')
@patch.object(gcp_tools, 'get_wzdx_schema')
@patch.object(gcp_tools, 'publish_wzdx_message')
@patch.object(navjoy_translator, 'wzdx_creator')
@patch.object(wzdx_translator, 'validate_wzdx')
@patch.dict(os.environ, {
    'project_id': 'project_id',
    'wzdx_topic_id': 'wzdx_topic_id',
    'publish_source': 'publish_source'
})
def test_main_success(validate_wzdx, wzdx_creator, publish_wzdx_message, get_wzdx_schema, get_new_568_data, pubsub):
    # the intent of this magic mock fuction is that we give a valid input, that publishes data
    gcp_568_translator.get_new_568_data = MagicMock(return_value='{}')
    gcp_tools.get_wzdx_schema = MagicMock(return_value='')
    gcp_tools.publish_wzdx_message = MagicMock()
    navjoy_translator.wzdx_creator = MagicMock(return_value='WZDx')
    wzdx_translator.validate_wzdx = MagicMock(
        return_value=True)

    gcp_568_translator.main(None, None)
    gcp_tools.publish_wzdx_message.assert_called_with('WZDx')


@patch('google.cloud.pubsub_v1.PublisherClient')
@patch.object(gcp_568_translator, 'get_new_568_data')
@patch.object(gcp_tools, 'get_wzdx_schema')
@patch.object(gcp_tools, 'publish_wzdx_message')
@patch.object(navjoy_translator, 'wzdx_creator')
@patch.object(wzdx_translator, 'validate_wzdx')
@patch.dict(os.environ, {
    'project_id': 'project_id',
    'wzdx_topic_id': 'wzdx_topic_id',
    'publish_source': 'publish_source'
})
def test_main_validation_failed(validate_wzdx, wzdx_creator, get_wzdx_schema, publish_wzdx_message, get_new_568_data, pubsub):
    # the intent of this magic mock fuction is that we give a valid input, that publishes data
    gcp_568_translator.get_new_568_data = MagicMock(return_value='')
    gcp_tools.get_wzdx_schema = MagicMock(return_value='')
    gcp_tools.publish_wzdx_message = MagicMock()
    navjoy_translator.wzdx_creator = MagicMock(return_value='WZDx')
    wzdx_translator.validate_wzdx = MagicMock(
        return_value=False)

    gcp_568_translator.main(None, None)
    gcp_tools.publish_wzdx_message.assert_not_called()

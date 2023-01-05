import os
import uuid
import argparse
from datetime import datetime
from unittest.mock import Mock, patch

import time_machine
import xmltodict
from wzdx.standard_to_enhanced import icone_translator
from wzdx.tools import wzdx_translator

from tests.data.standard_to_enhanced import icone_translator_data


@patch.object(argparse, 'ArgumentParser')
def test_parse_planned_events_arguments(argparse_mock):
    iconeFile, outputFile = icone_translator.parse_icone_arguments()
    assert iconeFile != None and outputFile != None


# --------------------------------------------------------------------------------Unit test for get_vehicle_impact function--------------------------------------------------------------------------------
def test_get_vehicle_impact_some_lanes_closed():
    test_description = "Roadwork - Lane Closed, MERGE LEFT [Trafficade, iCone]"
    test_vehicle_impact = icone_translator.get_vehicle_impact(test_description)
    expected_vehicle_impact = "some-lanes-closed"
    assert test_vehicle_impact == expected_vehicle_impact


def test_get_vehicle_impact_all_lanes_open():
    test_description = 'Road Ranger Emergency Personnel On-Scene. Move over - Caution [DBi, iCone]'
    test_vehicle_impact = icone_translator.get_vehicle_impact(test_description)
    expected_vehicle_impact = "all-lanes-open"
    assert test_vehicle_impact == expected_vehicle_impact


# --------------------------------------------------------------------------------Unit test for wzdx_creator function--------------------------------------------------------------------------------
def test_wzdx_creator_empty_icone_object():
    icone_obj = None
    test_wzdx = icone_translator.wzdx_creator(icone_obj)
    assert test_wzdx == None


def test_wzdx_creator_invalid_info_object():
    icone_obj = {
        "rtdh_timestamp": 1638894543.6077065,
        "rtdh_message_id": "b33b2851-0475-4c8c-8bb7-c63e449190a9",
        "event": {
            "type": "CONSTRUCTION",
            "source": {
                "id": "1245",
                "creation_timestamp": 1572916940000,
                "last_updated_timestamp": 1636142163000
            },
            "geometry": [
                [
                    -84.1238971,
                    37.1686478
                ],
                [
                    -84.1238971,
                    37.1686478
                ],
                [
                    -84.145861,
                    37.1913
                ],
                [
                    -84.145861,
                    37.1913
                ],
                [
                    -84.157105,
                    37.201197
                ],
                [
                    -84.167033,
                    37.206079
                ],
                [
                    -84.204074,
                    37.21931
                ]
            ],
            "header": {
                "description": "19-1245: Roadwork between MP 40 and MP 48",
                "start_timestamp": 1623183301000,
                "end_timestamp": "None"
            },
            "detail": {
                "road_name": "I-75 N",
                "road_number": "I-75 N",
                "direction": "northbound"
            },
            "additional_info": {

            }
        }
    }

    test_invalid_info_object = {
        'contact_name': "Heather Pickering-Hilgers",
        'contact_email': "heather.pickeringhilgers@state.co.us",
        'publisher': "iCone",
    }

    test_wzdx = icone_translator.wzdx_creator(
        icone_obj, test_invalid_info_object)
    assert test_wzdx == None


@patch.dict(os.environ, {
    'contact_name': 'Heather Pickering-Hilgers',
    'contact_email': 'heather.pickeringhilgers@state.co.us',
    'publisher': 'CDOT'
})
@patch('uuid.uuid4')
def test_wzdx_creator(mockuuid):
    uuid.uuid4 = Mock()
    uuid.uuid4.side_effect = 'we234de'

    icone_obj = {
        "rtdh_timestamp": 1638894543.6077065,
        "rtdh_message_id": "b33b2851-0475-4c8c-8bb7-c63e449190a9",
        "event": {
            "type": "CONSTRUCTION",
            "source": {
                "id": "1245",
                "creation_timestamp": 1572916940000,
                "last_updated_timestamp": 1636142163000
            },
            "geometry": [
                [
                    -84.1238971,
                    37.1686478
                ],
                [
                    -84.1238971,
                    37.1686478
                ],
                [
                    -84.145861,
                    37.1913
                ],
                [
                    -84.145861,
                    37.1913
                ],
                [
                    -84.157105,
                    37.201197
                ],
                [
                    -84.167033,
                    37.206079
                ],
                [
                    -84.204074,
                    37.21931
                ]
            ],
            "header": {
                "description": "19-1245: Roadwork between MP 40 and MP 48",
                "start_timestamp": 1623183301000,
                "end_timestamp": 1623186301000
            },
            "detail": {
                "road_name": "I-75 N",
                "road_number": "I-75 N",
                "direction": "northbound"
            }
        }
    }

    expected_wzdx = icone_translator_data.test_wzdx_creator_expected

    with time_machine.travel(datetime(2021, 4, 13, 0, 0, 0)):
        test_wzdx = icone_translator.wzdx_creator(icone_obj)
    test_wzdx = wzdx_translator.remove_unnecessary_fields(test_wzdx)
    assert expected_wzdx == test_wzdx


# --------------------------------------------------------------------------------unit test for parse_icone_sensor function--------------------------------------------------------------------------------
def test_parse_icone_sensor():
    valid_description = {'type': 'iCone', 'id': '#4', 'location': [41.3883260, -81.9707500], 'radar': {
        'average_speed': 63.52, 'std_dev_speed': 7.32, 'timestamp': '2020-08-21T15:55:00Z'}}
    test_sensor = icone_translator_data.test_parse_icone_sensor_test_sensor_1
    output_description = icone_translator.parse_icone_sensor(test_sensor)
    assert output_description == valid_description

    valid_description = {'type': 'iCone', 'id': '#4', 'location': [41.3883260, -81.9707500],
                         'radar': {'average_speed': 64.32, 'std_dev_speed': 6.11, 'timestamp': '2020-08-21T15:40:00Z'}}
    test_sensor = icone_translator_data.test_parse_icone_sensor_test_sensor_2
    output_description = icone_translator.parse_icone_sensor(test_sensor)
    assert output_description == valid_description


# --------------------------------------------------------------------------------unit test for parse_pcms_sensor function--------------------------------------------------------------------------------
def test_parse_pcms_sensor():
    valid_description = {'type': 'PCMS', 'id': 'I-75 NB - MP 48.3', 'timestamp': '2020-08-21T15:48:25Z',
                         'location': [37.2182000, -84.2027000], 'messages': [' ROADWORK / 5 MILES / AHEAD']}
    test_sensor = {'@type': 'PCMS', '@id': 'I-75 NB - MP 48.3', '@latitude': '37.2182000', '@longitude': '-84.2027000', 'message': {
        '@verified': '2020-08-21T15:48:25Z', '@latitude': '37.2178100', '@longitude': '-84.2024390', '@text': ' ROADWORK / 5 MILES / AHEAD'}}
    output_description = icone_translator.parse_pcms_sensor(test_sensor)
    assert output_description == valid_description


# --------------------------------------------------------------------------------unit test for create_description function--------------------------------------------------------------------------------
def test_create_description():
    test_description = icone_translator_data.test_create_description_description
    test_incident = """ <incident id="1246">
    <creationtime>2019-11-05T01:32:44Z</creationtime>
    <updatetime>2020-08-21T15:52:02Z</updatetime>
    <type>CONSTRUCTION</type>
    <description>19-1245: Roadwork between MP 48 and MP 40</description>
    <location>
      <street>I-75 S</street>
      <direction>ONE_DIRECTION</direction>
      <polyline>37.2066700,-84.1691290,37.2012230,-84.1573460,37.1858150,-84.1404820,37.1663450,-84.1214250,37.1478080,-84.1115880</polyline>
    </location>
    <starttime>2019-11-22T23:02:21Z</starttime>
    <sensor type="iCone" id="SB 1 - MP 40.8" latitude="37.1478080" longitude="-84.1115880" />
    <sensor type="iCone" id="SB 2 - MP 42.1" latitude="37.1663450" longitude="-84.1214250">
      <radar devID="1614" intervalEnd="2020-08-21T15:45:00Z" latitude="37.1663422" longitude="-84.1214254" numReads="67" avgSpeed="67.43" stDevSpeed="6.5561" />
      <radar devID="1614" intervalEnd="2020-08-21T15:50:00Z" latitude="37.1663422" longitude="-84.1214254" numReads="48" avgSpeed="68.54" stDevSpeed="6.2738" />
      <radar devID="1614" intervalEnd="2020-08-21T15:55:00Z" latitude="37.1663422" longitude="-84.1214254" numReads="38" avgSpeed="66.84" stDevSpeed="6.4339" />
    </sensor>
    <sensor type="iCone" id="SB 3 - MP 44.0" latitude="37.1858150" longitude="-84.1404820">
      <radar devID="1740" intervalEnd="2020-08-21T15:40:00Z" latitude="37.1857562" longitude="-84.1404956" numReads="9" avgSpeed="61.39" stDevSpeed="6.3463" />
      <radar devID="1740" intervalEnd="2020-08-21T15:45:00Z" latitude="37.1857562" longitude="-84.1404956" numReads="68" avgSpeed="65.51" stDevSpeed="6.5987" />
      <radar devID="1740" intervalEnd="2020-08-21T15:50:00Z" latitude="37.1857562" longitude="-84.1404956" numReads="33" avgSpeed="66.59" stDevSpeed="6.6288" />
    </sensor>
    <sensor type="iCone" id="SB 4 - MP 45.7" latitude="37.2012230" longitude="-84.1573460">
      <radar devID="1724" intervalEnd="2020-08-21T15:40:00Z" latitude="37.2012256" longitude="-84.1573747" numReads="21" avgSpeed="64.64" stDevSpeed="5.6432" />
      <radar devID="1724" intervalEnd="2020-08-21T15:45:00Z" latitude="37.2012256" longitude="-84.1573747" numReads="38" avgSpeed="69.21" stDevSpeed="6.9488" />
      <radar devID="1724" intervalEnd="2020-08-21T15:50:00Z" latitude="37.2012256" longitude="-84.1573747" numReads="62" avgSpeed="64.11" stDevSpeed="9.0186" />
      <radar devID="1724" intervalEnd="2020-08-21T15:55:00Z" latitude="37.2012256" longitude="-84.1573747" numReads="17" avgSpeed="66.91" stDevSpeed="5.3667" />
    </sensor>
    <sensor type="iCone" id="SB 5 - MP 47.5" latitude="37.2066700" longitude="-84.1691290">
      <radar devID="1735" intervalEnd="2020-08-21T15:45:00Z" latitude="37.2066724" longitude="-84.1691283" numReads="70" avgSpeed="67.00" stDevSpeed="6.2133" />   
    </sensor>
    <sensor type="iCone" id="SB 6 - MP 48.5" latitude="37.2193130" longitude="-84.2046600" />
    <sensor type="iCone" id="SB 7 - MP 49.5" latitude="37.2299854" longitude="-84.2221508">
      <radar devID="1719" intervalEnd="2020-08-21T15:40:00Z" numReads="19" avgSpeed="67.24" stDevSpeed="4.9229" />
      <radar devID="1719" intervalEnd="2020-08-21T15:45:00Z" numReads="38" avgSpeed="65.00" stDevSpeed="10.7934" />
      <radar devID="1719" intervalEnd="2020-08-21T15:50:00Z" numReads="62" avgSpeed="62.82" stDevSpeed="9.7647" />
      <radar devID="1719" intervalEnd="2020-08-21T15:55:00Z" numReads="41" avgSpeed="59.57" stDevSpeed="8.8250" />
    </sensor>
    <sensor type="iCone" id="SB 8 - MP 50.5" latitude="37.2378880" longitude="-84.2359180" />
    <display type="PCMS" id="I-75 SB - MP 50" latitude="37.2339700" longitude="-84.2290798">
      <message verified="2020-08-21T15:42:27Z" text=" ROADWORK / 4 MILES / AHEAD // 19 MILES / OF WORK / MP 48-29" />
      <message verified="2020-08-21T15:52:27Z" text=" ROADWORK / 4 MILES / AHEAD // 19 MILES / OF WORK / MP 48-29" />
    </display>
    <display type="PCMS" id="I-75 SB - MP 46" latitude="37.2059920" longitude="-84.1672690">
      <message verified="2020-08-21T15:48:32Z" latitude="37.2060070" longitude="-84.1673050" text=" ROADWORK / NEXT / 5 MILES // 19 MILES / OF WORK / MP 48-29" />
    </display>
  </incident>"""
    output_description = icone_translator.create_description(
        xmltodict.parse(test_incident)['incident'])
    assert output_description == test_description

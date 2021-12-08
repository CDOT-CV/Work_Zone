import os
import uuid
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import time_machine
import xmltodict
from wzdx import icone_translator


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
            }
        }
    }

    test_invalid_info_object = {
        'feed_info_id': "104d7746-e948bf9dfa",
        'metadata': {
            'wz_location_method': "channel-device-method",
            'lrs_type': "lrs_type",
            'contact_name': "Ashley Nylen",
            'contact_email': "ashley.nylen@state.co.us",
            'issuing_organization': "iCone",
        }
    }

    test_wzdx = icone_translator.wzdx_creator(
        icone_obj, test_invalid_info_object)
    assert test_wzdx == None


@patch.dict(os.environ, {
    'contact_name': 'Ashley Nylen',
    'contact_email': 'ashley.nylen@state.co.us',
    'issuing_organization': 'CDOT'
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
                "end_timestamp": "None"
            },
            "detail": {
                "road_name": "I-75 N",
                "road_number": "I-75 N",
                "direction": "northbound"
            }
        }
    }

    expected_wzdx = {
        'road_event_feed_info': {
            'feed_info_id': '104d7746-688c-44ed-b195-2ee948bf9dfa',
            'update_date': '2021-04-13T00:00:00Z',
            'publisher': 'CDOT',
            'contact_name': 'Ashley Nylen',
            'contact_email': 'ashley.nylen@state.co.us',
            'version': '3.1',
            'license': 'https://creativecommons.org/publicdomain/zero/1.0/',
            'data_sources': [
                {'data_source_id': 'w',
                 'feed_info_id': '104d7746-688c-44ed-b195-2ee948bf9dfa',
                 'organization_name': 'CDOT',
                 'contact_name': 'Ashley Nylen',
                 'contact_email': 'ashley.nylen@state.co.us',
                 'update_date': '2021-04-13T00:00:00Z',
                 'location_method': 'channel-device-method',
                 'lrs_type': 'lrs_type'}
            ]
        },
        'type': 'FeatureCollection',
        'features': [
                {
                    'type': 'Feature',
                    'properties': {
                        'road_event_id': '2',
                        'event_type': 'work-zone',
                        'data_source_id': 'w',
                        'start_date': '2021-06-08T20:15:01Z',
                        'end_date': None,
                        'start_date_accuracy': 'estimated',
                        'end_date_accuracy': 'estimated',
                        'beginning_accuracy': 'estimated',
                        'ending_accuracy': 'estimated',
                        'road_names': ['I-75 N'],
                        'direction': 'northbound',
                        'vehicle_impact': 'all-lanes-open',
                        'event_status': 'planned',
                        'description': '19-1245: Roadwork between MP 40 and MP 48',
                        'creation_date': '2019-11-05T01:22:20Z',
                        'update_date': '2021-11-05T19:56:03Z'
                    },
                    'geometry': {
                        'type': 'LineString',
                        'coordinates': [
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
                        ]
                    }
                }
        ]
    }

    with time_machine.travel(datetime(2021, 4, 13, 0, 0, 0)):
        test_wzdx = icone_translator.wzdx_creator(icone_obj)
    assert expected_wzdx == test_wzdx


# --------------------------------------------------------------------------------unit test for parse_icone_sensor function--------------------------------------------------------------------------------
def test_parse_icone_sensor():
    valid_description = {'type': 'iCone', 'id': '#4', 'location': [41.3883260, -81.9707500], 'radar': {
        'average_speed': 63.52, 'std_dev_speed': 7.32, 'timestamp': '2020-08-21T15:55:00Z'}}
    test_sensor = {"@type": "iCone", "@id": "#4", "@latitude": "41.3883260", "@longitude": "-81.9707500", "radar": [{"@devID": "1645", "@intervalEnd": "2020-08-21T15:40:00Z", "@latitude": "41.3883258", "@longitude": "-81.9707325", "@numReads": "22", "@avgSpeed": "64.32", "@stDevSpeed": "6.1080"}, {"@devID": "1645", "@intervalEnd": "2020-08-21T15:45:00Z", "@latitude": "41.3883258", "@longitude": "-81.9707325", "@numReads": "43", "@avgSpeed": "63.66", "@stDevSpeed": "5.1282"}, {
        "@devID": "1645", "@intervalEnd": "2020-08-21T15:50:00Z", "@latitude": "41.3883258", "@longitude": "-81.9707325", "@numReads": "59", "@avgSpeed": "63.52", "@stDevSpeed": "7.9526"}, {"@devID": "1645", "@intervalEnd": "2020-08-21T15:55:00Z", "@latitude": "41.3883258", "@longitude": "-81.9707325", "@numReads": "18", "@avgSpeed": "62.22", "@stDevSpeed": "11.9760"}]}
    output_description = icone_translator.parse_icone_sensor(test_sensor)
    assert output_description == valid_description

    valid_description = {'type': 'iCone', 'id': '#4', 'location': [41.3883260, -81.9707500],
                         'radar': {'average_speed': 64.32, 'std_dev_speed': 6.11, 'timestamp': '2020-08-21T15:40:00Z'}}
    test_sensor = {"@type": "iCone", "@id": "#4", "@latitude": "41.3883260", "@longitude": "-81.9707500", "radar": [
        {"@devID": "1645", "@intervalEnd": "2020-08-21T15:40:00Z", "@latitude": "41.3883258",
         "@longitude": "-81.9707325", "@numReads": "22", "@avgSpeed": "64.32", "@stDevSpeed": "6.1080"}]}
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
    test_description = "19-1245: Roadwork between MP 48 and MP 40\n sensors: \n{\n  \"type\": \"iCone\",\n  \"id\": \"SB 1 - MP 40.8\",\n  \"location\": [\n    37.147808,\n    -84.111588\n  ]\n}\n{\n  \"type\": \"iCone\",\n  \"id\": \"SB 2 - MP 42.1\",\n  \"location\": [\n    37.166345,\n    -84.121425\n  ],\n  \"radar\": {\n    \"average_speed\": 67.63,\n    \"std_dev_speed\": 6.44,\n    \"timestamp\": \"2020-08-21T15:55:00Z\"\n  }\n}\n{\n  \"type\": \"iCone\",\n  \"id\": \"SB 3 - MP 44.0\",\n  \"location\": [\n    37.185815,\n    -84.140482\n  ],\n  \"radar\": {\n    \"average_speed\": 65.5,\n    \"std_dev_speed\": 6.59,\n    \"timestamp\": \"2020-08-21T15:50:00Z\"\n  }\n}\n{\n  \"type\": \"iCone\",\n  \"id\": \"SB 4 - MP 45.7\",\n  \"location\": [\n    37.201223,\n    -84.157346\n  ],\n  \"radar\": {\n    \"average_speed\": 65.94,\n    \"std_dev_speed\": 7.49,\n    \"timestamp\": \"2020-08-21T15:55:00Z\"\n  }\n}\n{\n  \"type\": \"iCone\",\n  \"id\": \"SB 5 - MP 47.5\",\n  \"location\": [\n    37.20667,\n    -84.169129\n  ],\n  \"radar\": {\n    \"average_speed\": 67.0,\n    \"std_dev_speed\": 6.21,\n    \"timestamp\": \"2020-08-21T15:45:00Z\"\n  }\n}\n{\n  \"type\": \"iCone\",\n  \"id\": \"SB 6 - MP 48.5\",\n  \"location\": [\n    37.219313,\n    -84.20466\n  ]\n}\n{\n  \"type\": \"iCone\",\n  \"id\": \"SB 7 - MP 49.5\",\n  \"location\": [\n    37.2299854,\n    -84.2221508\n  ],\n  \"radar\": {\n    \"average_speed\": 63.03,\n    \"std_dev_speed\": 9.19,\n    \"timestamp\": \"2020-08-21T15:55:00Z\"\n  }\n}\n{\n  \"type\": \"iCone\",\n  \"id\": \"SB 8 - MP 50.5\",\n  \"location\": [\n    37.237888,\n    -84.235918\n  ]\n}\n displays: \n{\n  \"type\": \"PCMS\",\n  \"id\": \"I-75 SB - MP 50\",\n  \"timestamp\": \"2020-08-21T15:52:27Z\",\n  \"location\": [\n    37.23397,\n    -84.2290798\n  ],\n  \"messages\": [\n    \" ROADWORK / 4 MILES / AHEAD // 19 MILES / OF WORK / MP 48-29\"\n  ]\n}\n{\n  \"type\": \"PCMS\",\n  \"id\": \"I-75 SB - MP 46\",\n  \"timestamp\": \"2020-08-21T15:48:32Z\",\n  \"location\": [\n    37.205992,\n    -84.167269\n  ],\n  \"messages\": [\n    \" ROADWORK / NEXT / 5 MILES // 19 MILES / OF WORK / MP 48-29\"\n  ]\n}"
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

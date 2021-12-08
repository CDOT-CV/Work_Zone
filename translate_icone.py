from wzdx.raw_to_standard import icone

msg_string = """<?xml version='1.0' encoding='utf8'?>
<incidents timestamp="2020-08-21T15:54:01Z">
<incident id="1245">
    <creationtime>2019-11-05T01:22:20Z</creationtime>
    <updatetime>2021-11-05T19:56:03Z</updatetime>
    <type>CONSTRUCTION</type>
    <description>19-1245: Roadwork between MP 40 and MP 48</description>
    <location>
        <street>I-75 N</street>
        <direction>ONE_DIRECTION</direction>
        <polyline>37.1686478,-84.1238971,37.1686478,-84.1238971,37.1913000,-84.1458610,37.1913000,-84.1458610,37.2011970,-84.1571050,37.2060790,-84.1670330,37.2193100,-84.2040740</polyline>
    </location>
    <starttime>2021-06-08T20:15:01Z</starttime>
</incident>
</incidents>"""

print(icone.generate_standard_messages_from_string(msg_string))

{
    "rtdh_timestamp": 1638894117.0838838,
    "rtdh_message_id": "57b0dcbd-a80d-4c12-aa20-8b908c5c938f",
    "event": {
        "type": "CONSTRUCTION",
        "source": {
            "id": "1245",
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

test_generate_standard_messages_from_string_expected = [
    {
        "rtdh_timestamp": 1618272000,
        "rtdh_message_id": "we234de",
        "event": {
            "type": "CONSTRUCTION",
            "source": {
                "id": "1245",
                "creation_timestamp": 1572916940000,
                "last_updated_timestamp": 1598025122000,
            },
            "geometry": [
                [-84.112854, 37.157199],
                [-84.1238971, 37.1686478],
                [-84.145861, 37.1913],
                [-84.175297, 37.209348],
                [-84.201303, 37.216837],
            ],
            "header": {
                "description": "19-1245: Roadwork between MP 40 and MP 48",
                "start_timestamp": 1581700096000,
                "end_timestamp": 1618876800000,
            },
            "detail": {
                "road_name": "I-75 N",
                "road_number": "I-75 N",
                "direction": "northbound",
            },
            "additional_info": {
                "condition_1": True,
                "route_details_end": {},
                "route_details_start": {},
                "devices": [
                    {
                        "sensor_type": "sensor",
                        "details": {
                            "@id": "NB 1 - MP 48.7",
                            "@latitude": "37.2168370",
                            "@longitude": "-84.2013030",
                            "@type": "iCone",
                        },
                    },
                    {
                        "sensor_type": "sensor",
                        "details": {
                            "@id": "NB 2 - MP 46.1",
                            "@latitude": "37.2093480",
                            "@longitude": "-84.1752970",
                            "@type": "iCone",
                        },
                    },
                    {
                        "sensor_type": "sensor",
                        "details": {
                            "@id": "NB 3 - MP 44.3",
                            "@latitude": "37.1913000",
                            "@longitude": "-84.1458610",
                            "@type": "iCone",
                        },
                    },
                    {
                        "sensor_type": "sensor",
                        "details": {
                            "@id": "NB 4 - MP 42.5",
                            "@latitude": "37.1686478",
                            "@longitude": "-84.1238971",
                            "@type": "iCone",
                            "radar": [
                                {
                                    "@avgSpeed": "65.69",
                                    "@devID": "1738",
                                    "@intervalEnd": "2020-08-21T15:45:00Z",
                                    "@numReads": "58",
                                    "@stDevSpeed": "5.4874",
                                },
                                {
                                    "@avgSpeed": "68.55",
                                    "@devID": "1738",
                                    "@intervalEnd": "2020-08-21T15:50:00Z",
                                    "@numReads": "38",
                                    "@stDevSpeed": "6.5362",
                                },
                                {
                                    "@avgSpeed": "61.76",
                                    "@devID": "1738",
                                    "@intervalEnd": "2020-08-21T15:55:00Z",
                                    "@numReads": "34",
                                    "@stDevSpeed": "7.5638",
                                },
                            ],
                        },
                    },
                    {
                        "sensor_type": "sensor",
                        "details": {
                            "@id": "NB 5 - MP 41.5",
                            "@latitude": "37.1571990",
                            "@longitude": "-84.1128540",
                            "@type": "iCone",
                            "radar": [
                                {
                                    "@avgSpeed": "65.61",
                                    "@devID": "1652",
                                    "@intervalEnd": "2020-08-21T15:45:00Z",
                                    "@latitude": "37.1571584",
                                    "@longitude": "-84.1128100",
                                    "@numReads": "53",
                                    "@stDevSpeed": "7.0067",
                                },
                                {
                                    "@avgSpeed": "67.35",
                                    "@devID": "1652",
                                    "@intervalEnd": "2020-08-21T15:50:00Z",
                                    "@latitude": "37.1571584",
                                    "@longitude": "-84.1128100",
                                    "@numReads": "33",
                                    "@stDevSpeed": "5.7486",
                                },
                                {
                                    "@avgSpeed": "64.93",
                                    "@devID": "1652",
                                    "@intervalEnd": "2020-08-21T15:55:00Z",
                                    "@latitude": "37.1571584",
                                    "@longitude": "-84.1128100",
                                    "@numReads": "37",
                                    "@stDevSpeed": "7.6484",
                                },
                            ],
                        },
                    },
                    {
                        "sensor_type": "sensor",
                        "details": {
                            "@id": "NB 6 - MP 40.2",
                            "@latitude": "37.1392040",
                            "@longitude": "-84.1095680",
                            "@type": "iCone",
                            "radar": [
                                {
                                    "@avgSpeed": "60.69",
                                    "@devID": "1746",
                                    "@intervalEnd": "2020-08-21T15:45:00Z",
                                    "@latitude": "37.1392918",
                                    "@longitude": "-84.1094934",
                                    "@numReads": "36",
                                    "@stDevSpeed": "8.4259",
                                },
                                {
                                    "@avgSpeed": "61.50",
                                    "@devID": "1746",
                                    "@intervalEnd": "2020-08-21T15:50:00Z",
                                    "@latitude": "37.1392918",
                                    "@longitude": "-84.1094934",
                                    "@numReads": "20",
                                    "@stDevSpeed": "8.0799",
                                },
                                {
                                    "@avgSpeed": "60.92",
                                    "@devID": "1746",
                                    "@intervalEnd": "2020-08-21T15:55:00Z",
                                    "@latitude": "37.1392918",
                                    "@longitude": "-84.1094934",
                                    "@numReads": "19",
                                    "@stDevSpeed": "9.4728",
                                },
                            ],
                        },
                    },
                    {
                        "sensor_type": "sensor",
                        "details": {
                            "@id": "NB 7 - MP 39.4",
                            "@latitude": "37.1278140",
                            "@longitude": "-84.1071670",
                            "@type": "iCone",
                            "radar": [
                                {
                                    "@avgSpeed": "66.67",
                                    "@devID": "1729",
                                    "@intervalEnd": "2020-08-21T15:40:00Z",
                                    "@latitude": "37.1277596",
                                    "@longitude": "-84.1071477",
                                    "@numReads": "18",
                                    "@stDevSpeed": "5.0124",
                                },
                                {
                                    "@avgSpeed": "67.50",
                                    "@devID": "1729",
                                    "@intervalEnd": "2020-08-21T15:45:00Z",
                                    "@latitude": "37.1277621",
                                    "@longitude": "-84.1071502",
                                    "@numReads": "34",
                                    "@stDevSpeed": "5.4530",
                                },
                                {
                                    "@avgSpeed": "68.25",
                                    "@devID": "1729",
                                    "@intervalEnd": "2020-08-21T15:50:00Z",
                                    "@latitude": "37.1277616",
                                    "@longitude": "-84.1071522",
                                    "@numReads": "40",
                                    "@stDevSpeed": "6.2964",
                                },
                                {
                                    "@avgSpeed": "68.97",
                                    "@devID": "1729",
                                    "@intervalEnd": "2020-08-21T15:55:00Z",
                                    "@latitude": "37.1277617",
                                    "@longitude": "-84.1071526",
                                    "@numReads": "17",
                                    "@stDevSpeed": "7.0926",
                                },
                            ],
                        },
                    },
                    {
                        "sensor_type": "sensor",
                        "details": {
                            "@id": "NB 8 - MP 38.2",
                            "@latitude": "37.1110090",
                            "@longitude": "-84.1019720",
                            "@type": "iCone",
                        },
                    },
                    {
                        "sensor_type": "display",
                        "details": {
                            "@id": "I-75 NB - MP 42",
                            "@latitude": "37.1641000",
                            "@longitude": "-84.1176000",
                            "@type": "PCMS",
                            "message": {
                                "@latitude": "37.1641920",
                                "@longitude": "-84.1175260",
                                "@text": " ROADWORK / NEXT / 6 MILES // 22 MILES / OF WORK / MP 40-62",
                                "@verified": "2020-08-21T15:44:19Z",
                            },
                        },
                    },
                    {
                        "sensor_type": "display",
                        "details": {
                            "@id": "I-75 NB - MP 40",
                            "@latitude": "37.1341260",
                            "@longitude": "-84.1085480",
                            "@type": "PCMS",
                            "message": {
                                "@text": " ROADWORK / 2 MILES / AHEAD // 22 MILES / OF WORK / MP 40-62",
                                "@verified": "2020-08-21T15:48:17Z",
                            },
                        },
                    },
                    {
                        "sensor_type": "display",
                        "details": {
                            "@id": "I-75 NB - MP 35",
                            "@latitude": "37.0646870",
                            "@longitude": "-84.0980500",
                            "@type": "PCMS",
                            "message": {
                                "@latitude": "37.0647220",
                                "@longitude": "-84.0980650",
                                "@text": " ROADWORK / 6 MILES / AHEAD // 22 MILES / OF WORK / MP 40-62",
                                "@verified": "2020-08-21T15:48:16Z",
                            },
                        },
                    },
                ],
                "directionality": "ONE_DIRECTION",
            },
        },
    },
    {
        "rtdh_timestamp": 1618272000,
        "rtdh_message_id": "23wsg54h",
        "event": {
            "type": "CONSTRUCTION",
            "source": {
                "id": "1246",
                "creation_timestamp": 1572917564000,
                "last_updated_timestamp": 1598025122000,
            },
            "geometry": [
                [-84.169129, 37.20667],
                [-84.157346, 37.201223],
                [-84.140482, 37.185815],
                [-84.121425, 37.166345],
                [-84.111588, 37.147808],
            ],
            "header": {
                "description": "19-1245: Roadwork between MP 48 and MP 40",
                "start_timestamp": 1574463741000,
                "end_timestamp": 1618876800000,
            },
            "detail": {
                "road_name": "I-75 S",
                "road_number": "I-75 S",
                "direction": "southbound",
            },
            "additional_info": {
                "condition_1": True,
                "route_details_end": {},
                "route_details_start": {},
                "devices": [
                    {
                        "sensor_type": "sensor",
                        "details": {
                            "@id": "SB 1 - MP 40.8",
                            "@latitude": "37.1478080",
                            "@longitude": "-84.1115880",
                            "@type": "iCone",
                        },
                    },
                    {
                        "sensor_type": "sensor",
                        "details": {
                            "@id": "SB 2 - MP 42.1",
                            "@latitude": "37.1663450",
                            "@longitude": "-84.1214250",
                            "@type": "iCone",
                            "radar": [
                                {
                                    "@avgSpeed": "67.43",
                                    "@devID": "1614",
                                    "@intervalEnd": "2020-08-21T15:45:00Z",
                                    "@latitude": "37.1663422",
                                    "@longitude": "-84.1214254",
                                    "@numReads": "67",
                                    "@stDevSpeed": "6.5561",
                                },
                                {
                                    "@avgSpeed": "68.54",
                                    "@devID": "1614",
                                    "@intervalEnd": "2020-08-21T15:50:00Z",
                                    "@latitude": "37.1663422",
                                    "@longitude": "-84.1214254",
                                    "@numReads": "48",
                                    "@stDevSpeed": "6.2738",
                                },
                                {
                                    "@avgSpeed": "66.84",
                                    "@devID": "1614",
                                    "@intervalEnd": "2020-08-21T15:55:00Z",
                                    "@latitude": "37.1663422",
                                    "@longitude": "-84.1214254",
                                    "@numReads": "38",
                                    "@stDevSpeed": "6.4339",
                                },
                            ],
                        },
                    },
                    {
                        "sensor_type": "sensor",
                        "details": {
                            "@id": "SB 3 - MP 44.0",
                            "@latitude": "37.1858150",
                            "@longitude": "-84.1404820",
                            "@type": "iCone",
                            "radar": [
                                {
                                    "@avgSpeed": "61.39",
                                    "@devID": "1740",
                                    "@intervalEnd": "2020-08-21T15:40:00Z",
                                    "@latitude": "37.1857562",
                                    "@longitude": "-84.1404956",
                                    "@numReads": "9",
                                    "@stDevSpeed": "6.3463",
                                },
                                {
                                    "@avgSpeed": "65.51",
                                    "@devID": "1740",
                                    "@intervalEnd": "2020-08-21T15:45:00Z",
                                    "@latitude": "37.1857562",
                                    "@longitude": "-84.1404956",
                                    "@numReads": "68",
                                    "@stDevSpeed": "6.5987",
                                },
                                {
                                    "@avgSpeed": "66.59",
                                    "@devID": "1740",
                                    "@intervalEnd": "2020-08-21T15:50:00Z",
                                    "@latitude": "37.1857562",
                                    "@longitude": "-84.1404956",
                                    "@numReads": "33",
                                    "@stDevSpeed": "6.6288",
                                },
                            ],
                        },
                    },
                    {
                        "sensor_type": "sensor",
                        "details": {
                            "@id": "SB 4 - MP 45.7",
                            "@latitude": "37.2012230",
                            "@longitude": "-84.1573460",
                            "@type": "iCone",
                            "radar": [
                                {
                                    "@avgSpeed": "64.64",
                                    "@devID": "1724",
                                    "@intervalEnd": "2020-08-21T15:40:00Z",
                                    "@latitude": "37.2012256",
                                    "@longitude": "-84.1573747",
                                    "@numReads": "21",
                                    "@stDevSpeed": "5.6432",
                                },
                                {
                                    "@avgSpeed": "69.21",
                                    "@devID": "1724",
                                    "@intervalEnd": "2020-08-21T15:45:00Z",
                                    "@latitude": "37.2012256",
                                    "@longitude": "-84.1573747",
                                    "@numReads": "38",
                                    "@stDevSpeed": "6.9488",
                                },
                                {
                                    "@avgSpeed": "64.11",
                                    "@devID": "1724",
                                    "@intervalEnd": "2020-08-21T15:50:00Z",
                                    "@latitude": "37.2012256",
                                    "@longitude": "-84.1573747",
                                    "@numReads": "62",
                                    "@stDevSpeed": "9.0186",
                                },
                                {
                                    "@avgSpeed": "66.91",
                                    "@devID": "1724",
                                    "@intervalEnd": "2020-08-21T15:55:00Z",
                                    "@latitude": "37.2012256",
                                    "@longitude": "-84.1573747",
                                    "@numReads": "17",
                                    "@stDevSpeed": "5.3667",
                                },
                            ],
                        },
                    },
                    {
                        "sensor_type": "sensor",
                        "details": {
                            "@id": "SB 5 - MP 47.5",
                            "@latitude": "37.2066700",
                            "@longitude": "-84.1691290",
                            "@type": "iCone",
                            "radar": [
                                {
                                    "@avgSpeed": "67.00",
                                    "@devID": "1735",
                                    "@intervalEnd": "2020-08-21T15:45:00Z",
                                    "@latitude": "37.2066724",
                                    "@longitude": "-84.1691283",
                                    "@numReads": "70",
                                    "@stDevSpeed": "6.2133",
                                },
                                {
                                    "@avgSpeed": "64.05",
                                    "@devID": "1735",
                                    "@intervalEnd": "2020-08-21T15:50:00Z",
                                    "@latitude": "37.2066724",
                                    "@longitude": "-84.1691283",
                                    "@numReads": "42",
                                    "@stDevSpeed": "7.6332",
                                },
                                {
                                    "@avgSpeed": "62.17",
                                    "@devID": "1735",
                                    "@intervalEnd": "2020-08-21T15:55:00Z",
                                    "@latitude": "37.2066724",
                                    "@longitude": "-84.1691283",
                                    "@numReads": "45",
                                    "@stDevSpeed": "6.7055",
                                },
                            ],
                        },
                    },
                    {
                        "sensor_type": "sensor",
                        "details": {
                            "@id": "SB 6 - MP 48.5",
                            "@latitude": "37.2193130",
                            "@longitude": "-84.2046600",
                            "@type": "iCone",
                        },
                    },
                    {
                        "sensor_type": "sensor",
                        "details": {
                            "@id": "SB 7 - MP 49.5",
                            "@latitude": "37.2299854",
                            "@longitude": "-84.2221508",
                            "@type": "iCone",
                            "radar": [
                                {
                                    "@avgSpeed": "67.24",
                                    "@devID": "1719",
                                    "@intervalEnd": "2020-08-21T15:40:00Z",
                                    "@numReads": "19",
                                    "@stDevSpeed": "4.9229",
                                },
                                {
                                    "@avgSpeed": "65.00",
                                    "@devID": "1719",
                                    "@intervalEnd": "2020-08-21T15:45:00Z",
                                    "@numReads": "38",
                                    "@stDevSpeed": "10.7934",
                                },
                                {
                                    "@avgSpeed": "62.82",
                                    "@devID": "1719",
                                    "@intervalEnd": "2020-08-21T15:50:00Z",
                                    "@numReads": "62",
                                    "@stDevSpeed": "9.7647",
                                },
                                {
                                    "@avgSpeed": "59.57",
                                    "@devID": "1719",
                                    "@intervalEnd": "2020-08-21T15:55:00Z",
                                    "@numReads": "41",
                                    "@stDevSpeed": "8.8250",
                                },
                            ],
                        },
                    },
                    {
                        "sensor_type": "sensor",
                        "details": {
                            "@id": "SB 8 - MP 50.5",
                            "@latitude": "37.2378880",
                            "@longitude": "-84.2359180",
                            "@type": "iCone",
                        },
                    },
                    {
                        "sensor_type": "display",
                        "details": {
                            "@id": "I-75 SB - MP 50",
                            "@latitude": "37.2339700",
                            "@longitude": "-84.2290798",
                            "@type": "PCMS",
                            "message": [
                                {
                                    "@text": " ROADWORK / 4 MILES / AHEAD // 19 MILES / OF WORK / MP 48-29",
                                    "@verified": "2020-08-21T15:42:27Z",
                                },
                                {
                                    "@text": " ROADWORK / 4 MILES / AHEAD // 19 MILES / OF WORK / MP 48-29",
                                    "@verified": "2020-08-21T15:52:27Z",
                                },
                            ],
                        },
                    },
                    {
                        "sensor_type": "display",
                        "details": {
                            "@id": "I-75 SB - MP 46",
                            "@latitude": "37.2059920",
                            "@longitude": "-84.1672690",
                            "@type": "PCMS",
                            "message": {
                                "@latitude": "37.2060070",
                                "@longitude": "-84.1673050",
                                "@text": " ROADWORK / NEXT / 5 MILES // 19 MILES / OF WORK / MP 48-29",
                                "@verified": "2020-08-21T15:48:32Z",
                            },
                        },
                    },
                ],
                "directionality": "ONE_DIRECTION",
            },
        },
    },
]

test_generate_standard_messages_from_string_input = """<?xml version="1.0" encoding="UTF-8"?>
    <incidents timestamp="2020-08-21T15:54:01Z">
    <incident id="1245">
        <creationtime>2019-11-05T01:22:20Z</creationtime>
        <updatetime>2020-08-21T15:52:02Z</updatetime>
        <type>CONSTRUCTION</type>
        <description>19-1245: Roadwork between MP 40 and MP 48</description>
        <location>
        <street>I-75 N</street>
        <direction>ONE_DIRECTION</direction>
        <polyline>37.1571990,-84.1128540,37.1686478,-84.1238971,37.1913000,-84.1458610,37.2093480,-84.1752970,37.2168370,-84.2013030</polyline>
        </location>
        <starttime>2020-02-14T17:08:16Z</starttime>
        <sensor type="iCone" id="NB 1 - MP 48.7" latitude="37.2168370" longitude="-84.2013030" />
        <sensor type="iCone" id="NB 2 - MP 46.1" latitude="37.2093480" longitude="-84.1752970" />
        <sensor type="iCone" id="NB 3 - MP 44.3" latitude="37.1913000" longitude="-84.1458610" />
        <sensor type="iCone" id="NB 4 - MP 42.5" latitude="37.1686478" longitude="-84.1238971">
        <radar devID="1738" intervalEnd="2020-08-21T15:45:00Z" numReads="58" avgSpeed="65.69" stDevSpeed="5.4874" />
        <radar devID="1738" intervalEnd="2020-08-21T15:50:00Z" numReads="38" avgSpeed="68.55" stDevSpeed="6.5362" />
        <radar devID="1738" intervalEnd="2020-08-21T15:55:00Z" numReads="34" avgSpeed="61.76" stDevSpeed="7.5638" />
        </sensor>
        <sensor type="iCone" id="NB 5 - MP 41.5" latitude="37.1571990" longitude="-84.1128540">
        <radar devID="1652" intervalEnd="2020-08-21T15:45:00Z" latitude="37.1571584" longitude="-84.1128100" numReads="53" avgSpeed="65.61" stDevSpeed="7.0067" />
        <radar devID="1652" intervalEnd="2020-08-21T15:50:00Z" latitude="37.1571584" longitude="-84.1128100" numReads="33" avgSpeed="67.35" stDevSpeed="5.7486" />
        <radar devID="1652" intervalEnd="2020-08-21T15:55:00Z" latitude="37.1571584" longitude="-84.1128100" numReads="37" avgSpeed="64.93" stDevSpeed="7.6484" />
        </sensor>
        <sensor type="iCone" id="NB 6 - MP 40.2" latitude="37.1392040" longitude="-84.1095680">
        <radar devID="1746" intervalEnd="2020-08-21T15:45:00Z" latitude="37.1392918" longitude="-84.1094934" numReads="36" avgSpeed="60.69" stDevSpeed="8.4259" />
        <radar devID="1746" intervalEnd="2020-08-21T15:50:00Z" latitude="37.1392918" longitude="-84.1094934" numReads="20" avgSpeed="61.50" stDevSpeed="8.0799" />
        <radar devID="1746" intervalEnd="2020-08-21T15:55:00Z" latitude="37.1392918" longitude="-84.1094934" numReads="19" avgSpeed="60.92" stDevSpeed="9.4728" />
        </sensor>
        <sensor type="iCone" id="NB 7 - MP 39.4" latitude="37.1278140" longitude="-84.1071670">
        <radar devID="1729" intervalEnd="2020-08-21T15:40:00Z" latitude="37.1277596" longitude="-84.1071477" numReads="18" avgSpeed="66.67" stDevSpeed="5.0124" />
        <radar devID="1729" intervalEnd="2020-08-21T15:45:00Z" latitude="37.1277621" longitude="-84.1071502" numReads="34" avgSpeed="67.50" stDevSpeed="5.4530" />
        <radar devID="1729" intervalEnd="2020-08-21T15:50:00Z" latitude="37.1277616" longitude="-84.1071522" numReads="40" avgSpeed="68.25" stDevSpeed="6.2964" />
        <radar devID="1729" intervalEnd="2020-08-21T15:55:00Z" latitude="37.1277617" longitude="-84.1071526" numReads="17" avgSpeed="68.97" stDevSpeed="7.0926" />
        </sensor>
        <sensor type="iCone" id="NB 8 - MP 38.2" latitude="37.1110090" longitude="-84.1019720" />
        <display type="PCMS" id="I-75 NB - MP 42" latitude="37.1641000" longitude="-84.1176000">
        <message verified="2020-08-21T15:44:19Z" latitude="37.1641920" longitude="-84.1175260" text=" ROADWORK / NEXT / 6 MILES // 22 MILES / OF WORK / MP 40-62" />
        </display>
        <display type="PCMS" id="I-75 NB - MP 40" latitude="37.1341260" longitude="-84.1085480">
        <message verified="2020-08-21T15:48:17Z" text=" ROADWORK / 2 MILES / AHEAD // 22 MILES / OF WORK / MP 40-62" />
        </display>
        <display type="PCMS" id="I-75 NB - MP 35" latitude="37.0646870" longitude="-84.0980500">
        <message verified="2020-08-21T15:48:16Z" latitude="37.0647220" longitude="-84.0980650" text=" ROADWORK / 6 MILES / AHEAD // 22 MILES / OF WORK / MP 40-62" />
        </display>
    </incident>
    <incident id="1246">
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
        <radar devID="1735" intervalEnd="2020-08-21T15:50:00Z" latitude="37.2066724" longitude="-84.1691283" numReads="42" avgSpeed="64.05" stDevSpeed="7.6332" />
        <radar devID="1735" intervalEnd="2020-08-21T15:55:00Z" latitude="37.2066724" longitude="-84.1691283" numReads="45" avgSpeed="62.17" stDevSpeed="6.7055" />
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
    </incident>
    </incidents>"""

test_wzdx_creator_expected = {
    "feed_info": {
        "update_date": "2021-04-13T00:00:00Z",
        "publisher": "CDOT",
        "contact_name": "Heather Pickering-Hilgers",
        "contact_email": "heather.pickeringhilgers@state.co.us",
        "update_frequency": 300,
        "version": "4.2",
        "license": "https://creativecommons.org/publicdomain/zero/1.0/",
        "data_sources": [
            {
                "data_source_id": "w",
                "organization_name": "CDOT",
                "contact_name": "Heather Pickering-Hilgers",
                "contact_email": "heather.pickeringhilgers@state.co.us",
                "update_date": "2021-04-13T00:00:00Z",
                "update_frequency": 300,
            }
        ],
    },
    "type": "FeatureCollection",
    "features": [
        {
            "id": "1245",
            "type": "Feature",
            "properties": {
                "core_details": {
                    "data_source_id": "w",
                    "event_type": "work-zone",
                    "road_names": ["I-75 N"],
                    "direction": "northbound",
                    "description": "19-1245: Roadwork between MP 40 and MP 48",
                    "creation_date": "2019-11-05T01:22:20Z",
                    "update_date": "2021-11-05T19:56:03Z",
                },
                "start_date": "2021-06-08T20:15:01Z",
                "end_date": "2021-06-08T21:05:01Z",
                "is_start_date_verified": False,
                "is_end_date_verified": False,
                "is_start_position_verified": False,
                "is_end_position_verified": False,
                "location_method": "channel-device-method",
                "vehicle_impact": "all-lanes-open",
            },
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [-84.1238971, 37.1686478],
                    [-84.1238971, 37.1686478],
                    [-84.145861, 37.1913],
                    [-84.145861, 37.1913],
                    [-84.157105, 37.201197],
                    [-84.167033, 37.206079],
                    [-84.204074, 37.21931],
                ],
            },
        }
    ],
}

test_parse_icone_sensor_test_sensor_1 = {
    "@type": "iCone",
    "@id": "#4",
    "@latitude": "41.3883260",
    "@longitude": "-81.9707500",
    "radar": [
        {
            "@devID": "1645",
            "@intervalEnd": "2020-08-21T15:40:00Z",
            "@latitude": "41.3883258",
            "@longitude": "-81.9707325",
            "@numReads": "22",
            "@avgSpeed": "64.32",
            "@stDevSpeed": "6.1080",
        },
        {
            "@devID": "1645",
            "@intervalEnd": "2020-08-21T15:45:00Z",
            "@latitude": "41.3883258",
            "@longitude": "-81.9707325",
            "@numReads": "43",
            "@avgSpeed": "63.66",
            "@stDevSpeed": "5.1282",
        },
        {
            "@devID": "1645",
            "@intervalEnd": "2020-08-21T15:50:00Z",
            "@latitude": "41.3883258",
            "@longitude": "-81.9707325",
            "@numReads": "59",
            "@avgSpeed": "63.52",
            "@stDevSpeed": "7.9526",
        },
        {
            "@devID": "1645",
            "@intervalEnd": "2020-08-21T15:55:00Z",
            "@latitude": "41.3883258",
            "@longitude": "-81.9707325",
            "@numReads": "18",
            "@avgSpeed": "62.22",
            "@stDevSpeed": "11.9760",
        },
    ],
}

test_parse_icone_sensor_test_sensor_2 = {
    "@type": "iCone",
    "@id": "#4",
    "@latitude": "41.3883260",
    "@longitude": "-81.9707500",
    "radar": [
        {
            "@devID": "1645",
            "@intervalEnd": "2020-08-21T15:40:00Z",
            "@latitude": "41.3883258",
            "@longitude": "-81.9707325",
            "@numReads": "22",
            "@avgSpeed": "64.32",
            "@stDevSpeed": "6.1080",
        }
    ],
}

test_create_description_description = '19-1245: Roadwork between MP 48 and MP 40\n sensors: \n{\n  "type": "iCone",\n  "id": "SB 1 - MP 40.8",\n  "location": [\n    37.147808,\n    -84.111588\n  ]\n}\n{\n  "type": "iCone",\n  "id": "SB 2 - MP 42.1",\n  "location": [\n    37.166345,\n    -84.121425\n  ],\n  "radar": {\n    "average_speed": 67.63,\n    "std_dev_speed": 6.44,\n    "timestamp": "2020-08-21T15:55:00Z"\n  }\n}\n{\n  "type": "iCone",\n  "id": "SB 3 - MP 44.0",\n  "location": [\n    37.185815,\n    -84.140482\n  ],\n  "radar": {\n    "average_speed": 65.5,\n    "std_dev_speed": 6.59,\n    "timestamp": "2020-08-21T15:50:00Z"\n  }\n}\n{\n  "type": "iCone",\n  "id": "SB 4 - MP 45.7",\n  "location": [\n    37.201223,\n    -84.157346\n  ],\n  "radar": {\n    "average_speed": 65.94,\n    "std_dev_speed": 7.49,\n    "timestamp": "2020-08-21T15:55:00Z"\n  }\n}\n{\n  "type": "iCone",\n  "id": "SB 5 - MP 47.5",\n  "location": [\n    37.20667,\n    -84.169129\n  ],\n  "radar": {\n    "average_speed": 67.0,\n    "std_dev_speed": 6.21,\n    "timestamp": "2020-08-21T15:45:00Z"\n  }\n}\n{\n  "type": "iCone",\n  "id": "SB 6 - MP 48.5",\n  "location": [\n    37.219313,\n    -84.20466\n  ]\n}\n{\n  "type": "iCone",\n  "id": "SB 7 - MP 49.5",\n  "location": [\n    37.2299854,\n    -84.2221508\n  ],\n  "radar": {\n    "average_speed": 63.03,\n    "std_dev_speed": 9.19,\n    "timestamp": "2020-08-21T15:55:00Z"\n  }\n}\n{\n  "type": "iCone",\n  "id": "SB 8 - MP 50.5",\n  "location": [\n    37.237888,\n    -84.235918\n  ]\n}\n displays: \n{\n  "type": "PCMS",\n  "id": "I-75 SB - MP 50",\n  "timestamp": "2020-08-21T15:52:27Z",\n  "location": [\n    37.23397,\n    -84.2290798\n  ],\n  "messages": [\n    " ROADWORK / 4 MILES / AHEAD // 19 MILES / OF WORK / MP 48-29"\n  ]\n}\n{\n  "type": "PCMS",\n  "id": "I-75 SB - MP 46",\n  "timestamp": "2020-08-21T15:48:32Z",\n  "location": [\n    37.205992,\n    -84.167269\n  ],\n  "messages": [\n    " ROADWORK / NEXT / 5 MILES // 19 MILES / OF WORK / MP 48-29"\n  ]\n}'

import json

test_parse_xml_expected_icone_data = {
    "incidents": {
        "@timestamp": "2020-08-21T15:54:01Z",
        "incident": [
            {
                "@id": "1245",
                "creationtime": "2019-11-05T01:22:20Z",
                "updatetime": "2020-08-21T15:52:02Z",
                "type": "CONSTRUCTION",
                "description": "19-1245: Roadwork between MP 40 and MP 48",
                "location": {
                    "street": "I-75 N",
                    "direction": "ONE_DIRECTION",
                    "polyline": "37.1571990,-84.1128540,37.1686478,-84.1238971,37.1913000,-84.1458610,37.2093480,-84.1752970,37.2168370,-84.2013030",
                },
                "starttime": "2020-02-14T17:08:16Z",
                "sensor": [
                    {
                        "@type": "iCone",
                        "@id": "NB 1 - MP 48.7",
                        "@latitude": "37.2168370",
                        "@longitude": "-84.2013030",
                    },
                    {
                        "@type": "iCone",
                        "@id": "NB 2 - MP 46.1",
                        "@latitude": "37.2093480",
                        "@longitude": "-84.1752970",
                    },
                    {
                        "@type": "iCone",
                        "@id": "NB 3 - MP 44.3",
                        "@latitude": "37.1913000",
                        "@longitude": "-84.1458610",
                    },
                    {
                        "@type": "iCone",
                        "@id": "NB 4 - MP 42.5",
                        "@latitude": "37.1686478",
                        "@longitude": "-84.1238971",
                        "radar": [
                            {
                                "@devID": "1738",
                                "@intervalEnd": "2020-08-21T15:45:00Z",
                                "@numReads": "58",
                                "@avgSpeed": "65.69",
                                "@stDevSpeed": "5.4874",
                            },
                            {
                                "@devID": "1738",
                                "@intervalEnd": "2020-08-21T15:50:00Z",
                                "@numReads": "38",
                                "@avgSpeed": "68.55",
                                "@stDevSpeed": "6.5362",
                            },
                            {
                                "@devID": "1738",
                                "@intervalEnd": "2020-08-21T15:55:00Z",
                                "@numReads": "34",
                                "@avgSpeed": "61.76",
                                "@stDevSpeed": "7.5638",
                            },
                        ],
                    },
                    {
                        "@type": "iCone",
                        "@id": "NB 5 - MP 41.5",
                        "@latitude": "37.1571990",
                        "@longitude": "-84.1128540",
                        "radar": [
                            {
                                "@devID": "1652",
                                "@intervalEnd": "2020-08-21T15:45:00Z",
                                "@latitude": "37.1571584",
                                "@longitude": "-84.1128100",
                                "@numReads": "53",
                                "@avgSpeed": "65.61",
                                "@stDevSpeed": "7.0067",
                            },
                            {
                                "@devID": "1652",
                                "@intervalEnd": "2020-08-21T15:50:00Z",
                                "@latitude": "37.1571584",
                                "@longitude": "-84.1128100",
                                "@numReads": "33",
                                "@avgSpeed": "67.35",
                                "@stDevSpeed": "5.7486",
                            },
                            {
                                "@devID": "1652",
                                "@intervalEnd": "2020-08-21T15:55:00Z",
                                "@latitude": "37.1571584",
                                "@longitude": "-84.1128100",
                                "@numReads": "37",
                                "@avgSpeed": "64.93",
                                "@stDevSpeed": "7.6484",
                            },
                        ],
                    },
                    {
                        "@type": "iCone",
                        "@id": "NB 6 - MP 40.2",
                        "@latitude": "37.1392040",
                        "@longitude": "-84.1095680",
                        "radar": [
                            {
                                "@devID": "1746",
                                "@intervalEnd": "2020-08-21T15:45:00Z",
                                "@latitude": "37.1392918",
                                "@longitude": "-84.1094934",
                                "@numReads": "36",
                                "@avgSpeed": "60.69",
                                "@stDevSpeed": "8.4259",
                            },
                            {
                                "@devID": "1746",
                                "@intervalEnd": "2020-08-21T15:50:00Z",
                                "@latitude": "37.1392918",
                                "@longitude": "-84.1094934",
                                "@numReads": "20",
                                "@avgSpeed": "61.50",
                                "@stDevSpeed": "8.0799",
                            },
                            {
                                "@devID": "1746",
                                "@intervalEnd": "2020-08-21T15:55:00Z",
                                "@latitude": "37.1392918",
                                "@longitude": "-84.1094934",
                                "@numReads": "19",
                                "@avgSpeed": "60.92",
                                "@stDevSpeed": "9.4728",
                            },
                        ],
                    },
                    {
                        "@type": "iCone",
                        "@id": "NB 7 - MP 39.4",
                        "@latitude": "37.1278140",
                        "@longitude": "-84.1071670",
                        "radar": [
                            {
                                "@devID": "1729",
                                "@intervalEnd": "2020-08-21T15:40:00Z",
                                "@latitude": "37.1277596",
                                "@longitude": "-84.1071477",
                                "@numReads": "18",
                                "@avgSpeed": "66.67",
                                "@stDevSpeed": "5.0124",
                            },
                            {
                                "@devID": "1729",
                                "@intervalEnd": "2020-08-21T15:45:00Z",
                                "@latitude": "37.1277621",
                                "@longitude": "-84.1071502",
                                "@numReads": "34",
                                "@avgSpeed": "67.50",
                                "@stDevSpeed": "5.4530",
                            },
                            {
                                "@devID": "1729",
                                "@intervalEnd": "2020-08-21T15:50:00Z",
                                "@latitude": "37.1277616",
                                "@longitude": "-84.1071522",
                                "@numReads": "40",
                                "@avgSpeed": "68.25",
                                "@stDevSpeed": "6.2964",
                            },
                            {
                                "@devID": "1729",
                                "@intervalEnd": "2020-08-21T15:55:00Z",
                                "@latitude": "37.1277617",
                                "@longitude": "-84.1071526",
                                "@numReads": "17",
                                "@avgSpeed": "68.97",
                                "@stDevSpeed": "7.0926",
                            },
                        ],
                    },
                    {
                        "@type": "iCone",
                        "@id": "NB 8 - MP 38.2",
                        "@latitude": "37.1110090",
                        "@longitude": "-84.1019720",
                    },
                ],
                "display": [
                    {
                        "@type": "PCMS",
                        "@id": "I-75 NB - MP 42",
                        "@latitude": "37.1641000",
                        "@longitude": "-84.1176000",
                        "message": {
                            "@verified": "2020-08-21T15:44:19Z",
                            "@latitude": "37.1641920",
                            "@longitude": "-84.1175260",
                            "@text": " ROADWORK / NEXT / 6 MILES // 22 MILES / OF WORK / MP 40-62",
                        },
                    },
                    {
                        "@type": "PCMS",
                        "@id": "I-75 NB - MP 40",
                        "@latitude": "37.1341260",
                        "@longitude": "-84.1085480",
                        "message": {
                            "@verified": "2020-08-21T15:48:17Z",
                            "@text": " ROADWORK / 2 MILES / AHEAD // 22 MILES / OF WORK / MP 40-62",
                        },
                    },
                    {
                        "@type": "PCMS",
                        "@id": "I-75 NB - MP 35",
                        "@latitude": "37.0646870",
                        "@longitude": "-84.0980500",
                        "message": {
                            "@verified": "2020-08-21T15:48:16Z",
                            "@latitude": "37.0647220",
                            "@longitude": "-84.0980650",
                            "@text": " ROADWORK / 6 MILES / AHEAD // 22 MILES / OF WORK / MP 40-62",
                        },
                    },
                ],
            },
            {
                "@id": "1246",
                "creationtime": "2019-11-05T01:32:44Z",
                "updatetime": "2020-08-21T15:52:02Z",
                "type": "CONSTRUCTION",
                "description": "19-1245: Roadwork between MP 48 and MP 40",
                "location": {
                    "street": "I-75 S",
                    "direction": "ONE_DIRECTION",
                    "polyline": "37.2066700,-84.1691290,37.2012230,-84.1573460,37.1858150,-84.1404820,37.1663450,-84.1214250,37.1478080,-84.1115880",
                },
                "starttime": "2019-11-22T23:02:21Z",
                "sensor": [
                    {
                        "@type": "iCone",
                        "@id": "SB 1 - MP 40.8",
                        "@latitude": "37.1478080",
                        "@longitude": "-84.1115880",
                    },
                    {
                        "@type": "iCone",
                        "@id": "SB 2 - MP 42.1",
                        "@latitude": "37.1663450",
                        "@longitude": "-84.1214250",
                        "radar": [
                            {
                                "@devID": "1614",
                                "@intervalEnd": "2020-08-21T15:45:00Z",
                                "@latitude": "37.1663422",
                                "@longitude": "-84.1214254",
                                "@numReads": "67",
                                "@avgSpeed": "67.43",
                                "@stDevSpeed": "6.5561",
                            },
                            {
                                "@devID": "1614",
                                "@intervalEnd": "2020-08-21T15:50:00Z",
                                "@latitude": "37.1663422",
                                "@longitude": "-84.1214254",
                                "@numReads": "48",
                                "@avgSpeed": "68.54",
                                "@stDevSpeed": "6.2738",
                            },
                            {
                                "@devID": "1614",
                                "@intervalEnd": "2020-08-21T15:55:00Z",
                                "@latitude": "37.1663422",
                                "@longitude": "-84.1214254",
                                "@numReads": "38",
                                "@avgSpeed": "66.84",
                                "@stDevSpeed": "6.4339",
                            },
                        ],
                    },
                    {
                        "@type": "iCone",
                        "@id": "SB 3 - MP 44.0",
                        "@latitude": "37.1858150",
                        "@longitude": "-84.1404820",
                        "radar": [
                            {
                                "@devID": "1740",
                                "@intervalEnd": "2020-08-21T15:40:00Z",
                                "@latitude": "37.1857562",
                                "@longitude": "-84.1404956",
                                "@numReads": "9",
                                "@avgSpeed": "61.39",
                                "@stDevSpeed": "6.3463",
                            },
                            {
                                "@devID": "1740",
                                "@intervalEnd": "2020-08-21T15:45:00Z",
                                "@latitude": "37.1857562",
                                "@longitude": "-84.1404956",
                                "@numReads": "68",
                                "@avgSpeed": "65.51",
                                "@stDevSpeed": "6.5987",
                            },
                            {
                                "@devID": "1740",
                                "@intervalEnd": "2020-08-21T15:50:00Z",
                                "@latitude": "37.1857562",
                                "@longitude": "-84.1404956",
                                "@numReads": "33",
                                "@avgSpeed": "66.59",
                                "@stDevSpeed": "6.6288",
                            },
                        ],
                    },
                    {
                        "@type": "iCone",
                        "@id": "SB 4 - MP 45.7",
                        "@latitude": "37.2012230",
                        "@longitude": "-84.1573460",
                        "radar": [
                            {
                                "@devID": "1724",
                                "@intervalEnd": "2020-08-21T15:40:00Z",
                                "@latitude": "37.2012256",
                                "@longitude": "-84.1573747",
                                "@numReads": "21",
                                "@avgSpeed": "64.64",
                                "@stDevSpeed": "5.6432",
                            },
                            {
                                "@devID": "1724",
                                "@intervalEnd": "2020-08-21T15:45:00Z",
                                "@latitude": "37.2012256",
                                "@longitude": "-84.1573747",
                                "@numReads": "38",
                                "@avgSpeed": "69.21",
                                "@stDevSpeed": "6.9488",
                            },
                            {
                                "@devID": "1724",
                                "@intervalEnd": "2020-08-21T15:50:00Z",
                                "@latitude": "37.2012256",
                                "@longitude": "-84.1573747",
                                "@numReads": "62",
                                "@avgSpeed": "64.11",
                                "@stDevSpeed": "9.0186",
                            },
                            {
                                "@devID": "1724",
                                "@intervalEnd": "2020-08-21T15:55:00Z",
                                "@latitude": "37.2012256",
                                "@longitude": "-84.1573747",
                                "@numReads": "17",
                                "@avgSpeed": "66.91",
                                "@stDevSpeed": "5.3667",
                            },
                        ],
                    },
                    {
                        "@type": "iCone",
                        "@id": "SB 5 - MP 47.5",
                        "@latitude": "37.2066700",
                        "@longitude": "-84.1691290",
                        "radar": [
                            {
                                "@devID": "1735",
                                "@intervalEnd": "2020-08-21T15:45:00Z",
                                "@latitude": "37.2066724",
                                "@longitude": "-84.1691283",
                                "@numReads": "70",
                                "@avgSpeed": "67.00",
                                "@stDevSpeed": "6.2133",
                            },
                            {
                                "@devID": "1735",
                                "@intervalEnd": "2020-08-21T15:50:00Z",
                                "@latitude": "37.2066724",
                                "@longitude": "-84.1691283",
                                "@numReads": "42",
                                "@avgSpeed": "64.05",
                                "@stDevSpeed": "7.6332",
                            },
                            {
                                "@devID": "1735",
                                "@intervalEnd": "2020-08-21T15:55:00Z",
                                "@latitude": "37.2066724",
                                "@longitude": "-84.1691283",
                                "@numReads": "45",
                                "@avgSpeed": "62.17",
                                "@stDevSpeed": "6.7055",
                            },
                        ],
                    },
                    {
                        "@type": "iCone",
                        "@id": "SB 6 - MP 48.5",
                        "@latitude": "37.2193130",
                        "@longitude": "-84.2046600",
                    },
                    {
                        "@type": "iCone",
                        "@id": "SB 7 - MP 49.5",
                        "@latitude": "37.2299854",
                        "@longitude": "-84.2221508",
                        "radar": [
                            {
                                "@devID": "1719",
                                "@intervalEnd": "2020-08-21T15:40:00Z",
                                "@numReads": "19",
                                "@avgSpeed": "67.24",
                                "@stDevSpeed": "4.9229",
                            },
                            {
                                "@devID": "1719",
                                "@intervalEnd": "2020-08-21T15:45:00Z",
                                "@numReads": "38",
                                "@avgSpeed": "65.00",
                                "@stDevSpeed": "10.7934",
                            },
                            {
                                "@devID": "1719",
                                "@intervalEnd": "2020-08-21T15:50:00Z",
                                "@numReads": "62",
                                "@avgSpeed": "62.82",
                                "@stDevSpeed": "9.7647",
                            },
                            {
                                "@devID": "1719",
                                "@intervalEnd": "2020-08-21T15:55:00Z",
                                "@numReads": "41",
                                "@avgSpeed": "59.57",
                                "@stDevSpeed": "8.8250",
                            },
                        ],
                    },
                    {
                        "@type": "iCone",
                        "@id": "SB 8 - MP 50.5",
                        "@latitude": "37.2378880",
                        "@longitude": "-84.2359180",
                    },
                ],
                "display": [
                    {
                        "@type": "PCMS",
                        "@id": "I-75 SB - MP 50",
                        "@latitude": "37.2339700",
                        "@longitude": "-84.2290798",
                        "message": [
                            {
                                "@verified": "2020-08-21T15:42:27Z",
                                "@text": " ROADWORK / 4 MILES / AHEAD // 19 MILES / OF WORK / MP 48-29",
                            },
                            {
                                "@verified": "2020-08-21T15:52:27Z",
                                "@text": " ROADWORK / 4 MILES / AHEAD // 19 MILES / OF WORK / MP 48-29",
                            },
                        ],
                    },
                    {
                        "@type": "PCMS",
                        "@id": "I-75 SB - MP 46",
                        "@latitude": "37.2059920",
                        "@longitude": "-84.1672690",
                        "message": {
                            "@verified": "2020-08-21T15:48:32Z",
                            "@latitude": "37.2060070",
                            "@longitude": "-84.1673050",
                            "@text": " ROADWORK / NEXT / 5 MILES // 19 MILES / OF WORK / MP 48-29",
                        },
                    },
                ],
            },
        ],
    }
}

test_validate_wzdx_valid_wzdx_data = json.loads(
    """{
  "feed_info": {
    "publisher": "CDOT",
    "version": "4.1",
    "license": "https://creativecommons.org/publicdomain/zero/1.0/",
    "data_sources": [
      {
        "data_source_id": "0b509510-1043-47b8-b6b5-81e599f51273",
        "organization_name": "CDOT",
        "update_date": "2022-10-12T19:55:00Z",
        "update_frequency": 300,
        "contact_name": "Heather Pickering-Hilgers",
        "contact_email": "heather.pickeringhilgers@state.co.us"
      }
    ],
    "update_date": "2022-10-12T19:55:00Z",
    "update_frequency": 300,
    "contact_name": "Heather Pickering-Hilgers",
    "contact_email": "heather.pickeringhilgers@state.co.us"
  },
  "type": "FeatureCollection",
  "features": [{
      "id": "1245",
      "type": "Feature",
      "properties": {
        "core_details": {
          "event_type": "work-zone",
          "data_source_id": "0b509510-1043-47b8-b6b5-81e599f51273",
          "road_names": [
            "I-75 N"
          ],
          "direction": "northbound",
          "description": "19-1245: Roadwork between MP 40 and MP 48",
          "creation_date": "2019-11-05T01:22:20Z",
          "update_date": "2020-08-21T15:52:02Z"
        },
        "start_date": "2020-02-14T17:08:16Z",
        "end_date": "2022-10-19T19:54:00Z",
        "is_start_date_verified": false,
        "is_end_date_verified": false,
        "is_start_position_verified": false,
        "is_end_position_verified": false,
        "location_method": "channel-device-method",
        "vehicle_impact": "all-lanes-open"
      },
      "geometry": {
        "type": "LineString",
        "coordinates": [
          [
            -84.112854,
            37.157199
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
            -84.175297,
            37.209348
          ],
          [
            -84.201303,
            37.216837
          ]
        ]
      }
    }]}"""
)

test_validate_wzdx_invalid_location_method = json.loads(
    '{"feed_info": {"update_date": "2021-01-05T12:14:07Z", "publisher": "CDOT ", "contact_name": "Heather Pickering-Hilgers", "contact_email": "heather.pickeringhilgers@state.co.us", "update_frequency": 86400, "version": "3.0", "data_sources": [{"data_source_id": "d5333bb4-0ea2-4318-8934-91f8916d6a8e", "organization_name": "issuing_organization", "contact_name": "contact_name", "contact_email": "contact_email", "update_frequency": 86400, "update_date": "2021-01-05T12:14:07Z", "location_verify_method": "location_verify_method"}]}, "type": "FeatureCollection", "features": [{"type": "Feature", "properties": {"road_event_id": "3f6fc7b7-9133-41be-9636-994432c1d0c3", "event_type": "work-zone", "data_source_id": "d5333bb4-0ea2-4318-8934-91f8916d6a8e", "start_date": "2020-02-14T17:08:16Z", "end_date": "", "is_start_date_verified": false, "is_end_date_verified": false, "is_start_position_verified": false, "is_end_position_verified": false, "road_name": "I-75 N", "direction": "westbound", "vehicle_impact": "all-lanes-open", "relationship": {"relationship_id": "3ae833b0-123c-4c4d-b906-3e4f6949bee8", "road_event_id": "3f6fc7b7-9133-41be-9636-994432c1d0c3"}, "lanes": [], "road_number": "", "beginning_cross_street": "", "ending_cross_street": "", "total_num_lanes": 1, "types_of_work": [], "reduced_speed_limit": 25, "workers_present": false, "restrictions": [], "description": "19-1245: Roadwork between MP 40 and MP 48", "creation_date": "2019-11-05T01:22:20Z", "update_date": "2020-08-21T15:52:02Z"}, "geometry": {"type": "LineString", "coordinates": [[-84.112854, 37.157199], [-84.1238971, 37.1686478], [-84.145861, 37.1913], [-84.175297, 37.209348], [-84.201303, 37.216837]]}}, {"type": "Feature", "properties": {"road_event_id": "52a6ecf1-4bee-49e9-a3bc-47c6cf20db19", "event_type": "work-zone", "data_source_id": "d5333bb4-0ea2-4318-8934-91f8916d6a8e", "start_date": "2019-11-22T23:02:21Z", "end_date": "", "is_start_date_verified": false, "is_end_date_verified": false, "is_start_position_verified": false, "is_end_position_verified": false, "road_name": "I-75 S", "direction": "southbound", "vehicle_impact": "all-lanes-open", "relationship": {"relationship_id": "a5e54a72-d639-4945-9cf6-1b518f68399b", "road_event_id": "52a6ecf1-4bee-49e9-a3bc-47c6cf20db19"}, "lanes": [], "road_number": "", "beginning_cross_street": "", "ending_cross_street": "", "total_num_lanes": 1, "types_of_work": [], "reduced_speed_limit": 25, "workers_present": false, "restrictions": [], "description": "19-1245: Roadwork between MP 48 and MP 40", "creation_date": "2019-11-05T01:32:44Z", "update_date": "2020-08-21T15:52:02Z"}, "geometry": {"type": "LineString", "coordinates": [[-84.169129, 37.20667], [-84.157346, 37.201223], [-84.140482, 37.185815], [-84.121425, 37.166345], [-84.111588, 37.147808]]}}]}'
)

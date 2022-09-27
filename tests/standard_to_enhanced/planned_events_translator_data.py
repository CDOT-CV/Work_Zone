test_parse_work_zone_linestring_standard = {
        "rtdh_timestamp": 1642036259.3099449,
        "rtdh_message_id": "42fe21b8-102b-43e8-8668-23c55334a201",
        "event": {
            "type": 'work-zone',
            "source": {
                "id": "OpenTMS-Event1689408506",
                "creation_timestamp": 1635531964000,
                "last_updated_timestamp": 1635532501835
            },
            "geometry": [
                [
                    -108.279106,
                    39.195663
                ],
                [
                    -108.218549,
                    39.302392
                ]
            ],
            "header": {
                "description": "Between Exit 49: CO 65; Grand Mesa (5 miles east of the Palisade area) and US 6 (Debeque) from Mile Point 50 to Mile Point 60. Road closed expect delays due to bridge construction. Until May 1, 2022 at about 12:26PM MDT.",
                "start_timestamp": 1635531964000,
                "end_timestamp": 1651429564000
            },
            "detail": {
                "road_name": "I-70E",
                "road_number": "I-70E",
                "direction": "westbound"
            },
            "additional_info": {
                "lanes": [
                    {
                        "order": 1,
                        "type": "shoulder",
                        "status": "open"
                    },
                    {
                        "order": 2,
                        "type": "general",
                        "status": "closed"
                    },
                    {
                        "order": 3,
                        "type": "general",
                        "status": "closed"
                    },
                    {
                        "order": 4,
                        "type": "shoulder",
                        "status": "open"
                    }
                ],
                "restrictions": [],
                "beginning_milepost": 50.0,
                "ending_milepost": 60.0,
                "types_of_work": [{
                    "type_name": "below-road-work",
                    "is_architectural_change": True
                }]
            }
        }
    }

test_parse_work_zone_linestring_expected = {
        "id": "OpenTMS-Event1689408506",
        "type": "Feature",
        "properties": {
            "core_details": {
              "data_source_id": "",
              "event_type": "work-zone",
              "road_names": [
                  "I-70E"
              ],
                "direction": "westbound",
                "description": "Between Exit 49: CO 65; Grand Mesa (5 miles east of the Palisade area) and US 6 (Debeque) from Mile Point 50 to Mile Point 60. Road closed expect delays due to bridge construction. Until May 1, 2022 at about 12:26PM MDT.",
                "update_date": "2021-10-29T18:35:01Z",
            },
            "start_date": "2021-10-29T18:26:04Z",
            "end_date": "2022-05-01T18:26:04Z",
            "location_method": "channel-device-method",
            "start_date_accuracy": "estimated",
            "end_date_accuracy": "estimated",
            "beginning_accuracy": "estimated",
            "ending_accuracy": "estimated",
            "vehicle_impact": "some-lanes-closed",
            "beginning_milepost": 50.0,
            "ending_milepost": 60.0,
            "lanes": [
                {
                    "order": 1,
                    "type": "shoulder",
                    "status": "open"
                },
                {
                    "order": 2,
                    "type": "general",
                    "status": "closed"
                },
                {
                    "order": 3,
                    "type": "general",
                    "status": "closed"
                },
                {
                    "order": 4,
                    "type": "shoulder",
                    "status": "open"
                }
            ],
            "event_status": "completed"
        },
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [
                    -108.279106,
                    39.195663
                ],
                [
                    -108.218549,
                    39.302392
                ]
            ]
        }
    }

test_wzdx_creator_standard = {
        "rtdh_timestamp": 1642036259.3099449,
        "rtdh_message_id": "42fe21b8-102b-43e8-8668-23c55334a201",
        "event": {
            "type": "work-zone",
            "types_of_lanes": {
                "type_name": "below-road-work",
                "is_architectural_change": True
            },
            "source": {
                "id": "OpenTMS-Event1689408506",
                "creation_timestamp": 1635531964000,
                "last_updated_timestamp": 1635532501835
            },
            "geometry": [
                [
                    -108.279106,
                    39.195663
                ],
                [
                    -108.218549,
                    39.302392
                ]
            ],
            "header": {
                "description": "Between Exit 49: CO 65; Grand Mesa (5 miles east of the Palisade area) and US 6 (Debeque) from Mile Point 50 to Mile Point 60. Road closed expect delays due to bridge construction. Until May 1, 2022 at about 12:26PM MDT.",
                "start_timestamp": 1635531964000,
                "end_timestamp": 1651429564000
            },
            "detail": {
                "road_name": "I-70E",
                "road_number": "I-70E",
                "direction": "westbound"
            },
            "additional_info": {
                "lanes": [
                    {
                        "order": 1,
                        "type": "shoulder",
                        "status": "open"
                    },
                    {
                        "order": 2,
                        "type": "general",
                        "status": "closed"
                    },
                    {
                        "order": 3,
                        "type": "general",
                        "status": "closed"
                    },
                    {
                        "order": 4,
                        "type": "shoulder",
                        "status": "open"
                    }
                ],
                "restrictions": [],
                "beginning_milepost": 50.0,
                "ending_milepost": 60.0
            }
        }
    }

test_wzdx_creator_expected = {
        "road_event_feed_info": {
            "update_date": "2021-04-13T00:00:00Z",
            "publisher": "CDOT",
            "contact_name": "Ashley Nylen",
            "contact_email": "ashley.nylen@state.co.us",
            'update_frequency': 300,
            "version": "4.0",
            "license": "https://creativecommons.org/publicdomain/zero/1.0/",
            "data_sources": [
                {
                    "data_source_id": "w",
                    "organization_name": "CDOT",
                    "contact_name": "Ashley Nylen",
                    "contact_email": "ashley.nylen@state.co.us",
                    "update_date": "2021-04-13T00:00:00Z",
                    'update_frequency': 300,
                }
            ]
        },
        "type": "FeatureCollection",
        "features": [
            {
                "id": "OpenTMS-Event1689408506",
                "type": "Feature",
                "properties": {
                    "core_details": {
                        "data_source_id": "w",
                        "event_type": "work-zone",
                        "road_names": [
                            "I-70E"
                        ],
                        "direction": "westbound",
                        "description": "Between Exit 49: CO 65; Grand Mesa (5 miles east of the Palisade area) and US 6 (Debeque) from Mile Point 50 to Mile Point 60. Road closed expect delays due to bridge construction. Until May 1, 2022 at about 12:26PM MDT.",
                        'update_date': "2021-10-29T18:35:01Z",
                    },
                    "start_date": "2021-10-29T18:26:04Z",
                    "end_date": "2022-05-01T18:26:04Z",
                    "location_method": "channel-device-method",
                    "beginning_milepost": 50.0,
                    "ending_milepost": 60.0,
                    "start_date_accuracy": "estimated",
                    "end_date_accuracy": "estimated",
                    "beginning_accuracy": "estimated",
                    "ending_accuracy": "estimated",
                    "vehicle_impact": "some-lanes-closed",
                    "lanes": [
                        {
                            "order": 1,
                            "type": "shoulder",
                            "status": "open"
                        },
                        {
                            "order": 2,
                            "type": "general",
                            "status": "closed"
                        },
                        {
                            "order": 3,
                            "type": "general",
                            "status": "closed"
                        },
                        {
                            "order": 4,
                            "type": "shoulder",
                            "status": "open"
                        }
                    ],
                    "event_status": "planned"
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [
                            -108.279106,
                            39.195663
                        ],
                        [
                            -108.218549,
                            39.302392
                        ]
                    ]
                }
            }
        ]
    }
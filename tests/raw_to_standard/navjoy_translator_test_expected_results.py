test_expand_speed_zone_1_expected = [{
    "sys_gUid": "Form568-cb0fdaf0-c27a-4bef-aabd-442615dfb2d6",
    "data": {
        "srzmap": [
                {
                    "type": "LineString",
                    "coordinates": [
                        [
                            [
                                -103.17130040113868,
                                40.625392709715676
                            ],
                            [
                                -103.17889641706886,
                                40.61979008921054
                            ]
                        ]
                    ],
                },
        ],
        "streetNameFrom": "US-34",
        "direction": "eastbound",
        "requestedTemporarySpeed": "45",
        "workStartDate": "2021-08-09T13:00:00.000Z",
        "workEndDate": "2021-09-24T23:00:00.000Z",
        "reductionJustification": "Crews roadside.",
        'currentPostedSpeed': None,
        'mileMarkerEnd': None,
        'mileMarkerStart': None,
    }
},
    {
    "sys_gUid": "Form568-cb0fdaf0-c27a-4bef-aabd-442615dfb2d6",
        "data": {
            "srzmap": [
                {
                    "type": "LineString",
                    "coordinates": [
                        [
                            [
                                -103.17130040113868,
                                40.625392709715676
                            ],
                            [
                                -103.17889641706886,
                                40.61979008921054
                            ]
                        ]
                    ],
                },
            ],
            "streetNameFrom": "US-34",
            "direction": "westbound",
            "requestedTemporarySpeed": "45",
            "workStartDate": "2021-08-09T13:00:00.000Z",
            "workEndDate": "2021-09-24T23:00:00.000Z",
            "reductionJustification": "Crews roadside.",
            'currentPostedSpeed': None,
            'mileMarkerEnd': None,
            'mileMarkerStart': None,
        }
}]


test_expand_speed_zone_2_expected = [{
    "sys_gUid": "Form568-cb0fdaf0-c27a-4bef-aabd-442615dfb2d6",
    "data": {
        "srzmap": [
                {
                    "type": "LineString",
                    "coordinates": [
                        [
                            [
                                -103.17130040113868,
                                40.625392709715676
                            ],
                            [
                                -103.17889641706886,
                                40.61979008921054
                            ]
                        ]
                    ],
                },
        ],
        "streetNameFrom": "US-34",
        "direction": "eastbound",
        "requestedTemporarySpeed": "45",
        "workStartDate": "2021-08-09T13:00:00.000Z",
        "workEndDate": "2021-09-24T23:00:00.000Z",
        "reductionJustification": "Crews roadside.",
        'currentPostedSpeed': None,
        'mileMarkerEnd': None,
        'mileMarkerStart': None,

        "streetNameFrom2": "US-34",
        "directionOfTraffic2": " East/West ",
        "requestedTemporarySpeed2": "45",
        "workStartDate2": "2021-08-09T13:00:00.000Z",
        "workEndDate2": "2021-09-24T23:00:00.000Z",
        'currentPostedSpeed2': None,
        'mileMarkerEnd2': None,
        'mileMarkerStart2': None,
    }
},
    {
    "sys_gUid": "Form568-cb0fdaf0-c27a-4bef-aabd-442615dfb2d6",
        "data": {
            "srzmap": [
                {
                    "type": "LineString",
                    "coordinates": [
                        [
                            [
                                -103.17130040113868,
                                40.625392709715676
                            ],
                            [
                                -103.17889641706886,
                                40.61979008921054
                            ]
                        ]
                    ],
                },
            ],
            "streetNameFrom": "US-34",
            "direction": "westbound",
            "requestedTemporarySpeed": "45",
            "workStartDate": "2021-08-09T13:00:00.000Z",
            "workEndDate": "2021-09-24T23:00:00.000Z",
            "reductionJustification": "Crews roadside.",
            'currentPostedSpeed': None,
            'mileMarkerEnd': None,
            'mileMarkerStart': None,

            "streetNameFrom2": "US-34",
            "directionOfTraffic2": " East/West ",
            "requestedTemporarySpeed2": "45",
            "workStartDate2": "2021-08-09T13:00:00.000Z",
            "workEndDate2": "2021-09-24T23:00:00.000Z",
            'currentPostedSpeed2': None,
            'mileMarkerEnd2': None,
            'mileMarkerStart2': None,
        }
}]

test_expand_speed_zone_2_3_4_expected = [{
    "sys_gUid": "Form568-cb0fdaf0-c27a-4bef-aabd-442615dfb2d6",
    "data": {
        "srzmap": [
        ],
        "streetNameFrom": "US-34",
        "direction": "eastbound",
        "requestedTemporarySpeed": "1",
        "workStartDate": "2021-08-09T13:00:00.000Z",
        "workEndDate": "2021-09-24T23:00:00.000Z",
        "reductionJustification": "Crews roadside.",
        'currentPostedSpeed': None,
        'mileMarkerEnd': None,
        'mileMarkerStart': None,

        "streetNameFrom2": "US-34",
        "directionOfTraffic2": " East/West ",
        "requestedTemporarySpeed2": "2",
        "workStartDate2": "2021-08-09T13:00:00.000Z",
        "workEndDate2": "2021-09-24T23:00:00.000Z",
        'currentPostedSpeed2': None,
        'mileMarkerEnd2': None,
        'mileMarkerStart2': None,

        "streetNameFrom3": "US-34",
        "directionOfTraffic3": " East/West ",
        "requestedTemporarySpeed3": "3",
        "workStartDate3": "2021-08-09T13:00:00.000Z",
        "workEndDate3": "2021-09-24T23:00:00.000Z",
        'currentPostedSpeed3': None,
        'mileMarkerEnd3': None,
        'mileMarkerStart3': None,

        "streetNameFrom4": "US-34",
        "directionOfTraffic4": " East/West ",
        "requestedTemporarySpeed4": "4",
        "workStartDate4": "2021-08-09T13:00:00.000Z",
        "workEndDate4": "2021-09-24T23:00:00.000Z",
        'currentPostedSpeed4': None,
        'mileMarkerEnd4': None,
        'mileMarkerStart4': None,
    }
},
    {
    "sys_gUid": "Form568-cb0fdaf0-c27a-4bef-aabd-442615dfb2d6",
        "data": {
            "srzmap": [
            ],
            "streetNameFrom": "US-34",
            "direction": "westbound",
            "requestedTemporarySpeed": "1",
            "workStartDate": "2021-08-09T13:00:00.000Z",
            "workEndDate": "2021-09-24T23:00:00.000Z",
            "reductionJustification": "Crews roadside.",
            'currentPostedSpeed': None,
            'mileMarkerEnd': None,
            'mileMarkerStart': None,

            "streetNameFrom2": "US-34",
            "directionOfTraffic2": " East/West ",
            "requestedTemporarySpeed2": "2",
            "workStartDate2": "2021-08-09T13:00:00.000Z",
            "workEndDate2": "2021-09-24T23:00:00.000Z",
            'currentPostedSpeed2': None,
            'mileMarkerEnd2': None,
            'mileMarkerStart2': None,

            "streetNameFrom3": "US-34",
            "directionOfTraffic3": " East/West ",
            "requestedTemporarySpeed3": "3",
            "workStartDate3": "2021-08-09T13:00:00.000Z",
            "workEndDate3": "2021-09-24T23:00:00.000Z",
            'currentPostedSpeed3': None,
            'mileMarkerEnd3': None,
            'mileMarkerStart3': None,

            "streetNameFrom4": "US-34",
            "directionOfTraffic4": " East/West ",
            "requestedTemporarySpeed4": "4",
            "workStartDate4": "2021-08-09T13:00:00.000Z",
            "workEndDate4": "2021-09-24T23:00:00.000Z",
            'currentPostedSpeed4': None,
            'mileMarkerEnd4': None,
            'mileMarkerStart4': None,
        }
}, {
        "sys_gUid": "Form568-cb0fdaf0-c27a-4bef-aabd-442615dfb2d6",
        "data": {
            "srzmap": [
            ],
            "streetNameFrom": "US-34",
            "direction": "eastbound",
            "requestedTemporarySpeed": "2",
            "workStartDate": "2021-08-09T13:00:00.000Z",
            "workEndDate": "2021-09-24T23:00:00.000Z",
            "reductionJustification": "Crews roadside.",
            'currentPostedSpeed': None,
            'mileMarkerEnd': None,
            'mileMarkerStart': None,

            "streetNameFrom2": "US-34",
            "directionOfTraffic2": " East/West ",
            "requestedTemporarySpeed2": "2",
            "workStartDate2": "2021-08-09T13:00:00.000Z",
            "workEndDate2": "2021-09-24T23:00:00.000Z",
            'currentPostedSpeed2': None,
            'mileMarkerEnd2': None,
            'mileMarkerStart2': None,

            "streetNameFrom3": "US-34",
            "directionOfTraffic3": " East/West ",
            "requestedTemporarySpeed3": "3",
            "workStartDate3": "2021-08-09T13:00:00.000Z",
            "workEndDate3": "2021-09-24T23:00:00.000Z",
            'currentPostedSpeed3': None,
            'mileMarkerEnd3': None,
            'mileMarkerStart3': None,

            "streetNameFrom4": "US-34",
            "directionOfTraffic4": " East/West ",
            "requestedTemporarySpeed4": "4",
            "workStartDate4": "2021-08-09T13:00:00.000Z",
            "workEndDate4": "2021-09-24T23:00:00.000Z",
            'currentPostedSpeed4': None,
            'mileMarkerEnd4': None,
            'mileMarkerStart4': None,
        }
},
    {
        "sys_gUid": "Form568-cb0fdaf0-c27a-4bef-aabd-442615dfb2d6",
        "data": {
            "srzmap": [
            ],
            "streetNameFrom": "US-34",
            "direction": "westbound",
            "requestedTemporarySpeed": "2",
            "workStartDate": "2021-08-09T13:00:00.000Z",
            "workEndDate": "2021-09-24T23:00:00.000Z",
            "reductionJustification": "Crews roadside.",
            'currentPostedSpeed': None,
            'mileMarkerEnd': None,
            'mileMarkerStart': None,

            "streetNameFrom2": "US-34",
            "directionOfTraffic2": " East/West ",
            "requestedTemporarySpeed2": "2",
            "workStartDate2": "2021-08-09T13:00:00.000Z",
            "workEndDate2": "2021-09-24T23:00:00.000Z",
            'currentPostedSpeed2': None,
            'mileMarkerEnd2': None,
            'mileMarkerStart2': None,

            "streetNameFrom3": "US-34",
            "directionOfTraffic3": " East/West ",
            "requestedTemporarySpeed3": "3",
            "workStartDate3": "2021-08-09T13:00:00.000Z",
            "workEndDate3": "2021-09-24T23:00:00.000Z",
            'currentPostedSpeed3': None,
            'mileMarkerEnd3': None,
            'mileMarkerStart3': None,

            "streetNameFrom4": "US-34",
            "directionOfTraffic4": " East/West ",
            "requestedTemporarySpeed4": "4",
            "workStartDate4": "2021-08-09T13:00:00.000Z",
            "workEndDate4": "2021-09-24T23:00:00.000Z",
            'currentPostedSpeed4': None,
            'mileMarkerEnd4': None,
            'mileMarkerStart4': None,
        }
}, {
        "sys_gUid": "Form568-cb0fdaf0-c27a-4bef-aabd-442615dfb2d6",
        "data": {
            "srzmap": [
            ],
            "streetNameFrom": "US-34",
            "direction": "eastbound",
            "requestedTemporarySpeed": "3",
            "workStartDate": "2021-08-09T13:00:00.000Z",
            "workEndDate": "2021-09-24T23:00:00.000Z",
            "reductionJustification": "Crews roadside.",
            'currentPostedSpeed': None,
            'mileMarkerEnd': None,
            'mileMarkerStart': None,

            "streetNameFrom2": "US-34",
            "directionOfTraffic2": " East/West ",
            "requestedTemporarySpeed2": "2",
            "workStartDate2": "2021-08-09T13:00:00.000Z",
            "workEndDate2": "2021-09-24T23:00:00.000Z",
            'currentPostedSpeed2': None,
            'mileMarkerEnd2': None,
            'mileMarkerStart2': None,

            "streetNameFrom3": "US-34",
            "directionOfTraffic3": " East/West ",
            "requestedTemporarySpeed3": "3",
            "workStartDate3": "2021-08-09T13:00:00.000Z",
            "workEndDate3": "2021-09-24T23:00:00.000Z",
            'currentPostedSpeed3': None,
            'mileMarkerEnd3': None,
            'mileMarkerStart3': None,

            "streetNameFrom4": "US-34",
            "directionOfTraffic4": " East/West ",
            "requestedTemporarySpeed4": "4",
            "workStartDate4": "2021-08-09T13:00:00.000Z",
            "workEndDate4": "2021-09-24T23:00:00.000Z",
            'currentPostedSpeed4': None,
            'mileMarkerEnd4': None,
            'mileMarkerStart4': None,
        }
},
    {
        "sys_gUid": "Form568-cb0fdaf0-c27a-4bef-aabd-442615dfb2d6",
        "data": {
            "srzmap": [
            ],
            "streetNameFrom": "US-34",
            "direction": "westbound",
            "requestedTemporarySpeed": "3",
            "workStartDate": "2021-08-09T13:00:00.000Z",
            "workEndDate": "2021-09-24T23:00:00.000Z",
            "reductionJustification": "Crews roadside.",
            'currentPostedSpeed': None,
            'mileMarkerEnd': None,
            'mileMarkerStart': None,

            "streetNameFrom2": "US-34",
            "directionOfTraffic2": " East/West ",
            "requestedTemporarySpeed2": "2",
            "workStartDate2": "2021-08-09T13:00:00.000Z",
            "workEndDate2": "2021-09-24T23:00:00.000Z",
            'currentPostedSpeed2': None,
            'mileMarkerEnd2': None,
            'mileMarkerStart2': None,

            "streetNameFrom3": "US-34",
            "directionOfTraffic3": " East/West ",
            "requestedTemporarySpeed3": "3",
            "workStartDate3": "2021-08-09T13:00:00.000Z",
            "workEndDate3": "2021-09-24T23:00:00.000Z",
            'currentPostedSpeed3': None,
            'mileMarkerEnd3': None,
            'mileMarkerStart3': None,

            "streetNameFrom4": "US-34",
            "directionOfTraffic4": " East/West ",
            "requestedTemporarySpeed4": "4",
            "workStartDate4": "2021-08-09T13:00:00.000Z",
            "workEndDate4": "2021-09-24T23:00:00.000Z",
            'currentPostedSpeed4': None,
            'mileMarkerEnd4': None,
            'mileMarkerStart4': None,
        }
}, {
        "sys_gUid": "Form568-cb0fdaf0-c27a-4bef-aabd-442615dfb2d6",
        "data": {
            "srzmap": [
            ],
            "streetNameFrom": "US-34",
            "direction": "eastbound",
            "requestedTemporarySpeed": "4",
            "workStartDate": "2021-08-09T13:00:00.000Z",
            "workEndDate": "2021-09-24T23:00:00.000Z",
            "reductionJustification": "Crews roadside.",
            'currentPostedSpeed': None,
            'mileMarkerEnd': None,
            'mileMarkerStart': None,

            "streetNameFrom2": "US-34",
            "directionOfTraffic2": " East/West ",
            "requestedTemporarySpeed2": "2",
            "workStartDate2": "2021-08-09T13:00:00.000Z",
            "workEndDate2": "2021-09-24T23:00:00.000Z",
            'currentPostedSpeed2': None,
            'mileMarkerEnd2': None,
            'mileMarkerStart2': None,

            "streetNameFrom3": "US-34",
            "directionOfTraffic3": " East/West ",
            "requestedTemporarySpeed3": "3",
            "workStartDate3": "2021-08-09T13:00:00.000Z",
            "workEndDate3": "2021-09-24T23:00:00.000Z",
            'currentPostedSpeed3': None,
            'mileMarkerEnd3': None,
            'mileMarkerStart3': None,

            "streetNameFrom4": "US-34",
            "directionOfTraffic4": " East/West ",
            "requestedTemporarySpeed4": "4",
            "workStartDate4": "2021-08-09T13:00:00.000Z",
            "workEndDate4": "2021-09-24T23:00:00.000Z",
            'currentPostedSpeed4': None,
            'mileMarkerEnd4': None,
            'mileMarkerStart4': None,
        }
},
    {
        "sys_gUid": "Form568-cb0fdaf0-c27a-4bef-aabd-442615dfb2d6",
        "data": {
            "srzmap": [
            ],
            "streetNameFrom": "US-34",
            "direction": "westbound",
            "requestedTemporarySpeed": "4",
            "workStartDate": "2021-08-09T13:00:00.000Z",
            "workEndDate": "2021-09-24T23:00:00.000Z",
            "reductionJustification": "Crews roadside.",
            'currentPostedSpeed': None,
            'mileMarkerEnd': None,
            'mileMarkerStart': None,

            "streetNameFrom2": "US-34",
            "directionOfTraffic2": " East/West ",
            "requestedTemporarySpeed2": "2",
            "workStartDate2": "2021-08-09T13:00:00.000Z",
            "workEndDate2": "2021-09-24T23:00:00.000Z",
            'currentPostedSpeed2': None,
            'mileMarkerEnd2': None,
            'mileMarkerStart2': None,

            "streetNameFrom3": "US-34",
            "directionOfTraffic3": " East/West ",
            "requestedTemporarySpeed3": "3",
            "workStartDate3": "2021-08-09T13:00:00.000Z",
            "workEndDate3": "2021-09-24T23:00:00.000Z",
            'currentPostedSpeed3': None,
            'mileMarkerEnd3': None,
            'mileMarkerStart3': None,

            "streetNameFrom4": "US-34",
            "directionOfTraffic4": " East/West ",
            "requestedTemporarySpeed4": "4",
            "workStartDate4": "2021-08-09T13:00:00.000Z",
            "workEndDate4": "2021-09-24T23:00:00.000Z",
            'currentPostedSpeed4': None,
            'mileMarkerEnd4': None,
            'mileMarkerStart4': None,
        }
}]

test_generate_standard_messages_from_string_expected = [
    {
        "rtdh_timestamp": 1639062865.0398643,
        "rtdh_message_id": "we234de",
        "event": {
            "type": "",
            "source": {
                "id": "Form568-6ab4408e-d9c1-4ac0-ab1d-b16feb17f18d",
                "creation_timestamp": 1620750345352,
                "last_updated_timestamp": 1639088065040
            },
            "geometry": [
                [
                    -104.67872140544365,
                    40.42252930726312
                ],
                [
                    -104.67870531218956,
                    40.42358701413087
                ]
            ],
            "header": {
                "description": "Bridge Repair and replacement.",
                "justification": "Repairing and replacing the bridge. Crews will be roadside, various alternating single lane closures.",
                "reduced_speed_limit": "35",
                "start_timestamp": 1627905600000,
                "end_timestamp": 1627905600000
            },
            "detail": {
                "road_name": "US-85",
                "road_number": "US-85",
                "direction": "northbound"
            },
            "additional_info": {
                "normal_speed_limit": "45",
                "mileMarkerStart": "47.25",
                "mileMarkerEnd": "47.30"
            }
        }
    },
    {
        "rtdh_timestamp": 1639062865.0398643,
        "rtdh_message_id": "23wsg54h",
        "event": {
            "type": "",
            "source": {
                "id": "Form568-6ab4408e-d9c1-4ac0-ab1d-b16feb17f18d",
                "creation_timestamp": 1620750345352,
                "last_updated_timestamp": 1639088065040
            },
            "geometry": [
                [
                    -104.67870531218956,
                    40.42358701413087
                ],
                [
                    -104.67872140544365,
                    40.42252930726312
                ]
            ],
            "header": {
                "description": "Bridge Repair and replacement.",
                "justification": "Repairing and replacing the bridge. Crews will be roadside, various alternating single lane closures.",
                "reduced_speed_limit": "35",
                "start_timestamp": 1627905600000,
                "end_timestamp": 1627905600000
            },
            "detail": {
                "road_name": "US-85",
                "road_number": "US-85",
                "direction": "southbound"
            },
            "additional_info": {
                "normal_speed_limit": "45",
                "mileMarkerStart": "47.25",
                "mileMarkerEnd": "47.30"
            }
        }
    },
    {
        "rtdh_timestamp": 1639062865.0398643,
        "rtdh_message_id": "7fa1dfas",
        "event": {
            "type": "",
            "source": {
                "id": "Form568-2f560979-b6e9-4d28-a6e1-6120066ee992",
                "creation_timestamp": 1620749795783,
                "last_updated_timestamp": 1639088065040
            },
            "geometry": [
                [
                    -104.68001838896744,
                    40.40980683657896
                ],
                [
                    -104.67976089690201,
                    40.418367644368814
                ]
            ],
            "header": {
                "description": "Restriping operations.",
                "justification": "Crews will be roadside restriping in various alternating lane closures.",
                "reduced_speed_limit": "35",
                "start_timestamp": 1623070800000,
                "end_timestamp": 1623070800000
            },
            "detail": {
                "road_name": "US-85",
                "road_number": "US-85",
                "direction": "northbound"
            },
            "additional_info": {
                "normal_speed_limit": "45",
                "mileMarkerStart": "48",
                "mileMarkerEnd": "50"
            }
        }
    },
    {
        "rtdh_timestamp": 1639062865.0408645,
        "rtdh_message_id": "23h327j",
        "event": {
            "type": "",
            "source": {
                "id": "Form568-2f560979-b6e9-4d28-a6e1-6120066ee992",
                "creation_timestamp": 1620749795783,
                "last_updated_timestamp": 1639088065041
            },
            "geometry": [
                [
                    -104.67976089690201,
                    40.418367644368814
                ],
                [
                    -104.68001838896744,
                    40.40980683657896
                ]
            ],
            "header": {
                "description": "Restriping operations.",
                "justification": "Crews will be roadside restriping in various alternating lane closures.",
                "reduced_speed_limit": "35",
                "start_timestamp": 1623070800000,
                "end_timestamp": 1623070800000
            },
            "detail": {
                "road_name": "US-85",
                "road_number": "US-85",
                "direction": "southbound"
            },
            "additional_info": {
                "normal_speed_limit": "45",
                "mileMarkerStart": "48",
                "mileMarkerEnd": "50"
            }
        }
    }
]

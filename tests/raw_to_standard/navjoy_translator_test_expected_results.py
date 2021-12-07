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

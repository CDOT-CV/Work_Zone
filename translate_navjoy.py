from wzdx.raw_to_standard import navjoy_568
import json

msg_string = """
[
    {
        "sys_gUid": "Form568-6ab4408e-d9c1-4ac0-ab1d-b16feb17f18d",
        "data": {
            "srzmap": [
                {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [
                                -104.67900571959923,
                                40.42358701413087
                            ],
                            [
                                -104.6784049047799,
                                40.42358701413087
                            ],
                            [
                                -104.67841563361596,
                                40.422517055735916
                            ],
                            [
                                -104.67902717727135,
                                40.42254155879033
                            ],
                            [
                                -104.67900571959923,
                                40.42358701413087
                            ]
                        ]
                    ],
                    "className": "Form568"
                },
                {
                    "type": "Point",
                    "coordinates": [
                        -104.67878764081412,
                        40.42327902840428
                    ],
                    "className": "text"
                }
            ],
            "cdotEngineeringRegionNumber": "4",
            "methodOfHandlingTraffic": [],
            "professionalEngineerStamp/Certification": [],
            "permits": [],
            "cdotSection/DepartmentName": "LA Projects",
            "cdotPatrolNumber/Id": "1",
            "subAccountNumber": "48976-A",
            "mpaCode": "789465",
            "descriptionForProject": "Bridge Repair and replacement.",
            "streetNameFrom": "US-85",
            "mileMarkerStart": "47.25",
            "mileMarkerEnd": "47.30",
            "directionOfTraffic": " North/South",
            "currentPostedSpeed": "45",
            "requestedTemporarySpeed": "35",
            "reductionJustification": "Repairing and replacing the bridge. Crews will be roadside, various alternating single lane closures.",
            "document": [],
            "approval": {
                "description": "",
                "value": "Approved"
            },
            "signature": {
                "url": "https://assetgovprod.s3-us-west-2.amazonaws.com/Documents/Signature/Files/signature--938878001",
                "date": "2021-05-11T16:25:45.352Z",
                "name": "Jonathan Woodworth"
            },
            "workStartDate": "2021-08-02T12:00:00.000Z",
            "workEndDate": "2021-10-30T00:00:00.000Z",
            "cdotProjectEngineerName": {
                "sys_gUid": "User-905f1bf6-05fb-4354-beb8-8f095203f7d8",
                "firstName": "Bryce",
                "lastName": "Reeves",
                "title": "Traffic Design and LA Projects Manager"
            },
            "requestorName": {
                "sys_gUid": "User-905f1bf6-05fb-4354-beb8-8f095203f7d8",
                "username": "bryce.reeves@state.co.us",
                "firstName": "Bryce",
                "lastName": "Reeves",
                "agencyuser": "CDOT Region 4",
                "roleName": "CDOT Projects Requestor",
                "email": "bryce.reeves@state.co.us",
                "Name": "CDOT Region 4",
                "title": "Traffic Design and LA Projects Manager"
            },
            "taskChecklist": [
                "Is the Required Information Tab Complete?",
                "Are the requester and CDOT Engineer details accurate?",
                "Are the speed reduction details and the SRZ polygon accurate?",
                "Is the requested speed reduction valid based on the criteria shown in the Authority tab?"
            ]
        }
    },
    {
        "sys_gUid": "Form568-2f560979-b6e9-4d28-a6e1-6120066ee992",
        "data": {
            "srzmap": [
                {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [
                                -104.68031879637711,
                                40.418367644368814
                            ],
                            [
                                -104.67920299742691,
                                40.418367644368814
                            ],
                            [
                                -104.67928882811539,
                                40.40980683657896
                            ],
                            [
                                -104.68074794981949,
                                40.40980683657896
                            ],
                            [
                                -104.68031879637711,
                                40.418367644368814
                            ]
                        ]
                    ],
                    "className": "Form568"
                },
                {
                    "type": "Point",
                    "coordinates": [
                        -104.67991855002329,
                        40.415730628325946
                    ],
                    "className": "text"
                }
            ],
            "cdotEngineeringRegionNumber": "4",
            "methodOfHandlingTraffic": [],
            "professionalEngineerStamp/Certification": [],
            "permits": [],
            "cdotSection/DepartmentName": "Traffic and LA Projects",
            "cdotPatrolNumber/Id": "1",
            "subAccountNumber": "1458-A",
            "mpaCode": "124578",
            "descriptionForProject": "Restriping operations.",
            "streetNameFrom": "US-85",
            "mileMarkerStart": "48",
            "mileMarkerEnd": "50",
            "directionOfTraffic": " North/South",
            "currentPostedSpeed": "45",
            "requestedTemporarySpeed": "35",
            "workStartDate": "2021-06-07T13:00:00.000Z",
            "workEndDate": "2021-06-25T23:00:00.000Z",
            "reductionJustification": "Crews will be roadside restriping in various alternating lane closures.",
            "document": [],
            "approval": {
                "description": "",
                "value": "Approved"
            },
            "cdotProjectEngineerName": {
                "sys_gUid": "User-905f1bf6-05fb-4354-beb8-8f095203f7d8",
                "firstName": "Bryce",
                "lastName": "Reeves",
                "title": "Traffic Design and LA Projects Manager"
            },
            "requestorName": {
                "sys_gUid": "User-905f1bf6-05fb-4354-beb8-8f095203f7d8",
                "username": "bryce.reeves@state.co.us",
                "firstName": "Bryce",
                "lastName": "Reeves",
                "agencyuser": "CDOT Region 4",
                "roleName": "CDOT Projects Requestor",
                "email": "bryce.reeves@state.co.us",
                "Name": "CDOT Region 4",
                "title": "Traffic Design and LA Projects Manager"
            },
            "taskChecklist": [
                "Is the Required Information Tab Complete?",
                "Are the requester and CDOT Engineer details accurate?",
                "Are the speed reduction details and the SRZ polygon accurate?",
                "Is the requested speed reduction valid based on the criteria shown in the Authority tab?"
            ],
            "signature": {
                "url": "https://assetgovprod.s3-us-west-2.amazonaws.com/Documents/Signature/Files/signature--938878001",
                "date": "2021-05-11T16:16:35.783Z",
                "name": "Jonathan Woodworth"
            }
        }
    }
]
"""

print(json.dumps(navjoy_568.generate_standard_messages_from_string(msg_string), indent=2))

{
    'rtdh_timestamp': 1638846301.4691865,
    'rtdh_message_id': 'e5bba2f6-bbd0-4a61-8d64-b7c33657d35a',
    'event': {
        'type': '',
        'source': {
            'id': 'Form568-44819108-703c-4d6d-ae0d-7dca7319e5b0',
            'last_updated_timestamp': 1638871501469
        },
        'geometry': [
            [-104.82230842595187, 39.73946349406594],
            [-104.79432762150851, 39.73959547447038]
        ],
        'header': {
            'description': 'Maintenance for lane expansion',
            'justification': 'Lane expansion - maintenance work',
            'reduced_speed_limit': 45,
            'start_timestamp': 1630290600000,
            'end_timestamp': 1630290600000
        },
        'detail': {
            'road_name': '287',
            'road_number': '287',
            'direction': 'eastbound'
        }
    }
}

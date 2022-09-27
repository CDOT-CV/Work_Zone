test_parse_reduction_zone_linestring_standard = {
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

test_parse_reduction_zone_linestring_expected_feature = {
    'id': 'Form568-44819108-703c-4d6d-ae0d-7dca7319e5b0',
    "type": "Feature",
    "properties": {
        "core_details": {
            "data_source_id": '',
            "event_type": "work-zone",
            "road_names": ["287"],
            "direction": "eastbound",
            "description": "Maintenance for lane expansion. Lane expansion - maintenance work",
            "update_date": "2021-12-07T10:05:01Z"
        },
        "start_date": "2021-08-30T02:30:00Z",
        "end_date": "2021-08-30T02:30:00Z",
        "start_date_accuracy": "estimated",
        "end_date_accuracy": "estimated",
        "beginning_accuracy": "estimated",
        "ending_accuracy": "estimated",
        "vehicle_impact": "all-lanes-open",
        "event_status": "completed",
        "reduced_speed_limit": 45,
        'types_of_work': [{'type_name': 'surface-work',
                           'is_architectural_change': True}],
    },
    "geometry": {
        "type": "LineString",
        "coordinates": [
            [
                -104.82230842595187,
                39.73946349406594
            ],
            [
                -104.79432762150851,
                39.73959547447038
            ],
        ]
    }
}

test_wzdx_creator_standard = {
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

test_wzdx_creator_expected_wzdx = {
    'road_event_feed_info': {
        'update_date': '2021-04-13T00:00:00Z',
        'publisher': 'CDOT',
        'contact_name': 'Ashley Nylen',
        'contact_email': 'ashley.nylen@state.co.us',
        'version': '4.0',
        "update_frequency": 300,
        'license': 'https://creativecommons.org/publicdomain/zero/1.0/',
        'data_sources': [
            {
                'data_source_id': 'w',
                'organization_name': 'CDOT',
                'contact_name': 'Ashley Nylen',
                'contact_email': 'ashley.nylen@state.co.us',
                'update_date': '2021-04-13T00:00:00Z',
                "update_frequency": 300,
            }
        ]
    },
    'type': 'FeatureCollection',
    'features': [
        {
            'id': 'Form568-44819108-703c-4d6d-ae0d-7dca7319e5b0',
            'type': 'Feature',
            'properties': {
                'core_details': {
                    'data_source_id': 'w',
                    'event_type': 'work-zone',
                    'road_names': ['287'],
                    'direction': 'eastbound',
                    'description': 'Maintenance for lane expansion. Lane expansion - maintenance work',
                    'update_date': "2021-12-07T10:05:01Z"
                },
                'reduced_speed_limit': 45,
                'start_date': "2021-08-30T02:30:00Z",
                'end_date': "2021-08-30T02:30:00Z",
                'start_date_accuracy': 'estimated',
                'end_date_accuracy': 'estimated',
                'beginning_accuracy': 'estimated',
                'ending_accuracy': 'estimated',
                'vehicle_impact': 'all-lanes-open',
                'event_status': 'planned',
                'types_of_work': [
                    {
                        'type_name': 'surface-work',
                        'is_architectural_change': True
                    }
                ]
            },
            'geometry': {
                'type': 'LineString',
                'coordinates': [
                    [-104.82230842595187, 39.73946349406594],
                    [-104.79432762150851, 39.73959547447038]
                ]
            },
        }
    ]
}

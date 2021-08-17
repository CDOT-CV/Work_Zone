import os
import uuid
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import time_machine
from translator import cotrip_translator


@patch.dict(os.environ, {
    'contact_name': 'Ashley Nylen',
    'contact_email': 'ashley.nylen@state.co.us',
    'issuing_organization': 'CDOT'
})
@patch('uuid.uuid4')
def test_wzdx_creator(mockuuid):
    uuid.uuid4 = Mock()
    uuid.uuid4.side_effect = 'we234de'
    cotrip_obj = {
        "rtdh_timestamp": 1615866698.393723,
        "rtdh_message_id": "dd962abd-0afa-4810-aac0-165edb834e71",
        "event": {
            "type": "Construction",
            "sub_type": "Work Zone:roadway-relocation",
            "source": {
                "road_event_id": "349611",
                "type": "Road Work",
                "sub_type": "Road Construction",
                "collection_timestamp": 1615482720
            },
            "lrs": None,
            "geometry": "LINESTRING (-104.48011 37.007645, -104.480103 37.008034, -104.480125 37.008469, -104.480202 37.008904, -104.48024 37.009048, -104.480324 37.009338, -104.482475 37.015327, -104.482712 37.015945, -104.48288 37.016335, -104.482979 37.016521, -104.483208 37.016884, -104.483467 37.01722, -104.483612 37.01738, -104.483925 37.017681, -104.484253 37.017948, -104.484772 37.018295, -104.485138 37.01849, -104.485504 37.018661, -104.485886 37.01881, -104.486473 37.019005, -104.488014 37.019493)",
            "header": {
                "description": "Road Construction - I-25 (Main St.) business loop from MP 1-2",
                "start_timestamp": 1615813200,
                "end_timestamp": 1638255600
            },
            "detail": {
                "road_name": "I-25",
                "road_number": "I-25",
                "direction": "North"
            },
        }
    }
    expected_wzdx = {
        'road_event_feed_info': {
            'feed_info_id': '8d062f70-d53e-4029-b94e-b7fbcbde5885',
            'update_date': '2021-04-13T00:00:00Z', 'publisher': 'CDOT',
            'contact_name': 'Ashley Nylen',
            'contact_email': 'ashley.nylen@state.co.us',
            'version': '3.1',
            'license': 'https://creativecommons.org/publicdomain/zero/1.0/',
            'data_sources': [{
                'data_source_id': 'w',
                'feed_info_id': '8d062f70-d53e-4029-b94e-b7fbcbde5885',
                'organization_name': 'CDOT',
                'contact_name': 'Ashley Nylen',
                'contact_email': 'ashley.nylen@state.co.us',
                'update_date': '2021-04-13T00:00:00Z',
                'location_method': 'channel-device-method',
                'lrs_type': 'lrs_type'}]},
        'type': 'FeatureCollection',
        'features': [{
            'type': 'Feature',
            'properties': {
                'road_event_id': '2',
                'event_type': 'work-zone',
                'data_source_id': 'w',
                'start_date': '2021-03-15T13:00:00Z',
                'end_date': '2021-11-30T07:00:00Z',
                'start_date_accuracy': 'estimated',
                'end_date_accuracy': 'estimated',
                'beginning_accuracy': 'estimated',
                'ending_accuracy': 'estimated',
                'direction': 'northbound',
                'vehicle_impact': 'unknown',
                'event_status': 'active',
                'types_of_work': [
                    {
                        'type_name': 'roadway-relocation',
                        'is_architectural_change': True}],
                'description': 'Road Construction - I-25 (Main St.) business loop from MP 1-2',
                'creation_date': '2021-03-11T17:12:00Z',
                'update_date': '2021-03-16T03:51:38Z',
                'road_names': ['I-25']},
            'geometry': {
                'type': 'LineString',
                'coordinates': [[-104.48011, 37.007645], [-104.480103, 37.008034], [-104.480125, 37.008469], [-104.480202, 37.008904], [-104.48024, 37.009048], [-104.480324, 37.009338], [-104.482475, 37.015327], [-104.482712, 37.015945], [-104.48288, 37.016335], [-104.482979, 37.016521], [-104.483208, 37.016884], [-104.483467, 37.01722], [-104.483612, 37.01738], [-104.483925, 37.017681], [-104.484253, 37.017948], [-104.484772, 37.018295], [-104.485138, 37.01849], [-104.485504, 37.018661], [-104.485886, 37.01881], [-104.486473, 37.019005], [-104.488014, 37.019493]]}}]}

    with time_machine.travel(datetime(2021, 4, 13, 0, 0, 0)):
        test_wzdx = cotrip_translator.wzdx_creator(cotrip_obj)
    assert expected_wzdx == test_wzdx


def test_wzdx_creator_empty_cotrip_object():
    cotrip_obj = None
    test_wzdx = cotrip_translator.wzdx_creator(cotrip_obj)
    assert test_wzdx == None


@patch.dict(os.environ, {
    'contact_name': 'Ashley Nylen',
    'contact_email': 'ashley.nylen@state.co.us',
    'issuing_organization': 'CDOT'
})
def test_wzdx_creator_invalid_incidents_no_description():
    cotrip_obj = {
        "rtdh_timestamp": 1615866698.393723,
        "rtdh_message_id": "dd962abd-0afa-4810-aac0-165edb834e71",
        "event": {
            "type": "Construction",
            "sub_type": "Work Zone:roadway-relocation",
            "source": {
                "road_event_id": "349611",
                "type": "Road Work",
                "sub_type": "Road Construction",
                "collection_timestamp": 1615482720
            },
            "lrs": None,
            "geometry": "LINESTRING (-104.48011 37.007645, -104.480103 37.008034, -104.480125 37.008469, -104.480202 37.008904, -104.48024 37.009048, -104.480324 37.009338, -104.482475 37.015327, -104.482712 37.015945, -104.48288 37.016335, -104.482979 37.016521, -104.483208 37.016884, -104.483467 37.01722, -104.483612 37.01738, -104.483925 37.017681, -104.484253 37.017948, -104.484772 37.018295, -104.485138 37.01849, -104.485504 37.018661, -104.485886 37.01881, -104.486473 37.019005, -104.488014 37.019493)",
            "header": {
                "start_timestamp": 1615813200,
                "end_timestamp": 1638255600
            },
            "detail": {
                "road_name": "I-25",
                "road_number": "I-25",
                "direction": "North"
            },
        }
    }
    test_wzdx = cotrip_translator.wzdx_creator(cotrip_obj)
    assert test_wzdx == None


def test_wzdx_creator_invalid_info_object():
    cotrip_obj = {
        "rtdh_timestamp": 1615866698.393723,
        "rtdh_message_id": "dd962abd-0afa-4810-aac0-165edb834e71",
        "event": {
            "type": "Construction",
            "sub_type": "Work Zone:roadway-relocation",
            "source": {
                "road_event_id": "349611",
                "type": "Road Work",
                "sub_type": "Road Construction",
                "collection_timestamp": 1615482720
            },
            "lrs": None,
            "geometry": "LINESTRING (-104.48011 37.007645, -104.480103 37.008034, -104.480125 37.008469, -104.480202 37.008904, -104.48024 37.009048, -104.480324 37.009338, -104.482475 37.015327, -104.482712 37.015945, -104.48288 37.016335, -104.482979 37.016521, -104.483208 37.016884, -104.483467 37.01722, -104.483612 37.01738, -104.483925 37.017681, -104.484253 37.017948, -104.484772 37.018295, -104.485138 37.01849, -104.485504 37.018661, -104.485886 37.01881, -104.486473 37.019005, -104.488014 37.019493)",
            "header": {
                "description": "Road Construction - I-25 (Main St.) business loop from MP 1-2",
                "start_timestamp": 1615813200,
                "end_timestamp": 1638255600
            },
            "detail": {
                "road_name": "I-25",
                "road_number": "I-25",
                "direction": "North"
            },
        }
    }

    test_invalid_info_object = {
        'feed_info_id': "104d7746-e948bf9dfa",
        'metadata': {
            'wz_location_method': "channel-device-method",
            'lrs_type': "lrs_type",
            'contact_name': "Ashley Nylen",
            'contact_email': "ashley.nylen@state.co.us",
            'issuing_organization': "COtrip",
        }
    }

    test_wzdx = cotrip_translator.wzdx_creator(
        cotrip_obj, test_invalid_info_object)
    assert test_wzdx == None


# --------------------------------------------------------------------------------Unit test for parse_polyline function--------------------------------------------------------------------------------
def test_parse_polyline_valid_data():
    test_polyline = "LINESTRING (-104.828415 37.735142, -104.830933 37.741074)"
    test_coordinates = cotrip_translator.parse_polyline(test_polyline)
    valid_coordinates = [
        [
            -104.828415,
            37.735142
        ],
        [
            -104.830933,
            37.741074
        ]
    ]
    assert test_coordinates == valid_coordinates


def test_parse_polyline_null_parameter():
    test_polyline = None
    test_coordinates = cotrip_translator.parse_polyline(test_polyline)
    expected_coordinates = None
    assert test_coordinates == expected_coordinates


def test_parse_polyline_invalid_data():
    test_polyline = 'invalid'
    test_coordinates = cotrip_translator.parse_polyline(test_polyline)
    expected_coordinates = []
    assert test_coordinates == expected_coordinates


def test_parse_polyline_invalid_coordinates():
    test_polyline = 'a,b,c,d'
    test_coordinates = cotrip_translator.parse_polyline(test_polyline)
    expected_coordinates = []
    assert test_coordinates == expected_coordinates


# --------------------------------------------------------------------------------Unit test for parse_incident function--------------------------------------------------------------------------------
def test_parse_alert_success():
    cotrip_obj = {
        "rtdh_timestamp": 1615866698.394646,
        "rtdh_message_id": "6a04ed6f-2f3d-4da6-b6ea-061242b800bb",
        "event": {
            "type": "Construction",
            "sub_type": "Work Zone:below-road-work",
            "source": {
                "road_event_id": "287810",
                "id2": "27499",
                "name": "CDOT ITS",
                "type": "Road Work",
                "sub_type": "Bridge Construction",
                "collection_timestamp": 1607017441
            },
            "lrs": None,
            "geometry": "LINESTRING (-104.828415 37.735142, -104.830933 37.741074, -104.83094 37.741085, -104.831367 37.7421, -104.831383 37.742138, -104.831818 37.743164, -104.831825 37.743183, -104.832626 37.745064, -104.832634 37.745079, -104.834328 37.749054)",
            "header": {
                "name": "I-25 Northbound / Southbound I-25 and Butte Creek at approximately MP 58.7, north of the Town of Walsenburg, Huerfano County (Milemarker 58.08-59.01) (through December 2020)",
                "description": "Bridge Construction - I-25 and Butte Creek at approximately MP 58.7, north of the Town of Walsenburg, Huerfano County",
                "location_description": "I-25 and Butte Creek at approximately MP 58.7, north of the Town of Walsenburg, Huerfano County",
                "severity": "Moderate",
                "language": "English",
                "external_reference_url": "https://www.codot.gov/projects/i-25-butte-creek-bridge-replacement",
                "start_timestamp": 1538978400,
                "end_timestamp": 1609398000
            },
            "detail": {
                "description": "Replacement of bridges N-17-BN and N-17-S at I-25 and Butte Creek, as well as ancillary highway and drainage work to accommodate the new bridge structures.  Each bridge crosses over Butte Creek, as well as the frontage road Huerfano County Road 103.  Area inlets that are currently present in the median between the north and south bound lanes of I-25 will also be upgraded to accommodate the bridge and roadway improvements.",
                "work_updates": [],
                "road_name": "I-25",
                "road_number": "I-25",
                "direction": "North"
            },
            "additional_info": None
        }
    }

    test_feature = cotrip_translator.parse_alert(cotrip_obj)
    expected_feature = {


        "type": "Feature",
        "properties": {
            "road_event_id": None,
            "event_type": "work-zone",
            "data_source_id": None,
            "start_date": "2018-10-08T06:00:00Z",
            "end_date": "2020-12-31T07:00:00Z",
            "start_date_accuracy": "estimated",
            "end_date_accuracy": "estimated",
            "beginning_accuracy": "estimated",
            "ending_accuracy": "estimated",
            "road_names": ['I-25'],
            "direction": "northbound",
            "vehicle_impact": "unknown",

            "event_status": "completed",
            "types_of_work": [{'is_architectural_change': True,
                               'type_name': 'below-road-work'}],

            "description": "Bridge Construction - I-25 and Butte Creek at approximately MP 58.7, north of the Town of Walsenburg, Huerfano County",
            "creation_date": "2020-12-03T17:44:01Z",
            "update_date": "2021-03-16T03:51:38Z"
        },
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [
                    -104.828415,
                    37.735142
                ],
                [
                    -104.830933,
                    37.741074
                ],
                [
                    -104.83094,
                    37.741085
                ],
                [
                    -104.831367,
                    37.7421
                ],
                [
                    -104.831383,
                    37.742138
                ],
                [
                    -104.831818,
                    37.743164
                ],
                [
                    -104.831825,
                    37.743183
                ],
                [
                    -104.832626,
                    37.745064
                ],
                [
                    -104.832634,
                    37.745079
                ],
                [
                    -104.834328,
                    37.749054
                ]
            ]
        }
    }

    assert test_feature == expected_feature


def test_parse_alert_multiple_road_names():
    cotrip_obj = {
        "rtdh_timestamp": 1615866698.394646,
        "rtdh_message_id": "6a04ed6f-2f3d-4da6-b6ea-061242b800bb",
        "event": {
            "type": "Construction",
            "sub_type": "Work Zone:below-road-work",
            "source": {
                "road_event_id": "287810",
                "id2": "27499",
                "name": "CDOT ITS",
                "type": "Road Work",
                "sub_type": "Bridge Construction",
                "collection_timestamp": 1607017441
            },
            "lrs": None,
            "geometry": "LINESTRING (-104.828415 37.735142, -104.830933 37.741074, -104.83094 37.741085, -104.831367 37.7421, -104.831383 37.742138, -104.831818 37.743164, -104.831825 37.743183, -104.832626 37.745064, -104.832634 37.745079, -104.834328 37.749054)",
            "header": {
                "name": "I-25 Northbound / Southbound I-25 and Butte Creek at approximately MP 58.7, north of the Town of Walsenburg, Huerfano County (Milemarker 58.08-59.01) (through December 2020)",
                "description": "Bridge Construction - I-25 and Butte Creek at approximately MP 58.7, north of the Town of Walsenburg, Huerfano County",
                "location_description": "I-25 and Butte Creek at approximately MP 58.7, north of the Town of Walsenburg, Huerfano County",
                "severity": "Moderate",
                "language": "English",
                "external_reference_url": "https://www.codot.gov/projects/i-25-butte-creek-bridge-replacement",
                "start_timestamp": 1538978400,
                "end_timestamp": 1609398000
            },
            "detail": {
                "description": "Replacement of bridges N-17-BN and N-17-S at I-25 and Butte Creek, as well as ancillary highway and drainage work to accommodate the new bridge structures.  Each bridge crosses over Butte Creek, as well as the frontage road Huerfano County Road 103.  Area inlets that are currently present in the median between the north and south bound lanes of I-25 will also be upgraded to accommodate the bridge and roadway improvements.",
                "work_updates": [],
                "road_name": "I-25",
                "road_number": "I-24",
                "direction": "North"
            },
            "additional_info": None
        }
    }

    test_feature = cotrip_translator.parse_alert(cotrip_obj)
    expected_feature = {


        "type": "Feature",
        "properties": {
            "road_event_id": None,
            "event_type": "work-zone",
            "data_source_id": None,
            "start_date": "2018-10-08T06:00:00Z",
            "end_date": "2020-12-31T07:00:00Z",
            "start_date_accuracy": "estimated",
            "end_date_accuracy": "estimated",
            "beginning_accuracy": "estimated",
            "ending_accuracy": "estimated",
            "road_names": ["I-25", "I-24"],
            "direction": "northbound",
            "vehicle_impact": "unknown",


            "event_status": "completed",
            "types_of_work": [{'is_architectural_change': True,
                               'type_name': 'below-road-work'}],

            "description": "Bridge Construction - I-25 and Butte Creek at approximately MP 58.7, north of the Town of Walsenburg, Huerfano County",
            "creation_date": "2020-12-03T17:44:01Z",
            "update_date": "2021-03-16T03:51:38Z"
        },
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [
                    -104.828415,
                    37.735142
                ],
                [
                    -104.830933,
                    37.741074
                ],
                [
                    -104.83094,
                    37.741085
                ],
                [
                    -104.831367,
                    37.7421
                ],
                [
                    -104.831383,
                    37.742138
                ],
                [
                    -104.831818,
                    37.743164
                ],
                [
                    -104.831825,
                    37.743183
                ],
                [
                    -104.832626,
                    37.745064
                ],
                [
                    -104.832634,
                    37.745079
                ],
                [
                    -104.834328,
                    37.749054
                ]
            ]
        }
    }

    assert test_feature == expected_feature


def test_parse_alert_no_data():
    test_feature = cotrip_translator.parse_alert(None)
    expected_feature = None
    assert test_feature == expected_feature


def test_parse_alert_invalid_data():
    test_var = 'a,b,c,d'
    callback = MagicMock()
    test_feature = cotrip_translator.parse_alert(
        test_var, callback_function=callback)
    assert callback.called and test_feature == None

# --------------------------------------------------------------------------------Unit test for validate_ function--------------------------------------------------------------------------------


def test_validate_alert_valid_data():
    test_valid_output = {
        "rtdh_timestamp": 1615866698.393723,
        "rtdh_message_id": "dd962abd-0afa-4810-aac0-165edb834e71",
        "event": {
            "type": "Construction",
            "sub_type": "Work Zone:roadway-relocation",
            "source": {
                "road_event_id": "349611",
                "type": "Road Work",
                "sub_type": "Road Construction",
                "collection_timestamp": 1615482720
            },
            "lrs": None,
            "geometry": "LINESTRING (-104.48011 37.007645, -104.480103 37.008034, -104.480125 37.008469, -104.480202 37.008904, -104.48024 37.009048, -104.480324 37.009338, -104.482475 37.015327, -104.482712 37.015945, -104.48288 37.016335, -104.482979 37.016521, -104.483208 37.016884, -104.483467 37.01722, -104.483612 37.01738, -104.483925 37.017681, -104.484253 37.017948, -104.484772 37.018295, -104.485138 37.01849, -104.485504 37.018661, -104.485886 37.01881, -104.486473 37.019005, -104.488014 37.019493)",
            "header": {
                "description": "Road Construction - I-25 (Main St.) business loop from MP 1-2",
                "start_timestamp": 1615813200,
                "end_timestamp": 1638255600
            },
            "detail": {
                "road_name": "I-25",
                "road_number": "I-25",
                "direction": "North"
            },
        }
    }
    assert cotrip_translator.validate_alert(test_valid_output) == True


def test_validate_alert_missing_required_field_description():
    test_valid_output = {
        "rtdh_timestamp": 1615866698.393723,
        "rtdh_message_id": "dd962abd-0afa-4810-aac0-165edb834e71",
        "event": {
            "type": "Construction",
            "sub_type": "Work Zone:roadway-relocation",
            "source": {
                "road_event_id": "349611",
                "type": "Road Work",
                "sub_type": "Road Construction",
                "collection_timestamp": 1615482720
            },
            "lrs": None,
            "geometry": "LINESTRING (-104.48011 37.007645, -104.480103 37.008034, -104.480125 37.008469, -104.480202 37.008904, -104.48024 37.009048, -104.480324 37.009338, -104.482475 37.015327, -104.482712 37.015945, -104.48288 37.016335, -104.482979 37.016521, -104.483208 37.016884, -104.483467 37.01722, -104.483612 37.01738, -104.483925 37.017681, -104.484253 37.017948, -104.484772 37.018295, -104.485138 37.01849, -104.485504 37.018661, -104.485886 37.01881, -104.486473 37.019005, -104.488014 37.019493)",
            "header": {
                "start_timestamp": 1615813200,
                "end_timestamp": 1638255600
            },
            "detail": {
                "road_name": "I-25",
                "road_number": "I-25",
                "direction": "North"
            },
        }
    }
    assert cotrip_translator.validate_alert(test_valid_output) == False


def test_validate_alert_invalid_start_time():
    test_valid_output = {
        "rtdh_timestamp": 1615866698.393723,
        "rtdh_message_id": "dd962abd-0afa-4810-aac0-165edb834e71",
        "event": {
            "type": "Construction",
            "sub_type": "Work Zone:roadway-relocation",
            "source": {
                "road_event_id": "349611",
                "type": "Road Work",
                "sub_type": "Road Construction",
                "collection_timestamp": 1615482720
            },
            "lrs": None,
            "geometry": "LINESTRING (-104.48011 37.007645, -104.480103 37.008034, -104.480125 37.008469, -104.480202 37.008904, -104.48024 37.009048, -104.480324 37.009338, -104.482475 37.015327, -104.482712 37.015945, -104.48288 37.016335, -104.482979 37.016521, -104.483208 37.016884, -104.483467 37.01722, -104.483612 37.01738, -104.483925 37.017681, -104.484253 37.017948, -104.484772 37.018295, -104.485138 37.01849, -104.485504 37.018661, -104.485886 37.01881, -104.486473 37.019005, -104.488014 37.019493)",
            "header": {
                "description": "Road Construction - I-25 (Main St.) business loop from MP 1-2",
                "start_timestamp": "1638S255600",
                "end_timestamp": 1638255600
            },
            "detail": {
                "road_name": "I-25",
                "road_number": "I-25",
                "direction": "North"
            },
        }
    }
    assert cotrip_translator.validate_alert(test_valid_output) == False


def test_validate_alert_invalid():
    test_valid_output = 'invalid output'
    assert cotrip_translator.validate_alert(test_valid_output) == False


def test_validate_alert_no_data():
    test_valid_output = None
    assert cotrip_translator.validate_alert(test_valid_output) == False

# --------------------------------------------------------------------------------unit test for get_types_of_work function--------------------------------------------------------------------------------


def test_get_types_of_work():
    test_type_of_work = "Work Zone:roadway-relocation"
    expected = [{'is_architectural_change': True,
                 'type_name': 'roadway-relocation'}]
    actual = cotrip_translator.get_types_of_work(test_type_of_work)
    assert actual == expected


def test_get_types_of_work_none_type_of_work():
    test_type_of_work = None
    expected = []
    actual = cotrip_translator.get_types_of_work(test_type_of_work)
    assert actual == expected


def test_get_types_of_work_string_without_a_colon():
    test_type_of_work = "Work Zone roadway-relocation"
    expected = []
    actual = cotrip_translator.get_types_of_work(test_type_of_work)
    assert actual == expected


def test_get_types_of_work():
    test_type_of_work = "Work Zone:invalid"
    expected = []
    actual = cotrip_translator.get_types_of_work(test_type_of_work)
    assert actual == expected

# --------------------------------------------------------------------------------unit test for get_restrictions function--------------------------------------------------------------------------------


def test_get_restrictions():
    test_work_updates = [{
        "restrictions": [
            {
                "type": "Flagger Operations"
            }
        ]
    }]

    expected = []
    actual = cotrip_translator.get_restrictions(test_work_updates)

    assert actual == expected


def test_get_restrictions_none_work_updates():
    test_work_updates = None

    expected = []
    actual = cotrip_translator.get_restrictions(test_work_updates)
    assert actual == expected


def test_get_restrictions_empty_list():
    test_work_updates = []
    expected = []
    actual = cotrip_translator.get_restrictions(test_work_updates)
    assert actual == expected


def test_get_restrictions_invalid_list():
    test_work_updates = ["invalid", "data"]
    expected = []
    actual = cotrip_translator.get_restrictions(test_work_updates)
    assert actual == expected


def test_get_restrictions_valid():
    test_work_updates = [{
        "restrictions": [
            {
                "type": "travel-peak-hours-only"
            }
        ]
    }]

    expected = ['travel-peak-hours-only']
    actual = cotrip_translator.get_restrictions(test_work_updates)

    assert actual == expected


def test_get_restrictions_no_restriction():
    test_work_updates = [{
        "invalid": [
            {
                "type": "travel-peak-hours-only"
            }
        ]
    }]

    expected = []
    actual = cotrip_translator.get_restrictions(test_work_updates)

    assert actual == expected


def test_get_restrictions_empty_restriction():
    test_work_updates = [{
        "restrictions": []

    }]

    expected = []
    actual = cotrip_translator.get_restrictions(test_work_updates)

    assert actual == expected

# --------------------------------------------------------------------------------unit test for parse_reduced_speed_limit_from_description function--------------------------------------------------------------------------------


def test_parse_reduced_speed_limit_from_description():

    test_description = "&lt;a href=&quot; www.i25powers.com&quot;&gt;New Powers Blvd interchange under      construction. Work zone speed limit reduced to 65mph. Work adjacent to      highway and in median.&lt;/a&gt;"
    expected = '65'
    actual = cotrip_translator.parse_reduced_speed_limit_from_description(
        test_description)

    assert expected == actual


def test_parse_reduced_speed_limit_from_description_invalid():

    test_description = "This project consists of furnishing and installing CCTV cameras and communication equipment along three major locations: - I-70 between Tower Road and Bennett - I-25 south of 6th Avenue - Arapahoe Road and Revere Parkway  Work on this project will take place from Monday through Friday, from 7 a.m. to 4 p.m., and during construction motorists can expect traffic impacts that include reduced speed limits and lane closures."
    expected = None
    actual = cotrip_translator.parse_reduced_speed_limit_from_description(
        test_description)

    assert expected == actual


def test_parse_reduced_speed_limit_from_description_no_description():

    test_description = ""
    expected = None
    actual = cotrip_translator.parse_reduced_speed_limit_from_description(
        test_description)

    assert expected == actual

# --------------------------------------------------------------------------------unit test for get_rsz_from_event function--------------------------------------------------------------------------------


def test_get_rsz_from_event():
    test_event = {
        "header": {
            "description": "Bridge Construction - I-25 and Butte Creek at approximately MP 58.7, north of the Town of Walsenburg, Huerfano County",
        },
        "detail": {
            "description": "Replacement of bridges N-17-BN and N-17-S at I-25 and Butte Creek, as well as ancillary highway and drainage work to accommodate the new bridge structures.  Each bridge crosses over Butte Creek, as well as the frontage road Huerfano County Road 103.  Area inlets that are currently present in the median between the north and south bound lanes of I-25 will also be upgraded to accommodate the bridge and roadway improvements.",
            "work_updates": [{
                "description": "&lt;a href=&quot; www.i25powers.com&quot;&gt;New Powers Blvd interchange under      construction. Work zone speed limit reduced to 65mph. Work adjacent to      highway and in median.&lt;/a&gt;"

            }]
        }
    }

    expected = '65'

    actual = cotrip_translator.get_rsz_from_event(test_event)

    assert expected == actual


def test_get_rsz_from_event_invalid():
    test_event = {
        "header": {
            "description": "Bridge Construction - I-25 and Butte Creek at approximately MP 58.7, north of the Town of Walsenburg, Huerfano County",
        },
        "detail": {
            "description": "Replacement of bridges N-17-BN and N-17-S at I-25 and Butte Creek, as well as ancillary highway and drainage work to accommodate the new bridge structures.  Each bridge crosses over Butte Creek, as well as the frontage road Huerfano County Road 103.  Area inlets that are currently present in the median between the north and south bound lanes of I-25 will also be upgraded to accommodate the bridge and roadway improvements.",
            "work_updates": [{
                "description": "This project consists of furnishing and installing CCTV cameras and communication equipment along three major locations: - I-70 between Tower Road and Bennett - I-25 south of 6th Avenue - Arapahoe Road and Revere Parkway  Work on this project will take place from Monday through Friday, from 7 a.m. to 4 p.m., and during construction motorists can expect traffic impacts that include reduced speed limits and lane closures."
            }]
        }
    }

    expected = None

    actual = cotrip_translator.get_rsz_from_event(test_event)

    assert expected == actual


def test_get_rsz_from_event_empty_event():
    test_event = {}
    expected = None

    actual = cotrip_translator.get_rsz_from_event(test_event)

    assert expected == actual

from wzdx.raw_to_standard import icone


# --------------------------------------------------------------------------------Unit test for parse_polyline function--------------------------------------------------------------------------------
def test_parse_icone_polyline_valid_data():
    test_polyline = "34.8380671,-114.1450650,34.8380671,-114.1450650"
    test_coordinates = icone.parse_icone_polyline(
        test_polyline)
    valid_coordinates = [
        [
            -114.145065,
            34.8380671
        ],
        [
            -114.145065,
            34.8380671
        ]
    ]
    assert test_coordinates == valid_coordinates


def test_parse_polyline_null_parameter():
    test_polyline = None
    test_coordinates = icone.parse_icone_polyline(
        test_polyline)
    expected_coordinates = None
    assert test_coordinates == expected_coordinates


def test_parse_polyline_invalid_data():
    test_polyline = 'invalid'
    test_coordinates = icone.parse_icone_polyline(
        test_polyline)
    expected_coordinates = []
    assert test_coordinates == expected_coordinates


def test_parse_polyline_invalid_coordinates():
    test_polyline = 'a,b,c,d'
    test_coordinates = icone.wzdx_translator.parse_polyline(
        test_polyline)
    expected_coordinates = []
    assert test_coordinates == expected_coordinates


# --------------------------------------------------------------------------------Unit test for validate_incident function--------------------------------------------------------------------------------
def test_validate_incident_valid_data():
    test_valid_output = {
        '@id': 'U13631595_202012160845',
        'updatetime': '2020-12-16T17:18:00Z',
        'starttime': '2020-12-07T14:18:00Z',
        'description': 'Road constructions are going on',
        'creationtime': '2020-12-13T14:18:00Z',
        'location': {
            'polyline': '34.8380671,-114.1450650,34.8380671,-114.1450650',
            'street': 'I-70 N'
        }
    }
    assert icone.validate_incident(test_valid_output) == True


def test_validate_incident_missing_required_field_description():
    test_valid_output = {
        '@id': 'U13631595_202012160845',
        'updatetime': '2020-12-16T17:18:00Z',
        'starttime': '2020-12-07T14:18:00Z',
        'creationtime': '2020-12-13T14:18:00Z',
        'location': {
            'polyline': '34.8380671,-114.1450650,34.8380671,-114.1450650'
        }
    }
    assert icone.validate_incident(test_valid_output) == False


def test_validate_incident_invalid_start_time():
    test_valid_output = {
        '@id': 'U13631595_202012160845',
        'updatetime': '2020-12-16T17:18:00Z',
        'starttime': 'dsafsaf',
        'description': 'Road constructions are going on',
        'creationtime': '2020-12-13T14:18:00Z',
        'location': {
            'polyline': '34.8380671,-114.1450650,34.8380671,-114.1450650',
            'street': 'I-70 N'
        }
    }
    assert icone.validate_incident(test_valid_output) == False


def test_validate_incident_invalid():
    test_valid_output = 'invalid output'
    assert icone.validate_incident(test_valid_output) == False


def test_validate_incident_no_data():
    test_valid_output = None
    assert icone.validate_incident(test_valid_output) == False

from wzdx.monitoring.experimental import main


def test_compare_features():
    expected_diff = {}

    prod_feature = {
        "id": "6b646e79-1d50-5855-916a-f06e1af24900",
        "type": "Feature",
        "properties": {
            "core_details": {
              "event_type": "work-zone",
              "data_source_id": "c9a1044c-6518-4449-a93f-3954ffc55975",
              "road_names": ["US-550"],
              "direction": "northbound",
              "name": "OpenTMS-Event9834175545_northbound",
              "description": "Between County Road 24 (4 miles north of Ridgway) and County Road 2 (4 miles south of Colona) from Mile Point 109 to Mile Point 113. Paving operations. Alternating traffic. Starting May 5, 2023 at 7:00AM MDT until May 5, 2023 at about 7:00PM MDT.",
              "update_date": "2023-04-27T13:02:20Z"
            },
            "start_date": "2023-05-05T13:00:00Z",
            "end_date": "2023-05-06T01:00:00Z",
            "is_start_date_verified": False,
            "is_end_date_verified": False,
            "is_start_position_verified": False,
            "is_end_position_verified": False,
            "location_method": "channel-device-method",
            "work_zone_type": "static",
            "vehicle_impact": "all-lanes-open",
            "lanes": [{"order": 1, "type": "general", "status": "open"}],
            "beginning_cross_street": "County Road 24 (4 miles north of Ridgway)",
            "ending_cross_street": "County Road 2 (4 miles south of Colona)",
            "types_of_work": [{"type_name": "surface-work", "is_architectural_change": True}],
            "beginning_milepost": 113.0,
            "ending_milepost": 109.0
        },
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [-107.76452699899994, 38.270774138000036],
                [-107.76451915799998, 38.270761066000034],
                [-107.76353407499994, 38.26929077900007],
                [-107.76250378199995, 38.268196583000076],
                [-107.75996319699999, 38.265701222000075],
                [-107.75825543999997, 38.26354590900007],
                [-107.75725726399997, 38.26207989400007],
                [-107.75693063599999, 38.261138869000035],
                [-107.75685275599994, 38.25992015400004],
                [-107.75792796899998, 38.25353067700007],
                [-107.75858132799999, 38.250383353000075],
                [-107.75911637599995, 38.24850233500007],
                [-107.75925426699996, 38.24762412000007],
                [-107.75914922599998, 38.246867758000064],
                [-107.75882123299999, 38.24615979400005],
                [-107.75828017899994, 38.245551069000044],
                [-107.75708231399994, 38.24483012400003],
                [-107.755927139, 38.244529353000075],
                [-107.75074029099994, 38.24386022600004],
                [-107.74864881199994, 38.24334474500006],
                [-107.74694716599998, 38.24269452400006],
                [-107.74182768899999, 38.24032094300003],
                [-107.74004696799994, 38.23932664300003],
                [-107.73876402099995, 38.23825463700007],
                [-107.73602619399998, 38.23523739800004],
                [-107.73446450799997, 38.23401194200005],
                [-107.73131038699995, 38.232083396000064],
                [-107.73068569199995, 38.23157664200005],
                [-107.72958337299997, 38.23015195900007],
                [-107.72679233699995, 38.224772044000076],
                [-107.72679390199994, 38.223637127000075],
                [-107.72776237599999, 38.221720134000066],
                [-107.72816747399997, 38.220385185000055],
                [-107.72795128199999, 38.218591221000054]
            ]
        }
    }

    experimental_feature = {
        "id": "6b646e79-1d50-5855-916a-f06e1af24900",
        "type": "Feature",
        "properties": {
            "core_details": {
              "event_type": "work-zone",
              "data_source_id": "c9a1044c-6518-4449-a93f-3954ffc55975",
              "road_names": ["US-550"],
              "direction": "northbound",
              "name": "OpenTMS-Event9834175545_northbound",
              "description": "Between County Road 24 (4 miles north of Ridgway) and County Road 2 (4 miles south of Colona) from Mile Point 109 to Mile Point 113. Paving operations. Alternating traffic. Starting May 5, 2023 at 7:00AM MDT until May 5, 2023 at about 7:00PM MDT.",
              "update_date": "2023-04-27T13:02:20Z"
            },
            "start_date": "2023-05-05T13:00:00Z",
            "end_date": "2023-05-06T01:00:00Z",
            "is_start_date_verified": False,
            "is_end_date_verified": False,
            "is_start_position_verified": False,
            "is_end_position_verified": False,
            "location_method": "channel-device-method",
            "work_zone_type": "static",
            "vehicle_impact": "all-lanes-open",
            "lanes": [{"order": 1, "type": "general", "status": "open"}],
            "beginning_cross_street": "County Road 24 (4 miles north of Ridgway)",
            "ending_cross_street": "County Road 2 (4 miles south of Colona)",
            "types_of_work": [{"type_name": "surface-work", "is_architectural_change": True}],
            "beginning_milepost": 113.0,
            "ending_milepost": 109.0
        },
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [-107.76452699899994, 38.270774138000036],
                [-107.76451915799998, 38.270761066000034],
                [-107.76353407499994, 38.26929077900007],
                [-107.76250378199995, 38.268196583000076],
                [-107.75996319699999, 38.265701222000075],
                [-107.75825543999997, 38.26354590900007],
                [-107.75725726399997, 38.26207989400007],
                [-107.75693063599999, 38.261138869000035],
                [-107.75685275599994, 38.25992015400004],
                [-107.75792796899998, 38.25353067700007],
                [-107.75858132799999, 38.250383353000075],
                [-107.75911637599995, 38.24850233500007],
                [-107.75925426699996, 38.24762412000007],
                [-107.75914922599998, 38.246867758000064],
                [-107.75882123299999, 38.24615979400005],
                [-107.75828017899994, 38.245551069000044],
                [-107.75708231399994, 38.24483012400003],
                [-107.755927139, 38.244529353000075],
                [-107.75074029099994, 38.24386022600004],
                [-107.74864881199994, 38.24334474500006],
                [-107.74694716599998, 38.24269452400006],
                [-107.74182768899999, 38.24032094300003],
                [-107.74004696799994, 38.23932664300003],
                [-107.73876402099995, 38.23825463700007],
                [-107.73602619399998, 38.23523739800004],
                [-107.73446450799997, 38.23401194200005],
                [-107.73131038699995, 38.232083396000064],
                [-107.73068569199995, 38.23157664200005],
                [-107.72958337299997, 38.23015195900007],
                [-107.72679233699995, 38.224772044000076],
                [-107.72679390199994, 38.223637127000075],
                [-107.72776237599999, 38.221720134000066],
                [-107.72816747399997, 38.220385185000055],
                [-107.72795128199999, 38.218591221000054]
            ]
        }
    }

    actual_diff = main.compare_features(prod_feature, experimental_feature)

    assert actual_diff == expected_diff


def test_compare_features_invalid():
    expected_diff = {
        'properties/work_zone_type': {'prod': 'static', 'experimental': 'moving'},
        'properties/core_details/description': {'prod': 'Between County Road 24 (4 miles north of Ridgway) and County Road 2 (4 miles south of Colona) from Mile Point 109 to Mile Point 113. Paving operations. Alternating traffic. Starting May 5, 2023 at 7:00AM MDT until May 5, 2023 at about 7:00PM MDT.', 'experimental': 'Between County Road 24 (4 miles north of Ridgway) and County Road 2 (4 miles south of Colona) from Mile Point 109 to Mile Point 113. Paving operations. Alternating traffic. Starting May 5, 2023 at 7:00AM MDT until May 5, 2023 at about 7:00PM MDT. icone Message'},
        'properties/core_details/update_date': {'prod': '2023-04-27T13:02:20Z', 'experimental': '2023-04-27T14:02:20Z'},
        'properties/reduced_speed_limit_kph': {'prod': None, 'experimental': 40},
        'properties/start_date': {'prod': '2023-05-05T13:00:00Z', 'experimental': '2023-05-05T11:00:00Z'},
        'properties/end_date': {'prod': '2023-05-06T01:00:00Z', 'experimental': '2023-05-06T02:00:00Z'},
    }

    prod_feature = {
        "id": "6b646e79-1d50-5855-916a-f06e1af24900",
        "type": "Feature",
        "properties": {
            "core_details": {
              "event_type": "work-zone",
              "data_source_id": "c9a1044c-6518-4449-a93f-3954ffc55975",
              "road_names": ["US-550"],
              "direction": "northbound",
              "name": "OpenTMS-Event9834175545_northbound",
              "description": "Between County Road 24 (4 miles north of Ridgway) and County Road 2 (4 miles south of Colona) from Mile Point 109 to Mile Point 113. Paving operations. Alternating traffic. Starting May 5, 2023 at 7:00AM MDT until May 5, 2023 at about 7:00PM MDT.",
              "update_date": "2023-04-27T13:02:20Z"
            },
            "start_date": "2023-05-05T13:00:00Z",
            "end_date": "2023-05-06T01:00:00Z",
            "is_start_date_verified": False,
            "is_end_date_verified": False,
            "is_start_position_verified": False,
            "is_end_position_verified": False,
            "location_method": "channel-device-method",
            "work_zone_type": "static",
            "vehicle_impact": "all-lanes-open",
            "lanes": [{"order": 1, "type": "general", "status": "open"}],
            "beginning_cross_street": "County Road 24 (4 miles north of Ridgway)",
            "ending_cross_street": "County Road 2 (4 miles south of Colona)",
            "types_of_work": [{"type_name": "surface-work", "is_architectural_change": True}],
            "beginning_milepost": 113.0,
            "ending_milepost": 109.0
        },
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [-107.76452699899994, 38.270774138000036],
                [-107.76451915799998, 38.270761066000034],
                [-107.76353407499994, 38.26929077900007],
                [-107.76250378199995, 38.268196583000076],
                [-107.75996319699999, 38.265701222000075],
                [-107.75825543999997, 38.26354590900007],
                [-107.75725726399997, 38.26207989400007],
                [-107.75693063599999, 38.261138869000035],
                [-107.75685275599994, 38.25992015400004],
                [-107.75792796899998, 38.25353067700007],
                [-107.75858132799999, 38.250383353000075],
                [-107.75911637599995, 38.24850233500007],
                [-107.75925426699996, 38.24762412000007],
                [-107.75914922599998, 38.246867758000064],
                [-107.75882123299999, 38.24615979400005],
                [-107.75828017899994, 38.245551069000044],
                [-107.75708231399994, 38.24483012400003],
                [-107.755927139, 38.244529353000075],
                [-107.75074029099994, 38.24386022600004],
                [-107.74864881199994, 38.24334474500006],
                [-107.74694716599998, 38.24269452400006],
                [-107.74182768899999, 38.24032094300003],
                [-107.74004696799994, 38.23932664300003],
                [-107.73876402099995, 38.23825463700007],
                [-107.73602619399998, 38.23523739800004],
                [-107.73446450799997, 38.23401194200005],
                [-107.73131038699995, 38.232083396000064],
                [-107.73068569199995, 38.23157664200005],
                [-107.72958337299997, 38.23015195900007],
                [-107.72679233699995, 38.224772044000076],
                [-107.72679390199994, 38.223637127000075],
                [-107.72776237599999, 38.221720134000066],
                [-107.72816747399997, 38.220385185000055],
                [-107.72795128199999, 38.218591221000054]
            ]
        }
    }

    experimental_feature = {
        "id": "6b646e79-1d50-5855-916a-f06e1af24900",
        "type": "Feature",
        "properties": {
            "core_details": {
              "event_type": "work-zone",
              "data_source_id": "c9a1044c-6518-4449-a93f-3954ffc55975",
              "road_names": ["US-550"],
              "direction": "northbound",
              "name": "OpenTMS-Event9834175545_northbound",
              "description": "Between County Road 24 (4 miles north of Ridgway) and County Road 2 (4 miles south of Colona) from Mile Point 109 to Mile Point 113. Paving operations. Alternating traffic. Starting May 5, 2023 at 7:00AM MDT until May 5, 2023 at about 7:00PM MDT. icone Message",
              "update_date": "2023-04-27T14:02:20Z"
            },
            "start_date": "2023-05-05T11:00:00Z",
            "end_date": "2023-05-06T02:00:00Z",
            "is_start_date_verified": False,
            "is_end_date_verified": False,
            "is_start_position_verified": False,
            "is_end_position_verified": False,
            "location_method": "channel-device-method",
            "work_zone_type": "moving",
            "vehicle_impact": "all-lanes-open",
            "lanes": [{"order": 1, "type": "general", "status": "open"}],
            "beginning_cross_street": "County Road 24 (4 miles north of Ridgway)",
            "ending_cross_street": "County Road 2 (4 miles south of Colona)",
            "types_of_work": [{"type_name": "surface-work", "is_architectural_change": True}],
            "beginning_milepost": 113.0,
            "ending_milepost": 109.0,
            "reduced_speed_limit_kph": 40
        },
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [-107.76452699899994, 38.270774138000036],
                [-107.76451915799998, 38.270761066000034],
                [-107.76353407499994, 38.26929077900007],
                [-107.76250378199995, 38.268196583000076],
                [-107.75996319699999, 38.265701222000075],
                [-107.75825543999997, 38.26354590900007],
                [-107.75725726399997, 38.26207989400007],
                [-107.75693063599999, 38.261138869000035],
                [-107.75685275599994, 38.25992015400004],
                [-107.75792796899998, 38.25353067700007],
                [-107.75858132799999, 38.250383353000075],
                [-107.75911637599995, 38.24850233500007],
                [-107.75925426699996, 38.24762412000007],
                [-107.75914922599998, 38.246867758000064],
                [-107.75882123299999, 38.24615979400005],
                [-107.75828017899994, 38.245551069000044],
                [-107.75708231399994, 38.24483012400003],
                [-107.755927139, 38.244529353000075],
                [-107.75074029099994, 38.24386022600004],
                [-107.74864881199994, 38.24334474500006],
                [-107.74694716599998, 38.24269452400006],
                [-107.74182768899999, 38.24032094300003],
                [-107.74004696799994, 38.23932664300003],
                [-107.73876402099995, 38.23825463700007],
                [-107.73602619399998, 38.23523739800004],
                [-107.73446450799997, 38.23401194200005],
                [-107.73131038699995, 38.232083396000064],
                [-107.73068569199995, 38.23157664200005],
                [-107.72958337299997, 38.23015195900007],
                [-107.72679233699995, 38.224772044000076],
                [-107.72679390199994, 38.223637127000075],
                [-107.72776237599999, 38.221720134000066],
                [-107.72816747399997, 38.220385185000055],
                [-107.72795128199999, 38.218591221000054]
            ]
        }
    }

    actual_diff = main.compare_features(prod_feature, experimental_feature)

    assert actual_diff == expected_diff

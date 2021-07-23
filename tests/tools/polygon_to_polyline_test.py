from translator.tools import polygon_to_line


def test_polygon_to_polyline():
    coordinates = [[
        -105.02536913607729,
        39.7766424440161
    ],
        [
        -105.02503117774141,
        39.77663419842862
    ],
        [
        -105.0250819152026,
        39.771948514459645
    ],
        [
        -105.02539573365735,
        39.77195057599695
    ],
        [
        -105.02536913607729,
        39.7766424440161
    ]]
    polyline = polygon_to_line.polygon_to_polyline(coordinates)
    assert polyline != None

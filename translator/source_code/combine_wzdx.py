import json
import copy
from shapely.geometry.polygon import Polygon
from shapely.geometry import Point
import geopy
from geopy.distance import geodesic
import pyproj


def main():
    with open('combined_wzdx_message.geojson', 'w+') as f:
        wzdx_icone, wzdx_cotrip = wzdx_input()
        input = wzdx_cotrip['features'][0]['geometry']['coordinates']
        print(input)
        polygon = generate_polygon(input)
        feature = iterate_feature(polygon, wzdx_icone)
        if feature:
            f.write(json.dumps(combine_wzdx(
                wzdx_cotrip, wzdx_icone, feature), indent=2))


def generate_polygon(geometry):
    geodesic_pyproj = pyproj.Geod(ellps='WGS84')

    polygon_points = []
    polygon_left_points = []
    polygon_right_points = []

    box_width = 50

    for i in range(len(geometry)):
        if i == 0:
            p1 = geometry[i]
            p2 = geometry[i+1]
        else:
            p1 = geometry[i-1]
            p2 = geometry[i]

        fwd_azimuth, back_azimuth, distance = geodesic_pyproj.inv(
            p1[1], p1[0], p2[1], p2[0])

        print(fwd_azimuth)

        left = fwd_azimuth + 90
        right = fwd_azimuth - 90

        p1 = geometry[i]
        print(p1)
        origin = geopy.Point(p1[1], p1[0])
        left_point = geodesic(
            kilometers=box_width/1000).destination(origin, left)
        right_point = geodesic(
            kilometers=box_width/1000).destination(origin, right)

        polygon_left_points.append([left_point.latitude, left_point.longitude])
        polygon_right_points.append(
            [right_point.latitude, right_point.longitude])

    for i in polygon_left_points:
        polygon_points.append(i)

    for i in reversed(polygon_right_points):
        polygon_points.append(i)

    polygon_points.append(polygon_left_points[0])

    print(polygon_points)

    polygon = Polygon(polygon_points)
    return polygon


def isPointInPolygon(point, polygon):
    return polygon.contains(point)


def wzdx_input():
    icone_input = open(
        'translator/sample files/Output Message/icone_wzdx_translated.geojson', 'r').read()
    cotrip_input = open(
        'translator/sample files/Output Message/cotrip_wzdx_translated_output_message.geojson', 'r').read()
    return json.loads(icone_input), json.loads(cotrip_input)


def combine_wzdx(wzdx_cotrip, wzdx_icone, icone_feature):
    combined_wzdx = copy.deepcopy(wzdx_cotrip)
    combined_wzdx['features'][0]['properties']['vehicle_impact'] = icone_feature['properties']['vehicle_impact']
    combined_wzdx['road_event_feed_info']['data_sources'].append(
        wzdx_icone['road_event_feed_info']['data_sources'][0])

    return combined_wzdx


def iterate_feature(polygon, wzdx_message):
    for feature in wzdx_message['features']:
        for coord in feature['geometry']['coordinates']:
            if isPointInPolygon(Point(coord[1], coord[0]), polygon):
                return feature


if __name__ == "__main__":
    main()

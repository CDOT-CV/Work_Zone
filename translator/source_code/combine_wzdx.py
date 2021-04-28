import json
import copy
from shapely.geometry.polygon import Polygon
from shapely.geometry import Point
import geopy
from geopy.distance import geodesic
import pyproj


def main():
    with open('combined_wzdx_message.geojson', 'w+') as f:
        wzdx_icone = json.loads(open(
            'translator/sample files/Output Message/icone_wzdx_translated.geojson', 'r').read())
        wzdx_cotrip = json.loads(open(
            'translator/sample files/Output Message/cotrip_wzdx_translated_output_message.geojson', 'r').read())

        polygon = generate_polygon(
            wzdx_cotrip['features'][0]['geometry']['coordinates'])
        feature = iterate_feature(polygon, wzdx_icone)
        if feature:
            f.write(json.dumps(combine_wzdx(
                wzdx_cotrip, wzdx_icone, feature), indent=2))


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


# generate polygon from list of geometry ([[long, lat], ...])
def generate_polygon(geometry):
    geodesic_pyproj = pyproj.Geod(ellps='WGS84')

    # Initializing lists to create polygon
    polygon_left_points = []
    polygon_right_points = []

    # Width of generated path in meters (added to each side, so total width will be double this)
    box_width = 50

    for i in range(0, len(geometry)):
        # Set up points to calculate heading
        if i == 0:
            # first point, heading from first to second point
            p1 = geometry[i]
            p2 = geometry[i+1]
        else:
            # Not first point, heading from previous point to current point
            p1 = geometry[i-1]
            p2 = geometry[i]

        # Get forward heading between 2 points
        fwd_heading, _, __ = geodesic_pyproj.inv(
            p1[0], p1[1], p2[0], p2[1])

        # Get left and right vectors
        left = fwd_heading - 90
        right = fwd_heading + 90

        # Reset p1 to current point
        p1 = geometry[i]

        # get left and right points from direction and distance
        origin = geopy.Point(p1[1], p1[0])
        left_point = geodesic(meters=box_width).destination(origin, left)
        right_point = geodesic(meters=box_width).destination(origin, right)

        # Append points to left and right lists
        polygon_left_points.append([left_point.latitude, left_point.longitude])
        polygon_right_points.append(
            [right_point.latitude, right_point.longitude])

    # Create list of points in correct order (all left points, then all right points in reverese order)
    # This order is critical to prevent criss-crossing in the polygon
    polygon_points = []

    for i in polygon_left_points:
        polygon_points.append(i)

    for i in reversed(polygon_right_points):
        polygon_points.append(i)

    # Add first point again, to close polygon
    polygon_points.append(polygon_left_points[0])

    # Return generated polygon
    polygon = Polygon(polygon_points)
    return polygon


# Check if point is in polygon
def isPointInPolygon(point, polygon):
    return polygon.contains(point)


if __name__ == "__main__":
    main()

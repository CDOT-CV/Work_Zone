import math

import numpy as np
import pyproj


def angle_between_vectors_degrees(u, v):
    """Return the angle between two vectors in any dimension space,
    in degrees."""
    return np.degrees(
        math.acos(np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))))


def rotate(l, n):
    return l[-n:] + l[:-n]


coordinates = [
    [
        -105.15708984752104,
        39.62598162507104
    ],
    [
        -105.15091003795072,
        39.617386938794475
    ],
    [
        -105.1553732337515,
        39.60654288891114
    ],
    [
        -105.15181628653889,
        39.60601386741819
    ],
    [
        -105.1470097679842,
        39.61791587338656
    ],
    [
        -105.15370456168537,
        39.62796486262866
    ],
    [
        -105.15708984752104,
        39.62598162507104
    ]
]
print(coordinates)

coordinates = rotate(coordinates[:-1], 2)
coordinates.append(coordinates[0])
print(coordinates)

# angles = []
# geodesic = pyproj.Geod(ellps='WGS84')
# for i in range(len(coordinates) - 1):
#     i0 = i - 1
#     i1 = i
#     i2 = i + 1

#     if i == 0:
#         i0 = len(coordinates) - 2
#     elif i == len(coordinates) - 2:
#         i2 = 0

#     print(i0, i1, i2)
#     bearing_1, reverse_azimuth, distance = geodesic.inv(
#         coordinates[i1][0], coordinates[i1][1], coordinates[i0][0], coordinates[i0][1])
#     bearing_2, _, __ = geodesic.inv(
#         coordinates[i1][0], coordinates[i1][1], coordinates[i2][0], coordinates[i2][1])

#     angle = abs(bearing_1 - bearing_2)
#     if (angle > 180):
#         angle -= 180
#     # if (angle < -180):
#     #     angle += 180
#     angles.append(angle)
# print(angles)

corners = []
geodesic = pyproj.Geod(ellps='WGS84')
coordinates_padded = coordinates + coordinates[-3:]
print(len(coordinates_padded))
for i in range(len(coordinates_padded) - 4):
    i0 = i
    i1 = i + 1
    i2 = i + 2
    i3 = i + 3

    print(i0, i1, i2, i3)
    bearing_1, _, __ = geodesic.inv(
        coordinates_padded[i0][0], coordinates_padded[i0][1], coordinates_padded[i1][0], coordinates_padded[i1][1])
    bearing_2, _, __ = geodesic.inv(
        coordinates_padded[i1][0], coordinates_padded[i1][1], coordinates_padded[i2][0], coordinates_padded[i2][1])
    bearing_3, _, __ = geodesic.inv(
        coordinates_padded[i2][0], coordinates_padded[i2][1], coordinates_padded[i3][0], coordinates_padded[i3][1])
    if bearing_1 < 0:
        bearing_1 += 360
    if bearing_2 < 0:
        bearing_2 += 360
    if bearing_3 < 0:
        bearing_3 += 360
    print(bearing_1, bearing_2, bearing_3)

    angle_1 = bearing_1 - bearing_2
    angle_2 = bearing_2 - bearing_3
    print(angle_1, angle_2)

    net_angle = angle_1 + angle_2
    print(net_angle)
    if abs(net_angle - 180) < 50:
        corners.append([i1, i2, net_angle])
print(corners)


# for i in range(len(angles)):
#     i0 = i - 1
#     i1 = i
#     if i == 0:
#         i0 = len(angles) - 1

#     print(i0, i1)
#     print(angles[i0] + angles[i1])


# small_angles = []
# for i, angle in enumerate(angles):
#     if angle < 115:
#         small_angles.append([i, angle])

# if len(small_angles) != 4:
#     raise RuntimeError("Cannot convert polygon")


# for i, index in enumerate(small_angles):

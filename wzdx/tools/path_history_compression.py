import math
import logging
from wzdx.tools import polygon_tools

###
#   The following function computes lat and lon for a point distance "d" meters and bearing (heading)from an origin
#   with known lat1, lat2.
#
#   See https://www.movable-type.co.uk/scripts/latlong.html for more detail.
#
#   The function computes node point lat/lon for the adjacent lane's lane width (d) apart and 90 degree bearing
#   from the vehicle path data lane.
#
#   lat1    = Latitude of origin
#   lon1    = Longitude of origin
#   bearing = Destination direction in degree
#   dist    = Destination distance in km
###


def getEndPoint(lat1, lon1, bearing, d):
    R = 6371.0*1000  # Radius of the Earth in meters
    brng = math.radians(bearing)  # convert degrees to radians
    dist = d  # convert distance in meters
    lat1 = math.radians(lat1)  # Current lat point converted to radians
    lon1 = math.radians(lon1)  # Current long point converted to radians
    lat2 = math.asin(math.sin(lat1)*math.cos(d/R) +
                     math.cos(lat1)*math.sin(d/R)*math.cos(brng))
    lon2 = lon1 + math.atan2(math.sin(brng)*math.sin(d/R) *
                             math.cos(lat1), math.cos(d/R)-math.sin(lat1)*math.sin(lat2))
    lat2 = math.degrees(lat2)
    lon2 = math.degrees(lon2)
    return lat2, lon2

# ------------------------------------------------------------------------------------

###
#   Following function computes distance between two lat/lon points in meters...
#   Added on - 8-28-2017...
###


def getDist(origin, destination):
    lon1, lat1 = origin  # lon/lat of origin
    lon2, lat2 = destination  # lonlat of dest
    radius = 6371.0*1000  # meters

    dlat = math.radians(lat2-lat1)  # in radians
    dlon = math.radians(lon2-lon1)

    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d


def getChordLength(pt1, pt2):
    lon1 = math.radians(pt1[0])
    lat1 = math.radians(pt1[1])
    lon2 = math.radians(pt2[0])
    lat2 = math.radians(pt2[1])
    radius = 6371.0*1000  # meters
    try:
        # This line very occasionally fails, out of range exception for math.acos
        d = radius*math.acos(math.cos(lat1)*math.cos(lat2) *
                             math.cos(lon1-lon2) + math.sin(lat1)*math.sin(lat2))
    except:
        dlat = lat2-lat1  # in radians
        dlon = lon2-lon1

        a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
            * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        d = radius * c
    return d

# ------------------------------------------------------------------------------------


###
# Generate concise path history based on SAE J2945/1 2016-03, Section A.5
# Using Design Method One, section A.5.3.1
#
# path = [[long, lat], [long, lat], ...]
#
#
###


def generage_compressed_path(path):
    if len(path) <= 3:
        logging.error("Work zone is too short")
        return path

    ALLOWABLEERROR = 50
    SMALLDELTAPHI = 0.01
    CHORDLENGTHTHRESHOLD = 10000
    MAXESTIMATEDRADIUS = 8388607  # 7FFFFF

    PH_ConciseDataBuffer = []

    ###
    # Step 1
    ###
    i = 3
    Pstarting = path[i-2]
    Pprevious = path[i-1]
    Pnext = path[i]
    elementPos = 0
    totalDist = 0
    incrementDist = 0

    stopIndex = len(path) - 1

    PH_ConciseDataBuffer.append(path[i-3])
    PH_ConciseDataBuffer.append(path[i-2])
    elementPos += 1

    for i in range(i, len(path)):

        # Step 2
        eval = True
        actualChordLength = getChordLength(Pstarting, Pnext)
        if actualChordLength > CHORDLENGTHTHRESHOLD:
            actualError = ALLOWABLEERROR + 1
            eval = False
            # Go to step 7

    # Step 3
        heading_start = polygon_tools.get_heading_from_coordinates(
            [path[i-3], Pstarting])
        heading_next = polygon_tools.get_heading_from_coordinates(
            [Pprevious, Pnext])
        deltaHeadings = abs(heading_next - heading_start)
        if deltaHeadings > 180:
            deltaHeadings = 360 - deltaHeadings
        deltaHeadings = abs(math.radians(deltaHeadings))

    # Step 4
        if deltaHeadings < SMALLDELTAPHI and eval:
            actualError = 0
            estimatedRadius = MAXESTIMATEDRADIUS
            eval = False
            # Go to step 8
        elif eval:
            estimatedRadius = actualChordLength/(2*math.sin(deltaHeadings/2))

    # Step 5
        if eval:  # Allow step 4 to maintain 0 actualError
            d = estimatedRadius*math.cos(deltaHeadings/2)

    # Step 6
        if eval:  # Allow step 4 to maintain 0 actualError
            actualError = estimatedRadius - d

    # Step 7
        if actualError > ALLOWABLEERROR:
            incrementDist = actualChordLength
            totalDist += incrementDist
            PH_ConciseDataBuffer.append(path[i-1])

            Pstarting = path[i-1]
            Pprevious = path[i]
            if i < stopIndex:
                Pnext = path[i+1]
    # Step 8
        else:
            if i < stopIndex:
                Pnext = path[i+1]
            Pprevious = path[i]

        if i == stopIndex:
            incrementDist = actualChordLength
            totalDist += incrementDist
            PH_ConciseDataBuffer.append(path[i])

    # Step 9
        # Integrated into step 7
    return PH_ConciseDataBuffer

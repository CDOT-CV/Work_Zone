import math
import logging
from wzdx.tools import geospatial_tools


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

    ALLOWABLEERROR = 30
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
        heading_start = geospatial_tools.get_heading_from_coordinates(
            [path[i-3], Pstarting])
        heading_next = geospatial_tools.get_heading_from_coordinates(
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

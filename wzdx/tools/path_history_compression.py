import logging
import math

from ..tools import geospatial_tools


def getChordLength(pt1, pt2):
    lon1 = math.radians(pt1[0])
    lat1 = math.radians(pt1[1])
    lon2 = math.radians(pt2[0])
    lat2 = math.radians(pt2[1])
    radius = 6371.0 * 1000  # meters
    try:
        # This line very occasionally fails, out of range exception for math.acos
        d = radius * math.acos(
            math.cos(lat1) * math.cos(lat2) * math.cos(lon1 - lon2)
            + math.sin(lat1) * math.sin(lat2)
        )
    except:
        dLat = lat2 - lat1  # in radians
        dLon = lon2 - lon1

        a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(
            math.radians(lat1)
        ) * math.cos(math.radians(lat2)) * math.sin(dLon / 2) * math.sin(dLon / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
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
def generate_compressed_path(path):
    if len(path) <= 3:
        logging.error("Work zone is too short")
        return path

    ALLOWABLE_ERROR = 30
    SMALL_DELTA_PHI = 0.01
    CHORD_LENGTH_THRESHOLD = 10000
    MAX_ESTIMATED_RADIUS = 8388607  # 7FFFFF

    PH_ConciseDataBuffer = []

    ###
    # Step 1
    ###
    startIndex = 3
    pStarting = path[startIndex - 2]
    pPrevious = path[startIndex - 1]
    pNext = path[startIndex]
    elementPos = 0
    totalDist = 0
    incrementDist = 0

    stopIndex = len(path) - 1

    PH_ConciseDataBuffer.append(path[startIndex - 3])
    PH_ConciseDataBuffer.append(path[startIndex - 2])
    elementPos += 1

    for i in range(startIndex, len(path)):

        # Step 2
        eval = True
        actualChordLength = getChordLength(pStarting, pNext)
        if actualChordLength > CHORD_LENGTH_THRESHOLD:
            actualError = ALLOWABLE_ERROR + 1
            eval = False
            # Go to step 7

        # Step 3
        heading_start = geospatial_tools.get_heading_from_coordinates(
            [path[i - 3], pStarting]
        )
        heading_next = geospatial_tools.get_heading_from_coordinates([pPrevious, pNext])
        deltaHeadings = abs(heading_next - heading_start)
        if deltaHeadings > 180:
            deltaHeadings = 360 - deltaHeadings
        deltaHeadings = abs(math.radians(deltaHeadings))

        # Step 4
        if deltaHeadings < SMALL_DELTA_PHI and eval:
            actualError = 0
            estimatedRadius = MAX_ESTIMATED_RADIUS
            eval = False
            # Go to step 8
        elif eval:
            estimatedRadius = actualChordLength / (2 * math.sin(deltaHeadings / 2))

        # Step 5
        if eval:  # Allow step 4 to maintain 0 actualError
            d = estimatedRadius * math.cos(deltaHeadings / 2)

        # Step 6
        if eval:  # Allow step 4 to maintain 0 actualError
            actualError = estimatedRadius - d

        # Step 7
        if actualError > ALLOWABLE_ERROR:
            incrementDist = actualChordLength
            totalDist += incrementDist
            PH_ConciseDataBuffer.append(path[i - 1])

            pStarting = path[i - 1]
            pPrevious = path[i]
            if i < stopIndex:
                pNext = path[i + 1]
        # Step 8
        else:
            if i < stopIndex:
                pNext = path[i + 1]
            pPrevious = path[i]

        if i == stopIndex:
            incrementDist = actualChordLength
            totalDist += incrementDist
            PH_ConciseDataBuffer.append(path[i])

    # Step 9
    # Integrated into step 7
    return PH_ConciseDataBuffer

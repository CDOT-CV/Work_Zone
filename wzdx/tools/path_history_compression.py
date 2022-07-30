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


def getLanePt(laneType, path, mapPt, laneWidth, lanePad, refPtIdx, mapPtDist, laneStat, wpStat, dataLane, wzMapLen, speedList, dataFreq):

    ###
    #   Total number of lanes are in loc [0][0] in laneStat array
    ###
    if len(path) <= 3:
        logging.error("Work zone is too short")
        return None

    totDataPt = (len(list(path)))  # total data points (till end of array)
    tLanes = laneStat[0][0]  # total number of lanes...

    # Temporary list to store status of each node for each lane + WP state for the node
    lcwpStat = [0]*(tLanes+1)
    # 0 = no taper, 1 = taper-right, 2 = taper-left, 3=none, 4=either
    laneTaperStat = [0]*(tLanes)
    dL = dataLane - 1  # set lane number starting 0 as the left most lane
    distVec = 0
    stopIndex = 0
    startIndex = 0
    actualError = 0
    distFromLC = 0
    incrDistLC = False
    taperLength = speedList[0]*(laneWidth + lanePad)*3.28084
    currSpeedLimit = speedList[1]

    if speedList[0] <= 40:
        taperLength = ((laneWidth + lanePad)*3.28084*(speedList[0]**2)) / 60

    ALLOWABLEERROR = 1
    SMALLDELTAPHI = 0.01
    CHORDLENGTHTHRESHOLD = 500
    MAXESTIMATEDRADIUS = 8388607  # 7FFFFF
    if laneType == 1:
        if refPtIdx < 3:
            for i in range(0, refPtIdx):
                insertMapPt(mapPt, path, i, tLanes, laneWidth, dL,
                            lcwpStat, distVec, laneTaperStat, currSpeedLimit)
                distVec += path[i][0]/dataFreq
                # Rework to use actualChordLength
                return
        else:
            stopIndex = refPtIdx
    else:
        stopIndex = totDataPt
        startIndex = refPtIdx

    # Step 1
    i = startIndex + 2
    Pstarting = path[i-2]
    Pprevious = path[i-1]
    Pnext = path[i]
    totalDist = 0
    incrementDist = 0
    taperingLane = 0
    insertMapPt(mapPt, path, i-2, tLanes, laneWidth, dL,
                lcwpStat, distVec, laneTaperStat, currSpeedLimit)

    while i < stopIndex:
        # Step A
        requiredNode = False  # set to False
        if laneType == 2:  # WZ Lane
            # total number of lc/lo/wp are length of laneStat-1
            for lnStat in range(1, len(laneStat)):
                if laneStat[lnStat][0] == i-1:  # got LC/LO location
                    ln = laneStat[lnStat][1]-1
                    requiredNode = True  # set to True
                    if incrDistLC:  # other lane taper active, end other lane closure
                        laneTaperStat[taperingLane] = 0
                    incrDistLC = True
                    distFromLC = 0
                    taperingLane = ln
                    # get value from laneStat
                    lcwpStat[taperingLane] = laneStat[lnStat][2]
                    laneTaperVal = 3
                    if tLanes != 1:
                        if lcwpStat[ln] == 1:  # Lane closure
                            # Left lane, lane to right open
                            if ln == 0 and lcwpStat[1] == 0:
                                laneTaperVal = 1
                            # Right lane, lane to left open
                            elif ln == tLanes - 1 and lcwpStat[tLanes - 2] == 0:
                                laneTaperVal = 2
                            elif ln != 0 and ln != tLanes - 1:
                                leftLaneOpen = False
                                if lcwpStat[ln-1] == 0:
                                    leftLaneOpen = True
                                rightLaneOpen = False
                                if lcwpStat[ln+1] == 0:
                                    rightLaneOpen = True

                                if rightLaneOpen and leftLaneOpen:
                                    laneTaperVal = 4
                                elif leftLaneOpen:
                                    laneTaperVal = 2
                                elif rightLaneOpen:
                                    laneTaperVal = 1
                        else:
                            # Left lane, lane to right open
                            if ln == 0 and lcwpStat[1] == 0:
                                laneTaperVal = 2
                            # Right lane, lane to left open
                            elif ln == tLanes - 1 and lcwpStat[tLanes - 2] == 0:
                                laneTaperVal = 1
                            elif ln != 0 and ln != tLanes - 1:
                                leftLaneOpen = False
                                if lcwpStat[ln-1] == 0:
                                    leftLaneOpen = True
                                rightLaneOpen = False
                                if lcwpStat[ln+1] == 0:
                                    rightLaneOpen = True

                                if rightLaneOpen and leftLaneOpen:
                                    laneTaperVal = 4
                                elif leftLaneOpen:
                                    laneTaperVal = 1
                                elif rightLaneOpen:
                                    laneTaperVal = 2
                    laneTaperStat[taperingLane] = laneTaperVal

                    # laneTaperStat[laneStat[lnStat][1]-1] = 1       #get value from laneStat
                elif distFromLC >= taperLength:
                    requiredNode = True  # set to True
                    incrDistLC = False
                    distFromLC = 0
                    laneTaperStat[taperingLane] = 0  # get value from laneStat
                pass
            pass

            for wpZone in range(0, len(wpStat)):
                if wpStat[wpZone][0] == i-1:  # got WP Zone True/False
                    requiredNode = True  # set to True
                    # update WP Zone status
                    lcwpStat[tLanes] = wpStat[wpZone][1]
                    if wpStat[wpZone][1] == 1:
                        currSpeedLimit = speedList[2]
                    else:
                        currSpeedLimit = speedList[1]
                pass
            pass
        pass

    # Step 2
        eval = True
        actualChordLength = getChordLength(Pstarting, Pnext)
        if actualChordLength > CHORDLENGTHTHRESHOLD:
            actualError = ALLOWABLEERROR + 1
            eval = False
            # Go to step 7

    # Step 3
        deltaHeadings = abs(Pnext[4] - Pstarting[4])
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
        d = estimatedRadius*math.cos(deltaHeadings/2)

    # Step 6
        if eval:  # Allow step 4 to maintain 0 actualError
            actualError = estimatedRadius - d

    # Step 7
        if actualError > ALLOWABLEERROR or requiredNode:
            incrementDist = actualChordLength
            totalDist += incrementDist
            insertMapPt(mapPt, path, i-1, tLanes, laneWidth, dL,
                        lcwpStat, totalDist, laneTaperStat, currSpeedLimit)

            Pstarting = path[i-1]
            Pprevious = path[i]
            if i != stopIndex-1:
                Pnext = path[i+1]
            i += 1
    # Step 8
        else:
            if i != stopIndex-1:
                Pnext = path[i+1]
            Pprevious = path[i]
            i += 1

        if i == stopIndex:
            incrementDist = actualChordLength
            totalDist += incrementDist
            insertMapPt(mapPt, path, i-1, tLanes, laneWidth, dL,
                        lcwpStat, totalDist, laneTaperStat, currSpeedLimit)

        if incrDistLC:
            distFromLC += (path[i - 1][0] * 3.28084)/dataFreq
    # Step 9
        # Integrated into step 7

    if laneType == 1:
        wzMapLen[0] = totalDist
    else:
        wzMapLen[1] = totalDist

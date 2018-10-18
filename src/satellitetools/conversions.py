import utm, csv
from satellitetools.coordinates import WRSconvert as wrs

def utm2wrs(pointList, zone, hemisphere):

    wrsList = []
    conv = wrs.ConvertToWRS()
    for point in pointList:
        latlon = utm.to_latlon(point[0], point[1], zone, hemisphere)
        converted = conv.get_wrs(latlon[0], latlon[1])
        wrsList.append(converted)
    return wrsList

def getOptimalScene(sceneIDs):
    uniqueScenes = []
    for id in sceneIDs:
        for rowpath in id:
            if not uniqueScenes:
                uniqueScenes.append(rowpath)
            else:
                rowpathIsUnique = True
                for uniqueID in uniqueScenes:
                    if rowpath == uniqueID:
                        rowpathIsUnique = False
                if rowpathIsUnique:
                    uniqueScenes.append(rowpath)

    numcorners = len(sceneIDs)
    appearanceCount = [0 for i in range(len(uniqueScenes))]
    for id in sceneIDs:
        for rowpath in id:
            for i in range(len(uniqueScenes)):
                if rowpath == uniqueScenes[i]:
                    appearanceCount[i] = appearanceCount[i] + 1

    optimalScene = None
    for i in range(len(appearanceCount)):
        if appearanceCount[i] == numcorners:
            optimalScene = uniqueScenes[i]
    if optimalScene == None:
        sys.exit("Error: There is no scene containing all four corners and scene stitching is not implemented yet")
    return optimalScene

def getSceneIDfromCoords(ul_latlong, lr_latlong):

    ul = utm.from_latlon(ul_latlong[0], ul_latlong[1])
    lr = utm.from_latlon(lr_latlong[0], ul_latlong[1])

    # Infer other two corners
    ur = (lr[0],ul[1])
    ll = (ul[0],lr[1])

    if ul[2] == lr[2] and ul[3] == lr[3]:
        print('\n\n---> Converting specified corners from UTM to WRS')
        sceneIDs = utm2wrs([ul,ur,lr,ll],ul[2],ul[3])
        print('<--- Conversion complete')
    else:
        sys.exit("Error: Coordinates must be in same UTM zone")

    print('\n\n---> Searching for optimal scene')
    # See if there is a scene id that appears in all points
    # if there is not one, return an error
    optimalScene = getOptimalScene(sceneIDs)
    print('<--- Optimal scene found')

    # Convert to a string and return
    return str(optimalScene['path']).zfill(3)+str(optimalScene['row']).zfill(3)


def getSceneIDfromBathy(bathypath, zone, hemisphere='U'):
    (ul, lr) = findCornersInBathy(bathypath)

    # Infer other two corners
    ur = (lr[0],ul[1])
    ll = (ul[0],lr[1])

    print('\n\n---> Converting bathymetry corners from UTM to WRS')
    sceneIDs = utm2wrs([ul,ur,lr,ll],zone,hemisphere)
    print('<--- Conversion complete')

    print('\n\n---> Searching for optimal scene')
    optimalScene = getOptimalScene(sceneIDs)
    print('<--- Optimal scene found')

    # Convert to a string and return
    return str(optimalScene['path']).zfill(3)+str(optimalScene['row']).zfill(3)

def findCornersInBathy(bathypath):
    # Find boundaries from given data
    with open(bathypath, newline = '') as f:
        reader = csv.reader(f)

        #Skip header
        next(reader)

        #Initialize max & min
        l1 = next(reader)
        emax = float(l1[0])
        emin = float(l1[0])
        nmax = float(l1[1])
        nmin = float(l1[1])

        rowct = 1

        for row in reader:
            # Check for easting extrema
            E = float(row[0])
            if E > emax:
                emax = E
            elif E < emin:
                emin = E

            # Check for northing extrema
            N = float(row[1])
            if N > nmax:
                nmax = N
            elif N < nmin:
                nmin = N

            #Count number of rows
            rowct = rowct + 1

    # Add 10% buffer to edges
    emin = emin - 0.1 * (emax - emin)
    emax = emax + 0.1 * (emax - emin)

    nmin = nmin - 0.1 * (nmax - nmin)
    nmax = nmax + 0.1 * (nmax - nmin)

    subimageUL = (emin, nmax)
    subimageLR = (emax, nmin)

    return subimageUL, subimageLR

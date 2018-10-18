import os, sys, datetime, csv
import numpy as np
# from getpass import getpass
# from datetime import timedelta
# from PIL import Image as im
# import utm

def findValInMetadata(metadata, str):
    with open(metadata) as f:
        for line in f:
            if str in line:
                return(float(line.split()[2]))
                break
def getBathyMatrix(bathypath):
    # Load bathymetry data
    #bathydat = np.ndarray((rowct, 3))

    #bathydat = np.ndarray((3))
    with open(bathypath, newline = '') as f:
        reader = csv.reader(f)

        #Skip header
        next(reader)

        #initialize
        row1 = next(reader)
        bathydat = np.asarray([float(i) for i in row1])

        for row in reader:
            #bathydat[i,:] = np.asarray([float(i) for i in row])
            bathydat = np.dstack([bathydat, np.asarray([float(i) for i in row])])

    return bathydat

def getBandFileByDescription(sceneDirectory, description):
    for file in os.listdir(sceneDirectory):
        testDescription = getSingleBandDescription(file)
        if testDescription == description:
            return sceneDirectory + '/' + file

def getSingleBandDescription(bandfile):
    underscore = bandfile.rfind("_")
    dot = bandfile.rfind(".")
    bandname = bandfile[underscore + 1 : dot]

    return name2description(bandname)

def getAllBandDescriptions(sceneDirectory):
    bandFiles = list()
    for file in os.listdir(sceneDirectory):
        if file.endswith(".TIF"):
            bandFiles.append(file)

    #Find band names from bandFiles
    bandNames = list()
    for band in bandFiles:

        #Find relevant characters
        underscore = band.rfind("_")
        dot = band.rfind(".")

        #Extract name from end of file
        bandNames.append(band[underscore + 1 : dot])

    #Spatial Resolution Data
    spatRes = list()
    desc = list()
    for band in bandNames:
        desc.append(name2description(band))
        spatRes.append(name2resolution(band))

    return (desc, spatRes)

def getSceneDate(scene):
    year = datetime.date(year=int(scene[-12:-8]),month=1,day=1)
    daynum = datetime.timedelta(days=int(scene[-8:-5])-1)

    return year+daynum

def getNearestScene(sceneList, target):

    nearestScene = sceneList[0]
    daysToNearest = (getSceneDate(sceneList[0]) - target).days

    for scene in sceneList:

        daysToTarget = (getSceneDate(scene) - target).days

        if daysToTarget < daysToNearest:
            nearestScene = scene
            daysToNearest = daysToTarget

    return nearestScene

def sortScenes(scenes):
    # Get date and time from each scene
    dates = [getSceneDate(scene) for scene in scenes]

    ranks = [0 for x in range(len(dates))]
    for i in range(len(dates)):
        (r, s) = (1, 1)
        for j in range(len(dates)):
            if j != i and dates[j] < dates[i]:
                r += 1
            if j != i and dates[j] == dates[i]:
                s += 1

        # Use formula to obtain rank
        ranks[i] = r + (s - 1) / 2

    # Convert to integers and subtract 1
    ranks = [int(i-1) for i in ranks]

    # Sort folders
    scenesOrdered = [0 for i in range(len(ranks))]
    for i in range(len(ranks)):
        scenesOrdered[ranks[i]] = scenes[i]

    return scenesOrdered

def getBandFilePrefix(sceneDirectory):
    bandFiles = list()
    for file in os.listdir(sceneDirectory):
        if file.endswith(".TIF"):
            bandFiles.append(file)

    underscore = bandFiles[0].rfind("_")

    prefix = bandFiles[0][0:underscore]
    return prefix

def name2resolution(band):
    '''This function takes the name of the band (B1, B2, etc.) and returns
       the spatial resolution of that band as an integer
    '''
    if band == 'B1':
        return(30)
    elif band == 'B2':
        return(30)
    elif band == 'B3':
        return(30)
    elif band == 'B4':
        return(30)
    elif band == 'B5':
        return(30)
    elif band == 'B6':
        return(30)
    elif band == "B7":
        return(30)
    elif band == 'B8':
        return(15)
    elif band == 'B9':
        return(30)
    elif band == 'B10':
        return(100)
    elif band == 'B11':
        return(100)
    elif band == 'BQA':
        return(30)
    elif band == 'ANG':
        return(None)
    elif band == 'MTL':
        return(None)
    else:
        print( "BAND NAME NOT RECOGNIZED: ", band)
        sys.exit("Error: can't handle this type of file")

def name2description(band):
    '''This function takes the name of the band (B1, B2, etc.) and returns
       the description of that band as a string
    '''
    if band == 'B1':
        return("Coastal Aerosol")
    elif band == 'B2':
        return("Blue")
    elif band == 'B3':
        return("Green")
    elif band == 'B4':
        return("Red")
    elif band == 'B5':
        return("NIR")
    elif band == 'B6':
        return("SWIR 1")
    elif band == "B7":
        return("SWIR 2")
    elif band == 'B8':
        return("Panchromatic")
    elif band == 'B9':
        return("Cirrus")
    elif band == 'B10':
        return("TIRS 1")
    elif band == 'B11':
        return("TIRS 2")
    elif band == 'BQA':
        return("QA")
    elif band == 'ANG':
        return("SunAngle")
    elif band == 'MTL':
        return("Metadata")
    else:
        print( "BAND NAME NOT RECOGNIZED: ", band)
        sys.exit("Error: can't handle this type of file")

def description2name(name):
    '''This function takes the description of the band (red, blue, BQA) and returns
       the description of that band as a string
    '''
    if name == "Coastal Aerosol":
        return('B1')
    elif name == "Blue":
        return('B2')
    elif name == "Green":
        return('B3')
    elif name == "Red":
        return('B4')
    elif name == "NIR":
        return('B5')
    elif name == "SWIR 1":
        return('B6')
    elif name == "SWIR 2":
        return("B7")
    elif name == "Panchromatic":
        return('B8')
    elif name == "Cirrus":
        return('B9')
    elif name == "TIRS 1":
        return('B10')
    elif name == "TIRS 2":
        return('B11')
    elif name == "QA":
        return('BQA')
    elif name == "SunAngle":
        return('ANG')
    elif name == "Metadata":
        return('MTL')
    else:
        print( "BAND DESCRIPTION NOT RECOGNIZED: ", name)
        sys.exit("Error: can't handle this type of file")

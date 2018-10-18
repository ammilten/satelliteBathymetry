from satellitetools.dataretrieval import LSdownload as LS
from satellitetools.coordinates import WRSconvert as wrs
from satellitetools import helpers as utils
from satellitetools import retrieval
from satellitetools import bathymetry as B

import matplotlib
import matplotlib.animation as manimation
import matplotlib.pyplot as plt

import os, sys, utm
from PIL import Image as im
import numpy as np
from sklearn.neighbors import KNeighborsRegressor

from datetime import timedelta
from datetime import date

# from getpass import getpass
# import os
# import csv

class TSData:

    def __init__(self, scenes, subimageUL=None, subimageLR=None, bathyDataFile=None, bathydate=None, utmZone=None):

        '''Properties:
        REQUIRED
            scenes: List of directories containing satellite data
        OPTIONAL
            subimageUL: sub-image upper left coordinates in utm
            subimageLR: sub-image lower right coordinates in utm
            times: List of the datetimes corresponding to each directory in scenes
            bandnames: List of band names
            bathy: bathymetry data for this scene.
        '''
        self.scenes = scenes
        self.subimageLR = subimageLR
        self.subimageUL = subimageUL
        self.utmZone = utmZone
        self.bathy = bathyDataFile
        self.bathydate = bathydate


    def setSubImageManually(self, subimageUL, subimageLR, coords="utm"):
        if coords == "utm":
            self.subimageLR = subimageLR
            self.subimageUL = subimageUL
        elif coords == "latlon":
            ul = utm.from_latlon(subimageUL[0], subimageUL[1])
            lr = utm.from_latlon(subimageLR[0], subimageLR[1])
            self.subimageUL = (ul[0], ul[1])
            self.subimageLR = (lr[0], lr[1])


    def fitSubImageToBathyData(self, bathypath, keepData=False):
        '''
        bathypath is a path to the bathymetry data
        keepData is a logical that tells whether or not to assign the
            ImageData.bathy property. If the bathymetry data is large then keep
            this as False (the defualt)
        '''
        (ul,lr) = utils.findCornersInBathy(bathypath)

        self.subimageUL = ul
        self.subimageLR = lr

    def cropBand(self, imageFile):
        '''
        Crops the specified .TIF file to the subimage coordinates defined
        in this object. Returns a 2d numpy array with the data.
        '''

        # Get metadata using the same directory of imageFile
        slashpos = imageFile.rfind('/')
        sceneDirectory = imageFile[0:slashpos ]
        metadata = utils.getBandFileByDescription(sceneDirectory, 'Metadata')

        ule = utils.findValInMetadata(metadata, 'CORNER_UL_PROJECTION_X_PRODUCT')
        uln = utils.findValInMetadata(metadata, 'CORNER_UL_PROJECTION_Y_PRODUCT')

        lre = utils.findValInMetadata(metadata, 'CORNER_LR_PROJECTION_X_PRODUCT')
        lrn = utils.findValInMetadata(metadata, 'CORNER_LR_PROJECTION_Y_PRODUCT')

        # print('               | Easting | Northing')
        # print('Big Image UL   | ', ule, ' | ', uln)
        # print('Small Image UL | ', self.subimageUL[0], ' | ', self.subimageUL[1])
        # print('------------------------------------')
        # print('Big Image LR | ', lre, ' | ', lrn)
        # print('Small Image LR | ', self.subimageLR[0], ' | ', self.subimageLR[1])

        # Transform bathymetry box from UTM into px
        tlpxe = round((self.subimageUL[0] - ule) / 30)
        tlpxn = round((uln - self.subimageUL[1]) / 30)

        lrpxe = round((self.subimageLR[0] - ule) / 30)
        lrpxn = round((uln - self.subimageLR[1]) / 30)


        print('\nCropping', imageFile )
        print('This may take some time...')
        with im.open(imageFile) as largeImage:

            #Get pixel data and convert to numpy array
            pixels = list(largeImage.getdata())
            width, height = largeImage.size
            pixels = np.asarray([pixels[j*width : (j+1)*width] for j in range(height)])

            #Save data
            subImage = pixels[tlpxn:lrpxn, tlpxe:lrpxe]

        print('Success')

        return subImage

    def getImage(self, sceneDirectory, bands=['Red','Green','Blue']):
        band1File = utils.getBandFileByDescription(sceneDirectory, bands[0])
        band2File = utils.getBandFileByDescription(sceneDirectory, bands[1])
        band3File = utils.getBandFileByDescription(sceneDirectory, bands[2])

        print('\n\n---> Cropping Images:')
        r = self.cropBand(band1File)
        g = self.cropBand(band2File)
        b = self.cropBand(band3File)
        print('\n<--- Cropping complete')

        rgb = np.dstack((r,g,b)) / (np.power(2,16) - 1)

        return rgb

    def makemovie(self, destination, bands=['Red','Green','Blue']):
        print('\n=================== Creating Movie =====================')
        print('  Movie will be saved to',destination)
        print('========================================================')

        if self.subimageUL == None or self.subimageLR == None:
            sys.exit('\nError: Must have a sub-image defined otherwise the movie will be too large. Aborting.')

        slashpos = destination.rfind('/')
        movieName = destination[slashpos + 1:]
        if not movieName.endswith(".mp4"):
            sys.exit("Error: movie destination must end with *.mp4")

        #Order the scene directories by the time they occur
        scenesOrdered = utils.sortScenes(self.scenes)

        FFMpegWriter = manimation.writers['ffmpeg']
        metadata = dict(title='Movie Test', artist='Matplotlib',
                     comment='Movie support!')
        writer = FFMpegWriter(fps=5, metadata=metadata)

        fig = plt.figure()
        with writer.saving(fig, destination, 100):
            timestep = 1
            ntimesteps = len(scenesOrdered)
            for scene in scenesOrdered:
                print('\n\n---> Working on Time Step ', timestep, ' of ', ntimesteps)
                timestep = timestep + 1

                if scene == scenesOrdered[0]:
                    im = self.getImage(scenesOrdered[0], bands=bands)
                    l = plt.imshow(im)
                    date = utils.getSceneDate(scene)
                    plt.title(str(date))
                    writer.grab_frame()
                    print('\n<--- Saved frame',scene)
                else:
                    im = self.getImage(scene, bands)
                    l.set_data(im)
                    date = utils.getSceneDate(scene)
                    plt.title(str(date))
                    writer.grab_frame()
                    print('\n<--- Saved frame',scene)
        print('\n============= Successfully Created Movie ================')
        print('  Video is at ', destination)

    def getSubImageData(self, scene):
        '''
        ONLY gets bands that have a resolution of 30
        '''
        (desc, resolution) = utils.getAllBandDescriptions(scene)

        bandinds =  np.where(np.asarray(resolution) == 30)[0]

        prefix = utils.getBandFilePrefix(scene)
        bandfile = scene + '/' + prefix + '_' + utils.description2name(desc[int(bandinds[0])]) + '.TIF'
        subImage = self.cropBand(bandfile)

        for i in range(1, len(bandinds)):
            bandfile = scene + '/' + prefix + '_' + utils.description2name(desc[int(bandinds[i])]) + '.TIF'
            subImage = np.dstack([subImage, self.cropBand(bandfile)])

        return subImage

    def trainInverseModel(self, type='knn', k=5):

        bathysize = os.path.getsize(self.bathy) / 100000
        print('\n\n---> Loading bathymetry data from', self.bathy, ' (', bathysize , ' MB )')
        bathymetry = utils.getBathyMatrix(self.bathy)
        print('<--- Bathymetry data loaded')

        ## Assign bathymetry points to pixels
        pxe = np.rint((bathymetry[:,0] - self.subimageUL[0]) / 30)
        pxn = np.rint((self.subimageUL[1] - bathymetry[:,1]) / 30)

        ## Extract training data at all pixels
        nearestScene = utils.getNearestScene(self.scenes, self.bathydate)

        (desc, resolution) = utils.getAllBandDescriptions(nearestScene)

        bandinds =  np.where(np.asarray(resolution) == 30)[0]

        X = np.zeros((pxn.shape[1], bandinds.shape[0]))
        print('\n\n---> Preparing training data')
        for j in range(len(bandinds)):
            prefix = utils.getBandFilePrefix(nearestScene)
            bandfile = nearestScene + '/' + prefix + '_' + utils.description2name(desc[int(bandinds[j])]) + '.TIF'
            a = self.cropBand(bandfile)

            for i in range(pxn.shape[1]):
                X[i,j] = a[int(pxn[0,i]), int(pxe[0,i])]
        print('\n<--- Training data ready')

        print('\n\n---> Training model')
        model = KNeighborsRegressor(n_neighbors = k)
        model.fit(X, bathymetry[:,2].transpose())
        self.bathyInvModel = model
        print('<--- Model is ready')



    def predictBathymetry(self, datafolder, time=None, place=None):
        '''
        INPUTS:
            datafolder:
                Format: string
                Description: Path to the folder where you want to search for
                             and also save the satellite data you want to predict
                             bathymetry for

            time:
                Format: datetime.date object
                Description: The time of the scene that you want to predict

            place:
                Format: 2-tuple of 2-tuples
                Description: Contains the coordinates of the upper-left and
                             lower-right points of the image you want to predict,
                             respectively.
                             Example: ((latUL, lonUL), (latLR, lonLR))
        '''
        if time == None:
            time = self.bathydate
        if place == None:
            ULutm = utm.to_latlon(self.subimageUL[0], self.subimageUL[1], self.utmZone, 'U')
            LRutm = utm.to_latlon(self.subimageLR[0], self.subimageLR[1], self.utmZone, 'U')
            place = (ULutm, LRutm)

        # Step 1: find appropriate scene using the time and place
        # Step 2: Crop each band and store as a 3D array
        # Step 3: Use the trained model to make predictions

        print('\n\n---> Finding appropriate satellite data')
        searchDelta = timedelta(days=8)
        searchStart = time - searchDelta
        searchEnd = time + searchDelta

        print('Search Start: ', searchStart)
        print('Search End: ', searchEnd)
        targetscene = retrieval.fetchTSdata(place, searchStart, searchEnd, datafolder, type='latlon')
        print('\n<--- Found satellite data')

        print('\n\n---> Formatting prediction data')
        X = targetscene.getSubImageData(targetscene.scenes[0])
        print('\n<--- Prediction data ready')

        predictedBathymetry = self.bathyInvModel.predict(X.reshape(X.shape[0]*X.shape[1], X.shape[2]))
        predictionInfo = B.Bathymetry(predictedBathymetry.reshape(X.shape[0], X.shape[1]),
                                (targetscene.subimageUL, targetscene.subimageLR),
                                self.bathyInvModel,
                                utils.getSceneDate(targetscene.scenes[0]))
        print('<--- Prediction complete')
        return predictionInfo

    def plotSubImage(self, survey="off", date=None, bands=["Red", "Green", "Blue"]):
        # Step 1. find proper scene
        # Step 2. Feed proper scene to getImage
        # Step 3. Generate a matplotlib plot
        # Step 4 (optional). Overlay survey lines

        # Default date is the date of the bathymetry survey supplied
        if date == None:
            date = self.bathydate

        scene = utils.getNearestScene(self.scenes, date)

        im = self.getImage(scene, bands)

        (fig, ax) = plt.subplots()
        ax.imshow(im)
        fig.suptitle(date)

        if survey == "on":
            # 1. Load bathy data
            # 2. Convert to pixels
            # 3. Add pixels to plot
            bathysize = os.path.getsize(self.bathy) / 100000
            print('\n\n---> Loading bathymetry data from', self.bathy, ' (', bathysize , ' MB )')
            bathymetry = utils.getBathyMatrix(self.bathy)
            print('<--- Bathymetry data loaded')

            pxe = np.asarray([np.round((i - self.subimageUL[0]) / 30) for i in bathymetry[:,0]])
            pxn = np.asarray([np.round((self.subimageUL[1] - i) / 30) for i in bathymetry[:,1]])

            ax.scatter(pxe, im.shape[0]-pxn, s=5, c='k')

        return fig

from getpass import getpass
from datetime import timedelta
import os, sys, utm

from .timeseriesdata import TSData
from .conversions import getSceneIDfromCoords
from .conversions import getSceneIDfromBathy
from .conversions import findCornersInBathy

from satellitetools.dataretrieval import LSdownload as LS


def fetchTSdata(scene_data, start_date, end_date, datafolder, utm_zone=None, cloud_thresh_pct=100, type="scene"):

    '''
    Author: Alex Miltenberger, ammilten@stanford.edu

    This gigantic function downloads satellite data from USGS and saves it
    to a TSData object which is a memory-efficient way of storing the data
    needed to make movies and perform analysis of time-series satellite images.

    INPUTS:
        scene_data:
            Format: string, OR 2-tuple of 2-tuples, OR path to bathymetry
            If using string option: Must be 6 characters representing the WRS
                                    row and path of a Landsat scene. "type"
                                    keyword arg MUST be set to "scene".
            If using tuple option:  Tuple must contain the Upper-Left and
                                    Lower-Right coordinates of the small image
                                    you are interested in, in that order. MUST
                                    be lat-long format and "type" keyword arg
                                    MUST be set to "latlon"
            If using path option:   Must be a string representing a path to a
                                    '*.csv' file containing bathymetry data.
                                    "type" MUST be set to "bathy"

        start_date:
            Format: datetime.date object containing earliest date of interest.

        end_date:
            Format: datetime.date object containing latest date of interest.

        datafolder:
            Format: string containing path where you want the downloaded data
                    to be stored.
        utm_zone:
            Format: Integer representing the UTM zone that the bathymetry data
                    is in. Only required for type='bathy'

        cloud_thresh_pct:
            Format: Float between 0 and 100. Used to remove cloudy images above
                    this threshold.

        type:
            Format: string with three options right now. Must be "scene",
                    "latlon", or "bathy", depending on the type of input into
                    the first arg.
    OUTPUTS:
        TSData object containing the following fields:

        ALWAYS SET:
            TSData.scenes: list of directories representing individual satellite scenes
        OPTIONAL:
            TSData.subimageUL: 2-tuple of UTM coordinates (easting, northing)
                               for Upper-Left corner of small image. Only set by
                               this function if type="latlon". Lat-Lon is first
                               converted to UTM and then stored.
            TSData.subimageLR: 2-tuple of UTM coordinates (easting, northing)
                               for Lower-Right corner of small image. Only set by
                               this function if type="latlon". Lat-Lon is first
                               converted to UTM and then stored.
            TSData.bathy:      String containing bath to bathymetry file. Only
                               set if type="bathy"
    '''

    bathypath = None
    UL = None
    LR = None
    if type == "latlon":
        scene = getSceneIDfromCoords(scene_data[0], scene_data[1])
        UL = utm.from_latlon(scene_data[0][0], scene_data[0][1])
        LR = utm.from_latlon(scene_data[1][0], scene_data[1][1])
        utm_zone = UL[2]
        UL = (UL[0], UL[1])
        LR = (LR[0], LR[1])
    elif type == "bathy":
        scene = getSceneIDfromBathy(scene_data, utm_zone)
        bathypath = scene_data
        (UL, LR) = findCornersInBathy(bathypath)
    elif type == "scene":
        scene = scene_data
        utm_zone = None
    else:
        sys.exit("Error: cannot determine Landsat scene ID from input")

    # Prompt for user name and password
    username = input('\n\nUSGS Username (email): ')
    p = getpass(prompt='USGS Password: ')

    if not os.path.exists(datafolder):
        os.mkdir(datafolder)

    produit='LC8'
    path=scene[0:3]
    row=scene[3:6]

    global downloaded_ids
    downloaded_ids=[]

    print('\n\n---> Connecting to USGS EarthExplorer')
    LS.connect_earthexplorer(username, p)
    print('<--- Connected')

    # rep_scene="%s/SCENES/%s_%s/GZ"%(datafolder,path,row)   #Original
    rep_scene="%s"%(datafolder)    #Modified vbnunes
    if not(os.path.exists(rep_scene)):
        os.makedirs(rep_scene)
    if produit.startswith('LC8'):
        repert='12864'
        stations=['LGN']
    if produit.startswith('LE7'):
        repert='12267'
        stations=['EDC','SGS','AGS','ASN','SG1','CUB','COA']
    if produit.startswith('LT5'):
        repert='12266'
        stations=['GLC','ASA','KIR','MOR','KHC', 'PAC', 'KIS', 'CHM', 'LGS', 'MGR', 'COA', 'MPS', 'CUB','JSA']

    check=1
    curr_date=LS.next_overpass(start_date,int(path),produit)

    print('\n\n---> Searching for satellite data')
    while (curr_date < end_date):
        date_asc=curr_date.strftime("%Y%j")
        notfound = False
        print( '\nSearching for images on (julian date): ' + date_asc + '...')
        curr_date=curr_date+timedelta(16)
        for station in stations:
            for version in ['00','01','02']:
                nom_prod=produit+scene+date_asc+station+version
                tgzfile=os.path.join(rep_scene,nom_prod+'.tgz')
                lsdestdir=os.path.join(rep_scene,nom_prod)
                url="https://earthexplorer.usgs.gov/download/%s/%s/STANDARD/EE"%(repert,nom_prod)
                print( url)
                if os.path.exists(lsdestdir):
                    print( '   product %s already downloaded and unzipped'%nom_prod)
                    downloaded_ids.append(nom_prod)
                    check = 0
                elif os.path.isfile(tgzfile):
                    print( '   product %s already downloaded'%nom_prod)

                    p=LS.unzipimage(nom_prod,rep_scene)
                    if p==1:
                        check=LS.check_cloud_limit(lsdestdir,cloud_thresh_pct)
                        if check==0:
                            downloaded_ids.append(nom_prod)
                else:
                    try:
                        LS.downloadChunks(url,"%s"%rep_scene,nom_prod+'.tgz')
                    except:
                        print( '   product %s not found'%nom_prod)
                        notfound = True
                    if notfound != True :
                        p = LS.unzipimage(nom_prod,rep_scene)
                        if p==1:
                            print(lsdestdir)
                            check=LS.check_cloud_limit(lsdestdir,cloud_thresh_pct)
                            if check==0:
                                downloaded_ids.append(nom_prod)

    LS.log(datafolder,downloaded_ids)
    print('\n<--- Data retrieval complete')

    ## Prepare ImageData object for return
    # Specify folders in this date range
    sceneDirectories = []
    for id in downloaded_ids:
        sceneDirectories.append(datafolder + '/' + id)

    return TSData(scenes=sceneDirectories, subimageUL=UL, subimageLR=LR, bathyDataFile=bathypath, utmZone=utm_zone)

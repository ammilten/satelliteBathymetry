import sys
from os.path import dirname
sys.path.append(dirname('/home/ammilten/Programs/bathy/v1/src/satellitetools'))

import satellitetools as st
from datetime import datetime

# Parameters
startdate = datetime(year=2014, month=1, day=1)
enddate = datetime(year=2015, month=1, day=1)
datafolder = '/home/ammilten/Programs/bathy/data/MontereyBaySatDat'
bathydata = '/home/ammilten/Programs/bathy/data/usgsMontereyBayData/usgsMontereyBay14Oct.csv'
zone = 10

# Download time-series data using bathymetry data
TS = st.retrieval.fetchTSdata(bathydata, startdate, enddate, datafolder, bathyzone_utm=zone, type="bathy")

# Put together the movie
moviePath = datafolder + '/movie.mp4'
TS.makemovie(moviePath)

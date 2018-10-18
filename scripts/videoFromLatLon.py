
import sys
from os.path import dirname
sys.path.append(dirname('/home/ammilten/Programs/bathy/v1/src/satellitetools'))

import satellitetools as st
from datetime import datetime

# Parameters
startdate = datetime(year=2013, month=6, day=1)
enddate = datetime(year=2013, month=8, day=1)
datafolder = '/home/ammilten/Programs/bathy/data/Miami'
ul_latlong = (25.931612, -80.215620)
lr_latlong = (25.751580, -80.097708)

# Download time-series data using specified coordinates
TS = st.retrieval.fetchTSdata((ul_latlong, lr_latlong), startdate, enddate, datafolder, type="latlon")

# Put together the movie
moviePath = datafolder + '/Biscayne.mp4'
TS.makemovie(moviePath)

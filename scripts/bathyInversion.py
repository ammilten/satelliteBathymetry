import sys
from os.path import dirname
sys.path.append(dirname('/home/ammilten/Programs/bathy/v1/src/satellitetools'))

import satellitetools as st
from datetime import date

# Parameters
startdate = date(year=2017, month=9, day=1)
enddate = date(year=2017, month=11, day=1)
datafolder = '/home/ammilten/Programs/bathy/data/MagothyBay'
bathydata = '/home/ammilten/Programs/bathy/data/pointsMagothyBathymetry2017.csv'
zone = 18

# Download time-series data using bathymetry data
TS = st.retrieval.fetchTSdata(bathydata, startdate, enddate, datafolder, utm_zone=zone, type="bathy")
TS.bathydate = date(year=2017, month=10, day=14)

# Perform inversion
TS.trainInverseModel()
MontereyBayBathymetry = TS.predictBathymetry(datafolder)

# Display
map = TS.plotSubImage(survey='on')
map.show()
input()

bmap = MontereyBayBathymetry.plotBathymetry()
bmap.show()
input()

# bathy
Map changes in bathymetry over time using satellite imagery

## Current State:
### 10/4/2018
Changed the functions from a software format to a library format. By that I mean there is no longer a `main.py` script. You can find examples of how to use the library in the `scripts/` directory. 

The goal of this development is to make an easy-to-use library for fetching and processing satellite imagery, specifically for bathymetry inversions. The library should make for easy-to-read scripts that perform the data analysis. 

Currently the library can only download the data from the USGS website and make a basic RGB movie from it. There are several different options for defining the subsection to make a movie of. 

In the near future I will be adding bathymetry inversion, prediction, and analysis tools. After that I forsee adding other image processing tools specifically tailored for satellite imagery and time-series data. 

# How to use
1. Clone the master branch to your local machine.
2. Set up dependencies. Make sure everything is set up for python3 and not python2. See the `dependecies` script.
3. Try running one of the example scripts, probably the `videoFromLatLon.py` script using the command `python3 videoFromLatLon.py`. It may take quite a while to do the downloading and making the movie. 

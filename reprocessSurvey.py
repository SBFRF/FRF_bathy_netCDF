g# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 16:30:08 2020

@author: sb
"""
import glob, os
from surveyToNetCDF import convertText2NetCDF
import datetime as DT
# location to look for files
surveyArchiveLocation = "/mnt/gaia/Survey/DATA/archive/"
#prefix for file output name
surveyOutPrefix = "/data/fdif/FRF/survey/gridded"
surveyOutPrefix = '.'
raise NotImplementedError, "need to check how to handle versions"
# find list of files to re-rpocess
flist = sorted(glob.glob(surveyArchiveLocation+'*.csv'))
# loop through each file in a list
for f in flist:
    #extension = f.split('.')[-1]   # keep file extension
    # generate new file version number
    newVnum = '_v'+DT.datetime.today().strftime("%Y%m%d")+'.nc'
    # generate base files name
    filenameBase = "_".join(os.path.basename(flist[0]).split('_')[:-1])+newVnum
    # generate output filename and path
    outFname = os.path.join(surveyOutPrefix, filenameBase )
    # reprocess



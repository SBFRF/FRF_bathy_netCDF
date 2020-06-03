"""This file converts netCDF using a path and globbing on it for both transect and grids
can be run from terminal
"""
import sys, getopt, os
import makenc, glob
import netCDF4 as nc
import numpy as np
import sblib as sb
import py2netCDF as p2nc
import datetime as DT
from surveyToNetCDF import fillFRFgridTemplate
from surveyToNetCDF import preprocessGridFile

def convertText2NetCDF(globPath):
    """This function searches the given path for both grids and transect files present at the FRF to make the data into
    netCDF files.
    
    the below yaml's have to be in the same folder as the
    
    :param globPath: a path to find the yaml files and the data
    :return:
    
    """
    ## INPUTS
    yamlPath = 'yamlFiles/'
    gridGlobalYaml = yamlPath + 'grid_Global.yml'  # grid Global yaml
    gridVarYaml = yamlPath + 'grid_variables.yml'  # grid yaml location
    transectGlobalYaml = yamlPath + 'transect_Global.yml'
    transectVarYaml = yamlPath + 'transect_variables.yml'

    gridList = glob.glob(os.path.join(globPath, 'FRF_*latlon.txt')) # searching for grid files
    filelist = glob.glob(os.path.join(globPath, 'FRF_*.csv')) # searching for transect Files

    logFile = os.path.join(globPath, 'Bathy_LOG.log')

    errorFname, errors = [],[]
    # creating a list of transect files to look for
    print('Converting %d Transect (csv) file(s) to netCDF ' % len(filelist))
    for transectFname in filelist:
        try:
            Tofname = transectFname[:-3] + 'nc'
            print('  <II> Making %s ' % Tofname)
            # first make transect
            TransectDict = sb.import_FRF_Transect(transectFname)  # import frf Transect product
            TransectDict['time'] = nc.date2num(TransectDict['time'], 'seconds since 1970-01-01')
            makenc.makenc_FRFTransect(bathyDict=TransectDict, ofname=Tofname, globalYaml=transectGlobalYaml, varYaml=transectVarYaml)
        except Exception as e:
            print(e)
            errors.append(e)
            errorFname.append(transectFname)

    print('Converting %d Grid (txt) file to netCDF ' % len(gridList))
    for gridFname in gridList:
        try:
            # load text file
            outDict = sb.importFRFgrid(gridFname)
            
            outDict, date = preprocessGridFile(outDict, gridFname)
            ofname = 'FRF_geomorphology_DEMs_surveyDEM_{}.nc'.format(date)
            print('  <II> Making %s ' %ofname)
            p2nc.makenc_generic(ofname, gridGlobalYaml, gridVarYaml, data=outDict)

        except Exception as e:
            print(e)
            errors.append(e)
            errorFname.append(gridFname)

    # log errors
    # log errors that were encountered during file creation
    f = open(logFile, 'w+')  # opening file
    f.write('File, Error\n')  # writing headers
    for aa in range(0, len(errorFname)):  # looping through errors
            f.write('%s,\n %s\n----------------------------\n\n' %(errorFname[aa], errors[aa]))
    f.close()

if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
    #  Location of where to look for files to convert
    if len(args) is 0:
        globPath = '.'
    else:
        globPath = args[0]

    convertText2NetCDF(globPath)
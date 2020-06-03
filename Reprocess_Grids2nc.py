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
            # read the file name parts
            split = os.path.basename(gridFname).split('_')
            # assign what I can
            outDict['surveyNumber'] = int(split[2])
            
            split = os.path.basename(gridFname).split('_')
            # assign what I can
            outDict['surveyNumber'] = int(split[2])
            # process data into background data size and shape (with fill values)

            #check to make sure that xFRF and yFRF are in total dataset.
            outDict['xFRF'], outDict['yFRF'], outDict['longitude'], outDict['latitutde'], \
            outDict['elevation'] = fillFRFgridTemplate(xFRF=np.unique(outDict['raw_x']),
                                                       yFRF=np.unique(outDict['raw_y']),
                                                       elev=outDict['raw_z'])
            # now parse platform
            if split[5].lower() == 'crab':
                outDict['surveyPlatform'] = 0
            elif split[5].lower() == 'larc':
                outDict['surveyPlatform'] = 1
            else:
                raise AttributeError('do not understand survey platform')
            # now parse instrumentation
            if split[6].lower() == 'level':
                outDict['instrumentation'] = 0
            elif split[6].lower() == 'zeiss':
                outDict['instrumentation'] = 1
            elif split[6].lower() == 'geodimeter':
                outDict['instrumentation'] = 2
            elif split[6].lower() == 'gps':
                outDict['instrumentation'] = 3
            else:
                raise AttributeError('do not understand instrumentation')
            
            #now parse version date
            outDict['version'] = nc.date2num(DT.datetime.strptime(split[8], 'v%Y%m%d'), 'seconds since 1970-01-01')
            outDict['time'] = nc.date2num(DT.datetime.strptime(split[1], '%Y%m%d'), 'seconds since 1970-01-01')

            # now parse project name
            outDict['project'] = "{:16s}".format(str(split[3]))

            ofname = 'FRF_geomorphology_DEMs_surveyDEM_{}.nc'.format(split[1])
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
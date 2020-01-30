import sys, getopt, os
sys.path.append('/home/spike/CMTB/')
import makenc, glob, time
from matplotlib import pyplot as plt
import netCDF4 as nc
import numpy as np
import sblib as sb

def convertText2NetCDF(fnameIn, fnameOut=None):
    """
    This function searches the given path for both grids and transect files present at the FRF to make the data into
    netCDF files
    the below yaml's have to be in the same folder as the
    
    :param fnameIn: a path to find the yaml files and the data
    :return:
    """
    yamlPath = 'yamlFiles/'
    gridGlobalYaml = yamlPath + 'grid_Global.yml'  # grid Global yaml
    gridVarYaml = yamlPath + 'grid_variables.yml'  # grid yaml location
    transectGlobalYaml = yamlPath + 'transect_Global.yml'
    transectVarYaml = yamlPath + 'transect_variables.yml'    
    
    ## INPUTS  - rename
    if fnameIn.split('.')[-1] in ['txt', "txt'"]:
        filelist = []
        gridList = [fnameIn]  
    elif fnameIn.split('.')[-1] in ["csv'", 'csv']:
        filelist = [fnameIn]
        gridList = []
    else:
        filelist = []
        gridList = []
        print '<<ERROR>> No Files To Convert to NetCDF'
        
    logFile = fnameIn[:-4].split('/')[-1]+ 'BathyNetCDFConversion.log'
    errorFname, errors = [],[]

    # creating a list of transect files to look for
    for transectFname in filelist:
        try:
            if fnameOut is None:
                Tofname = transectFname.split('.')[0] + '.nc'
            elif fnameOut.endswith('.nc'):
                Tofname = fnameOut 
            else: 
                Tofname = fnameOut + ".nc"
            print '  <II> Making %s ' % Tofname
            # first make transect
            TransectDict = sb.import_FRF_Transect(transectFname)
            TransectDict['time'] = nc.date2num(TransectDict['time'], 'seconds since 1970-01-01')  # turn data points into epoch time
            # now generate a date only 
            TransectDict['date'] = [time.mktime(TransectDict['date'][ii].timetuple()) for ii in range(TransectDict['date'].shape[0])]
            makenc.makenc_FRFTransect(bathyDict=TransectDict, ofname=Tofname,
                                      globalYaml=transectGlobalYaml, varYaml=transectVarYaml)
        except Exception, e:
            print e
            errors.append(e)
            errorFname.append(transectFname)
    # looping through grids in grid List
    for gridFname in gridList:
        try:
            ofname = gridFname.split('.')[0] + '.nc'
            print '  <II> Making %s ' %ofname
            makenc.convert_FRFgrid(gridFname, ofname, gridGlobalYaml, gridVarYaml, plotFlag=False)

        except Exception, e:
            print e
            errors.append(e)
            errorFname.append(gridFname)

    # log errors
    # log errors that were encountered during file creation
    if len(errors) > 0:
        if not os.path.exists('logs'):
            os.makedirs('logs')
        f = open('logs/' + logFile, 'w')  # opening file
        f.write('File, Error\n')  # writing headers
        for aa in range(0, len(errorFname)):  # looping through errors
            f.write('%s,\n %s\n----------------------------\n\n' %(errorFname[aa], errors[aa]))
        f.close()

if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
    
    #  Location of where to look for files to convert
    #globPath = args[0]
    #if globPath.startswith("'") and globPath.endswith("'"):
    #    globPath = globPath[1:-1]
    fname = args[0]
    convertText2NetCDF(fname)
    
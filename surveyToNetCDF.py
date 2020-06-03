"""This file converts netCDF using specific file name inputs for both transect and grids
can be run from terminal
"""
import sys, getopt, os
import geoprocess as gp
import makenc, time
import netCDF4 as nc
import sblib as sb
import py2netCDF as p2nc
import datetime as DT
import numpy as np

def convertText2NetCDF(fnameIn):
    """This function searches the given path for both grids and transect files present at the FRF to make the data into
    netCDF files.
    

    the below yaml's have to be in the same folder as the
    
    :param fnameIn: a path to find the yaml files and the data
    :return:
    """
    ## INPUTS
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
        print('<<ERROR>> No Files To Convert to NetCDF')
        
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

def fillFRFgridTemplate(xFRF, yFRF, elev, **kwargs):
    """ Function will take place this grid into the larger FRF template grid initalized by keyword arguments
    
    Args:
        xFRF: 1d array of xFRF values in grid (non-unique)
        yFRF: 1d array of yFRF values in grid (non-unique)
        elev: 1d array of elevation values in grid
        **kwargs: modify the background grid size for FRF template (not recommended as this can affect TDS
        concatenation)
        
    Keyword Args:
        'gridYmax':  maximum FRF Y distance for netCDF file (default=1100)
        'gridYmin':  minimum FRF Y distance for netCDF file (default=-100)
        'gridXmax':  maximum FRF X distance for netCDF file (default=950)
        'gridXmin':  minimum FRF xdistance for netCDF file (default=50)
        
    Returns:
        2D arrays that match size of previous files for xFRF, yFRF, lon, lat, Elevation with fill values surrounding
        the output from this particular input dataset (survey)
        
    """
    # netCDF standardized format for FRF grid
    gridYmax = kwargs.get('gridYmax',  1100)  # maximum FRF Y distance for netCDF file
    gridYmin = kwargs.get('gridYmin', -100)   # minimum FRF Y distance for netCDF file
    gridXmax = kwargs.get('gridXmax', 950)    # maximum FRF X distance for netCDF file
    gridXmin = kwargs.get('grixXmin', 50)     # minimum FRF xdistance for netCDF file
    fill_value = '-999'
    
    # parse input parameters
    dx = np.median(np.diff(xFRF))                                                       # get grid resolution in x
    dy = np.max(np.diff(yFRF))                                                          # get grid resolution in y
    xgrid = np.unique(xFRF)                                                             # create singular xGrid values
    ygrid = np.unique(yFRF)                                                             # create singular yGrid values
    zgrid = np.reshape(elev, (ygrid.shape[0], xgrid.shape[0]))                          # add time dimension
    
    # initalize netCDF output grid based on
    ncXFRF = np.linspace(gridXmin, gridXmax, num=(gridXmax - gridXmin) / dx + 1, endpoint=True)
    ncYFRF = np.linspace(gridYmin, gridYmax, num=(gridYmax - gridYmin) / dy + 1, endpoint=True)
    ncElevation = np.full((1, np.shape(ncYFRF)[0], np.shape(ncXFRF)[0]), fill_value=fill_value, dtype=np.float64)
    
    # find the overlap locations between input grid and the nodes used for the netCDF file
    xOverlap = np.intersect1d(xgrid, ncXFRF)
    yOverlap = np.intersect1d(ygrid, ncYFRF)
    assert len(yOverlap) >= 3, 'The overlap between grid nodes and netCDF grid nodes is short'
    
    lastX = np.argwhere(ncXFRF == xOverlap[-1]).squeeze()  # these are indicies of the max overlap
    firstX = np.argwhere(ncXFRF == xOverlap[0]).squeeze()  # these are indicies of the min overlap
    lastY = np.argwhere(ncYFRF == yOverlap[-1]).squeeze()  # these are indices of the max overlap between the two grids
    firstY = np.argwhere(ncYFRF == yOverlap[0]).squeeze()  # these are indices of the min overlap between the two grids
    
    # fill the frame grid with the loaded data
    ncElevation[0, firstY:lastY+1, firstX:lastX+1] = zgrid
    
    # run data check
    assert set(xOverlap).issubset(ncXFRF), 'The FRF X values in your function do not fit into the netCDF format, please rectify'
    assert set(yOverlap).issubset(ncYFRF), 'The FRF Y values in your function do not fit into the netCDF format, please rectify'
    
    # convert lon/lat from template x/y FRF
    lonOut, latOut = [], []
    xx, yy = np.meshgrid(ncXFRF, ncYFRF)
    for val in zip(xx.flatten(), yy.flatten()):
        coords = gp.FRFcoord(val[0], val[1])
        lonOut.append(coords['Lon'])
        latOut.append(coords['Lat'])
    
    lonOut = np.reshape(lonOut, (ncYFRF.shape[0], ncXFRF.shape[0]))
    latOut = np.reshape(latOut, (ncYFRF.shape[0], ncXFRF.shape[0]))
    
    return ncXFRF, ncYFRF, lonOut, latOut, ncElevation

if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
    
    #  Location of where to look for files to convert
    globPath = args[0]
    if globPath.startswith("'") and globPath.endswith("'"):
        globPath = globPath[1:-1]
    convertText2NetCDF(globPath)



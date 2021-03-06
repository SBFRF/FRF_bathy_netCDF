"""
Created on 2/19/2016
This script is desinged to create netCDF files using the netCDF4 module from python as
part of the Coastal Model Test Bed (CMTB)

@author: Spicer Bak
@contact: Spicer.Bak@usace.army.mil
"""

import numpy as np
import netCDF4 as nc
import csv
import datetime as DT
import yaml
import time as ttime
import sblib as sb


def readflags(flagfname, header=1):
    """
    This function reads the flag file from the data in to the STWAVE CMTB runs
    :param flagfname: the relative/absolute location of the flags file
    :return: flags of data dtype=dictionary
    """
    times = []
    waveflag = []
    windflag = []
    WLflag = []
    curflag = []
    allflags = []
    with open(flagfname, 'rb') as f:
        reader = csv.reader(f)  # opening file
        for row in reader:  # iteratin

            # g over the open file
            if len(row) > 1 and row[0] != 'Date':
                waveflag.append(int(row[2]))  # appending wave data flag
                windflag.append(int(row[3]))  # appending Wind data flag
                WLflag.append(int(row[4]))  # appending Water Level Flag data
                curflag.append(int(row[5]))  # appending ocean Currents flag data
                times.append(DT.datetime.strptime(row[0]+row[1], '%Y-%m-%d%H%M'))
                allflags.append([int(row[2]), int(row[3]), int(row[4]), int(row[5])])
    # creating array of flags
    allflags = np.array(allflags)

    # putting data into a dictionary
    flags = {'time': times,
             'windflag': windflag,
             'waveflag': waveflag,
             'WLflag': WLflag,
             'curflag': curflag,
             'allflags': allflags
             }
    return flags

def checkflags(flags, ):
    """
    This function is here to ensure that the flags are of equal length as the time
    :param flags:
    :return:
    """

def import_template_file(yaml_location):
    """
    This function loads a yaml file and returns the attributes in dictionary
    written by: ASA
    :param yaml_location: yaml file location
    :return:
    """
    # load the template
    f = open(yaml_location)
    # use safe_load instead load
    vars_dict = yaml.safe_load(f)
    f.close()
    return vars_dict

def init_nc_file(nc_filename, attributes):
    """
    Create the netCDF file and write the Global Attributes
    written by ASA
    """

    ncfile = nc.Dataset(nc_filename, 'w')

    # Write some Global Attributes
    for key, value in attributes.items():
        # Skip and empty fields or this will bomb
        #print 'key %s; value %s' %( key, value)
        if value is not None:
            setattr(ncfile, key, value)
        #if key == 'geospatial_lat_min':
        #    lat = float(value)
        #if key == 'geospatial_lon_min':
        #    lon = float(value)

    dt_today = ttime.strftime("%Y-%m-%d")
    ncfile.date_created = dt_today
    ncfile.date_issued = dt_today

    # ID is a unique identifier for the file
    # ncfile.id = os.path.split(nc_filename)[1].split('.nc')[0]

    # ncfile.qcstage = '3'
    # ncfile.qcstage_possible_values = '0, 1, 2, 3'
    # ncfile.qcstage_value_meanings = 'None, Processed_R/T, Post-Processed, Final'

    #return ncfile, lat, lon
    return ncfile

def write_data_to_nc(ncfile, template_vars, data_dict, write_vars='_variables'):
    '''
    This function actually writes the variables and the variable attributes to
    the netCDF file
    ncfile is an open fid

    written by: ASA
    in the yaml, the "[variable]:" needs to be in the data dictionary,
     the output netcdf variable will take the name "name:"
    '''

    # Keep track of any errors found
    num_errors = 0
    error_str = ''

    # write some more global attributes if present
    if '_attributes' in template_vars:
        for var in template_vars['_attributes']:
            if var in data_dict:
                setattr(ncfile, var, data_dict[var])

    # List all possible variable attributes in the template
    possible_var_attr = ['standard_name', 'long_name', 'coordinates', 'flag_values', 'flag_meanings',
                         'positive', 'valid_min', 'valid_max', 'calendar', 'description', 'cf_role', 'missing_value']

    # Write variables to file
    accept_vars = template_vars['_variables']

    for var in accept_vars:
        if var in data_dict:
            try:
                if "fill_value" in template_vars[var]:
                    new_var = ncfile.createVariable(template_vars[var]["name"],
                                                    template_vars[var]["data_type"],
                                                    template_vars[var]["dim"],
                                                    fill_value=template_vars[var]["fill_value"])
                else:
                    new_var = ncfile.createVariable(template_vars[var]["name"],
                                                    template_vars[var]["data_type"],
                                                    template_vars[var]["dim"])

                new_var.units = template_vars[var]["units"]

                # Write the attributes
                for attr in possible_var_attr:
                    if attr in template_vars[var]:
                        if template_vars[var][attr] == 'NaN':
                            setattr(new_var, attr, np.nan)
                        else:
                            setattr(new_var, attr, template_vars[var][attr])
                # Write the short_name attribute as the variable name
                if 'short_name' in template_vars[var]:
                    new_var.short_name = template_vars[var]["short_name"]
                else:
                    new_var.short_name = template_vars[var]["name"]
                # _____________________________________________________________________________________
                # Write the data (1D, 2D, or 3D)
                #______________________________________________________________________________________
                if var == "station_name":
                    station_id = data_dict[var]
                    data = np.empty((1,), 'S'+repr(len(station_id)))
                    data[0] = station_id
                    new_var[:] = nc.stringtochar(data)
                elif len(template_vars[var]["dim"]) == 0:
                    try:
                        new_var[:] = data_dict[var]
                    except Exception as e:
                        new_var = data_dict[var]

                elif len(template_vars[var]["dim"]) == 1:
                    # catch some possible errors for frequency and direction arrays
                    if template_vars[var]["data_type"] == 'str':
                        for i, c in enumerate(template_vars[var]["data_type"]):
                            new_var[i] = data_dict[var][i]
                    else:
                        try:
                            new_var[:] = data_dict[var]
                        except IndexError:
                            try:
                                new_var[:] = data_dict[var][0][0]
                            except Exception as e:
                                raise e

                elif len(template_vars[var]["dim"]) == 2:
                    # create an empty 2d data set of the correct sizes
                    try:
                        # handles row vs col data, rather than transposing the array just figure out which it is
                        length = data_dict[var][0].shape[1]
                        if data_dict[var][0].shape[0] > length:
                            length = data_dict[var][0].shape[0]

                        x = np.empty([data_dict[var].shape[0], length], np.float64)
                        for i in range(data_dict[var].shape[0]):
                            # squeeze the 3d array in to 2d as dimension is not needed
                            x[i] = np.squeeze(data_dict[var][i])
                        new_var[:, :] = x
                    except Exception as e:
                        # if the tuple fails must be right...right?
                        new_var[:] = data_dict[var]

                elif len(template_vars[var]["dim"]) == 3:
                    # create an empty 3d data set of the correct sizes
                    # this portion was modified by Spicer Bak
                    assert data_dict[var].shape == new_var.shape, 'The data must have the Same Dimensions  (missing time?)'
                    x = np.empty([data_dict[var].shape[0], data_dict[var].shape[1], data_dict[var].shape[2]], np.float64)
                    for i in range(data_dict[var].shape[0]):
                        x[i] = data_dict[var][i]
                    new_var[:, :, :] = x[:, :, :]

            except Exception as e:
                num_errors += 1
                error_str += 'ERROR WRITING VARIABLE: ' + var + ' - ' + str(e) + '\n'
                print(error_str)

    return num_errors, error_str


def makenc_field(data_lib, globalyaml_fname, flagfname, ofname, griddata, var_yaml_fname):
    """
    This is a function that takes wave nest dictionary and Tp_nest dictionnary and creates the high resolution
    near shore field data from the Coastal Model Test Bed


    :param data_lib:  data lib is a library of data with keys the same name as associated variables to be written in the
                    netCDF file to be created
    :param globalyaml_fname:
    :param flagfname:
    :param ofname: the file name to be created
    :param griddata:
    :param var_yaml_fname:
    :return:
    """

    # import global atts
    globalatts = import_template_file(globalyaml_fname)
    # import variable data and meta
    var_atts = import_template_file(var_yaml_fname)
    # import flag data
    flags = readflags(flagfname)['allflags']
    data_lib['flags'] = flags
    globalatts['grid_dx'] = griddata['dx']
    globalatts['grid_dy'] = griddata['dy']
    globalatts['n_cell_y'] = griddata['NJ']
    globalatts['n_cell_x'] = griddata['NI']
    # making bathymetry the length of time so it can be concatnated
    if data_lib['waveHsField'].shape[1] != data_lib['bathymetry'].shape[1]:
        data_lib['waveHsField']=data_lib['waveHsField'][:,:data_lib['bathymetry'].shape[1],:]
    data_lib['bathymetry'] = np.full_like(data_lib['waveHsField'], data_lib['bathymetry'], dtype=np.float32 )
    if 'bathymetryDate' in data_lib:
        data_lib['bathymetryDate'] = np.full_like(data_lib['time'], data_lib['bathymetryDate'], dtype=np.float32 )


    #data_lib['bathymetry'] =
    fid = init_nc_file(ofname, globalatts)  # initialize and write inital globals

    #### create dimensions
    tdim = fid.createDimension('time', np.shape(data_lib['waveHsField'])[0])
    xdim = fid.createDimension('X_shore', np.shape(data_lib['waveHsField'])[1])
    ydim = fid.createDimension('Y_shore', np.shape(data_lib['waveHsField'])[2])
    inputtypes = fid.createDimension('in_type', np.shape(flags)[1]) # there are 4 input dtaa types for flags
    statnamelen = fid.createDimension('station_name_length', len(data_lib['station_name']))
    #if 'bathymetryDate' in data_lib:
    #    bathyDate_length = fid.createDimension('bathyDate_length', np.shape(data_lib['bathymetry'])[0])

    # bathydate = fid.createDimension('bathyDate_length', np.size(data_lib['bathymetryDate']))

    # write data to the nc file
    write_data_to_nc(fid, var_atts, data_lib)
    # close file
    fid.close()

def makenc_FRFTransect(bathyDict, ofname, globalYaml, varYaml):
    """
    This function makes netCDF files from csv Transect data library created with sblib.load_FRF_transect

    :
    :return:
    """
    globalAtts = import_template_file(globalYaml)  # loading global meta data attributes from  yaml
    varAtts = import_template_file(varYaml)  # loading variables to write and associated meta data

    # initializing output ncfile
    fid =init_nc_file(ofname, globalAtts)

    # creating dimensions of data
    tdim = fid.createDimension('time', np.shape(bathyDict['time'])[0])

    # write data to the ncfile
    write_data_to_nc(fid, varAtts, bathyDict)
    # close file
    fid.close()

def makenc_FRFGrid(gridDict, ofname, globalYaml, varYaml):
    """
    This is a function that makes netCDF files from the FRF Natural neighbor tool created by
    Spicer Bak using the pyngl library. the transect dictionary is created using the natural
    neighbor tool in FRF_natneighbor.py

    :param tranDict:
    :param ofname:
    :param globalYaml:
    :param varYaml:
    :return: netCDF file with gridded data in it
    """
    globalAtts = import_template_file(globalYaml)
    varAtts = import_template_file(varYaml)

    # create netcdf file
    fid = init_nc_file(ofname, globalAtts)

    # creating dimensions of data
    xFRF = fid.createDimension('xFRF', np.shape(gridDict['xFRF'])[0])
    yFRF = fid.createDimension('yFRF', np.shape(gridDict['yFRF'])[0])
    time = fid.createDimension('time', np.size(gridDict['time']))

    # write data to file
    write_data_to_nc(fid, varAtts, gridDict)
    # close file
    fid.close()

def makenc_Station(stat_data, globalyaml_fname, flagfname, ofname, griddata, stat_yaml_fname):
    """

    This function will make netCDF files from the station output data from the
    Coastal Model Test Bed of STWAVE for the STATion files

    :param stat_data:
    :param globalyaml_fname:
    :param flagfname:
    :param ofname:
    :param griddata:
    :param stat_yaml_fname:

    :return: a nc file with station data in it
    """
     # import global yaml data
    globalatts = import_template_file(globalyaml_fname)
    # import variable data and meta
    stat_var_atts = import_template_file(stat_yaml_fname)
    # import flag data
    flags = readflags(flagfname)['allflags']
    stat_data['flags'] = flags # this is a library of flags
    globalatts['grid_dx'] = griddata['dx']
    globalatts['grid_dy'] = griddata['dy']
    globalatts['n_cell_y'] = griddata['NJ']
    globalatts['n_cell_x'] = griddata['NI']
    fid = init_nc_file(ofname, globalatts)  # initialize and write inital globals

    #### create dimensions
    tdim = fid.createDimension('time', np.shape(stat_data['time'])[0])  #
    inputtypes = fid.createDimension('input_types_length', np.shape(flags)[1])  # there are 4 input data types for flags
    statnamelen = fid.createDimension('station_name_length', len(stat_data['station_name']))
    northing = fid.createDimension('Northing', 1)
    easting = fid.createDimension('Easting', 1 )
    Lon = fid.createDimension('Lon', np.size(stat_data['Lon']))
    Lat = fid.createDimension('Lat', np.size(stat_data['Lat']))
    dirbin = fid.createDimension('waveDirectionBins', np.size(stat_data['waveDirectionBins']))
    frqbin = fid.createDimension('waveFrequency', np.size(stat_data['waveFrequency']))
    
    #
    # convert to Lat/lon here

    # write data to the nc file
    write_data_to_nc(fid, stat_var_atts, stat_data)
    # close file
    fid.close()

def convert_FRFgrid(xyz, ofname, globalYaml, varYaml, plotFlag=False):
    """
    This function will convert the FRF gridded text product into a NetCDF file

    :param gridFname: xyz data from sb.loadgrid
    :param ofname:  output netcdf filename
    :param globalYaml: a yaml file containing global meta data
    :param varYaml:  a yaml file containing variable meta data
    :return: None
    """
    # Defining rigid parameters of the FRF grid
    # defining the bounds of the FRF gridded product
    gridYmax = 1100  # maximum FRF Y distance for netCDF file
    gridYmin = -100  # minimum FRF Y distance for netCDF file
    gridXmax = 950   # maximum FRF X distance for netCDF file
    gridXmin = 50    # minimum FRF xdistance for netCDF file
    fill_value = '-999'
    # main body
    # load Grid from file

    
    # make dictionary in right form
    dx = np.median(np.diff(xyz['x']))
    dy = np.max(np.diff(xyz['y']))
    xgrid = np.unique(xyz['x'])
    ygrid = np.unique(xyz['y'])

    # putting the loaded grid into a 2D array
    zgrid = np.zeros((len(xgrid), len(ygrid)))
    rc = 0
    for i in range(np.size(ygrid, axis=0)):
        for j in range(np.size(xgrid, axis=0)):
            zgrid[j, i] = xyz['z'][rc]
            rc += 1
    if plotFlag == True:
        from matplotlib import pyplot as plt
        plt.pcolor(xgrid, ygrid, zgrid.T)
        plt.colorbar()
        plt.title('FRF GRID %s' % ofname[:-3].split('/')[-1])
        plt.savefig(ofname[:-4] + '_RawGridTxt.png')
        plt.close()
    # making labels in FRF coords for the netCDF grid
    ncXcoord = np.linspace(gridXmin, gridXmax, num=(gridXmax - gridXmin) / dx + 1, endpoint=True)
    ncYcoord = np.linspace(gridYmin, gridYmax, num=(gridYmax - gridYmin) / dy + 1, endpoint=True)
    frame = np.full((np.shape(ncXcoord)[0], np.shape(ncYcoord)[0]), fill_value=fill_value, dtype=np.float64)

    # find the overlap locations between text file grid and the nodes used for the netCDF file
    xOverlap = np.intersect1d(xgrid, ncXcoord)
    yOverlap = np.intersect1d(ygrid, ncYcoord)
    assert len(yOverlap) >= 3, 'The overlap between grid nodes and netCDF grid nodes is short'
    
    lastX = np.argwhere(ncXcoord == xOverlap[-1])[0][0]  # these are indicies of the max overlap
    firstX = np.argwhere(ncXcoord == xOverlap[0])[0][0]  # these are indicies of the min overlap
    lastY = np.argwhere(ncYcoord == yOverlap[-1])[0][0]  # these are indices of the max overlap between the two grids
    firstY = np.argwhere(ncYcoord == yOverlap[0])[0][0]  # these are indices of the min overlap between the two grids

    # fill the frame grid with the loaded data
    frame[firstX:lastX+1, firstY:lastY+1] = zgrid

    # run data check
    assert set(xOverlap).issubset(ncXcoord), 'The FRF X values in your function do not fit into the netCDF format, please rectify'
    assert set(yOverlap).issubset(ncYcoord), 'The FRF Y values in your function do not fit into the netCDF format, please rectify'


    collectionTypes = ['GPS', 'Geodimeter', 'Zeiss', 'Level']
    surveyVehicles = ['CRAB', 'LARC']
    # Parse MetaData from Filename
    fields = gridFname.split('_')
    for fld in fields:
        if len(fld) == 8:  # survey Date
            try:  # tr
                int(fld)  # try to convert it to a number incase one of the other fields are 8 char long
                time = nc.date2num(DT.datetime.strptime(fld, '%Y%m%d'), 'seconds since 1970-01-01')
                # break was here when only time was of interest
            except ValueError:
                continue
        elif len(fld) == 4 and fld in surveyVehicles:  # survey vehicles
            if fld == 'CRAB':
                surveyVehicle = 0
            elif fld == 'LARC':
                surveyVehicle = 1
        elif len(fld) == 4:  # survey Number
            try:
                surveyNumber = int(fld)
            except ValueError:
                continue
        elif fld == 'NAVD88':  # survey Datum
            datum = fld
        elif fld in collectionTypes:  # identifying collection method
            if fld == 'Level':
                surveyInstrumentation = 0
            elif fld == 'Zeiss':
                surveyInstrumentation = 1
            elif fld == 'Geodimeter':
                surveyInstrumentation = 2
            elif fld == 'GPS':
                surveyInstrumentation = 3
        elif fld[0] == 'v':  # version number
            versionDate = fld
    # wrapping up data into dictionary for output
    gridDict = {'zgrid': frame.T,
                'xgrid': ncXcoord,
                'ygrid': ncYcoord,
                'time': time,
                'surveyVehicle': surveyVehicle,
                'surveyNumber': surveyNumber,
                'surveyInstrumentation': surveyInstrumentation,
                'datum': datum,
                'versionDate': versionDate,
                'project': fields[3]
                }
    # creating lat/lon and state plane coords
    # xgrid, ygrid = np.meshgrid(gridDict['xgrid'], gridDict['ygrid'])
    xx, yy = np.meshgrid(gridDict['xgrid'], gridDict['ygrid'])
    latGrid = np.zeros(np.shape(yy))
    lonGrid = np.zeros(np.shape(xx))
    statePlN = np.zeros(np.shape(yy))
    statePlE = np.zeros(np.shape(xx))
    for iy in range(0, np.size(gridDict['zgrid'], axis=0)):
        for ix in range(0, np.size(gridDict['zgrid'], axis=1)):
            coords = sb.FRFcoord(xx[iy, ix], yy[iy, ix])  # , grid[iy, ix]))
            statePlE[iy, ix] = coords['StateplaneE']
            statePlN[iy, ix] = coords['StateplaneN']
            latGrid[iy, ix] = coords['Lat']
            lonGrid[iy, ix] = coords['Lon']
            assert xx[iy, ix] == coords['FRF_X']
            assert yy[iy, ix] == coords['FRF_Y']

    # put these data into the dictionary that matches the yaml
    gridDict['latitude'] = latGrid
    gridDict['longitude'] = lonGrid
    gridDict['easting'] = statePlE
    gridDict['northing'] = statePlN
    gridDict['xFRF'] = gridDict.pop('xgrid')
    gridDict['yFRF'] = gridDict.pop('ygrid')
    # addding 3rd dimension for time
    a = (gridDict.pop('zgrid')).T # switches  x and y FRF here
    gridDict['elevation'] = np.full([1, a.shape[0], a.shape[1]], fill_value=[a], dtype=np.float32)

# making the netCDF file from the gridded data
    makenc_FRFGrid(gridDict, ofname, globalYaml, varYaml)

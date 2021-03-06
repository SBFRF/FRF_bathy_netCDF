# -*- coding: utf-8 -*-
"""
Author: spicer bak, phd
Contact: spicer.bak@usace.army.mil
Association: USACE CHL Field Research Facility


my own library with useful functions and tips from which i found to be helpful
on various general functions that don't fit into specific other codes
this folder needs to be added to sys.path to use
"""
import numpy as np
import datetime as DT

import csv
from matplotlib import colors as mc
from matplotlib import pyplot as plt



def makegif(flist, ofname, size=None, dt=0.5):
    """
    This function uses imageio to create gifs from a list of images

    kwargs for mimwrite http://imageio.readthedocs.org/en/latest/format_gif.html#gif

    :param flist: a sorted list of files to be made into gifs (including path)
    :param ofname: output gif filename (including path)
    :param size: size of pictures (default not resized)
    :param loop: number of loops to do, 0 is default and infinite
    :return:
    """
    # images = [Image.open(fn) for fn in flist]
    #
    # for im in images:
    #     im.thumbnail(size, Image.ANTIALIAS)
    # images2gif.writeGif(ofname, images, duration=dt, nq=15)
    import imageio
    images = []
    if size != None:
        for im in images:
            im.thumbnail(size, Image.ANTIALIAS)
    for filename in flist:
        images.append(imageio.imread(filename))
    imageio.mimwrite(ofname, images, duration=dt)

def find_nearest(array, value):
    '''
	Function looks for value in array and returns the closest array value
	(to 'value') and index of that value
	'''
    idx = (np.abs(array - value)).argmin()
    return array[idx], idx


def SBcleanangle(directions, deg=360):
    '''
	This function cleans an array of angles (in degrees) to all positive
	values ranging from 0 to 360
	
	Currently is designed for only degree angles
	'''
    for ii in range(0, len(directions)):
        if directions[ii] >= 360:
            directions[ii] = directions[ii] - 360
        elif directions[ii] < 0:
            directions[ii] = directions[ii] + 360
    return directions


def FRFcoord(p1, p2):
    '''
    #  returns a dictionary of data with keys:
        'StateplaneE':spE,
        'StateplaneN':spN,
        'FRF_Y':Y,
        'FRF_X':X,
        'Lat'
        'Lon'

     [ ALat, ALon, spN, spE, Y, X] = frfCoord(p1, p2)
    #
    #  15 Dec 2014
    #  Kent Hathaway.
    #  Translated from Matlab to python 2015-11-30 - Spicer Bak
    #
    #  Uses new fit (angles and scales) Bill Birkemeier determined in Nov 2014
    #
    #  This version will determine the input based on values, outputs FRF, lat/lon,
    #  and state plane coordinates.  Uses NAD83-2011.
    #
    #  IO:
    #  p1 = FRF X (m), or Longitude (deg + or -), or state plane Easting (m)
    #  p2 = FRF Y (m), or Latitude (deg), or state plane Northing (m)
    #
    #  X = FRF cross-shore (m)
    #  Y = FRF longshore (m)
    #  ALat = latitude (decimal degrees)
    #  ALon = longitude (decimal degrees, positive, or W)
    #  spN = state plane northing (m)
    #  spE = state plane easting (m)

    NAD83-86	2014
    Origin Latitude          36.1775975
    Origin Longitude         75.7496860
    m/degLat             110963.357
    m/degLon              89953.364
    GridAngle (deg)          18.1465
    Angle FRF to Lat/Lon     71.8535
    Angle FRF to State Grid  69.9747
    FRF Origin Northing  274093.1562
    Easting              901951.6805

    #  Debugging values
    p1=566.93;  p2=515.11;  % south rail at 1860
    ALat = 36.1836000
    ALon = 75.7454804
    p2= 36.18359977;  p1=-75.74548109;
    SP:  p1 = 902307.92; 	p2 = 274771.22;
    '''
    assert np.size(p1) == 1, 'This function does not support lists or arrays '
    r2d = 180.0 / np.pi;

    Eom = 901951.6805;  # % E Origin State Plane
    Nom = 274093.1562;  # % N Origin State Plane
    # ALat0=10.65583950;            % Origin Lat minutes
    # ALon0=44.9811435;             % Origin Lon minutes
    ALat0 = 36.1775975;  # % Origin Lat minutes
    ALon0 = 75.7496860;  # % Origin Lon minutes
    DegLat = 110963.35726;  # % m/deg Lat
    DegLon = 89953.36413;  # % m/deg long
    GridAngle = 18.1465 / r2d;
    spAngle = (90 - 69.974707831) / r2d

    # Determine Data type
    if np.floor(abs(p1)) == 75 and np.floor(p2) == 36:  # lat/lon input
        # to FRF coords
        ALat = p1
        ALon = p2  # DESIGNATING LAT/LON VARS
        if p1 < 0:
            p1 = -p1
        ALatLeng = (p2 - ALat0) * DegLat
        ALonLeng = -(p1 - ALon0) * DegLon
        R = np.sqrt(ALatLeng ** 2 + ALonLeng ** 2)
        Ang1 = np.arctan2(ALonLeng, ALatLeng)
        Ang2 = Ang1 + GridAngle;
        X = R * np.sin(Ang2)
        Y = R * np.cos(Ang2)
        # to StatePlane
        Ang2 = Ang2 - spAngle
        AspN = R * np.cos(Ang2)
        AspE = R * np.sin(Ang2)
        spN = AspN + Nom
        spE = AspE + Eom

    elif (p1 > 800000) and p2 > 200000:  # state plane input
        spE = p1
        spN = p2  # designating stateplane vars
        # to FRF coords
        spLengE = p1 - Eom
        spLengN = p2 - Nom
        R = np.sqrt(spLengE ** 2 + spLengN ** 2)
        Ang1 = np.arctan2(spLengE, spLengN)
        Ang2 = Ang1 + spAngle
        X = R * np.sin(Ang2)
        Y = R * np.cos(Ang2)
        # to Lat Lon
        Ang2 = Ang1 - (GridAngle - spAngle)  # %
        ALatLeng = R * np.cos(Ang2)
        ALonLeng = R * np.sin(-Ang2)  # % neg to go west
        ALat = ALatLeng / DegLat + ALat0  # % was 60 * ALatLeng./DegLat + ALat0;
        ALon = ALonLeng / DegLon + ALon0

    elif (p1 > -10000 and p1 < 10000) and (p2 > -10000 and p2 < 10000):  # FRF input
        X = p1
        Y = p2;
        R = np.sqrt(p1 ** 2 + p2 ** 2);
        Ang1 = np.arctan2(p1, p2);  # % CW from Y
        Ang2 = Ang1 - GridAngle;  # %
        ALatLeng = R * np.cos(Ang2);
        ALonLeng = R * np.sin(-Ang2);  # % neg to go west
        ALat = ALatLeng / DegLat + ALat0;  # % was 60 * ALatLeng./DegLat + ALat0;
        ALon = ALonLeng / DegLon + ALon0;

        #  to state plane
        Ang2 = Ang1 - spAngle;
        AspN = R * np.cos(Ang2);
        AspE = R * np.sin(Ang2);
        spN = AspN + Nom;
        spE = AspE + Eom;


    else:
        print('<<ERROR>> Cound not determine input type, returning NaNs')
        ALat = float('NaN');
        ALon = float('NaN');
        spN = float('NaN');
        spE = float('NaN');
        Y = float('NaN');
        X = float('NaN');
    coords = {'StateplaneE': spE,
              'StateplaneN': spN,
              'FRF_Y': Y,
              'FRF_X': X,
              'Lat': ALat,
              'Lon': ALon}
    return coords


def findbtw(data, lwth, upth, type=0):
    '''
	This function finds both values and indicies of a list values between two values
	upth = upper level threshold
	lwth = lower level threshold
	list = list (or numpy array?)
	type:
		0 = non inclusive  ie. lwth < list <  upth
		1 = low incluisve  ie. lwth <=list <  upth
		2 = high inclusive ie. lwth < list <= upth
		3 = all inclusive  ie  lwth <=list <= upth
	'''
    indices = []
    vals = []
    shp = np.shape(data)
    if len(shp) == 2:
        for i, in enumerate(data):
            for j, elem in enumerate(range):
                if type == 0:
                    if elem < upth and elem > lwth:
                        indices.append((i, j))
                        vals.append(elem)
                elif type == 1:
                    if elem < upth and elem >= lwth:
                        indices.append((i, j))
                        vals.append(elem)
                elif type == 2:
                    if elem <= upth and elem > lwth:
                        indices.append((i, j))
                        vals.append(elem)
                elif type == 3:
                    if elem <= upth and elem >= lwth:
                        indices.append((i, j))
                        vals.append(elem)
    if len(shp) == 1:
        for j, elem in enumerate(data):
            if type == 0:
                if elem < upth and elem > lwth:
                    indices.append((j))
                    vals.append(elem)
            elif type == 1:
                if elem < upth and elem >= lwth:
                    indices.append((j))
                    vals.append(elem)
            elif type == 2:
                if elem <= upth and elem > lwth:
                    indices.append((j))
                    vals.append(elem)
            elif type == 3:
                if elem <= upth and elem >= lwth:
                    indices.append((j))
                    vals.append(elem)

    return indices, vals
def unpackDictionary(pack):
    """
    This function unpacks a dictionary into variables
    :param pack:
    :return:
    """
    for key, val in list(pack.items()):  # unpack the keys from the dictionary to individual variables
        exec (key + '=val')

class Bunch(object):
    """
    allows user to access dictionary data from 'object'
    instead of object['key']
    def __init__(self, adict):
    do x = Bunch(object)
    x.key
    """
    def __init__(self):
        self.__dict__.update(object)

def roundtime(dt=None, roundTo=60):
    """"Round a datetime object to any time laps in seconds
       dt : datetime.datetime object, default now.
       roundTo : Closest number of seconds to round to, default 1 minute.
       Author: Thierry Husson 2012 - Use it as you want but don't blame me.
       modified by SB to include lists of datetime objects,
       returned as a list if it came in as a list, if it came in as a datetime object
       it is returned as such
    """
    # making dt a list

    if np.size(dt) > 1:
        dtlist = dt
    elif np.size(dt) == 1:
        dtlist = [dt]
    elif np.size(dt) == None:
        dtlist = [DT.datetime.now()]
        # checking to make datetime
        # if type(dt[0] != DT.datetime):
        # trying to convert epoch time to datetime object  if need be but doen'st solve problem currently working on

    # looping through list
    for ii, dt in enumerate(dtlist):
        seconds = (dt - dt.min).seconds
        # // is a floor division, not a comment on following line:
        rounding = (seconds + roundTo / 2) // roundTo * roundTo
        dtlist[ii] = dt + DT.timedelta(0, rounding - seconds, -dt.microsecond)
    if len(dtlist) == 1:
        dtlist = dtlist[0]
    return dtlist


def cart2pol(x, y):
    '''
	this translates from cartesian coords to polar coordinates (radians)
	'''
    r = np.sqrt(x ** 2 + y ** 2)
    theta = np.arctan2(y, x)
    return r, theta


def pol2cart(r, theta):
    '''
	this translates from polar coords (radians) to polar coordinates
	'''
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    return x, y


def angle_correct(angle_in, rad=0):
    """
    this function takes angles in that are both positve and negative
    and corrects them to posivitve only
    :param angle_in:
    :param rad: radian =0 input angles are in degrees radian =1 input anglesa are in radian
    :return:
    """
    angle_in = np.array(angle_in)
    try:
        assert (angle_in == 0).all() is not True, 'All of the Angles are 0, cannot correct'
    except AssertionError:
        return angle_in
    if rad == 0:
        if (angle_in == 0).all():
            print('WARNING - Correcting angles of Zero')
        elif (np.abs(angle_in) < 2 * np.pi).all():
            print(' WARNING angles are all < 2Pi , ensure that angles are in degrees not radians')
        shape = np.shape(angle_in)
        if len(shape) == 0:
            posmask = angle_in >= 360
            negmask = angle_in < 0
            while negmask.any() or posmask.any():
                if negmask.any() == True:
                    angle_in += 360
                elif posmask.any() == True:
                    angle_in -= 360
                posmask = angle_in >= 360
                negmask = angle_in < 0
        if len(shape) == 1:
            posmask = angle_in >= 360
            negmask = angle_in < 0
            while negmask.any() or posmask.any():
                if negmask.any():  # filter negs out
                    idxneg = np.where(negmask)
                    angle_in[idxneg] += 360
                if posmask.any():  # filter overly positives out
                    idxpos = np.where(posmask)
                    angle_in[idxpos] -= 360
                posmask = angle_in >= 360
                negmask = angle_in < 0
        elif len(shape) == 2:
            for ii in range(0, np.size(angle_in, axis=0)):
                angle_in_2 = np.zeros((np.size(angle_in[ii, :])))  # initializing
                angle_in_2 = angle_in[ii, :]  # taking small chunk 1D array
                posmask = angle_in_2 >= 360  # seeing what's over 360
                negmask = angle_in_2 < 0  # seeing what's under 0
                while negmask.any() or posmask.any():
                    if negmask.any():  # filter negs out
                        idxneg = np.where(negmask)  # finding ids of where
                        if np.size(angle_in_2) == 1 and negmask == True:  # if there's only 1 instance
                            angle_in_2 += 360
                        else:
                            angle_in_2[idxneg] += 360
                    if posmask.any():  # filter overly positives out
                        idxpos = np.where(posmask)
                        if np.size(angle_in_2) == 1 and posmask == True:
                            angle_in_2 -= 360
                        else:
                            angle_in_2[idxpos] -= 360
                    posmask = angle_in_2 >= 360
                    negmask = angle_in_2 < 0
                angle_in[ii, :] = angle_in_2

        elif len(shape) == 3:
            for yy in range(0, np.size(angle_in, axis=1)):
                angle_in_3 = np.zeros(np.size(angle_in, axis=1))
                angle_in_3 = angle_in[:, yy, :]
                for ii in range(0, np.size(angle_in, axis=0)):
                    angle_in_2 = np.zeros((np.size(angle_in_3[ii, :])))  # initializing
                    angle_in_2 = angle_in_3[ii, :]  # taking small chunk 1D array
                    posmask = angle_in_2 >= 360  # seeing what's over 360
                    negmask = angle_in_2 < 0  # seeing what's under 0
                    while negmask.any() or posmask.any():
                        if negmask.any():  # filter negs out
                            idxneg = np.where(negmask)  # finding ids of where
                            if np.size(angle_in_2) == 1 and negmask == True:  # if there's only 1 instance
                                angle_in_2 += 360
                            else:
                                angle_in_2[idxneg] += 360
                        if posmask.any():  # filter overly positives out
                            idxpos = np.where(posmask)
                            if np.size(angle_in_2) == 1 and posmask == True:
                                angle_in_2 -= 360
                            else:
                                angle_in_2[idxpos] -= 360
                        posmask = angle_in_2 >= 360
                        negmask = angle_in_2 < 0
                    angle_in_3[ii, :] = angle_in_2
                angle_in[:, yy, :] = angle_in_3
    else:
        print('<<ERROR>> this function only takes angles in as degrees right now')
        raise
    assert (angle_in < 360).all() and (angle_in >= 0).all(), 'The angle correction function didn''t work properly'
    return angle_in
def statsBryant(observations, models):
    """
    This function does Non-Directional Statsistics
    These statistics are from the Bryant Wave stats CHETN - I - 91
    :param observations: array of observational data
    :param models:  array of model data
    :return: stats library
    """
    assert len(observations) == len(models), 'these data must be the same length'

    residuals = models - observations
    bias = np.sum(residuals)/len(observations)

    ## RMSE's
    # demeaned RMSE
    RMSEdemeaned = np.sqrt( np.sum((residuals - bias)**2) / (len(observations)-1) )
    # regular RMSE
    RMSE = np.sqrt( np.sum(residuals**2) /len(observations))
    # normalized RMSE or percentage
    RMSEnorm = np.sqrt( np.sum( residuals**2) / np.sum(observations**2))
    # scatter index - a normalize measure of error often times presented as %
    ScatterIndex=RMSE/np.mean(observations)
    # symetric Slope
    symr = np.sqrt(np.sum(models**2)/np.sum(models**2))
    r2 = np.sum( (observations - observations.mean()) * (models-models.mean())) /( np.sqrt(np.sum((observations - observations.mean()) ** 2)) * np.sqrt(np.sum((models - models.mean()) ** 2)))
    # wilmont 1985
    topW = np.abs(models - observations).sum()
    botW =  (np.abs(models - observations.mean()) + np.abs(observations - observations.mean())).sum()
    Wilmont = 1 - topW/botW

    xRMS = np.sqrt(np.sum(observations**2/len(observations)))
    pRMS = 1 - RMSE/xRMS
    pBias = 1 - np.abs(bias)/xRMS
    IMEDS = (pRMS + pBias)/2
    stats = {'bias': bias,
             'RMSEdemeaned' : RMSEdemeaned,
             'RMSE'         : RMSE,
             'RMSEnorm'     : RMSEnorm,
             'scatterIndex' : ScatterIndex,
             'symSlope'     : symr,
             'corr'         : r2,
             'PscoreWilmont': Wilmont,
             'PscoreIMEDS'  : IMEDS,
             'meta': 'please see Bryant, et al.(2016). Evaluation Statistics computed for the WIS) ERDC/CHL CHETN-I-91'}
    return stats

def printStatDict(dict):
    for key in dict:
        if key not in ['residuals', 'fitline','meta']:
            print('%s, %.3f' %(key, dict[key]))

def timeMatch(obs_time, obs_data, model_time, model_data):
    """
    This is the time match function from the IMEDs lite version created by ASA
    This has been removed from the IMEDS package to simplify use.
    This method returns the matching model data to the closest obs point.
    :param obs_time: observation times, in
    :param obs_data: matching observation data, any shape
    :param model_time:  modeling time
    :param model_data:  modeling data (any shape)
    :return:
    """

    time = np.array([])
    obs_data_s = np.array([])
    model_data_s = np.array([])

    threshold = min(np.median(np.diff(obs_time)) / 2.0 - 43,
                    np.median(np.diff(model_time)) / 2.0 - 43)

    # Loop through model records
    for data, record in zip(model_data, model_time):
        in1 = np.where(obs_time <= record)[0]
        in2 = np.where(obs_time >= record)[0]

        if in1.size == 0 or in2.size == 0:
            continue

        if in1[-1] == in2[0]:  # Times match up
            indx = in2[0]
        else:
            d1 = record - obs_time[in1[-1]]
            d2 = obs_time[in2[0]] - record
            if min(d1, d2) > threshold:
                continue
            elif (d1 <= d2):
                indx = in1[-1]
            elif (d2 < d1):
                indx = in2[0]

        if (np.isnan(obs_data[indx]).all() or np.isnan(data).all()):
            continue

        time = np.append(time, record)
        obs_data_s = np.append(obs_data_s, obs_data[indx])
        model_data_s = np.append(model_data_s, data)

    # if self.variable_name == 'wavePeakFrequency':
    #     obs_data_s = np.divide(1.0, obs_data_s)
    return time, obs_data_s, model_data_s


def waveStat(spec, dirbins, frqbins, lowFreq=0.05, highFreq=0.5):
    """
    this function will calculate the mean direction from a full spectrum
    only calculates on one 2D spectrum at a time
    defaults to 0.05 hz to 0.5 hz frequency for the statistics
    Input:
        %     spec  Frequency-direction spectra (2D)       shape(record,frqbin,dirbin)
        %  frqbins  Frequency vector (not assumed constant)
        %  dirbins  Direction vector (assumed constant)
        %
    Outputs (MKS, Hz, degrees, degrees CW from true north):
        %   Hmo   Significant wave height
        %    Tp   Period of the peak energy in the frequency spectra, (1/Fp).  AKA Tpd, not to be
        %           confused with parabolic fit to spectral period
        %    Tm02   Mean spectral period (Tm0,2, from moments 0 & 2), sqrt(m0/m2)
        %    Tm01   Average period, frequency sprectra weighted, from first moment (Tm0,1)
        %    Dp   Peak direction at the peak frequency
        %   Dmp   Mean direction at the peak frequency
        %    Dm   Mean wave direction
        %  sprdF  Freq-spec spread (m0*m4 - m2^2)/(m0*m4)  (one definition)
        %  sprdD  Directional spread (m0*m4 - m2^2)/(m0*m4)  (one definition, Kuik 1988, buoys),
        %         total sea-swell
        %         sprdD = r2d * sqrt(2.0 * (1.0 - sqrt(Xcomp.^2 + Ycomp^2)));
        %         where  Xcomp = sum(sin(Drad) .* Ds .* dwdir) ./ sum(Ds .* dwdir);
        %                Ycomp = sum(cos(Drad) .* Ds .* dwdir) ./ sum(Ds .* dwdir);
        % sprdDhp  half-power direction width in direction spectra at peak freq (not currently incorporated)
        %  Tm10 - Mean Absolute wave Period from -1 moment

            return order [ Hm0, Tp, TmSecondMoment, Tm01,  Dp, Dm, Dmp, sprdF, sprdD, stats], Tm10
        Code Translated by Spicer Bak from: fd2BulkStats.m written by Kent Hathaway
        
    """
    assert type(frqbins) in [np.ndarray, np.ma.MaskedArray], 'the input frqeuency bins must be a numpy array'
    assert type(dirbins) in [np.ndarray, np.ma.MaskedArray], 'the input DIRECTION bins must be a numpy array'
    assert np.array(spec).ndim == 3, 'Spectra must be a 3 dimensional array'
    try:
        assert (spec != 0).all() is not True, 'Spectra must have energy to calculate statistics, all values are 0'
    except AssertionError:
        return 0
    # finding delta freqeucny (may change as in CDIP spectra)
    frq = np.array(np.zeros(len(frqbins) + 1))  # initializing frqbin bucket
    frq[0] = frqbins[0]
    frq[1:] = frqbins
    df = np.diff(frq, n=1)  # dhange in frequancy banding
    dd = np.abs(np.median(np.diff(dirbins)))  # dirbins[2] - dirbins[1]  # assume constant directional bin size

    # finding delta degrees
    # frequency spec
    fspec = np.sum(spec, axis=2) * dd  # fd spectra - sum across the frequcny bins to leave 1 x n-frqbins
    # doing moments over 0.05 to 0.33 Hz (3-20s waves) (mainly for m4 sake)
    [idx, vals] = findbtw(frqbins, lowFreq, highFreq, type=3)

    m0 = np.sum(fspec * df, axis=1)  # 0th momment
    m1 = np.sum(fspec[:, idx] * df[idx] * frqbins[idx], axis=1)  #  1st moment
    m2 = np.sum(fspec[:, idx] * df[idx] * frqbins[idx] ** 2, axis=1) # 2nd moment
    m3 = np.sum(fspec[:, idx] * df[idx] * frqbins[idx] ** 3, axis=1)  # 3rd moment
    m4 = np.sum(fspec[:, idx] * df[idx] * frqbins[idx] ** 4, axis=1) # 4th moment
    m11 = np.sum(fspec[:, idx] * df[idx] * frqbins[idx] ** -1, axis=1) # negitive one moment

    # sigwave height
    Hm0 = 4 * np.sqrt(m0)
    # period stuff
    ipf = fspec.argmax(axis=1)  # indix of max frequency
    Tp = 1 / frqbins[ipf]  # peak period
    Tm02 = np.sqrt(m0 / m2)  # mean period
    Tm01 = m0 / m1  # average period - cmparible to TS Tm
    Tm10 =  m11 / m0
    # directional stuff
    Ds = np.sum(spec * np.tile(df, (len(dirbins), 1)).T, axis=1)  # directional spectra
    Dsp = []
    for ii in range(0, len(ipf)):
        Dsp.append(spec[ii, ipf[ii], :])  # direction spectra at peak-f
    Dsp = np.array(Dsp)
    idp = Dsp.argmax(axis=1)  # index of direction at peak frquency
    Dp = dirbins[idp]  # peak direction

    Drad = np.deg2rad(dirbins)  # making a radian degree bin
    # mean wave direction (e.g. Kuik 1988, USACE WIS)
    Xcomp = np.sum(np.sin(Drad) * Ds * dirbins, axis=1) / np.sum(Ds * dirbins, axis=1)
    Ycomp = np.sum(np.cos(Drad) * Ds * dirbins, axis=1) / np.sum(Ds * dirbins, axis=1)
    #Dm = np.rad2deg(np.arctan2(np.sum(np.sin(Drad) * Ds * dirbins, axis=1),
    #                           np.sum(np.cos(Drad) * Ds * dirbins, axis=1)))  # converting back to degrees
    Dm = np.rad2deg(np.arctan2(Xcomp, Ycomp))

    for ii in range(0, np.size(Dm, axis=0)):
        if Dm[ii] >= 360:
            Dm[ii] = 360 - Dm[ii]
        elif Dm[ii] < 0:
            Dm[ii] = 360 + Dm[ii]
            # Vector Dm (Hesser)
    sint = np.sin(Drad)  # sine of dirbins
    cost = np.cos(Drad)  # cosine of dirbins

    sint2 = np.tile(sint, [len(frqbins), 1])  # 2d diretion size of the spectra
    cost2 = np.tile(cost, [len(frqbins), 1])
    delsq = np.tile(df, [len(dirbins), 1]).T

    xsum = np.zeros(np.size(spec, axis=0))
    ysum = np.zeros(np.size(spec, axis=0))
    # summing across all directions

    for ii in range(0, np.size(spec, axis=0)):
        xsum[ii] = sum(np.sum(cost2 * delsq * spec[ii, :, :], axis=1))  # summing along directions, then
        ysum[ii] = sum(np.sum(sint2 * delsq * spec[ii, :, :], axis=1))

    vavgdir = np.arctan2(ysum, xsum)
    vavgdir = np.rad2deg(vavgdir)
    vavgdir = angle_correct(vavgdir)

    # Mean direction at the peak frequency
    Dmp = np.rad2deg(np.arctan2(np.sum(np.sin(Drad) * Dsp * dirbins, axis=1),
                                np.sum(np.cos(Drad) * Dsp * dirbins, axis=1)))  # converting back to degrees
    for ii in range(0, np.size(Dmp, axis=0)):
        if Dmp[ii] >= 360:
            Dmp[ii] = 360 - Dmp[ii]
        elif Dmp[ii] < 0:
            Dmp[ii] = 360 + Dmp[ii]
    # f-spec spread
    sprdF = (m0 * m4 - m2 ** 2) / (m0 * m4)

    # fd-spec spread
    sprdD = np.rad2deg(np.sqrt(2.0 * (1.0 - np.sqrt(Xcomp ** 2 + Ycomp ** 2))))

    ##### Exceprt from Kent's code for spreading - not sure how to handle
    #        % fd-spec spread, do a linear interp to get closer to half-power
    # % from the delta-deg increments
    # hp = np.max(Dsp)/2;
    # ihp=find(Dsp > hp);
    #
    #  % Left (d1) and right (d2) interps: Y=Dir, X=E
    # d1=interp1([Dsp(ihp(1)-1) Dsp(ihp(1)+1)], [dwdir(ihp(1)-1) dwdir(ihp(1)+1)], hp);
    # d2=interp1([Dsp(ihp(end)-1) Dsp(ihp(end)+1)], [dwdir(ihp(end)-1) dwdir(ihp(end)+1)], hp);
    # sprdDhp = d2 - d1;

    # wrapping up data into dictionary
    meta = 'Tp - peak period, Tm - mean period, Tave - average period, comparable to Time series mean period, Dp - peak direction, Dm - mean direction, Dmp - mean direction at peak frequency, vavgdir - Vector Averaged Mean Direction,sprdF - frequency spread, sprdD - directional spread'
    stats = {'Hm0': Hm0,
             'Tp': Tp,
             'Tm': Tm02,
             'Tave': Tm01,
             'Dp': Dp,
             'Dm': Dm,
             'Dmp': Dmp,
             'VecAvgMeanDir': vavgdir,
             'sprdF': sprdF,
             'sprdD': sprdD,
             'meta': meta
             }
    # print meta
    return Hm0, Tp, Tm02, Tm01, Dp, Dm, Dmp, vavgdir, sprdF, sprdD, stats, Tm10


def geo2STWangle(geo_angle_in, pierang=71.8, METin=1, fixanglesout=0):
    """
    This rotates an angle (angle_in) from geographic Meterological convention 0= True North
    and puts it to an STWAVE angle 0 is onshore
    variable pierang is the angle from shore to 90 degrees (shore coordinates) in geographic convention
    ie the pier at Duck NC is at an angle of 71.8 degrees TN and this is assumed to be shore perpendicular

    :param geo_angle_in:  an array or list of angles to be rotated from MET convention of angle from
    :param pierang:  the angle of the pier, from this the azimuth is calculated (MET CONVENTION)
    :param METin:  =1 if the input angle is in MET convention (angle from)
    :param fixanglesout: if set to 1, will correct out angles to +/-180
    :return: angle_out
    """
    assert len(np.shape(geo_angle_in)) <= 1, 'function geo2STWangle not tested in more than 1 dimension'
    azimuth = 270 - pierang
    geo_angle_in = np.array(geo_angle_in)
    if METin == 1:
        ocean_angle_in = angle_correct(geo_angle_in + 180)  # to 'ocean' from 'MET' convention
    else:
        ocean_angle_in = geo_angle_in
    rotate = angle_correct(90 - azimuth)  # converting azimuth to oceean convention
    STWangle = angle_correct(rotate - ocean_angle_in)  # rotation of angles to grid convention
    assert len(np.shape(STWangle)) < 2, 'This function handles only 1D arrays currently, try loop'
    #  putting into +/- 180 degrees
    if fixanglesout == 1:
        flip = np.argwhere(STWangle > 180)  # arguments that need to be flipped
        STWangle[flip] -= 360
    return STWangle

def write_grid(ofname, grid_dict):
    """
    This function takes the gridded product created by frf_grid_prod and writes
    the data to a csv file, it requires a dictionary in with the grid, and a list
    for the x coordinates (xgrid) and a list for the y coordinates (ygrid)

    """
    xcoord = grid_dict['xgrid']
    ycoord = grid_dict['ygrid']
    grid = grid_dict['grid'].T  # this grid produced is the
                #transpose of the mesh grids produced below
    xx, yy = np.meshgrid(xcoord, ycoord)
    f= open(ofname,'w')
    for iy in range(0, np.size(grid, axis=0)):
        for ix in range(0, np.size(grid, axis=1)):
            f.write("%f, %f, %f\n" % (xx[iy, ix], yy[iy, ix], grid[iy, ix]))
    f.close()

def STWangle2geo(STWangle, pierang=71.8, METout=1):
    """
    This is the complementary function to geo2STWangle,  It takes STWAVE angles (local coordinate system with a towards
     definition and + CCW)
    and translates them into geospatial grid angles (with a MET -from- convention and a CW+ convention)

    :rtype: 1D array of angles in geographic convention both met or ocean convention
    :param gridangle: an array or list of angles to be rotated
    :param pierang:  the (MET CONVENTION)
    :param METout:  if left 1, this creates output into a MET conveinton with the definition in the from
    :return: angle_out
    """
    assert len(np.shape(STWangle)) <= 3, 'STWangle2geo has not been tested in greater than 3dimensions'
    azimuth = 270 - pierang  # rotation of the Grid in local coordinate
    rotate = angle_correct(90 - azimuth)  # putting azimuth into ocean (towards) convention
    angle_out = rotate - STWangle
    if METout == 1:
        angle_out += 180
    angle_out = angle_correct(angle_out)  # correcting to < +360
    return angle_out


def whatIsYesterday(now=DT.date.today(), string=1, days=1):
    """
    this function finds what yesterday's date string is in the format
    of yyy-mm-dd
    :params:
    now:: the date to start counting backwards from
    string:: (1) output is in stiring format (default)
             (2) output is in datetime format
    days:: how many days to count backwards from
           default = 1
    
    """

    yesterday = now - DT.timedelta(days)
    if string == 1:
        yesterday = DT.date.strftime(yesterday, '%Y-%m-%d')
    return yesterday


def createDateList(start, end, delta):
    """
    creates a generator of dates
    """
    curr = start
    while curr <= end:
        yield curr
        curr += delta


def importFRFgrid(fname_in):
    '''
    This function imports a file comma seperated and returns a dictionary with keys x, y, z
    the file to be imported must be x y z order
    :param file:
    :param save: default false, will display, if true provide args
    :return: dictionary of frf grid x, y, z values
    '''
    import csv
    # import file with given path above

    raw_x, raw_y = [], []
    ptCt, raw_z = [], []
    raw_lon, raw_lat = [], []
    with open(fname_in, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == 1:
                ptCt = row[0]
            elif len(row) == 3:
                raw_x.append(row[0])  # x in string format
                raw_y.append(row[1])  # y in string format
                raw_z.append(row[2])  # z in string format
            elif len(row) == 5:
                raw_lon.append(float(row[0]))
                raw_lat.append(float(row[1]))
                raw_z.append(float(row[2]))  # z in string format
                raw_x.append(float(row[3]))  # x in string format
                raw_y.append(float(row[4]))  # y in string format
            elif len(row) == 0:
                continue
            else:
                raise ImportError('File format not understood')

    # initializing values to make strictly numbers, imported as strings
    # num_x = np.zeros(len(raw_x))
    # num_y = np.zeros(len(raw_y))
    # num_z = np.zeros(len(raw_z))
    # # making strings into floating point numbers
    # for ii in range(0, len(raw_x)):
    #     num_x[ii] = float(raw_x[ii])
    #     num_y[ii] = float(raw_y[ii])
    #     num_z[ii] = float(raw_z[ii])
    # gridding


    # format dictionary for output
    out = {'raw_x': raw_x,
           'raw_y': raw_y,
           'raw_z': raw_z,
           'raw_lon': raw_lon,
           'raw_lat': raw_lat
           }
    return out

def import_FRF_Transect(fname):
    """
    This function import a FRF transect csv file
    Comma Separated Value (CSV) ASCII data.  Column Header (not included in the file):
    Locality,Profile,SurveyNumber,Latitude,Longitude,Northing,Easting,FRF_offshore,
    FRF_longshore,Elevation,Ellipsoid,Date,Time,time_sec.

        Data Column headings Explanation:

        1) Locality Code (character) - "39" represents Duck, NC
        2) Profile Number (integer)
        3) Survey Number (integer) - sequential since initial survey
        4) Latitude (decimal degrees)
        5) Longitude (decimal degrees)
        6) Northing (decimal meters) - NAD83 North Carolina State Plane Coordinate
        7) Easting (decimal meters) - NAD83 North Carolina State Plane Coordinates
        8) FRF offshore coordinate: distance offshore from the local baseline
        9) FRF longshore coordinate: distance alongshore from the local origin
        10) Elevation - relative to the North American Vertical Datum in meters (NAVD88)
        11) Ellipsoid - optional, if used this is the geographic ellipsoid of the point
        12) Date - date data point was collected (YYYYMMDD)
        13) Time (hhmmss): Time data point was collected - in 24-hr Eastern Standard Time (EST)
        14) Time_sec: Time (EST) data point was collected in seconds past midnight

        Filename - the filename includes 7 fields with details about the contents of the file:

        1) Location (FRF)
        2) Survey Job (FRF)
        3) Survey Date (YYYYMMDD)
        4) Survey Number
        5) Vertical Datum (NAVD88)
        6) Vessel used (LARC)
        7) Survey Instrument (GPS)

    :param fname: name/location of a FRF measured bathymetry transect file
    :return: dictionary of all fields
    )
    """
    import pytz
    c0, c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13 = [], [], [], [], [], [], [], [], [], [], [], [], [], []
    with open(fname, 'r') as csvfile:  # opening the file
        reader = csv.reader(csvfile, delimiter=',')  # reading the lines
        for row in reader:
            c0.append(str(row[0]))  # Locality Code
            c1.append(int(row[1]))  # Profile number
            c2.append(int(row[2]))  # survey number
            c3.append(float(row[3]))  # Latitude
            c4.append(float(row[4]))  # Longitude
            c5.append(float(row[5]))  # Northing
            c6.append(float(row[6]))  # Easting
            c7.append(float(row[7]))  # FRF xshore
            c8.append(float(row[8]))  # FRF Long shore
            c9.append(float(row[9]))  # Elevation (NAVD88)
            c10.append(float(row[10]))  # Ellipsoid
            c11.append(row[11])  # YYMMDD
            c12.append(row[12])  # hhmmss
            #    c13.append(row[13])   seconds past midnight
    # convert EST to UTC

    date,time = [], []
    for ii in range(0, len(c12)):
        #print(ii, ''.join([c11[ii], c12[ii]]))
        try:  # data are in UTC already
            time.append(DT.datetime.strptime(''.join([c11[ii], c12[ii]]), 
                                '%Y%m%d%H%M%S.%f'))
            date.append(time[-1].date())
        except(ValueError):
            del c0[ii], c1[ii], c2[ii], c3[ii], c4[ii],c5[ii], c6[ii],c7[ii]
            del c8[ii], c9[ii], c10[ii]
            pass  # date doesn't convert properly (bad datapoint)
    # now make survey platform decision
    if fname.split('_')[-4] == 'LARC':
        Collection_Platform = 1
    elif fname.split('_')[-4] == 'CRAB':
        Collection_Platform = 2
    elif fname.split('_')[-4] == 'CRAB-Sled':
        Collection_Platform = 3
    elif fname.split('_')[-4] == 'Topo':
        Collection_Platform = 4
    else:
        Collection_Platform = 5
    
    bathyDict = {'Collection_Platform': Collection_Platform,
                 'Locality_Code': np.array(c0),
                 'Profile_number': np.array(c1),
                 'Survey_number': np.array(c2),
                 'Latitude': np.array(c3),
                 'Longitude': np.array(c4),
                 'Northing': np.array(c5),
                 'Easting': np.array(c6),
                 'xFRF': np.array(c7),
                 'yFRF': np.array(c8),
                 'Elevation': np.array(c9),
                 'Ellipsoid': np.array(c10),
                 'time': np.array(time), #  datetime object
                 'date': np.array(date),
                 'meta': 'date and Time has been converted to a UTC datetimeta object, elevation is in NAVD88',
                 }
    return bathyDict


def pltFRFgrid(xyzDict, save=False):
    """
    This function plots a dictionary of values with keys x, y, z

    :param save:
    :return:
    """
    x = xyzDict['x']
    y = xyzDict['y']
    z = xyzDict['z']

    levels = np.linspace(np.min(z), np.max(z), 35)  # the established levels to be plotted (maybe do this in log)
    # levels = np.logspace(cbar_min, cbar_max**(1/cbar_max), num=35, endpoint=True, base=10)
    norm = mc.BoundaryNorm(levels, 256)  # color palate for contourplots
    plt.imshow(x, y, z)

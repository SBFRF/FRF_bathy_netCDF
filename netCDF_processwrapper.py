import os
import surveyToNetCDF

dataDir = '/home/mikef/PycharmProjects/netcdf_Survey/data'

fileList = os.listdir(dataDir)

for file in fileList:
    if file.endswith('.csv'):
        surveyToNetCDF.convertText2NetCDF(dataDir + '/' + file)
    #if file.endswith('.txt'):
        #surveyToNetCDF.convertText2NetCDF(dataDir + '/' + file)



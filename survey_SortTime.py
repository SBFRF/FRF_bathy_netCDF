import pandas as pd

def surveySortTime(fname):
    """reads in .csv survey point file sorts based on hypack time
    (seconds) and then saves .csv with same name for input to
    surveyToNetCDF.py"""
    if fname.split('.')[-1] in ["csv'", 'csv']:
        df = pd.read_csv(fname,header=None)
        df.columns = ['loc','lineNo','sureyNo','lat','long','easting','norhting','FRFX','FRFY','elevation','ellipsoid','date','time','hypacktime']
        sortedTransect = df.sort_values(by=['hypacktime'], axis=0)
        sortedTransect.to_csv(fname[:-4] + '.csv',header=False,index=False)
    else:
        None







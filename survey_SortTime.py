import pandas as pd
import datetime

def surveySortTime(fname):
    """reads in .csv survey point file sorts based on hypack time
    (seconds) and then saves .csv with same name for input to
    surveyToNetCDF.py"""
    if fname.split('.')[-1] in ["csv'", 'csv']:
        df = pd.read_csv(fname, header=None)
        print('*** working on file***{}'.format(fname))
        df.columns = ['loc', 'lineNo', 'sureyNo', 'lat', 'long', 'easting', 'norhting', 'FRFX', 'FRFY', 'elevation',
                      'ellipsoid', 'date', 'time', 'hypacktime']
        df['time'] = df['time'].astype(int)
        df['datetime'] = df['date'].astype(str) + df['time'].astype(str)
        combinedDateTime = df['datetime']

        for num, val in enumerate(combinedDateTime):
            if len(val) == 9:
                newVal = val.ljust(5 + len(val), '0')
                combinedDateTime = combinedDateTime._set_value(num, newVal)

        df['datetime'] = combinedDateTime

        df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce', format='%Y%m%d%H%M%S')
        df['epochtime'] = df['datetime'].apply(lambda x: (x - datetime.datetime(1970, 1, 1)).total_seconds())
        df = df.sort_values(by=['epochtime'], axis=0).reset_index(drop=True)

        df['interp'] = df['epochtime'].duplicated()
        df['newdata'] = df['epochtime'][df['interp']]

        num = 0.25
        for val in range(len(df) - 1):
            if df.loc[val, 'interp'] == True:
                df.loc[val, 'newdata'] = df.loc[val, 'newdata'] + num
                num = num + 0.25

            else:
                if df.loc[val, 'interp'] == False:
                    num = 0.25

        df.newdata.fillna(df.epochtime, inplace=True)
        df = df.sort_values(by=['newdata'], axis=0).reset_index(drop=True)
        df['datetime'] = pd.to_datetime(df['newdata'], unit='s')
        df = df.drop_duplicates(subset=['datetime'])

        df['date'] = df['datetime'].dt.strftime('%Y%m%d')
        df['time'] = df['datetime'].dt.strftime('%H%M%S.%f').astype('str')

        del df['datetime'], df['epochtime'], df['interp'], df['newdata']
        df.to_csv(fname[:-4] + '.csv', header=False, index=False)
    else:
        None







"""
Loads data from specified file and creates df.index as datetime.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from configuration import CSV_DELIMITER
from data.structures import FileFormat


def loadRawData(fileFormat: FileFormat, inPath: str, fileName: str) -> pd.DataFrame:
    filePath = f"{inPath}/{fileName}"

    if fileFormat == FileFormat.PT6:
        SKIP_ROWS = [0, 1]
        df = pd.read_csv(f"{inPath}/{fileName}", delimiter=CSV_DELIMITER, encoding='cp1250', skiprows=SKIP_ROWS)  # utf_8 | cp1250

    elif fileFormat == FileFormat.H80AI:
        SKIP_ROWS = [0, 1, 2, 3]
        colNames = ['t', 'IAS_LH', 'Pressure_Alt', 'Engine_LH_NG', 'Engine_LH_ITT', 'Engine_LH_NP', 'Engine_LH_TQ', 'Engine_LH_FF', 'Engine_RH_NG',
                    'Engine_RH_ITT', 'Engine_RH_NP', 'Engine_RH_TQ', 'Engine_RH_FF', 'dummy']

        df = pd.read_csv(f"{inPath}/{fileName}", delimiter=',', encoding='cp1250', skiprows=SKIP_ROWS, names=colNames)  # utf_8 | cp1250

        # delete dummy column (the line ends with ',' and thus pandas creates empty column)
        del df['dummy']

    elif fileFormat == FileFormat.H80GE:
        SKIP_ROWS = [0]

        colNames = ['Counter', 'PressureAltitude', 'EngLFireWarn', 'ALTcoarse', 'ALTfine', 'TAT', 'IAS', 'EngRn1', 'EngLn1', 'EngLn2', 'EngRn2',
                    'ColdJunctionTemp', 'EngLFuelFlow', 'EngLittAux', 'EngRFuelFlow', 'EngRFireWarn', 'EngRittAux', 'EngLtorque', 'EngRtorque', 'dummy']

        df = pd.read_csv(f"{inPath}/{fileName}", delimiter=',', encoding='cp1250', skiprows=SKIP_ROWS, names=colNames)  # utf_8 | cp1250

        # delete dummy column (the line ends with ',' and thus pandas creates empty column)
        del df['dummy']

    df = df.drop(df.tail(1).index)  # drop last row - often mangled
    df = df.replace('', np.nan)     # replace empty strings by NaN - such will be dropped later on

    # create index as datetime object:
    if fileFormat == FileFormat.H80AI:
        with open(filePath, 'r', encoding="latin-1") as f:
            line = f.readline()     # read the first line in format 2628-F01.01-FDR.dat,8/14/2020 10:32:18 AM,

        d = line.split(',')[1]      # '8/14/2020 10:32:18 AM'
        startDt = datetime.strptime(d, '%m/%d/%Y %H:%M:%S %p')  # start DT of the file
        df.index = df.index.map(lambda x: startDt + timedelta(0, x))

        df['ts'] = df.index.map(lambda x: x.timestamp())

        del df['t']     # not needed anymore

    elif fileFormat == FileFormat.H80GE:
        # start datetime index based on the date & time from filename:
        fn = fileName[fileName.rfind('/')+1:]       # 'MSN3217_20200403_084854.csv'
        dtStr = fn[fn.find('_')+1:fn.rfind('.')]    # '20200403_084854'
        startDt = datetime.strptime(dtStr, '%Y%d%m_%H%M%S')
        df.index = df.index.map(lambda x: startDt + timedelta(0, x))    # TODO nepracuje s Counterem - DODELAT!!

        df['ts'] = df.index.map(lambda x: x.timestamp())

        del df['Counter']  # not needed anymore

    else:
        dateTimeColName = df.keys()[0]
        try:
            df.index = pd.to_datetime(df.get(dateTimeColName), format="%d/%m/%Y %H:%M:%S")
        except ValueError:
            try:
                df.index = pd.to_datetime(df.get(dateTimeColName), format="%d/%m/%Y %H:%M:%S.%f")
            except ValueError:
                try:
                    df.index = pd.to_datetime(df.get(dateTimeColName), format="%Y-%m-%d %H:%M:%S")
                except ValueError:
                    df.index = pd.to_datetime(df.get(dateTimeColName), format="%d.%m.%Y %H:%M:%S")

        df = df.drop(columns=[dateTimeColName])

    # strip all whitespaces from columns:
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    # replace empty strings by nan-s:
    df = df.replace('', np.nan)

    return df


if __name__ == '__main__':
    inPath = '/home/ibisek/wqz/prog/python/lu.vut.dataAnalyser/data/'
    outPath = '/tmp/00/'

    fileName = 'SN-131014-H80-200_030413.csv'

    dataFrame = loadRawData(inPath, fileName)

    print("## DATAFILE HEAD:\n", dataFrame.head())


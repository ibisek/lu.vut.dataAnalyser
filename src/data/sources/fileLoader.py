"""
Loads data from specified file and creates df.index as datetime.
"""

import numpy as np
import pandas as pd
from configuration import CSV_DELIMITER


def loadRawData(inPath, fileName):
    filePath = f"{inPath}/{fileName}"

    SKIP_ROWS = [0, 1]
    df = pd.read_csv(f"{inPath}/{fileName}", delimiter=CSV_DELIMITER, encoding='cp1250', skiprows=SKIP_ROWS)     # utf_8 | cp1250
    # df.drop(row=1)

    # colNames = df[0]
    # df = df.drop([0])  # drop row[0] ~ col names
    # df = df.drop(axis=0, index=[0, 1])  # drop the first two rows
    df = df.drop(df.tail(1).index)  # drop last row - often mangled
    df = df.replace('', np.nan)     # replace empty strings by NaN - such will be dropped later on

    # create index as datetime object:
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


"""
Generates temperature-pressure XY plot for all data within steady states
to identify conditions in which a particular airplane flies.
"""

import json
from os import walk
import pandas as pd
import matplotlib.pyplot as plt

from configuration import CSV_DELIMITER
from fileUtils import loadSteadyStates
from dataAnalysis.steadyStatesUtils import rowWithinSteadyState


if __name__ == '__main__':

    SS_PATH = '/home/ibisek/btsync/doma/radec/in/letova-data-2/json'
    FILTERED_DATA_PATH = '/home/ibisek/btsync/doma/radec/in/letova-data-2/filtered'
    OUT_PATH = '/tmp/00'

    # load Steady States (SS) file names:
    ssFiles = []
    for (dirpath, dirnames, filenames) in walk(SS_PATH):
        ssFiles.extend(filenames)

    allDf = pd.DataFrame()

    for ssIndex, ssFile in enumerate(ssFiles):
        print('[INFO] Loading', ssFile)

        ssFilePath = f"{SS_PATH}/{ssFile}"
        ssIntervals = loadSteadyStates(None, ssFilePath)

        filteredDataFilename = ssFile.replace('-steadyStates.json', '-selectedChannelsFiltered.csv')
        print('[INFO] filteredDataFilename:', filteredDataFilename)

        df = pd.read_csv(f"{FILTERED_DATA_PATH}/{filteredDataFilename}", delimiter=CSV_DELIMITER)
        # convert int index to datetime object:
        dateTimeColName = df.keys()[0]
        df.index = pd.to_datetime(df.get(dateTimeColName), format="%Y-%m-%d %H:%M:%S")
        df = df.drop(columns=[dateTimeColName])

        df['P0'] = df['P0'] / 100   # [Pa] -> [hPa]

        for i in range(len(df)):
            row = df.iloc[i]
            if rowWithinSteadyState(ssIntervals, row):
                allDf = allDf.append(row)

        allDf = allDf.append(df)

        # if ssIndex >= 2:
        #     break

    print("[INFO] Num rows in allDf:", len(allDf))

    # 'T0' = fn 'P0'
    allDf.sort_values(by='P0', inplace=True)

    plt.close('all')
    fig, ax = plt.subplots()
    allDf.plot('P0', y=['T0'], marker='.', markersize=0.1, ls='None', lw=1, ax=ax)

    # ax.legend()  # to redraw the legend and to show also the plain markers in the legend
    ax.get_legend().remove()

    # flip x axis so the values go up with decreasing pressure = increasing altitude:
    plt.xlim(plt.xlim()[1], plt.xlim()[0])

    plt.title("T0 ~ P0")
    plt.xlabel("P0 [hPa]")
    plt.ylabel("T0 [deg.C]")

    fn = f"{OUT_PATH}/T0-P0.png"
    plt.savefig(fn, dpi=300)

    print('UFON1')

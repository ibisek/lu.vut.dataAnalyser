"""
Ingests raw data files in specified directory and submits them for further processing.
"""

import sys
import os
import matplotlib.pyplot as plt
from plotting import plotChannelsOfInterest, plotChannelsOfInterestMultiY
from dataSources.fileLoader import loadRawData
from dataSources.gpxGenerator import genGpx
from pandas import DataFrame
import numpy as np
import matplotlib.dates as mdates

from fileUtils import composeFilename, loadSteadyStates
from dataAnalysis.steadyStatesUtils import rowWithinSteadyState
from configuration import IN_PATH, OUT_PATH, NG_THRESHOLD, SP_THRESHOLD, \
    KEYS_FOR_STEADY_STATE_DETECTION, STEADY_STATE_WINDOW_LEN, STEADY_STATE_DVAL

from dataPreprocessing.channelSelection import channelSelection
from dataPreprocessing.dataFiltering import filterData
from dataPreprocessing.dataStandartisation import standardiseData

from dataAnalysis.limitingStateDetector import detectLimitingStates
from dataAnalysis.steadyStatesDetector import SteadyStatesDetector
from dataAnalysis.correlations import analyseCorrelations
from dataAnalysis.regression import doRegression, doRegressionOnSteadySections, \
    doRegressionOnSteadyAllSectionsCombined, doRegressionOnSteadySectionsAvgXY, doRegressionOnSteadySectionsAvgXXXY


def omitRowsBelowThresholds(dataFrame:DataFrame, originalFileName:str, ngThreshold=NG_THRESHOLD, spThreshold=SP_THRESHOLD):

    # drop rows where NG < 90 %
    if 'NG' not in dataFrame.keys():
        print(f"[WARN] 'NG' column not present in data file '{originalFileName}'!")
        return dataFrame

    indexNames = dataFrame[(dataFrame['NG'] < ngThreshold)].index
    if len(indexNames) > 0:
        dataFrame = dataFrame.drop(indexNames)

    indexNames = dataFrame[(dataFrame['SP'] < spThreshold)].index
    if len(indexNames) > 0:
        dataFrame = dataFrame.drop(indexNames)

    return dataFrame


def _displaySteadyStateDetection(dataFrame:DataFrame, originalFileName:str):
    intervals = loadSteadyStates(originalFileName)

    numRows = len(dataFrame)
    arr = np.zeros([numRows])
    for i in range(len(dataFrame)):
        arr[i] = 1 if rowWithinSteadyState(intervals, dataFrame.iloc[i]) else 0
    dataFrame = dataFrame.assign(SS=arr)

    if len(dataFrame) == 0:
        return

    for key in KEYS_FOR_STEADY_STATE_DETECTION:
        if key == 'SS':
            continue

        # steady indicator within ranges of the particular channel:
        min = dataFrame[key].min()
        max = dataFrame[key].max()
        dataFrame['STEADY'] = dataFrame['SS'].apply(lambda x: max if x else min)

        plt.close('all')

        ax = dataFrame[key].plot(figsize=(20, 15), marker='.', markersize=10, ls='')
        dataFrame['STEADY'].plot(figsize=(20, 15), ls='-', ax=ax)

        plt.legend(fontsize=20)
        plt.xlabel('date-time', fontsize=20)
        plt.ylabel('values')
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
        plt.xticks(rotation=90)
        # plt.show()

        suffix = f"steadyStates-{key}"
        fn = composeFilename(originalFileName, suffix, 'png')
        # plt.savefig(fn)
        try:
            plt.savefig(fn)
        except ValueError as e:
            print(f"[ERROR] when plotting SS for {fn}:", str(e))

        plt.close()


if __name__ == '__main__':
    inPath = IN_PATH
    outPath = OUT_PATH

    for fileName in sorted(os.listdir(inPath)):
        filePath = f"{inPath}/{fileName}"

        if os.path.isfile(filePath):
            if fileName.endswith('.xlsx'):
                # TODO convert xls to csv?
                pass

            elif fileName.endswith('.csv'):
                print(f"[INFO] Reading file '{filePath}'..")

                # genGpx(inPath, fileName)
                # continue

                rawDataFrame = loadRawData(inPath, fileName)
                rawDataFrame = channelSelection(rawDataFrame, fileName)

                if len(rawDataFrame) == 0:
                    continue

                filteredDataFrame = filterData(rawDataFrame, fileName)

                # detectLimitingStates(rawDataFrame, fileName)    # limiting states detection on filtered data!

                standardisedDataFrame = standardiseData(filteredDataFrame, fileName)

                standardisedDataFrame = omitRowsBelowThresholds(standardisedDataFrame, fileName)

                # analyseCorrelations(filteredDataFrame, fileName)

                SteadyStatesDetector(windowDt=STEADY_STATE_WINDOW_LEN, dVal=STEADY_STATE_DVAL).detectSteadyStates(filteredDataFrame, fileName)
                # _displaySteadyStateDetection(standardisedDataFrame, fileName)

                # try:
                #     # plotChannelsOfInterest(rawDataFrame, fileName, suffix='raw')
                #     # plotChannelsOfInterest(filteredDataFrame, fileName, suffix='filtered')
                #     # plotChannelsOfInterest(standardisedDataFrame, fileName, suffix='std')
                #
                #     plotChannelsOfInterestMultiY(rawDataFrame, fileName, suffix='flightOverview-raw')
                #     plotChannelsOfInterestMultiY(filteredDataFrame, fileName, suffix='flightOverview-filtered')
                #     plotChannelsOfInterestMultiY(standardisedDataFrame, fileName, suffix='flightOverview-reduced', reducedChannels=True)
                #
                # except Exception as e:
                #     print("[ERROR] in plotting:", e)

                # doRegression(standardisedDataFrame, fileName)
                # doRegressionOnSteadySections(standardisedDataFrame, fileName)
                # doRegressionOnSteadyAllSectionsCombined(standardisedDataFrame, fileName)
                doRegressionOnSteadySectionsAvgXY(standardisedDataFrame, fileName)
                # doRegressionOnSteadySectionsAvgXXXY(standardisedDataFrame, fileName)

    print('Finished for now.')

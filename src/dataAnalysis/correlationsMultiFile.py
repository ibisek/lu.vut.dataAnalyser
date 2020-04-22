"""
Calculates correlation of all "flight data 2" files within steady states.
"""

import os
import json
import pandas as pd

from configuration import CSV_DELIMITER
from fileUtils import composeFilename
from dataIngestion import loadSteadyStates
from dataAnalysis.correlations import analyseCorrelations


if __name__ == '__main__':
    IN_PATH = '/home/ibisek/wqz/prog/python/lu.vut.dataAnalyser/data/in'
    OUT_PATH = '/home/ibisek/wqz/prog/python/lu.vut.dataAnalyser/data/out/log/'

    inPath = IN_PATH
    outPath = OUT_PATH

    allDf = pd.DataFrame()

    jsonFiles = [fileName for fileName in os.listdir(outPath) if fileName.endswith('.json')]

    for fn in sorted(jsonFiles):
        filePath = f"{outPath}/{fn}"

        with open(filePath, 'r') as f:
            j = json.load(f)

            originalFileName = j['configuration']['fileName']
            intervals = loadSteadyStates(originalFileName)
            reducedDataFilePath = composeFilename(originalFileName, 'reduced', 'csv')  # load filtered+reduced channels

            df = pd.read_csv(reducedDataFilePath, delimiter=CSV_DELIMITER)

            for i in intervals:
                startIndex = i['startIndex']
                endIndex = i['endIndex']

                allDf = allDf.append(df.iloc[startIndex:endIndex])

    analyseCorrelations(allDf, 'allSteadyStates.csv')

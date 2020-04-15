"""
Calculates correlation between all columns in given file.
"""

import sys
from pandas.core.series import Series
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from dataSources.fileLoader import loadRawData

from configuration import OUT_PATH


def analyseCorrelations(dataFrame, originalFileName, outPath=OUT_PATH):
    df = dataFrame
    # print("## DATAFILE HEAD:\n", df.head())

    CORR_METHODS = ['pearson', 'kendall', 'spearman']
    # CORR_METHODS = ['pearson']
    results = dict()
    for corrMethod in CORR_METHODS:
        print(f"Running correlation method '{corrMethod}'..")
        c = df.corr(method=corrMethod)
        # print(f"## CORRELATION {corrMethod}:\n", c)

        d = dict()

        keys = c.keys()
        for keyFrom in keys:
            values: Series = c.get(keyFrom)
            for keyTo in keys:
                corrValue = values[keyTo]

                if keyFrom == keyTo or np.isnan(corrValue) or corrValue >= 1 or corrValue <= 0.5:
                    continue

                l = sorted([keyFrom, keyTo])
                pairName = f"{l[0]}-{l[1]}"

                d[pairName] = corrValue

        # sort by value - correlation:
        d = {k: v for k, v in sorted(d.items(), key=lambda item: item[1], reverse=True)}

        # and store results:
        results[corrMethod] = d

    fn = OUT_PATH + originalFileName[:originalFileName.rindex('.')] + '-correlation.csv'
    print(f"Writing to '{fn}'")
    with open(fn, 'w') as f:

        # print header:
        f.write(f"{originalFileName}\n")
        numResValuesPerMethod = list()
        resValues = list()
        headerLine1 = ""
        headerLine2 = ""
        for m in CORR_METHODS:
            headerLine1 += f";corrMethod:{m};"
            headerLine2 += "channel;value;"
            resValues.append([i for i in results[m].items()])
            numResValuesPerMethod.append(len(results[m].values()))
        f.write(headerLine1 + '\n')
        f.write(headerLine2 + '\n')

        # print all rows:
        for row in range(max(numResValuesPerMethod)):
            s = ""
            for col in range(len(resValues)):
                if row < len(resValues[col]):
                    s += f"{resValues[col][row][0]};{resValues[col][row][1]};"
                else:
                    s += ";;"
            f.write(s + '\n')


if __name__ == '__main__':
    inPath = '/home/ibisek/wqz/prog/python/lu.vut.dataAnalyser/data/'

    fileName = 'SN-131014-H80-200_030413.csv'
    if len(sys.argv) == 2:
        fileName = sys.argv[1]

    filePath = inPath + fileName

    dataFrame = loadRawData(inPath, fileName)

    analyseCorrelations(dataFrame, fileName)

    print('KOHEU.')

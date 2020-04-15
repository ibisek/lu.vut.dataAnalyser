"""
https://ourcodingclub.github.io/2019/01/07/pandas-time-series.html
https://www.datacamp.com/community/tutorials/time-series-analysis-tutorial
https://towardsdatascience.com/four-ways-to-quantify-synchrony-between-time-series-data-b99136c4a9c9

https://pandas.pydata.org/pandas-docs/stable/user_guide/missing_data.html
https://pandas.pydata.org/pandas-docs/stable/user_guide/visualization.html
"""

import sys
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

if __name__ == '__main__':
    inPath = '/home/ibisek/wqz/prog/python/lu.vut.dataAnalyser/data/'
    outPath = '/tmp/00/'

    fileName = 'SN-131014-H80-200_030413.csv'
    if len(sys.argv) == 2:
        fileName = sys.argv[1]

    filePath = inPath + fileName

    df = pd.read_csv(filePath, delimiter=';', encoding='utf8', usecols=[0, 1, 2, 3, 4, 16], names=["datetime", "ng", "nv", "mk", "qp", "itt"])
    # df.drop(row=1)

    df = df.drop([0])  # drop row[0] ~ col names

    # create index as datetime object:
    df.index = pd.to_datetime(df["datetime"], format="%d/%m/%Y %H:%M:%S")
    df = df.drop(columns=["datetime"])

    # all data as numbers:
    df = df.astype(float)
    # fill missing values:
    df.interpolate()

    print("## DATAFILE HEAD:\n", df.head())

    plt.close('all')

    # ax = df.plot(figsize=(20, 15))
    # # df.plot(subplots=True, figsize=(20, 15), style='.')
    # # df.plot(x=df.index, y=["g", "nv", "Mk", "Qp"], figsize=(20, 15))
    # # df.plot(y=["Mk"], figsize=(20, 15))
    # # df.plot(y=["g", "nv"], style='*')
    # # df.plot(x="g", y=["nv"])

    channelsOfInterest = ["nv", "mk"]
    # channelsOfInterest = ["itt"]

    # remove high-frequency noise:
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.resample.html
    # df[["nv", "Mk"]].resample("10S").median().plot(figsize=(20, 10))    # 10 seconds/ median / mean
    filteredDf = df[channelsOfInterest].rolling(10).median()
    # filteredDf = df[channelsOfInterest].rolling(10).mean()

    # plot raw + filtered together:
    ax = df.plot(y=channelsOfInterest)
    ax = filteredDf.plot(ax=ax, y=channelsOfInterest, linewidth=2, fontsize=20)

    # first-order differencing (subtracts the trend (rolling mean) from the original signal):
    # filteredDf.diff().plot(subplots=True, figsize=(20, 10), fontsize=20)

    plt.legend(fontsize=20)
    plt.xlabel('date-time', fontsize=20)
    # plt.ylabel('values')
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
    plt.xticks(rotation=90)
    plt.show()

    # --

    from pandas.core.series import Series

    CORR_METHODS = ['pearson', 'kendall', 'spearman']
    results = dict()
    for corrMethod in CORR_METHODS:
        c = df.corr(method=corrMethod)
        # print(f"## CORRELATION {corrMethod}:\n", c)

        d = dict()

        keys = c.keys()
        for keyFrom in keys:
            values: Series = c.get(keyFrom)
            for keyTo in keys:
                corrValue = values[keyTo]
                if keyFrom == keyTo or np.isnan(corrValue) or corrValue >= 1 or corrValue <= 0:
                    continue

                l = sorted([keyFrom, keyTo])
                pairName = f"{l[0]}-{l[1]}"

                d[pairName] = corrValue

        # sort by value - correlation:
        d = {k: v for k, v in sorted(d.items(), key=lambda item: item[1], reverse=True)}

        # and store results:
        results[corrMethod] = d

    fn = outPath + fileName[:fileName.rindex('.')] + '-correlation.csv'
    print(f"Writing to '{fn}'")
    with open(fn, 'w') as f:

        # print header:
        f.write(f"{fileName}\n")
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
                    s += "ll"
            f.write(s+'\n')

    print('KOHEU.')

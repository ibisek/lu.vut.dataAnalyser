"""
Skript to contrast 1.xlsx data to all -AT and -OH available
"""

import pandas as pd
import matplotlib.pyplot as plt

from configuration import CSV_DELIMITER, UNITS
from dataAnalysis.regression import doRegressionForKeys
from fileUtils import composeFilename


def readFlightData():
    inPath = '/home/ibisek/btsync/doma/radec/out-2020-05-06'
    fileName = '1.csv'

    SKIP_ROWS = [0, 1]
    df = pd.read_csv(f"{inPath}/{fileName}", delimiter=CSV_DELIMITER, encoding='cp1250', skiprows=SKIP_ROWS)  # utf_8 | cp1250

    ndf = pd.DataFrame(index=df.index)

    ndf = ndf.assign(SPR=df['SPHR0'])
    ndf = ndf.assign(ITT=df['ITT'])
    ndf = ndf.assign(ITTR=df['ITTR0'])
    ndf = ndf.assign(FCR=df['FCR0'])
    ndf = ndf.assign(PK0C=df['pK0C'])
    ndf = ndf.assign(T2R=df['T2R0'])
    ndf = ndf.assign(NG=df['nG'])
    ndf = ndf.assign(NGR=df['nGR0'])

    ndf['SPR'] = ndf['SPR'] * 1000  # [kW] -> [W]
    ndf['T2R'] = ndf['T2R'] - 273.15  # [K] -> [deg.C]

    return ndf


if __name__ == '__main__':

    # 1.xlsx data:
    df1 = readFlightData()

    engines = ['SN131014', 'SN132018', 'SN141016',
               'SN132014', 'SN133005', 'SN141015']

    functions = [
        ['SPR', 'PK0C'],    # 1
        ['SPR', 'NGR'],     # 2
        ['ITT', 'NG'],      # 3
        ['FCR', 'SPR'],     # 4
        ['FCR', 'ITTR'],    # 5
        ['FCR', 'PK0C'],    # 6
        ['FCR', 'T2R'],      # 7
        ['FCR', 'NGR'],     # 8
        ['PK0C', 'T2R'],     # 9
        ['PK0C', 'NGR'],    # 10
        ['T2R', 'NGR'],      # 11
    ]

    for function in functions:
        yKey = function[0]
        xKey = function[1]

        dfATs = dict()
        dfOHs = dict()
        for engine in engines:
            # print(f"[INFO] engine '{engine}': {yKey} = fn({xKey})")

            inPath = f"/home/ibisek/wqz/prog/python/lu.vut.dataAnalyser/data/out/{engine}"
            try:
                fileName = f"{engine}_AT-{yKey}=fn({xKey})-poly.csv"
                dfAT = pd.read_csv(f"{inPath}/{fileName}", delimiter=CSV_DELIMITER, encoding='cp1250')
                dfATs[engine] = dfAT
            except FileNotFoundError as e:
                print(f"[WARN] File '{fileName}' not available - skipping.")

            try:
                fileName = f"{engine}_OH-{yKey}=fn({xKey})-poly.csv"
                dfOH = pd.read_csv(f"{inPath}/{fileName}", delimiter=CSV_DELIMITER, encoding='cp1250')
                dfOHs[engine] = dfOH
            except FileNotFoundError as e:
                print(f"[WARN] File '{fileName}' not available - skipping.")

        # assert len(dfATs) == len(dfOHs) == 6

        # regress x-y values. This will set 'yPred' channel to the dataFrame with interpolated values
        doRegressionForKeys(df1, 'no filename', yKey, [xKey], plot=False, saveDataToFile=False)

        COLORS = ['b', 'b', 'g', 'g', 'c', 'c', 'm', 'm', 'y', 'y', 'r', 'r', 'k', ]
        lineStyles = []
        colors = []

        xKeys = []
        yKeys = []
        combinedDf = pd.DataFrame()
        for i, engine in enumerate(engines):
            if engine in dfATs:
                xk = f"{xKey}-{engine}-AT"
                yk = f"{engine}-AT"
                combinedDf[xk] = dfATs[engine][xKey]
                combinedDf[yk] = dfATs[engine]['yPred']
                xKeys.append(xk)
                yKeys.append(yk)
                lineStyles.append('dotted')
                colors.append(COLORS[i * 2])

            if engine in dfOHs:
                xk = f"{xKey}-{engine}-OH"
                yk = f"{engine}-OH"
                combinedDf[xk] = dfOHs[engine][xKey]
                combinedDf[yk] = dfOHs[engine]['yPred']
                xKeys.append(xk)
                yKeys.append(yk)
                lineStyles.append('dashed')
                colors.append(COLORS[i * 2 + 1])

        xk = xKey+'-flight'
        yk = 'flight'
        combinedDf[xk] = df1[xKey]
        combinedDf[yk] = df1['yPred']
        xKeys.append(xk)
        yKeys.append(yk)
        lineStyles.append('solid')
        colors.append('black')

        plt.close('all')

        # nicer plotting:
        markers = ['', '', '', '', '', '', '', '', '', '', '', '', '', ]
        markerSizes = [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, ]
        # lineStyles = ['dotted', 'dashed', 'dotted', 'dashed', 'dotted', 'dashed', 'dotted', 'dashed',
        #               'dotted', 'dashed', 'dotted', 'dashed', 'solid']
        # colors = ['b', 'b', 'g', 'g', 'c', 'c', 'm', 'm', 'y', 'y', 'r', 'r', 'k', ]

        fig, ax = plt.subplots()
        fig.set_size_inches(10, 6)  # ~ 16:9

        for xk, yk, marker, markerSize, lineStyle, color in zip(xKeys, yKeys, markers, markerSizes, lineStyles, colors):
            combinedDf.sort_values(by=xk, inplace=True)
            combinedDf.plot(xk, y=[yk], marker=marker, markersize=markerSize, ls=lineStyle, lw=1, ax=ax, color=color)
            ax.legend()     # to redraw the legend and to show also the plain markers in the legend
            # plt.ylim([230, 300])
            # plt.xlim([90, 105])

        plt.title(f"{yKey} = fn({xKey})")
        plt.xlabel(f"{xKey} [{UNITS[xKey]}]")
        plt.ylabel(f"{yKey} [{UNITS[yKey]}]")

        rootPath = '/home/ibisek/wqz/prog/python/lu.vut.dataAnalyser/data/out'
        fn = f"{rootPath}/{yKey}=fn({xKey}).png"
        plt.savefig(fn, dpi=300)


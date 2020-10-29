"""
Script to contrast 1.xlsx data to all -AT and -OH available
"""

import pandas as pd
import matplotlib.pyplot as plt

from configuration import CSV_DELIMITER, UNITS
from data.analysis.regression import doRegressionForKeys


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

    ndf['SPR'] = ndf['SPR'] * 1000      # [kW] -> [W]
    ndf['T2R'] = ndf['T2R'] - 273.15   # [K] -> [deg.C]

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

    for engine in engines:
        for function in functions:
            yKey = function[0]
            xKey = function[1]

            # regress x-y values. This will set 'yPred' channel to the dataFrame with interpolated values
            doRegressionForKeys(df1, 'no filename', yKey, [xKey], plot=False, saveDataToFile=False)

            print(f"[INFO] engine '{engine}': {yKey} = fn({xKey})")

            try:
                inPath = f"/home/ibisek/wqz/prog/python/lu.vut.dataAnalyser/data/out/{engine}"
                fileName = f"{engine}_AT-{yKey}=fn({xKey})-poly.csv"
                dfAT = pd.read_csv(f"{inPath}/{fileName}", delimiter=CSV_DELIMITER, encoding='cp1250')
                fileName = f"{engine}_OH-{yKey}=fn({xKey})-poly.csv"
                dfOH = pd.read_csv(f"{inPath}/{fileName}", delimiter=CSV_DELIMITER, encoding='cp1250')
            except FileNotFoundError as e:
                print(f"[WARN] File '{fileName}' not available - skipping.")
                continue

            combinedDf = pd.DataFrame()
            combinedDf[xKey+'-AT'] = dfAT[xKey]
            combinedDf[yKey + '-AT'] = dfAT[yKey]
            combinedDf[yKey + '-AT-reg'] = dfAT['yPred']
            combinedDf[xKey+'-OH'] = dfOH[xKey]
            combinedDf[yKey + '-OH'] = dfOH[yKey]
            combinedDf[yKey + '-OH-reg'] = dfOH['yPred']
            combinedDf[xKey+'-1'] = df1[xKey]
            combinedDf[yKey + '-1'] = df1[yKey]
            combinedDf[yKey + '-1-reg'] = df1['yPred']

            plt.close('all')

            # nicer plotting:
            xKeys = [xKey+'-AT', xKey+'-AT', xKey+'-OH', xKey+'-OH', xKey+'-1', xKey+'-1']
            yKeys = [yKey+'-AT', yKey+'-AT-reg', yKey+'-OH', yKey+'-OH-reg', yKey+'-1', yKey+'-1-reg']
            markers = ['+', '.', '+', '.', '+', '.']
            markerSizes = [3, 3, 3, 3, 3, 3]
            lineStyles = ['None', ':', 'None', ':', 'None', ':']
            fig, ax = plt.subplots()
            for xk, yk, marker, markerSize, lineStyle, in zip(xKeys, yKeys, markers, markerSizes, lineStyles):
                combinedDf.sort_values(by=xk, inplace=True)
                combinedDf.plot(xk, y=[yk], marker=marker, markersize=markerSize, ls=lineStyle, lw=1, ax=ax)
                ax.legend()     # to redraw the legend and to show also the plain markers in the legend

            plt.title(f"{engine}: {yKey} = fn({xKey})")
            plt.xlabel(f"{xKey} [{UNITS[xKey]}]")
            plt.ylabel(f"{yKey} [{UNITS[yKey]}]")

            rootPath = '/home/ibisek/wqz/prog/python/lu.vut.dataAnalyser/data/out'
            fn = f"{rootPath}/{engine}:{yKey}=fn({xKey}).png"
            plt.savefig(fn, dpi=300)


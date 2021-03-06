#
# Coefficient of polynomial regression:
# @see https://stackoverflow.com/questions/51906274/cannot-understand-with-sklearns-polynomialfeatures
# Polynom 2nd degree:
# Z = fn (a, b, c) -> coefs = [1, a, b, c, a^2, b^2, c^2, ab, bc, ca] -> 10 coeffs
# Z = fn (a,b,c,d) -> coefs = [1, a, b, c, d, a^2, b^2, c^2, d^2, ab, bc, cd, ac, ad, bd] -> 15 coefs
#

import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
from collections import namedtuple
from sklearn.linear_model import LinearRegression

from fileUtils import composeFilename, composeFilename2, loadSteadyStates
from configuration import OUT_PATH, NOMINAL_DATA, UNITS
from data.analysis.ibiModel import IbiModel

RegressionResult = namedtuple('RegressionResult', ['id', 'ts', 'engineId', 'fileId', 'fn', 'xValue', 'yValue', 'delta', 'a', 'b', 'c', 'xMin', 'xMax'])


def doRegression1(dataFrame: DataFrame, originalFileName: str):
    """
    One dimensional regression.
    :param dataFrame:
    :param originalFileName:
    :return:
    """

    keys = ['NG', 'TQ', 'FF', 'ITT', 'p0', 'pt', 't1', 'NP']
    #         0     1     2     3     4      5     6     7
    pairs = [(2, 1), (3, 1), (2, 3), (2, 0), (0, 1), (3, 0), (4, 6)]  # y = fn(x)
    # pairs = [(2, 1)]  # y = fn(x)

    # dataFrame = dataFrame.fillna(0)
    dataFrame = dataFrame.interpolate()

    for pair in pairs:
        # values into numpy array:
        x = dataFrame.iloc[:, pair[1]].values.reshape(-1, 1)
        y = dataFrame.iloc[:, pair[0]].values.reshape(-1, 1)

        predictor = LinearRegression()  # https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html
        # predictor = Ridge(alpha=1.0)              # https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html#sklearn.linear_model.Ridge
        # predictor = Lasso(alpha=0.1)              # https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html#sklearn.linear_model.Lasso
        # predictor = ElasticNet(random_state=0)    # https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.ElasticNet.html#sklearn.linear_model.ElasticNet
        predictor.fit(x, y)
        yPred = predictor.predict(x)

        plt.close('all')
        plt.scatter(x, y)
        plt.plot(x, yPred, color='red')
        plt.title(f"{keys[pair[0]]}  = fn({keys[pair[1]]}); k={lr.coef_[0][0]:04f}")
        plt.xlabel(keys[pair[1]])
        plt.ylabel(keys[pair[0]])

        suffix = f"{keys[pair[0]]}=fn({keys[pair[1]]})"
        fn = composeFilename(originalFileName, suffix, 'png')
        plt.savefig(fn)

        # plt.show()
        print('ON SCREEN')


def doRegressionForKeys(dataFrame: DataFrame, originalFileName: str, yKey: str, xKeys: list,
                        fileNameSuffix='', plot=True, saveDataToFile=True, outPath=OUT_PATH, engineIndex=1):
    """
    * Multidimensional regression through the entire flight.
    * Multidimensional regression where NG >= 90%
    :param dataFrame:
    :param originalFileName:
    :param yKey
    :param xKeys
    :param fileNameSuffix
    :param plot
    :param saveDataToFile
    :param outPath
    :param engineIndex
    :return:
    """
    # keys = ['NG', 'TQ', 'FF', 'ITT', 'p0', 'pt', 't1', 'NP', 'P']
    #         0     1     2     3     4      5     6     7    8

    # dataFrame = dataFrame.fillna(0)
    # dataFrame = dataFrame.interpolate()
    dataFrame.dropna(inplace=True)

    if len(dataFrame) == 0:
        print('[WARN] no data left to regress!')
        return None, None

    x = dataFrame[xKeys]
    y = dataFrame[yKey]

    coefsStr = "coefs unknown"
    yPred = None
    model = None
    regressionCoefficients = []
    goLinear = False

    # if goLinear:
    #     model = LinearRegression()
    #     model.fit(x, y)
    #     yPred = model.predict(x)
    #
    #     coefsStr = ";".join(f"{x:0.6f}" for x in model.coef_) if len(xKeys) == 1 else None
    #     regressionCoefficients = [x for x in model.coef_]
    #
    # else:
    #     poly = PolynomialFeatures(degree=2)    # 2 is just enuf! :)
    #     regressor = Ridge()
    #     # regressor = LinearRegression()
    #     model = make_pipeline(poly, regressor)
    #     model.fit(x, y)
    #     yPred = model.predict(x)
    #
    #     coefsStr = ";".join(f"{x:0.6f}" for x in regressor.coef_) if len(xKeys) == 1 else None
    #     if len(xKeys) == 1:
    #         regressionCoefficients = [x for x in regressor.coef_]
        # poly.get_feature_names()  -> ['1', 'x0', 'x0^2']
        # DataFrame(poly.transform(x), columns=poly.get_feature_names(x.columns))

    model = IbiModel()
    if goLinear:
        model.fit(x[xKeys[0]], y, 1)     # a*x + b
    else:
        model.fit(x[xKeys[0]], y, 2)     # a*x^2 + b*x + c

    yPred = model.predict(x[xKeys[0]])
    coefsStr = ";".join(f"{x:0.10f}" for x in model.coefs) if len(xKeys) == 1 else None

    dataFrame['yPred'] = yPred.values
    # dataFrame = dataFrame.assign(yPred=yPred)

    xKeysStr = ",".join(xKeys)

    if saveDataToFile:
        suffix = f"{yKey}=fn({xKeysStr})"
        suffix += "-lin" if goLinear else "-poly"
        fn = composeFilename2(originalFileName, suffix, 'csv')
        fp = f"{outPath}/{fn}"
        print(f"[INFO] Saving regressed dataFrame to '{fp}'")
        dataFrame[xKeys + [yKey, 'yPred']].to_csv(fp, sep=';')

    if coefsStr:    # if none -> multidimensional - can be shown but is useless
        print("COEFs;", coefsStr)

    if plot and len(xKeys) == 1:    # dunno how to display multidim array :P
        plt.close('all')

        try:
            doXYPlot = True
            if doXYPlot:
                # X-Y plot:

                # simple plotting:
                # dataFrame.plot(xKeys[0], y=[yKey, 'yPred'], marker='.', markersize=5, linestyle='')

                # nicer plotting:
                cols = [yKey, 'yPred']
                markers = ['+', '.']
                markerSizes = [1, 1]
                lineStyles = ['', ':']
                fig, ax = plt.subplots()
                dataFrame.sort_values(by=xKeys[0], inplace=True)
                for col, marker, markerSize, lineStyle, in zip(cols, markers, markerSizes, lineStyles):
                    dataFrame.plot(xKeys[0], y=[col], marker=marker, markersize=markerSize, ls=lineStyle, lw=1, ax=ax)
                    ax.legend()  # to redraw the legend and to show also the plain markers in the legend

                xKey = xKeys[0]
                plt.xlabel(f"{xKey} [{UNITS[xKey]}]")
                plt.ylabel(f"{yKey} [{UNITS[yKey]}]")   # this refuses to work..

            else:
                # time-based plot:
                dataFrame[[yKey, 'yPred']].plot(marker='.', markersize=1, linestyle='')
                plt.xlabel('date-time')

            plt.title(f"{yKey} = fn({xKeysStr})")     # \nk={coefsStr}
            plt.ylabel(yKey)
            # plt.show()

            suffix = f"{yKey}=fn({xKeysStr})"
            suffix += "-lin" if goLinear else "-poly"
            fn = composeFilename2(originalFileName, suffix, 'png', engineIndex=engineIndex)
            fp = f"{outPath}/{fn}"
            plt.savefig(fp, dpi=300)

        except KeyError as e:   # often raised upon plotting X=X
            print('[ERROR] in regression plot', e)

    return model, model.coefs


def doRegression(dataFrame: DataFrame, originalFileName: str, fileNameSuffix=''):

    d = dict()
    d['ITT'] = ['NG', 'NP', 'FC', 'TQ']    # , 'pt'
    # d['TQ'] = ['NG', 'NP', 'FC', 'ITT']
    # d['PT'] = ['NG', 'NP', 'FC', 'ITT']
    # d['FC'] = ['NG', 'NP', 'TQ', 'ITT']
    # d['NG'] = ['NP', 'FC', 'TQ', 'ITT']

    for yKey, xKeys in d.items():

        df = dataFrame.copy()   # deep copy.. just for sure
        print(f"{yKey} = fn {xKeys}")

        model, regressionCoefficients = doRegressionForKeys(df, originalFileName, yKey, xKeys, fileNameSuffix)
        oneRowOfDf = dataFrame[xKeys].iloc[1, :]  # extract data structure..
        oneRowOfDf[xKeys] = [NOMINAL_DATA[k] for k in xKeys]    # .. and fill it with nominal values

        # [v for k, v in NOMINAL_DATA.items() if k in xKeys]
        yVal = model.predict([oneRowOfDf])[0]
        delta = yVal - NOMINAL_DATA[yKey]

        motorId = originalFileName[:originalFileName.index('.')]
        xKeysStr = ",".join(xKeys)
        print(f"PRED; {motorId}; {yKey} = fn ({xKeysStr}); {yVal:.2f}; shall be; {NOMINAL_DATA[yKey]:.2f}; delta; {delta:.2f}")


def doRegressionOnSection(dataFrame: DataFrame, originalFileName: str, startIndex: int, endIndex: int):
    df = dataFrame.iloc[startIndex: endIndex, :]

    print(f"\nstartIndex;{startIndex};endIndex;{endIndex};", end='')
    suffix = f"-{startIndex}-{endIndex}"
    doRegression(df, originalFileName, suffix)


def doRegressionOnSteadySections(dataFrame: DataFrame, originalFileName: str):
    intervals = loadSteadyStates(originalFileName)

    for i in intervals:
        startIndex = i['startIndex']
        endIndex = i['endIndex']
        doRegressionOnSection(dataFrame, originalFileName, startIndex, endIndex)


def doRegressionOnSteadyAllSectionsCombined(dataFrame: DataFrame, originalFileName: str):
    """
    Combines/concatenates all steady states from one flight into one dataFrame and does regression on that one.
    :param dataFrame:
    :param originalFileName:
    :return:
    """
    intervals = loadSteadyStates(originalFileName)

    # combinedDf = DataFrame(index=dataFrame.index)
    combinedDf = DataFrame()
    for i in intervals:
        startIndex = i['startIndex']
        endIndex = i['endIndex']
        combinedDf = combinedDf.append(dataFrame.iloc[startIndex:endIndex, :])

    combinedDf.dropna(inplace=True)     # there certainly are holes between the intervals

    doRegression(combinedDf, originalFileName, '-combined')


def doRegressionOnSteadySectionsAvgXY(dataFrame: DataFrame, originalFileName: str, outPath=OUT_PATH, engineIndex=1):
    """
    Single dimensional regression Y = fn(X)
    :param dataFrame:
    :param originalFileName:
    :param outPath:
    :param engineIndex: default 1
    :return: list of RegressionResults
    """
    intervals = loadSteadyStates(originalFileName=originalFileName, ssDir=outPath, engineIndex=engineIndex)
    numIntervals = len(intervals)

    l = list()  # Y = fn(X)

    # l.append(('FC', 'SP'))
    # l.append(('NG', 'SP'))
    # l.append(('ITT', 'SP'))
    # l.append(('ITT', 'NG'))

    # l.append(('FCR', 'SPR'))
    # l.append(('NGR', 'SPR'))
    # l.append(('ITTR', 'SPR'))
    # l.append(('ITTR', 'NGR'))

    # l.append(('SPR', 'NGR'))    # 2
    # l.append(('ITT', 'NG'))     # 3
    # l.append(('FCR', 'SPR'))    # 4
    # l.append(('FCR', 'ITTR'))   # 5
    # l.append(('FCR', 'NGR'))    # 8
    # if 'PK0C' in dataFrame.keys():
    #     l.append(('SPR', 'PK0C'))  # 1
    #     l.append(('FCR', 'PK0C'))  # 6
    #     l.append(('PK0C', 'NGR'))  # 10
    # if 'T2R' in dataFrame.keys():
    #     l.append(('FCR', 'T2R'))   # 7
    #     l.append(('PK0C', 'T2R'))  # 9
    #     l.append(('T2R', 'NGR'))   # 11

    # l.append(('OILT', 'SP'))
    # l.append(('OILT', 'SPR'))
    # l.append(('OILT', 'NG'))
    # l.append(('OILT', 'NGR'))
    # l.append(('OILP', 'SP'))
    # l.append(('OILP', 'SPR'))
    # l.append(('OILP', 'NG'))
    # l.append(('OILP', 'NGR'))

    # pro web-aplikaci:
    l.append(('NGR', 'SPR'))
    l.append(('ITTR', 'SPR'))
    l.append(('ITTR', 'NGR'))
    l.append(('FCR', 'SPR'))
    l.append(('FCR', 'NGR'))

    results = []

    for yKey, xKey in l:
        df = pd.DataFrame()
        allKeys = [xKey, yKey]

        # use all data from the steady state for the regression:
        for row, interval in enumerate(intervals, start=0):
            startIndex = interval['startIndex']
            endIndex = interval['endIndex']

            sectionDf = dataFrame.iloc[startIndex:endIndex, :]

            df = df.append(sectionDf[allKeys])

        # use just average values from the steady state for the regression:
        # arr = np.zeros([numIntervals, 2])   # (x, y)
        # for row, interval in enumerate(intervals, start=0):
        #     startIndex = interval['startIndex']
        #     endIndex = interval['endIndex']
        #
        #     sectionDf = dataFrame.iloc[startIndex:endIndex, :]
        #
        #     arr[row, 0] = np.average(sectionDf[xKey].values)
        #     arr[row, 1] = np.average(sectionDf[yKey].values)
        #
        # df = pd.DataFrame(data=arr)     # numpy array to df
        # df.rename(columns={0: xKey, 1: yKey}, inplace=True)     # set correct col names/keys
        # df.sort_values(by=[xKey], inplace=True)   # sort order by X value (so they don't make loops on the chart)

        # and now do the regression:
        model, coeffs = doRegressionForKeys(df, originalFileName, yKey, [xKey], fileNameSuffix='', outPath=outPath, engineIndex=engineIndex)
        if not model or not any(coeffs):
            continue

        if xKey in NOMINAL_DATA:
            xVal = NOMINAL_DATA[xKey]

            min = df[xKey].min()
            max = df[xKey].max()
            mean = df[xKey].mean()

            xVal = mean     # TODO temporary experiment as the nominal xVal doesn't frequently fit into the x-data range

            print(f"[INFO] REGRESSION in; {originalFileName}; of; {yKey} = fn ({xKey}); val; {xVal}; into range; {min:.02f}; {max:.02f}")

            if xVal < min or xVal > max:
                print(f"[WARN] Omitting; {yKey} = fn ({xKey}); {xVal} not in range <{min:.02f}, {max:.02f}>")
                continue

            # [v for k, v in NOMINAL_DATA.items() if k in xKeys]
            yVal = model.predict([[xVal]])[0]
            delta = yVal - NOMINAL_DATA[yKey]
            # deltaPct = (yVal-NOMINAL_DATA[yKey])/NOMINAL_DATA[yKey] * 100

            unitRunId = originalFileName[:originalFileName.index('.')]
            print(f"PRED; {unitRunId}; {yKey} = fn ({xKey}); {yVal:.2f}")
            # print(f"PRED; {unitRunId}; {yKey} = fn ({xKey}); {yVal:.2f}; shall be; {NOMINAL_DATA[yKey]:.2f}; delta; {delta:.2f}; deltaPct; {deltaPct:.2f}")

            # unitId = unitRunId[:unitRunId.index('_')]
            # unitLogFilename = f"{unitId}-analyses.csv"

            ts = int(dataFrame.index[0].to_pydatetime().timestamp())     # [s] unix ts of start of this file
            (a, b, c) = coeffs if len(coeffs) == 3 else (0, 0, 0)
            res: RegressionResult = RegressionResult(id=None, engineId=None, fileId=None, xValue=xVal, delta=delta,
                                                     fn=f"{yKey}-fn-{xKey}", ts=ts, yValue=yVal, a=a, b=b, c=c, xMin=min, xMax=max)
            results.append(res)

    return results


def doRegressionOnSteadySectionsAvgXXXY(dataFrame: DataFrame, originalFileName: str):
    """
    Multi dimensional regression Y = fn(X1, X2, ..)
    :param dataFrame:
    :param originalFileName:
    :return:
    """
    intervals = loadSteadyStates(originalFileName)
    numIntervals = len(intervals)

    l = list()  # Y = fn(X1, X2, ..)

    # l.append(('ITT', ['NG', 'TQR', 'SPR', 'NGR']))
    # l.append(('ITTR', ['NG', 'TQR', 'SPR', 'NGR']))

    # l.append(('ITTR', ['NGR', 'P0', 'T0']))   # lepsi 1+2
    # l.append(('ITT', ['NG', 'P0', 'T0']))

    # l.append(('ITTR', ['SPR', 'P0', 'T0']))   # lepsi 1; 21% vs 34
    # l.append(('ITT', ['SP', 'P0', 'T0']))     # lepsi 2; 0.1% vs 0.6%

    # l.append(('FCR', ['NGR', 'P0', 'T0']))
    # l.append(('FC', ['NG', 'P0', 'T0']))    # lepsi 1+2

    # l.append(('FCR', ['SPR', 'P0', 'T0']))
    # l.append(('FC', ['SP', 'P0', 'T0']))      # lepsi 1+2;

    l.append(('SPR', ['NGR', 'P0', 'T0']))  # lepsi 2; o chlup
    l.append(('SP', ['NG', 'P0', 'T0']))    # lepsi 1

    for yKey, xKeys in l:

        df = pd.DataFrame()
        allKeys = xKeys.copy()
        allKeys.append(yKey)

        # arr = np.zeros([numIntervals, len(xKeys) + 1])   # (x1, x2, .. , y)
        for row, interval in enumerate(intervals, start=0):
            startIndex = interval['startIndex']
            endIndex = interval['endIndex']

            sectionDf = dataFrame.iloc[startIndex:endIndex, :]

            df = df.append(sectionDf[allKeys])

        # and now do the regression:
        model, regressionCoefficients = doRegressionForKeys(df, originalFileName, yKey, xKeys, fileNameSuffix='')
        if not model:
            return False

        xVals = [NOMINAL_DATA[key] for key in xKeys]

        mins = df[xKeys].min()
        maxs = df[xKeys].max()

        # print(f"[INFO] REGRESSION in; {originalFileName}; of; {yKey} = fn ({xKeys}); {xVals}; into range; {mins:.02f}; {maxs:.02f}")
        #
        # if xVal < min or xVal > max:
        #     print(f"[WARN] Omitting; {yKey} = fn ({xKey}); {xVal} not in range <{min:.02f}, {max:.02f}>")
        #     continue

        # [v for k, v in NOMINAL_DATA.items() if k in xKeys]
        yVal = model.predict([xVals])[0]
        delta = yVal - NOMINAL_DATA[yKey]
        deltaPct = (yVal-NOMINAL_DATA[yKey])/NOMINAL_DATA[yKey] * 100

        unitRunId = originalFileName[:originalFileName.index('.')]
        print(f"PRED; {unitRunId}; {yKey} = fn ({','.join(xKeys)}); {yVal:.2f}; shall be; {NOMINAL_DATA[yKey]:.2f}; delta; {delta:.2f}; deltaPct; {deltaPct:.2f}")

        # unitId = unitRunId[:unitRunId.index('_')]
        # unitLogFilename = f"{unitId}-analyses.csv"

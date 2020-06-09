
import shutil
import pandas as pd
from pathlib import Path

from configuration import STEADY_STATE_WINDOW_LEN, STEADY_STATE_DVAL, CSV_DELIMITER

from dataSources.fileLoader import loadRawData
from fileUtils import loadSteadyStates, composeFilename2

from dataPreprocessing.channelSelection import channelSelection
from dataPreprocessing.dataFiltering import filterData
from dataPreprocessing.dataStandartisation import standardiseData
from dataPreprocessing.omitRows import omitRowsBelowThresholds

from dataAnalysis.steadyStatesDetector import SteadyStatesDetector
from dataAnalysis.regression import doRegressionOnSteadySectionsAvgXY, RegressionResult, doRegressionForKeys
from dataAnalysis.limitingStateDetector import detectLimitingStates
from dataAnalysis.ibiModel import IbiModel

from dao.configurationDao import getConfiguration
from dao.fileDao import File, FileStatus, getFileForProcessing, setFileStatus, listFiles, listFilesForNominalCalculation
from dao.regressionResultDao import saveRegressionResult, getRegressionResults


c = getConfiguration()
FILE_INGESTION_ROOT = c['FILE_INGESTION_ROOT']
FILE_STORAGE_ROOT = c['FILE_STORAGE_ROOT']

print("[INFO] FILE_INGESTION_ROOT:", FILE_INGESTION_ROOT)
print("[INFO] FILE_STORAGE_ROOT:", FILE_STORAGE_ROOT)


def checkForWork():
    file: File = getFileForProcessing()
    if not file:
        print("[INFO] No work")
        return None

    print(f"[INFO] Processing file id '{file.id}'")

    # TODO uncomment (!)
    # setFileStatus(file=file, status=FileStatus.UNDER_ANALYSIS)

    return file


def prepare(file: File):
    srcFilePath = f"{FILE_INGESTION_ROOT}/{file.id}"

    dstDir = f"{FILE_STORAGE_ROOT}/{file.id}"
    dstFilePath = f"{dstDir}/{file.name}"

    try:
        # create workdir in FILE_STORAGE_ROOT:
        print(f"[INFO]: mkdir '{dstDir}'")
        Path(dstDir).mkdir(parents=True, exist_ok=True)

        # cp file from FILE_STORAGE_ROOT to FILE_STORAGE_ROOT:
        print(f"[INFO]: cp '{srcFilePath}' '{dstFilePath}'")
        shutil.copy(src=srcFilePath, dst=dstFilePath, follow_symlinks=True)

    except FileNotFoundError as e:
        print(f"[ERROR] when copying file:\n ", str(e))
        return False

    return True


def process(file: File):
    inPath = f"{FILE_STORAGE_ROOT}/{file.id}"
    fileName = file.name

    rawDataFrame = loadRawData(inPath, fileName)
    rawDataFrame = channelSelection(rawDataFrame, fileName, outPath=inPath)

    if len(rawDataFrame) == 0:
        return True

    filteredDataFrame = filterData(rawDataFrame, fileName, outPath=inPath)
    detectLimitingStates(filteredDataFrame, fileName, outPath=inPath)

    standardisedDataFrame = standardiseData(filteredDataFrame, fileName, outPath=inPath)
    standardisedDataFrame = omitRowsBelowThresholds(standardisedDataFrame, fileName)

    SteadyStatesDetector(windowDt=STEADY_STATE_WINDOW_LEN, dVal=STEADY_STATE_DVAL).detectSteadyStates(standardisedDataFrame, fileName, outPath=inPath)


    # results: RegressionResult = doRegressionOnSteadySectionsAvgXY(dataFrame=standardisedDataFrame, originalFileName=fileName, outPath=inPath)
    # print("results:", results)
    #
    # for res in results:
    #     # TODO XXX save info db
    #     pass

    _calcRegressionDeltaForFile(file)


def _readReducedDataFromFile(file: File):
    """
    Reads reduced data from specified file.
    :param file:
    :return: dataFrame with reduced data
    """
    directory = f"{FILE_STORAGE_ROOT}/{file.id}"
    reducedDataFilePath = f"{directory}/" + composeFilename2(file.name, 'reduced', 'csv')
    df = pd.read_csv(reducedDataFilePath, delimiter=CSV_DELIMITER)
    return df


def _filterOutUnsteadyRecords(file: File, df: pd.DataFrame):
    ssDf = pd.DataFrame()

    # keep data points from within steady (ss) states only:
    directory = f"{FILE_STORAGE_ROOT}/{file.id}"
    ssIntervals = loadSteadyStates(originalFileName=file.name, ssDir=directory)
    for interval in ssIntervals:
        subDf = df.iloc[interval['startIndex']:interval['endIndex']]
        ssDf = ssDf.append(subDf)

    return ssDf


def calcNominalValues(engineId: int):
    NUM = 20
    files: File = listFilesForNominalCalculation(engineId=engineId, limit=NUM)
    # TODO uncomment (!)
    # if len(files) != NUM:
    #     print(f"[WARN] No enough files for nominal data calculation: {len(files)}; required: {NUM}")
    #     return

    # (1) load steady data from all files into one steady states dataframe (ssDf):
    ssDf = pd.DataFrame()
    for file in files:
        # (1a) read reduced dataFrame from file:
        df = _readReducedDataFromFile(file)
        df = _filterOutUnsteadyRecords(file=file, df=df)
        ssDf = ssDf.append(df)

    # (2) calculate regression curves:
    l = list()  # Y = fn(X)
    l.append(('NGR', 'SPR'))
    l.append(('ITTR', 'SPR'))
    l.append(('ITTR', 'NGR'))
    l.append(('FCR', 'SPR'))
    l.append(('FCR', 'NGR'))

    dir = f"{FILE_STORAGE_ROOT}/nominal-eid-{engineId}"
    Path(dir).mkdir(parents=True, exist_ok=True)

    for yKey, xKey in l:
        df = ssDf.copy()
        model, coeffs = doRegressionForKeys(dataFrame=df, originalFileName=f"eid-{engineId}.none",
                                            yKey=yKey, xKeys=[xKey], fileNameSuffix='', outPath=dir,
                                            saveDataToFile=False, plot=True)

        # (2b) use average x-value and calculate y-value from the regression curve:
        xVal = df[xKey].mean()
        yVal = model.predictVal(xVal)  # this is the nominal value for particular function y = fn(x)

        # (2c) store results into db:
        function = f"{yKey}-fn-{xKey}"
        nominalValue = yVal
        (a, b, c) = coeffs
        xMin = df[xKey].min()
        xMax = df[xKey].max()
        res = RegressionResult(id=None, ts=0, engineId=engineId, fileId=file.id, fn=function, val=nominalValue, a=a, b=b, c=c, xMin=xMin, xMax=xMax)
        saveRegressionResult(res=res, engineId=engineId)

    # (3) recalculate all regression results to these new nominal values:
    recalcAllRegressionResultsForEngine(engineId)


def _calcRegressionDeltaForFile(file: File):
    nominalRRs: dict = getRegressionResults(engineId=file.engineId, fileId=None)
    if len(nominalRRs.keys()) == 0:
        return  # no nominal values calculated (yet?)

    reducedDf = _readReducedDataFromFile(file)
    ssDf = _filterOutUnsteadyRecords(file=file, df=reducedDf)

    for function in nominalRRs.keys():
        yKey, _, xKey = function.split('-')

        xValue = ssDf[xKey].mean()
        xMin = ssDf[xKey].min()
        xMax = ssDf[xKey].max()

        nrr: RegressionResult = nominalRRs[function]
        print(f"[INFO] {function}: xValue = {xValue:.2f} into <{nrr.xMin:.2f}; {nrr.xMax:.2f}>")

        model = IbiModel(coefs=(nrr.a, nrr.b, nrr.c))
        yValue = model.predictVal(xValue)

        yDelta = yValue - nrr.val
        print(f"[INFO] nominal = {nrr.val:.2f}; yVal = {yValue:.2f}; yDelta = {yDelta:.5f}")

        # 'id', 'ts', 'engineId', 'fileId', 'fn', 'val', 'a', 'b', 'c', 'xMin', 'xMax'
        fileRR = RegressionResult(id=None, ts=int(reducedDf['ts'][0]), engineId=file.engineId, fileId=file.id, fn=function, val=yDelta,
                                  a=0, b=0, c=0, xMin=xMin, xMax=xMax)

        saveRegressionResult(res=fileRR, file=file)


def recalcAllRegressionResultsForEngine(engineId: int):
    """
    Recalculates regression results deltas by speficic nominal values for particular engine.
    :param engineId:
    :return:
    """

    files = listFiles(engineId=engineId)
    for file in files:
        # TODO uncomment(!)
        # if file.status != FileStatus.ANALYSIS_COMPLETE:
        #     continue    # ignore empty or failed files

        print(f"[INFO] Recalculation regression deltas for engineId: {engineId}; file.id: {file.id}")
        _calcRegressionDeltaForFile(file)


if __name__ == '__main__':
    # file: File = checkForWork()
    #
    # if file and prepare(file):
    #     process(file)
    #     # TODO uncomment (!)
    #     # setFileStatus(file=file, status=FileStatus.ANALYSIS_COMPLETE)

    # calcNominalValues(1)
    recalcAllRegressionResultsForEngine(1)

    print('KOHEU.')

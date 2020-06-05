
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

from dao.configurationDao import getConfiguration
from dao.fileDao import File, FileStatus, getFileForProcessing, setFileStatus, listFilesForNominalCalculation
from dao.regressionResultDao import saveRegressionResult


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

    SteadyStatesDetector(windowDt=STEADY_STATE_WINDOW_LEN, dVal=STEADY_STATE_DVAL).detectSteadyStates(filteredDataFrame, fileName, outPath=inPath)

    results: RegressionResult = doRegressionOnSteadySectionsAvgXY(dataFrame=standardisedDataFrame, originalFileName=fileName, outPath=inPath)
    print("results:", results)

    for res in results:
        # TODO XXX save info db
        pass


def calcNominalValues(engineId: int):
    NUM = 20
    files: File = listFilesForNominalCalculation(engineId=engineId, limit=NUM)
    # TODO uncomment (!)
    # if len(files) != NUM:
    #     print(f"[WARN] No enough files for nominal data calculation: {len(files)}; required: {NUM}")
    #     return

    # (1) load data from all files into one dataframe:
    ssDf = pd.DataFrame()

    for file in files:
        dir = f"{FILE_STORAGE_ROOT}/{file.id}"
        # (1a) read reduced data from file:
        reducedDataFilePath = f"{dir}/" + composeFilename2(file.name, 'reduced', 'csv')
        df = pd.read_csv(reducedDataFilePath, delimiter=CSV_DELIMITER)

        # (1b) keep data points from within steady (ss) states only:
        ssIntervals = loadSteadyStates(originalFileName=file.name, ssDir=dir)
        for interval in ssIntervals:
            subDf = df.iloc[interval['startIndex']:interval['endIndex']]
            ssDf = ssDf.append(subDf)

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
        res = RegressionResult(fn=function, ts=0, val=nominalValue, a=a, b=b, c=c, xMin=xMin, xMax=xMax)
        saveRegressionResult(res=res, engineId=engineId)

        # TODO recalculate all regression results to this new nominal


if __name__ == '__main__':
    # file: File = checkForWork()
    #
    # if file and prepare(file):
    #     process(file)
    #     # TODO uncomment (!)
    #     # setFileStatus(file=file, status=FileStatus.ANALYSIS_COMPLETE)

    calcNominalValues(1)

    print('KOHEU.')

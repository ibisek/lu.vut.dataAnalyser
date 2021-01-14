"""
Step #1:
    * reacts on notification in DB there is a new file to ingest.
    * pre-processes this file and creates related files and entries in DB & influx
"""

import os
import shutil
from time import sleep
import pandas as pd
from pathlib import Path
from typing import List

from configuration import STEADY_STATE_WINDOW_LEN, STEADY_STATE_DVAL, CSV_DELIMITER

from fileUtils import loadSteadyStates, composeFilename2

from data.preprocessing.channelSelection import channelSelection
from data.preprocessing.dataFiltering import filterData
from data.preprocessing.dataStandartisation import standardiseData
from data.preprocessing.omitRows import omitRowsBelowThresholds

from data.analysis.steadyStatesDetector import SteadyStatesDetector
from data.analysis.regression import RegressionResult, doRegressionForKeys, doRegressionOnSteadySectionsAvgXY
from data.analysis.limitingStateDetector import detectLimitingStates
from data.analysis.ibiModel import IbiModel

from data.sources.fileLoader import loadRawData
from data.structures import EngineWork

from plotting import plotChannelsOfInterestMultiY

from dao.configurationDao import getConfiguration
from db.dao.filesDao import File, FileStatus, FilesDao, FileFormat

from dao.regressionResultDao import saveRegressionResult, getRegressionResults
from dao.flightRecordingDao import FlightRecordingDao, RecordingType

from db.dao.enginesDao import EnginesDao
from db.dao.cyclesDao import CyclesDao
from db.dao.flightsDao import FlightsDao


dbConfiguration = getConfiguration()
FILE_INGESTION_ROOT = dbConfiguration['FILE_INGESTION_ROOT']
FILE_STORAGE_ROOT = dbConfiguration['FILE_STORAGE_ROOT']
print("[INFO] FILE_INGESTION_ROOT:", FILE_INGESTION_ROOT)
print("[INFO] FILE_STORAGE_ROOT:", FILE_STORAGE_ROOT)


def checkForWork():
    filesDao = FilesDao()

    file: File = filesDao.getFileForProcessing()
    if not file:
        print("[INFO] No work")
        return None

    print(f"[INFO] Initiating work on file id '{file.id}'")

    return file


def migrate(file: File):
    """
    Migratess specified file from upload into storage directory.
    It may happen the file has been moved in previous processing attempt, hence the check if the file exists in the storage_root.
    :param file:
    :return: True if the file is physically available in the storage_root
    """
    srcFilePath = f"{FILE_INGESTION_ROOT}/{file.id}"

    dstDir = f"{FILE_STORAGE_ROOT}/{file.id}"
    dstFilePath = f"{dstDir}/{file.name}"

    try:
        # create workdir in FILE_STORAGE_ROOT:
        print(f"[INFO] mkdir '{dstDir}'")
        Path(dstDir).mkdir(parents=True, exist_ok=True)

        # cp file from FILE_INGESTION_ROOT to FILE_STORAGE_ROOT:
        print(f"[INFO] cp '{srcFilePath}' '{dstFilePath}'")
        shutil.copy(src=srcFilePath, dst=dstFilePath, follow_symlinks=True)

    except FileNotFoundError as e:
        print(f"[ERROR] when copying file:\n ", str(e))

    # check existence in the destination dir:
    return os.path.exists(dstFilePath)


def preprocess(file: File) -> List[EngineWork]:
    inPath = f"{FILE_STORAGE_ROOT}/{file.id}"
    fileName = file.name

    if type(file.format) is int:
        file.format = FileFormat(file.format)

    rawDataFrame = loadRawData(fileFormat=file.format, inPath=inPath, fileName=fileName)
    rawDataFrames = channelSelection(fileFormat=file.format, dataFrame=rawDataFrame, originalFileName=fileName, outPath=inPath)

    if len(rawDataFrames) == 0:
        return []

    # fetch flightId for current file:
    flightId = FlightsDao.getFlightIdForFile(file.id)
    # fetch engine IDs for this raw flight instance:
    engineIds = EnginesDao().getEngineIdsForRawFlight(flightId)
    assert len(rawDataFrames) == len(engineIds)

    engineWorks: List[EngineWork] = []

    for engineIndex, rawDataFrame in enumerate(rawDataFrames, start=1):
        engineId = engineIds[engineIndex-1]

        filteredDataFrame = filterData(rawDataFrame, fileName, outPath=inPath)
        detectLimitingStates(filteredDataFrame, fileName, outPath=inPath)

        standardisedDataFrame = standardiseData(filteredDataFrame, fileName, outPath=inPath)
        standardisedDataFrame = omitRowsBelowThresholds(standardisedDataFrame, fileName)

        # create new cycle for per engine record (or replace existing by empty one)
        cycleDao = CyclesDao()
        cycle = cycleDao.createNew()
        oldCycle = cycleDao.getOne(idx=0, flight_id=flightId, engine_id=engineId)
        if oldCycle:
            cycle.id = oldCycle.id
        cycle.file_id = file.id
        cycle.engine_id = engineId
        cycle.flight_id = flightId
        cycleDao.save(cycle)
        print(f"[INFO] Created new cycle if {cycle.id} for flight id {flightId} on engine id {engineId}")

        flightIdx = 0
        cycleIdx = 0
        frDao = FlightRecordingDao()
        print(f"[INFO] Storing flight recordings into influx..", end='')
        frDao.storeDf(engineId=engineId, flightId=flightId, flightIdx=flightIdx, cycleId=cycle.id, cycleIdx=cycleIdx, df=rawDataFrame, recType=RecordingType.RAW)
        frDao.storeDf(engineId=engineId, flightId=flightId, flightIdx=flightIdx, cycleId=cycle.id, cycleIdx=cycleIdx, df=filteredDataFrame, recType=RecordingType.FILTERED)
        frDao.storeDf(engineId=engineId, flightId=flightId, flightIdx=flightIdx, cycleId=cycle.id, cycleIdx=cycleIdx, df=standardisedDataFrame, recType=RecordingType.STANDARDIZED)
        print(f" flushing.. ", end='')
        while not frDao.queueEmpty():
            print('#', end='')
            sleep(1)    # wait until the data is stored in influx; is has been causing problems when requesting early retrieval
        print(f" done.")

        engineWorks.append(EngineWork(engineId=engineId, flightId=flightId, flightIdx=flightIdx, cycleId=cycle.id, cycleIdx=cycleIdx))

        # TODO the remaining analyses (LU.VUT) are not run at this stage of development
        # continue

        SteadyStatesDetector(windowDt=STEADY_STATE_WINDOW_LEN, dVal=STEADY_STATE_DVAL).detectSteadyStates(filteredDataFrame, fileName, outPath=inPath, engineIndex=engineIndex)
        # steadyStates = loadSteadyStates(originalFileName=fileName, ssDir=inPath, engineIndex=engineIndex)
        # if len(steadyStates) == 0:
        #     FilesDao.setFileStatus(file=file, status=FileStatus.NO_STEADY_STATES)
        #     continue

        # save data from steady states and with NG>=NG_THRESHOLD to file:
        ssDf = _filterOutUnsteadyRecords(file, standardisedDataFrame)
        if len(ssDf) > 0:
            fn = composeFilename2(file.name, 'steadyStatesData', 'csv', engineIndex=engineIndex)
            fp = f"{inPath}/{fn}"
            print(f"[INFO] Writing detected steady states data to '{fp}'")
            ssDf.to_csv(fp, sep=';', encoding='utf_8')

        plotChannelsOfInterestMultiY(dataFrame=standardisedDataFrame, originalFileName=fileName, suffix='flightOverview-reduced',
                                     reducedChannels=True, outPath=inPath, engineIndex=engineIndex)

        results: RegressionResult = doRegressionOnSteadySectionsAvgXY(dataFrame=standardisedDataFrame, originalFileName=fileName, outPath=inPath)
        # print("results:", results)
        for res in results:
            print('[INFO] Regression result:', str(res))
            saveRegressionResult(res=res, file=file, engineId=engineId)

        calcRegressionDeltaForFile(file=file, engineId=engineId)

    return engineWorks


def _readReducedDataFromFile(file: File):
    """
    Reads reduced data from specified file.
    :param file:
    :return: dataFrame with reduced data
    """
    directory = f"{FILE_STORAGE_ROOT}/{file.id}"
    reducedDataFilePath = f"{directory}/" + composeFilename2(file.name, 'reduced', 'csv')
    df = pd.read_csv(reducedDataFilePath, delimiter=CSV_DELIMITER)

    df = omitRowsBelowThresholds(df, reducedDataFilePath)

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
    NUM = 50
    files: File = FilesDao.listFilesForNominalCalculation(engineId=engineId, limit=NUM)
    # TODO uncomment (!)
    if len(files) != NUM:
        print(f"[WARN] No enough files for nominal data calculation: {len(files)}; required: {NUM}")
        return

    # (1) load steady data from all files into one steady states dataframe (ssDf):
    ssDf = pd.DataFrame()
    for file in files:
        # (1a) read reduced dataFrame from file:
        df = _readReducedDataFromFile(file)
        df = _filterOutUnsteadyRecords(file=file, df=df)
        ssDf = ssDf.append(df)

    # (2) calculate regression curves:
    l = list()  # Y = fn(X)
    l.append(('SPR', 'NGR'))
    l.append(('ITTR', 'SPR'))
    l.append(('ITTR', 'NGR'))
    l.append(('FCR', 'SPR'))
    l.append(('FCR', 'NGR'))
    l.append(('FCR', 'ITTR'))

    dir = f"{FILE_STORAGE_ROOT}/nominal-engineId-{engineId}"
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
        (a, b, c) = coeffs
        xMin = df[xKey].min()
        xMax = df[xKey].max()
        res = RegressionResult(id=None, ts=0, engineId=engineId, fileId=file.id, fn=function,
                               xValue=xVal, yValue=yVal, delta=0,
                               a=a, b=b, c=c, xMin=xMin, xMax=xMax)
        saveRegressionResult(res=res, engineId=engineId)

    # (3) recalculate all regression results to these new nominal values:
    recalcAllRegressionResultsForEngine(engineId)


def calcRegressionDeltaForFile(file: File, engineId: int):
    """
    Calculates delta from nominal values for each available function.
    :param file:
    :param engineId:
    :return: True if delta was calculated
    """

    nominalRRs: dict = getRegressionResults(engineId=engineId, fileId=None)
    if len(nominalRRs.keys()) == 0:
        return  # no nominal values calculated (yet?)

    reducedDf = _readReducedDataFromFile(file)
    ssDf = _filterOutUnsteadyRecords(file=file, df=reducedDf)

    if len(ssDf) == 0:
        print(f"[WARN] No steady states (SS) for file if {file.id}!")
        return False

    for function in nominalRRs.keys():
        yKey, _, xKey = function.split('-')

        xValue = ssDf[xKey].mean()
        xMin = ssDf[xKey].min()
        xMax = ssDf[xKey].max()

        # calc regression for specific file and keys:
        ssDf = ssDf.copy()
        model, _ = doRegressionForKeys(dataFrame=ssDf, originalFileName=f"eid-{engineId}.none",
                                       yKey=yKey, xKeys=[xKey], fileNameSuffix='', outPath=dir,
                                       saveDataToFile=False, plot=False)

        yValueCurrentFile = model.predictVal(xValue)  # this is the nominal value for particular function y = fn(x)

        # put file's xVal into nominal function:
        nrr: RegressionResult = nominalRRs[function]
        print(f"[INFO] {function}: xValue = {xValue:.2f} into <{nrr.xMin:.2f}; {nrr.xMax:.2f}>")
        nominalModel = IbiModel(coefs=(nrr.a, nrr.b, nrr.c))
        yValueNominal = nominalModel.predictVal(xValue)

        yDelta = yValueNominal - yValueCurrentFile
        print(f"[INFO] nominal = {nrr.yValue:.2f}; yVal = {yValueNominal:.2f}; yDelta = {yDelta:.5f}")

        # 'id', 'ts', 'engineId', 'fileId', 'fn', 'val', 'a', 'b', 'c', 'xMin', 'xMax'
        fileRR = RegressionResult(id=None, ts=int(reducedDf['ts'].iloc[0]), engineId=engineId, fileId=file.id, fn=function,
                                  xValue=xValue, yValue=yValueCurrentFile, delta=yDelta,
                                  a=model.a, b=model.b, c=model.c, xMin=xMin, xMax=xMax)

        saveRegressionResult(res=fileRR, file=file)

    return True


def recalcAllRegressionResultsForEngine(engineId: int):
    """
    Recalculates regression results deltas FOR ALL FILES by specific pre-calculated nominal values for particular engine.
    :param engineId:
    :return:
    """

    files = FilesDao.listFiles(engineId=engineId)
    for file in files:
        # TODO uncomment(!)
        if file.status != FileStatus.ANALYSIS_COMPLETE:
            continue    # ignore empty or failed files

        print(f"[INFO] Recalculation regression deltas for engineId: {engineId}; file.id: {file.id}")
        calcRegressionDeltaForFile(file)


if __name__ == '__main__':
    while True:
        # file: File = checkForWork()

        from db.dao.filesDao import FilesDao
        filesDao = FilesDao()
        file = filesDao.getOne(id=2182)

        if not file:
            break

        res = migrate(file)
        if not res:
            break

        from flow.fileFormatIdentification import FileFormatDetector
        FileFormatDetector.identify(file)

        engineWorks: List[EngineWork] = preprocess(file)
        for ew in engineWorks:
            print(f"## ew:", ew)

        break

    # ENGINE_ID = 1
    # calcNominalValues(ENGINE_ID)
    # recalcAllRegressionResultsForEngine(ENGINE_ID)

    print('KOHEU.')

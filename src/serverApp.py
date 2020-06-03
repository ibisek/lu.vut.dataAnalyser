
import shutil
from pathlib import Path

from configuration import STEADY_STATE_WINDOW_LEN, STEADY_STATE_DVAL

from dataSources.fileLoader import loadRawData

from dataPreprocessing.channelSelection import channelSelection
from dataPreprocessing.dataFiltering import filterData
from dataPreprocessing.dataStandartisation import standardiseData
from dataPreprocessing.omitRows import omitRowsBelowThresholds

from dataAnalysis.steadyStatesDetector import SteadyStatesDetector
from dataAnalysis.regression import doRegressionOnSteadySectionsAvgXY

from dao.configurationDao import getConfiguration
from dao.fileDao import File, FileStatus, getFileForProcessing, setFileStatus

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
    # detectLimitingStates(rawDataFrame, fileName)    # limiting states detection on filtered data!

    standardisedDataFrame = standardiseData(filteredDataFrame, fileName, outPath=inPath)
    standardisedDataFrame = omitRowsBelowThresholds(standardisedDataFrame, fileName)

    SteadyStatesDetector(windowDt=STEADY_STATE_WINDOW_LEN, dVal=STEADY_STATE_DVAL).detectSteadyStates(filteredDataFrame, fileName, outPath=inPath)

    doRegressionOnSteadySectionsAvgXY(dataFrame=standardisedDataFrame, originalFileName=fileName, outPath=inPath)


if __name__ == '__main__':
    file: File = checkForWork()

    if file and prepare(file):
        process(file)

        # TODO store results somewhere, somehow

        # TODO uncomment (!)
        # setFileStatus(file=file, status=FileStatus.ANALYSIS_COMPLETE)

    print('KOHEU.')

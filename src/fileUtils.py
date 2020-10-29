
import os
import json
import pandas as pd

from configuration import OUT_PATH

from data.analysis.steadyStatesDetector import SteadyStatesDetector


def loadSteadyStates(originalFileName: str, ssDir: str = None):
    """
    :param originalFileName:
    :param ssDir
    :return: list of intervals of steady states (from a json file)
    """
    intervals = []
    ssFileName = SteadyStatesDetector.getFilename(originalFileName)
    ssFilePath = f"{ssDir}/{ssFileName}"

    try:
        with open(ssFilePath, 'r') as f:
            jsonStr = "".join(f.readlines())
            j = json.loads(jsonStr)
            intervals = j['intervals']
    except Exception as ex:
        print(f"[ERROR] when loading steady states from '{ssFilePath}':\n" + str(ex))
        return []

    # convert time-fields from str to Timestamp:
    for interval in intervals:
        interval['startTime'] = pd.to_datetime(interval['startTime'], format="%Y-%m-%d %H:%M:%S")
        interval['endTime'] = pd.to_datetime(interval['endTime'], format="%Y-%m-%d %H:%M:%S")

    return intervals


def composeFilename2(originalFileName, postfix, extension):
    fn = originalFileName[:originalFileName.index('.')]
    fn = f"{fn}-{postfix}.{extension}"

    return fn


def composeFilename(originalFileName, postfix, extension):
    raise NotImplementedError()

    unitRunId = originalFileName[:originalFileName.index('.')]
    engineId = ''
    if '_' in unitRunId:
        engineId = unitRunId[:unitRunId.index('_')]

    outDir = f"{OUT_PATH}/{engineId}"
    if not os.path.exists(outDir):
        os.mkdir(outDir)

    # fn = OUT_PATH + unitRunId + '-' + f"{yKey}=fn({xKeysStr})" + fileNameSuffix + '.png'
    fn = f"{outDir}/{unitRunId}-{postfix}.{extension}"

    return fn

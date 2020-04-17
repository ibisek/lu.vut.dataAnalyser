
import os
import json
import pandas as pd

from configuration import OUT_PATH

from dataAnalysis.steadyStatesDetector import SteadyStatesDetector


def loadSteadyStates(originalFileName: str):
    """
    :param originalFileName:
    :return: list of intervals of steady states (from a json file)
    """
    intervals = []
    fn = SteadyStatesDetector.getFilename(originalFileName)
    try:
        with open(fn, 'r') as f:
            jsonStr = "".join(f.readlines())
            j = json.loads(jsonStr)
            intervals = j['intervals']
    except Exception as ex:
        print(f"[ERROR] when loading steady states from '{fn}':\n" + str(ex))
        return []

    # convert time-fields from str to Timestamp:
    for interval in intervals:
        interval['startTime'] = pd.to_datetime(interval['startTime'], format="%Y-%m-%d %H:%M:%S")
        interval['endTime'] = pd.to_datetime(interval['endTime'], format="%Y-%m-%d %H:%M:%S")

    return intervals


def composeFilename(originalFileName, postfix, extension):
    unitRunId = originalFileName[:originalFileName.index('.')]
    engineId = unitRunId[:unitRunId.index('_')]

    outDir = f"{OUT_PATH}/{engineId}"
    if not os.path.exists(outDir):
        os.mkdir(outDir)

    # fn = OUT_PATH + unitRunId + '-' + f"{yKey}=fn({xKeysStr})" + fileNameSuffix + '.png'
    fn = f"{outDir}/{unitRunId}-{postfix}.{extension}"

    return fn

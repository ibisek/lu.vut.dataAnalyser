"""
Detects limiting states / crossing limiting boundaries on selected channels.

* Tq / Torque: >106%; 100% Tq = 2740Nm -> 106% = 2904 Nm
* Ng / generator RPM: >101.5% nominal; 100% Ng = 36660 RPM -> 101.5% = 37210
* Np / propeller RPM: > 2080 RPM
"""

import json
from configuration import OUT_PATH

TQ_LIMIT = 2904
NG_LIMIT = 101.5
NP_LIMIT = 2080

# TQ_KEY = 'Mk (Nm)'
# NG_KEY = 'nG (%)'
# NP_KEY = 'nV (1/min)'
TQ_KEY = 'TQ'
NG_KEY = 'NG'
NP_KEY = 'NP'


def _findOverrunIntervals(dataFrame, key, limit):
    """
    :param dataFrame:
    :param key: channel/series key/name
    :param limit: value limit
    :return: list of (from, to, maxVal)
    """
    df = dataFrame[dataFrame[key] > limit][key]     # data series with values above limit only
    intervals = []  # overrun intervals

    if len(df) > 0:     # if there are any at all
        intervalStart = df.index[0]
        maxVal = 0
        for i in range(1, len(df)):
            if df[i] > maxVal:
                maxVal = df[i]
            dt = (df.index[i] - df.index[i - 1]).seconds

            if dt > 10:
                intervals.append((intervalStart, df.index[i - 1], maxVal))  # the previous data point is the end of the interval
                intervalStart = df.index[i]     # .. and this is the new start

        intervals.append((intervalStart, df.index[-1], maxVal))  # till the end

    return intervals


def _limitOverrunsAsFormattedList(name, limitOverrunsList):
    if len(limitOverrunsList) == 0:
        return None

    l = list()
    for item in limitOverrunsList:
        (start, end, maxVal) = item
        d = dict()
        d["start"] = str(start)
        d["end"] = str(end)
        d["maxVal"] = maxVal
        d["duration"] = (end - start).seconds
        l.append(d)

    d = dict()
    d["name"] = name
    d["overruns"] = l

    return d


def detectLimitingStates(dataFrame, originalFileName, outPath=OUT_PATH):
    print(f"[INFO] Detecting states over limits in '{originalFileName}'..")

    # data exceeding nG limit:
    tqLimitOverruns = _findOverrunIntervals(dataFrame, TQ_KEY, TQ_LIMIT)
    ngLimitOverruns = _findOverrunIntervals(dataFrame, NG_KEY, NG_LIMIT)
    npLimitOverruns = _findOverrunIntervals(dataFrame, NP_KEY, NP_LIMIT)

    l = list()

    tqList = _limitOverrunsAsFormattedList(TQ_KEY, tqLimitOverruns)
    if tqList:
        l.append(tqList)

    ngList = _limitOverrunsAsFormattedList(NG_KEY, ngLimitOverruns)
    if ngList:
        l.append(ngList)

    npList = _limitOverrunsAsFormattedList(NP_KEY, npLimitOverruns)
    if npList:
        l.append(npList)

    if len(l) > 0:
        j = json.dumps(l, indent=2)

        fn = OUT_PATH + originalFileName[:originalFileName.rindex('.')] + '-limitsOverruns.json'
        fp = f"{outPath}/{fn}"
        with open(fp, 'w') as f:
            f.write(j)

"""
Detects steady states for specified time window.
"""

import os
import json
import numpy as np
from math import isnan
from configuration import OUT_PATH, KEYS_FOR_STEADY_STATE_DETECTION
import fileUtils


class SteadyStatesDetector(object):
    dataFrame = None
    originalFileName = None

    def __init__(self, windowDt=30, dVal=0.01):
        """
        @:param windowDt: starting window for steady sample [s]
        @:param dVal: value difference from mean of the window. 0.02 = +/-1%(mean)
        """

        self.windowDt = windowDt
        self.dVal = dVal

    def _findEndIndex(self, series, startIndex):
        """
        @:return endIndex for given time window; meaning tEnd-tStart <= windowDt
        """
        endIndex = 0
        start = series.index[startIndex]
        for j in range(startIndex + 1, len(series) - 1):
            end = series.index[j]
            dt = (end - start).seconds
            if dt > self.windowDt or j == len(series)-1:
                endIndex = j
                break

        return endIndex

    def _isSteadyInterval(self, key, startIndex):
        """
        :param key: key of a channel
        :param startIndex:
        :return: (steady, endIndex) of the window on specified channel.
                The window interval may get extended as long as the steady
                conditions are met.
        """
        s = self.dataFrame[key]
        n = len(self.dataFrame)

        endIndex = self._findEndIndex(s, startIndex)
        if endIndex == 0:
            return False, 0

        isSteady = True
        extendedRange = False
        while True:
            values = s[startIndex:endIndex].values
            if len(values) > 0:
                minVal = np.min(values)
                maxVal = np.max(values)
                avgVal = np.average(values)

                if isnan(minVal) or isnan(maxVal) or isnan(avgVal):
                    return False, 0

                if minVal < avgVal * (1 - self.dVal/2) or maxVal > avgVal * (1 + self.dVal/2):
                    if not extendedRange:
                        return False, 0
                    else:
                        isSteady = True     # is steady in the shorter interval
                        endIndex -= 1       # with the previous it was still within range
                        break

                extendedRange = True

            if endIndex < n-1:
                endIndex += 1
            else:
                break

        return isSteady, endIndex

    def _areSteadyIntervals(self, keys, startIndex):
        """
        Just calls _isSteadyInterval() for multiple keys
        Breaks the search once any of the channels is not steady at least within the minimal window.
        :param keys:
        :param startIndex:
        :return:
        """
        endIndexes = list()
        for key in keys:
            isSteady, endIndex = self._isSteadyInterval(key, startIndex)

            if not isSteady:
                return None

            endIndexes.append(endIndex)

        return endIndexes

    def _getSteadyInterval(self, keys, startIndex):
        """
        Finds steady intervals for multiple keys / channels.
        :param keys:
        :param startIndex:
        :return: List of endindexes for all channels; None if at least one of the channels is not steady.
        """
        endIndexes = self._areSteadyIntervals(keys, startIndex)
        if endIndexes:  # is null if one is not steady
            # print('endIndexes:', endIndexes)
            endIndex = min(endIndexes)  # take the shortest interval -common for all
            return endIndex

        return None

    def detectSteadyStates(self, dataFrame, originalFileName):
        """
        :param dataFrame:
        :param originalFileName: used for saving output to a file
        :return: nix
        """
        self.dataFrame = dataFrame
        self.originalFileName = originalFileName

        print(f"[INFO] Detecting steady states in '{originalFileName}'..")
        # print(self.dataFrame.head())

        fn = self.getFilename(originalFileName)
        if os.path.exists(fn):
            print('  - already detected')
            return  # do not re-detect

        # Kanaly ze zkusebnovych dat:
        # -- OLD --
        # [0] Ng
        # [2] Tq / Mk
        # [3]  FF / Q prutok paliva
        # [15] t4 = ITT
        # [21] p0 vnejsi tlak
        # [26] pt tlak paliva do trysky
        # --
        # [?] alt - vyska letu
        # [?] indikovana rychlost
        # -- NEW --
        # ['NG', 'TQ', 'FC', 'ITT', 'p0', 'pt', 't1', 'NP']

        # keyIndexes = (0, 1, 2, 3, 4, 5)
        # try:
        #     keys = [self.dataFrame.keys()[i] for i in keyIndexes]
        # except Exception:
        #     print("[ERROR] Some key(s) are missing!")
        #     return
        keys = KEYS_FOR_STEADY_STATE_DETECTION

        results = list()
        startIndex = 0
        while startIndex < len(self.dataFrame) - 10:    # 10: there just needs to be some data points at the end
            endIndex = self._getSteadyInterval(keys, startIndex)
            if endIndex:    # all channels are stable
                dt = dataFrame.index[endIndex] - dataFrame.index[startIndex]
                print(f"idx: {startIndex} -> {endIndex}; {endIndex - startIndex} data points")
                print(f"{dataFrame.index[startIndex]}\n{dataFrame.index[endIndex]}\n => {dt.seconds} sec.")

                # remove few points from beginning and aend of the interval:
                numPoints = endIndex - startIndex
                if numPoints > 10:
                    startIndex += 2
                    endIndex -= 2

                numPoints = endIndex - startIndex
                if numPoints >= 4:  # ignore data-sparse intervals:
                    d = dict()
                    d["startIndex"] = startIndex
                    d["endIndex"] = endIndex
                    d["startTime"] = str(dataFrame.index[startIndex])
                    d["endTime"] = str(dataFrame.index[endIndex])
                    d["duration"] = dt.seconds
                    results.append(d)

                startIndex = endIndex + 1

            else:
                startIndex += 1

        d = dict()
        d["configuration"] = {
            "windowDt": self.windowDt,
            "dVal": self.dVal,
            "fileName": originalFileName,
            "columnKeys": keys,
            "channels": keys}
        d["intervals"] = results

        j = json.dumps(d, indent=2)

        fn = self.getFilename(originalFileName)
        print(f"Writing detected steady states to '{fn}'")
        with open(fn, 'w') as f:
            f.write(j)

    @staticmethod
    def getFilename(originalFileName):
        return fileUtils.composeFilename(originalFileName, 'steadyStates', 'json')

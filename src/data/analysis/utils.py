
from pandas import Series

from data.structures import FlightMode, Interval


def findIntervals(s: Series, aboveVal, minDuration: int = 0) -> Interval:
    intervals = []
    startTs = endTs = None
    for i in range(len(s)):
        if not startTs and s.iloc[i] > aboveVal:
            startTs = s.index[i]

        if startTs and s.iloc[i] < aboveVal:
            endTs = s.index[i]
            duration = (endTs - startTs).seconds
            if duration > minDuration:
                intervals.append(Interval(start=startTs, end=endTs))

            startTs = endTs = None

    if startTs and not endTs:
        endTs = s.tail(1).index[0]
        intervals.append(Interval(start=startTs, end=endTs))

    return intervals

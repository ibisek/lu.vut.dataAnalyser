"""
influx:
    select * from flights where engine_id='2' and flight_id='2' and cycle_id='2' and type='fil' limit 10

TODO az na to budou data:
TODO (4) opakovane spousteni:  NG < 40% a pak zase NG na 60%; L410: NG=57% && NP <240-480> (pro PT6 neresit)
"""

import math
from datetime import timedelta
from pandas import DataFrame, Series, Timestamp

import matplotlib.pyplot as plt
from typing import List

from data.analysis.utils import findIntervals
from data.structures import Interval, EngineWork
from dao.flightRecordingDao import FlightRecordingDao, RecordingType
from dao.engineLimits import EngineLimits


def detectFlights(df: DataFrame) -> List[Interval]:
    """
    Takeoff and climb intervals cannot be reliably used for flights separation
    due to its unrealistically set conditions. Hence this workaround.
    :param df:
    :return:
    """
    FLIGHT_MIN_DURATION = 120   # [s]
    IAS_THR = 60                # [km/h]
    NG_THR = 60                 # [%]

    iasKey = 'IAS' if 'IAS' in df.keys() else 'TAS'

    flights: List[Interval] = findIntervals(df[iasKey], IAS_THR, FLIGHT_MIN_DURATION)

    if len(flights) > 0:
        for flight in flights:
            tmpDf = df[:flight.start].loc[df['NG'] < NG_THR]
            if tmpDf.empty:
                continue
            flight.start = tmpDf.tail(1).index[0]
            flight.end += timedelta(seconds=10)

    return flights


def _findLandingAfter(df: DataFrame, afterIndexTs: Timestamp):
    """
    Finds next landing (IAS = 0) after specified index ts.

    :param df:
    :param afterIndexTs:
    :return: index ts
    """
    tempDf = df.copy(deep=True)[afterIndexTs:]
    iasKey = 'IAS' if 'IAS' in df.keys() else 'TAS'

    tempDf2 = tempDf.loc[tempDf[iasKey] <= 0.1]
    if not tempDf2.empty:
        return tempDf2.index[0]  # == 0 does not work

    return None


def _findClimbEndAfter(df: DataFrame, afterIndexTs: Timestamp):
    """
    :param df:
    :param afterIndexTs:
    :return: ts of take-off end (decrease from peak NG after take-off start by 2%)
    """
    ngMax = 0
    for index, row in df[afterIndexTs:].iterrows():
        ng = row['NG']

        if ng > ngMax:
            ngMax = ng

        if ng < ngMax * 0.96 and row['dALT'] <= 1:  # [m/s]
            tsTakeOffIndexEnd = index
            return tsTakeOffIndexEnd

    return None


def detectTakeOffs(df: DataFrame, ngStart=100.1, ngEnd=100.1) -> List[Interval]:
    """
    Detection of TAKE-OFF window/interval.
    Ng>100,1% po dobu delší jak 10 sec, až po pokles pod 100,1%
    start: NG >= 100,1%
    end: NG < 100,1%
    duration min: 10s
    :param df:
    :param ngStart
    :param ngEnd
    :return:
    """

    TO_MIN_DURATION = 10  # [s]

    df = df.copy(deep=True)
    iasKey = 'IAS' if 'IAS' in df.keys() else 'TAS'

    takeOffs: List[Interval] = []

    numSuchDataPoints = len(df.loc[df['NG'] > ngStart])
    if numSuchDataPoints >= TO_MIN_DURATION:
        doLoop = True
        tsTakeOffIndexStart = df.loc[df['NG'] > ngStart].index[0]
        while doLoop:
            df = df[tsTakeOffIndexStart:]  # df starting from the moment of takeoff

            tsTakeOffIndexEnd = df.loc[df['NG'] < ngEnd].index[0]
            if not tsTakeOffIndexStart:
                doLoop = False

            else:
                duration = (tsTakeOffIndexEnd - tsTakeOffIndexStart).seconds
                if duration < TO_MIN_DURATION:
                    df = df[tsTakeOffIndexEnd:]     # chop off the df from this point
                    tsTakeOffIndexStart = df.loc[df['NG'] > ngStart].index[0]   # find new start
                    continue

                interval = Interval(start=tsTakeOffIndexStart, end=tsTakeOffIndexEnd)
                takeOffs.append(interval)

                tsTakeOffIndexStart = None
                df = df[tsTakeOffIndexEnd:]

    return takeOffs


def detectClimbs(df: DataFrame) -> List[Interval]:
    """
    Detection of CLIMB (after take-off) window/interval.
    start: IAS (TAS) > 10 km/h
    end: NG = 0.98NG_max

    :param df:
    :return: [climbStartindex, climbEndIndex]
    """

    x = df.copy(deep=True)
    iasKey = 'IAS' if 'IAS' in df.keys() else 'TAS'

    TO_START_IAS_DELTA = 4  # [km/h]
    # TO_START_IAS_THRESHOLD = 20  # [km/h]
    # tmpDf = x.loc[df[iasKey] > TO_START_IAS_THRESHOLD]
    # if tmpDf.empty:
    #     return []
    # tsClimbIndexStart = tmpDf.index[0]

    TO_START_IAS_THRESHOLD = 50     # [km/h]
    TO_START_NG_THRESHOLD = 80      # [%]
    # TO_START_dALT_THRESHOLD = 1     # [m/s]
    x['dALT'] = x['ALT'].diff().rolling(6, center=True).mean()
    # x['dIAS'] = x[iasKey].diff().rolling(6, center=True).mean()
    # tmpDf = x.loc[x['dALT'] >= TO_START_dALT_THRESHOLD].loc[x['NG'] >= TO_START_NG_THRESHOLD].loc[x[iasKey] >= TO_START_IAS_THRESHOLD]
    tmpDf = x.loc[x['NG'] >= TO_START_NG_THRESHOLD].loc[x[iasKey] >= TO_START_IAS_THRESHOLD]
    if tmpDf.empty:
        return []
    tsClimbIndexStart = tmpDf.index[0]

    climbs: List[Interval] = list()
    doLoop = True
    while doLoop:
        x = x[tsClimbIndexStart:]  # df starting from the moment of takeoff

        tsClimbIndexEnd = _findClimbEndAfter(x, tsClimbIndexStart)
        if not tsClimbIndexStart or not tsClimbIndexEnd:
            doLoop = False

        else:
            interval = Interval(start=tsClimbIndexStart, end=tsClimbIndexEnd)
            climbs.append(interval)

            # plot the takeoff section:
            # x = x[:tsClimbIndexEnd]
            # x['dIAS'] = df[iasKey].diff() * 10
            # x['TO_dIAS'] = x['dIAS'].apply(lambda x: 1 if x > TO_START_IAS_DELTA else 0)
            # x['ALTx'] = x['ALT'] / 10
            # x['dALT'] = x['ALT'].diff() * 10
            # x['TO'] = x[iasKey].apply(lambda x: 100 if x > 0 else 0)
            # x[[iasKey, 'TO', 'NG', 'ALTx', 'dALT', 'dIAS']].plot()
            # plt.show()

            tsLanding = _findLandingAfter(x, tsClimbIndexEnd)  # start searching from this ts again
            if not tsLanding:
                doLoop = False
            else:
                tmpDf1 = x[tsLanding:]  # chop the previous data away
                tmpDf2 = tmpDf1.loc[x[iasKey] > TO_START_IAS_THRESHOLD]
                if len(tmpDf2.index) == 0:
                    doLoop = False
                else:
                    tsClimbIndexStart = tmpDf2.index[0]

    # x[['ALT', 'dALT', 'NG', iasKey]].plot()
    return climbs


def detectRepeatedTakeOffs(df: DataFrame, climbIntervals: List[Interval]) -> List[Interval]:
    """
    Detection of repeated TAKE-OFF window/interval.
    start: IAS (TAS) < 80kt && GS >> 0
    end: NG = 0.98NG_max

    :param df:
    :param climbIntervals:
    :param takeOffs:
    :return: Interval
    """
    if len(climbIntervals) == 0:
        return []

    firstTakeOffTs = climbIntervals[0].start
    lastLandingTs = climbIntervals[len(climbIntervals) - 1].end
    df = df[firstTakeOffTs: lastLandingTs]

    RTO_START_IAS_THRESHOLD_HIGH = 80 * 1.852  # [kt] -> [km/h]
    RTO_START_IAS_THRESHOLD_LOW = 50 * 1.852  # [kt] -> [km/h]

    iasKey = 'IAS' if 'IAS' in df.keys() else 'TAS'

    repeatedTakeoffs: List[Interval] = []

    wasAboveThr = False
    isBelowThr = False
    ngGtThr = False
    rptToStartTs = None
    rptToEndTs = None
    # for index, row in df.iterrows():
    for i in range(len(df)):
        row = df.iloc[i]

        if not wasAboveThr and row[iasKey] > RTO_START_IAS_THRESHOLD_HIGH:
            wasAboveThr = True
        # if row[iasKey] < RTO_START_IAS_THRESHOLD_LOW:
        #     wasAboveThr = False

        isBelowThr = True if wasAboveThr and row[iasKey] < RTO_START_IAS_THRESHOLD_HIGH else False
        ngGtThr = True if wasAboveThr and isBelowThr and row['NG'] > 80 else False  # it was fast, then slowed down, but NG is high

        if ngGtThr:
            rptToStartTs = row.name

            # if in the next 60s we don't see landing (IAS < low thr), this is beginning of repeated takeoff
            sampleSpacing = (df.iloc[i + 1].name - df.iloc[i].name).seconds
            x = df[rptToStartTs:].head(int(1 / sampleSpacing * 60))
            x = x[x[iasKey] < RTO_START_IAS_THRESHOLD_LOW]
            if len(x) != 0:  # there is landing after this NG spike
                wasAboveThr = False
                continue

            # find repeated take-off end:
            rptToEndTs = _findClimbEndAfter(df, rptToStartTs)
            if rptToEndTs:
                repeatedTakeoffs.append(Interval(start=rptToStartTs, end=rptToEndTs))
                wasAboveThr = False  # initiate new RTO search

    return repeatedTakeoffs


def detectTaxi(df: DataFrame) -> List[Interval]:
    """
    Detection of TAXIing.
    GS in <min, max>
    len >= 20s

    :param df:
    :return:
    """

    x = df.copy(deep=True)

    TAXI_LOW_SPEED_THR = 10  # [km/h]
    TAXI_HIGH_SPEED_THR = 50  # [km/h]
    TAXI_MIN_DURATION = 20  # [s]

    gsKey = 'GS'
    if 'GS' not in df.keys():   # some buggers don't have GS in the data
        gsKey = 'IAS' if 'IAS' in df.keys() else 'TAS'

    x['TAXI_flag'] = x[gsKey].apply(lambda x: 1 if TAXI_LOW_SPEED_THR < x < TAXI_HIGH_SPEED_THR else 0)
    x['TAXI_state_change'] = x['TAXI_flag'].diff()  # mark where taxiing changes (stopped -> taxiing | taxiing -> stop)
    changesInGS: Series = x.loc[x['TAXI_state_change'] != 0]['TAXI_state_change']  # select only rows with changes
    changesInGS = changesInGS.dropna()

    taxiIntervals = list()
    taxiStart = None
    for index, item in changesInGS.iteritems():
        if item == 1:  # TAXI start
            taxiStart = index
        if item == -1 and taxiStart:  # TAXI end
            taxiEnd = index
            sec = (taxiEnd - taxiStart).seconds
            if sec >= TAXI_MIN_DURATION:
                taxiIntervals.append(Interval(start=taxiStart, end=taxiEnd))

    # plot TAXI flags:
    # x[['GS', 'TAXI_flag']].plot()
    # plt.show()

    return taxiIntervals


def detectEngineStartups(df: DataFrame) -> List[Interval]:
    """
    Detection of engine startups.
    start: NG < 30%
    end: NG stable on 60% or below

    :param df:
    :return: list of intervals
    """
    NG_LOW_THR = 0  # [%]

    startups = []

    if len(df.loc[df['NG'] < 30]) == 0:     # the engine was not down
        return startups

    df = df.copy(deep=True)

    while True:
        tmpDf = df.loc[df['NG'] > NG_LOW_THR]
        if tmpDf.empty:
            break

        startIndex = tmpDf.index[0]  # first index above low thr
        df = df[startIndex:]
        dNG = df['NG'].diff().rolling(5, center=True).mean()
        ser = dNG[dNG < 0].head(1)
        if ser.empty:
            break
        endIndex = ser.index[0]  # until first derivation is < 0 (non-rising value)

        interval = Interval(start=startIndex, end=endIndex)
        startups.append(interval)
        # print(f'[INFO] Detected engine startup in interval {interval.start} -> {interval.end}')

        df = df.loc[df['NG'] < NG_LOW_THR]
        if len(df) == 0:
            break

    return startups


def detectEngineIdles(df: DataFrame) -> List[Interval]:
    """
    Detection of engine idling.
    NG < 57%
    len >= 10s

    :param df:
    :return:
    """
    NG_THR = 57  # [%]
    MIN_DURATION = 10  # [s]

    intervals = list()

    idleStart = idleEnd = None
    for index, row in df.iterrows():
        if not idleStart and row['NG'] < NG_THR:
            idleStart = index

        if idleStart and row['NG'] > NG_THR:
            idleEnd = index
            sec = (idleEnd - idleStart).seconds
            if sec >= MIN_DURATION:
                intervals.append(Interval(start=idleStart, end=idleEnd))

            idleStart = None
            idleEnd = None

    lastRow = df.tail(1)
    if idleStart and not idleEnd and lastRow['NG'][0] < NG_THR:
        idleEnd = lastRow.index[0]
        sec = (idleEnd - idleStart).seconds
        if sec >= MIN_DURATION:
            intervals.append(Interval(start=idleStart, end=idleEnd))

    return intervals


def detectEngineCruises(df: DataFrame) -> List[Interval]:
    """
    Detection of engine-in-cruise-mode intervals.
    60 < NG < 97.8%
    len >= 10s

    :param df:
    :return:
    """
    NG_THR_MIN = 60  # [%]
    NG_THR_MAX = 97.8  # [%]
    MIN_DURATION = 10  # [s]

    intervals = list()

    intervalStart = intervalEnd = None
    for index, row in df.iterrows():
        if not intervalStart and NG_THR_MIN < row['NG'] < NG_THR_MAX:
            intervalStart = index

        if intervalStart and (row['NG'] < NG_THR_MIN or row['NG'] > NG_THR_MAX):
            intervalEnd = index
            sec = (intervalEnd - intervalStart).seconds
            if sec >= MIN_DURATION:
                intervals.append(Interval(start=intervalStart, end=intervalEnd))

            intervalStart = None

    return intervals


def detectEngineShutdowns(df: DataFrame) -> List[Interval]:
    """
    Detection of engine shutdown.
    start: NG < 57% with stable decrease all the way till
    end: NG ~ 10% or 0% on ground

    :param df:
    :return: list of intervals
    """
    NG_HIGH_THR = 57  # [%]
    NG_LOW_THR = 10  # [%]

    df = df.copy(deep=True)
    shutdowns = []

    tmpDf = df.loc[df['NG'] >= EngineLimits.H80['NGLimIdle']]
    if tmpDf.empty:
        return []

    engUpIndex = tmpDf.index[0]  # first index where the engine was above idle
    df = df[engUpIndex:]
    # df['NG'].plot()
    while True:
        x = df.loc[df['NG'] < NG_HIGH_THR]  # find data below high thr
        if x.empty:
            return shutdowns

        sdStartIndex = df.loc[df['NG'] < NG_HIGH_THR].index[0]
        df = df[sdStartIndex:]

        x = df.loc[df['NG'] < NG_LOW_THR]  # find data below low thr
        if x.empty:
            return shutdowns

        endIndex = df.loc[df['NG'] < NG_LOW_THR].index[0]  # first index below low thr
        x = df[:endIndex]

        # TODO.. perhaps one nice sunny day
        print('[WARN] NO DATA WAS EVER AVAILABLE FOR ENGINE SHUTDOWN DETECTION IMPLEMENTATION!')
        break

    return shutdowns


def detectPropellerFeatheringIntervals(df: DataFrame):
    """
    Detection of propeller in feathering position.
    240rpm < NP < 830rpm
    NG > 57%
    :param df:
    :return:
    """
    intervals = list()
    df = df[['NP', 'NG']].copy()

    df['feather'] = df['NP'].apply(lambda x: 1 if 240 < x < 830 else 0) & df['NG'].apply(lambda x: 1 if x > 57 else 0)

    intervalStart = None
    for index, row in df.iterrows():
        if not intervalStart and row['feather'] == 1:
            intervalStart = index

        if intervalStart and row['feather'] == 0:
            intervalEnd = index
            intervals.append(Interval(start=intervalStart, end=intervalEnd))

            intervalStart = None

    return intervals


if __name__ == '__main__':

    frDao = FlightRecordingDao()

    # ew = EngineWork(engineId=1, flightId=1, flightIdx=0, cycleId=20, cycleIdx=0)  # PT6
    ew = EngineWork(engineId=2, flightId=2, flightIdx=0, cycleId=21, cycleIdx=0)  # H80 AI.1
    # ew = EngineWork(engineId=2, flightId=2, flightIdx=0, cycleId=22, cycleIdx=0)  # H80 AI.2
    # ew = Engine(engineId=X, flightId=2, flightIdx=0, cycleId=X, cycleIdx=0)      # H80 GE

    df = frDao.loadDf(engineId=ew.engineId, flightId=ew.flightId, flightIdx=ew.flightIdx, cycleId=ew.cycleId, cycleIdx=ew.cycleIdx,
                      recType=RecordingType.FILTERED)

    flightIntervals = detectFlights(df)
    for i, flight in enumerate(flightIntervals):
        print(f'[INFO] flight #{i} {flight.start} -> {flight.end}')

    engineStartups = detectEngineStartups(df)
    for i, engineStartup in enumerate(engineStartups):
        print(f'[INFO] engine startup #{i} {engineStartup.start} -> {engineStartup.end}')

    takeoffs = detectTakeOffs(df)
    for i, takeoff in enumerate(takeoffs):
        print(f'[INFO] takeoff #{i} {takeoff.start} -> {takeoff.end}')

    climbIntervals = detectClimbs(df)
    for i, climb in enumerate(climbIntervals):
        print(f'[INFO] climb #{i} {climb.start} -> {climb.end}:')

    repeatedTakeoffs = detectRepeatedTakeOffs(df, climbIntervals)
    for i, interval in enumerate(repeatedTakeoffs):
        print(f'[INFO] Repeated takeoff #{i} {interval.start} -> {interval.end}')

    taxiIntervals = detectTaxi(df)
    for interval in taxiIntervals:
        dur = (interval.end - interval.start).seconds
        print(f"[INFO] taxi {interval.start} -> {interval.end}; dur: {dur}s")

    engineIdles = detectEngineIdles(df)
    for i, idle in enumerate(engineIdles):
        print(f'[INFO] engine idle #{i} {idle.start} -> {idle.end}', )

    engineCruiseIntervals = detectEngineCruises(df)
    for i, cruise in enumerate(engineCruiseIntervals):
        print(f'[INFO] cruise #{i} {cruise.start} -> {cruise.end}', )

    propInFeatherPosIntervals = detectPropellerFeatheringIntervals(df)
    for i, feather in enumerate(propInFeatherPosIntervals):
        print(f'[INFO] prop. feather #{i} {feather.start} -> {feather.end}', )

    engineShutdownIntervals = detectEngineShutdowns(df)
    for i, shutdown in enumerate(engineShutdownIntervals):
        print(f'[INFO] engine shutdown #{i} {shutdown.start} -> {shutdown.end}', )

    frDao.influx.stop()

    # iasKey = 'IAS' if 'IAS' in df.keys() else 'TAS'
    # df[['GS', iasKey, 'NG', 'NP', 'ALT']].plot()
    # plt.show()
    print('KOHEU.')

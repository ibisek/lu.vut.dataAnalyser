"""
influx:
    select * from flights where engine_id='2' and flight_id='2' and cycle_id='2' and type='fil' limit 10

TODO az na to budou data:
TODO (4) opakovane spousteni:  NG < 40% a pak zase NG na 60%; L410: NG=57% && NP <240-480> (pro PT6 neresit)
"""

from datetime import timedelta
from pandas import DataFrame, Series, Timestamp

import matplotlib.pyplot as plt
from typing import List

from dao.flightRecordingDao import FlightRecordingDao, RecordingType
from data.structures import Interval, EngineWork


def _findLandingAfter(df: DataFrame, afterIndexTs: Timestamp):
    """
    Finds next landing (IAS = 0) after specified index ts.

    :param df:
    :param afterIndexTs:
    :return: index ts
    """
    x = df.copy(deep=True)[afterIndexTs:]
    iasKey = 'IAS' if 'IAS' in df.keys() else 'TAS'
    landingTs = x.loc[x[iasKey] <= 0.1].index[0]  # == 0 does not work

    return landingTs


def _findTakeoffEndAfter(df: DataFrame, afterIndexTs: Timestamp):
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

        if ng < ngMax * 0.98:
            tsTakeOffIndexEnd = index
            return tsTakeOffIndexEnd

    return None


def detectTakeOff(df: DataFrame, ngStart=100.1, ngEnd=100.1) -> List[Interval]:
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

    df = df.copy(deep=True)
    iasKey = 'IAS' if 'IAS' in df.keys() else 'TAS'

    takeOffs: List[Interval] = list()

    numSuchDataPoints = len(df.loc[df['NG'] > ngStart])
    while numSuchDataPoints:
        tsTakeOffIndexStart = df.loc[df['NG'] > ngStart].index[0]
        # TODO find the interval..
        raise NotImplementedError('ERROR: detectTakeOff NOT implemented yet! (no data)')

        # TODO cut-off df after the end and search again:
        numSuchDataPoints = len(df.loc[df['NG'] > ngStart])

    return takeOffs


def detectClimbs(df: DataFrame) -> List[Interval]:
    """
    Detection of CLIMB window/interval.
    start: IAS (TAS) > 10 km/h
    end: NG = 0.98NG_max

    :param df:
    :return: takeoffStart index, takeoffEndIndex
    """

    x = df.copy(deep=True)

    TO_START_IAS_DELTA = 4  # [km/h]
    TO_START_IAS_THRESHOLD = 20  # [km/h]

    iasKey = 'IAS' if 'IAS' in df.keys() else 'TAS'

    tsTakeOffIndexStart = df.loc[df[iasKey] > TO_START_IAS_THRESHOLD].index[0]

    climbs: List[Interval] = list()
    doLoop = True
    while doLoop:
        x = x[tsTakeOffIndexStart:]  # df starting from the moment of takeoff

        tsTakeOffIndexEnd = _findTakeoffEndAfter(x, tsTakeOffIndexStart)
        if not tsTakeOffIndexStart:
            doLoop = False

        else:
            interval = Interval(start=tsTakeOffIndexStart, end=tsTakeOffIndexEnd)
            climbs.append(interval)

            # plot the takeoff section:
            # x = x[:tsTakeOffIndexEnd]
            # x['dIAS'] = df[iasKey].diff() * 10
            # x['TO_dIAS'] = x['dIAS'].apply(lambda x: 1 if x > TO_START_IAS_DELTA else 0)
            # x['ALTx'] = x['ALT'] / 10
            # x['dALT'] = x['ALT'].diff() * 10
            # x['TO'] = x[iasKey].apply(lambda x: 100 if x > 0 else 0)
            # x[[iasKey, 'TO', 'NG', 'ALTx', 'dALT', 'dIAS', 'TQx']].plot()
            # plt.show()

            tsLanding = _findLandingAfter(x, tsTakeOffIndexEnd)  # start searching from this ts again
            x = x[tsLanding:]  # chop the previous data away
            xx = x.loc[x[iasKey] > TO_START_IAS_THRESHOLD]
            if len(xx.index) == 0:
                doLoop = False
            else:
                tsTakeOffIndexStart = xx.index[0]

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
            rptToEndTs = _findTakeoffEndAfter(df, rptToStartTs)
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

    TAXI_LOW_SPEED_THR = 2  # [km/h]
    TAXI_HIGH_SPEED_THR = 50  # [km/h]
    TAXI_MIN_DURATION = 20  # [s]

    x['TAXI_flag'] = x['GS'].apply(lambda x: 1 if TAXI_LOW_SPEED_THR < x < TAXI_HIGH_SPEED_THR else 0)
    x['TAXI_state_change'] = x['TAXI_flag'].diff()  # mark where taxiing changes (stopped 2 taxiing | taxiing to stop)
    changesInGS: Series = x.loc[x['TAXI_state_change'] != 0]['TAXI_state_change']  # select only rows with changes
    changesInGS = changesInGS.dropna()

    taxiIntervals = list()
    taxiStart = None
    for index, item in changesInGS.iteritems():
        if item == 1:  # TAXI start
            taxiStart = index
        if item == -1:  # TAXI end
            taxiEnd = index
            sec = (taxiEnd - taxiStart).seconds
            if sec >= TAXI_MIN_DURATION:
                taxiIntervals.append(Interval(start=taxiStart, end=taxiEnd))

    # plot TAXI flags:
    # x[['GS', 'TAXI_flag']].plot()
    # plt.show()

    return taxiIntervals


def detectEngineStartup(df: DataFrame) -> Interval:
    """
    Detection of engine startup.
    start: NG < 40%
    end: NG stable on 60% or below

    :param df:
    :return:
    """

    x = df.copy(deep=True)

    NG_LOW_THR = 30  # [%]
    ENGINE_STARTUP_DURATION_MAX = 60  # [s]

    ngBelowTh: Series = x['NG'].loc[x['NG'] < NG_LOW_THR].diff().dropna()
    if len(ngBelowTh) == 0:
        return None

    engineStartupStart = ngBelowTh.loc[ngBelowTh > 0].index[0]

    x['dNG'] = x['NG'].diff()

    engineStartupEndEst = engineStartupStart + timedelta(0, ENGINE_STARTUP_DURATION_MAX)  # estimate startup time no longer than thr
    engineStartupSeries = x[engineStartupStart:engineStartupEndEst]['dNG']

    engineStartupEnd = engineStartupSeries.loc[engineStartupSeries <= 0].index[0]  # first row where dNG <= 0

    # plot startup section:
    # x['NGx'] = x['NG'] * 10
    # x['dNGx'] = x['dNG'] * 100
    # x['dNPx'] = x['NP'].diff() * 10
    # x[engineStartupStart:engineStartupEndEst][['NGx', 'NP', 'dNGx', 'dNPx']].plot()
    # plt.show()

    return Interval(start=engineStartupStart, end=engineStartupEnd)


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


if __name__ == '__main__':

    frDao = FlightRecordingDao()

    ew = EngineWork(engineId=1, flightId=1, cycleId=1)  # PT6
    # ew = Engine(engineId=2, flightId=2, cycleId=2)      # H80 AI
    # ew = Engine(engineId=3, flightId=2, cycleId=3)      # H80 GE

    df = frDao.loadDf(engineId=ew.engineId, flightId=ew.flightId, cycleId=ew.cycleId, recType=RecordingType.FILTERED)

    takeoffs = detectTakeOff(df)
    for i, takeoff in enumerate(takeoffs):
        print(f'[INFO] takeoff #{i} {takeoff.start} -> {takeoff.end}')

    climbs = detectClimbs(df)
    for i, climb in enumerate(climbs):
        print(f'[INFO] climb #{i} {climb.start} -> {climb.end}:')

    repeatedTakeoffs = detectRepeatedTakeOffs(df, climbs)
    for i, interval in enumerate(repeatedTakeoffs):
        print(f'[INFO] Repeated takeoff #{i} {interval.start} -> {interval.end}')

    taxiIntervals = detectTaxi(df)
    for interval in taxiIntervals:
        dur = (interval.end - interval.start).seconds
        print(f"[INFO] taxi {interval.start} -> {interval.end}; dur: {dur}s")

    engineStartup = detectEngineStartup(df)  # TODO startup-S?
    if engineStartup:
        print(f'[INFO] engine startup {engineStartup.start} -> {engineStartup.end}:', )

    engineIdles = detectEngineIdles(df)
    for idle in engineIdles:
        print(f'[INFO] engine idle {idle.start} -> {idle.end}', )

    frDao.influx.stop()

    # iasKey = 'IAS' if 'IAS' in df.keys() else 'TAS'
    # df[['GS', iasKey, 'NG', 'NP', 'ALT']].plot()
    # plt.show()
    print('KOHEU.')

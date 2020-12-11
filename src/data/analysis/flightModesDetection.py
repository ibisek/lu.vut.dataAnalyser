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

    FLIGHT_MIN_DURATION = 60  # [s]
    iasKey = 'IAS' if 'IAS' in df.keys() else 'TAS'

    return findIntervals(df[iasKey], 100, FLIGHT_MIN_DURATION)   # 100km/h, min 10s


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

        if ng < ngMax * 0.98:
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
                    continue

                interval = Interval(start=tsTakeOffIndexStart, end=tsTakeOffIndexEnd)
                takeOffs.append(interval)

                tsTakeOffIndexStart = None
                df = df[tsTakeOffIndexEnd:]

    return takeOffs


def detectClimbs(df: DataFrame) -> List[Interval]:
    """
    Detection of CLIMB window/interval.
    start: IAS (TAS) > 10 km/h
    end: NG = 0.98NG_max

    :param df:
    :return: [climbStartindex, climbEndIndex]
    """

    x = df.copy(deep=True)

    TO_START_IAS_DELTA = 4  # [km/h]
    TO_START_IAS_THRESHOLD = 20  # [km/h]

    iasKey = 'IAS' if 'IAS' in df.keys() else 'TAS'

    tsClimbIndexStart = df.loc[df[iasKey] > TO_START_IAS_THRESHOLD].index[0]

    climbs: List[Interval] = list()
    doLoop = True
    while doLoop:
        x = x[tsClimbIndexStart:]  # df starting from the moment of takeoff

        tsClimbIndexEnd = _findClimbEndAfter(x, tsClimbIndexStart)
        if not tsClimbIndexStart:
            doLoop = False

        else:
            interval = Interval(start=tsClimbIndexStart, end=tsClimbIndexEnd)
            climbs.append(interval)

            # plot the takeoff section:
            # x = x[:tsClimbIndexStart]
            # x['dIAS'] = df[iasKey].diff() * 10
            # x['TO_dIAS'] = x['dIAS'].apply(lambda x: 1 if x > TO_START_IAS_DELTA else 0)
            # x['ALTx'] = x['ALT'] / 10
            # x['dALT'] = x['ALT'].diff() * 10
            # x['TO'] = x[iasKey].apply(lambda x: 100 if x > 0 else 0)
            # x[[iasKey, 'TO', 'NG', 'ALTx', 'dALT', 'dIAS']].plot()
            # plt.show()

            tsLanding = _findLandingAfter(x, tsClimbIndexEnd)  # start searching from this ts again
            x = x[tsLanding:]  # chop the previous data away
            xx = x.loc[x[iasKey] > TO_START_IAS_THRESHOLD]
            if len(xx.index) == 0:
                doLoop = False
            else:
                tsClimbIndexStart = xx.index[0]

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


def detectEngineStartups(df: DataFrame) -> List[Interval]:
    """
    Detection of engine startups.
    start: NG < 30%
    end: NG stable on 60% or below

    :param df:
    :return: list of intervals
    """
    NG_LOW_THR = 0  # [%]

    df = df.copy(deep=True)
    startups = []

    while True:
        startIndex = df.loc[df['NG'] > NG_LOW_THR].index[0]  # first index above low thr
        df = df[startIndex:]
        dNG = df['NG'].diff().rolling(5, center=True).mean()
        endIndex = dNG[dNG < 0].head(1).index[0]   # until first derivation is < 0 (non-rising value)

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
    NG_THR_MIN = 60    # [%]
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

    engUpIndex = df.loc[df['NG'] >= EngineLimits.H80['NGLimIdle']].index[0]  # first index where the engine was above idle
    df = df[engUpIndex:]
    # df['NG'].plot()
    while True:
        x = df.loc[df['NG'] < NG_HIGH_THR]     # find data below high thr
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
        raise NotImplementedError('[FATAL] NO DATA WAS AVAILABLE FOR ENGINE SHUTDOWN DETECTION IMPLEMENTATION!')

    return shutdowns


if __name__ == '__main__':

    frDao = FlightRecordingDao()

    # ew = EngineWork(engineId=1, flightId=1, cycleId=20)  # PT6
    ew = EngineWork(engineId=2, flightId=2, cycleId=21)  # H80 AI.1
    # ew = EngineWork(engineId=2, flightId=2, cycleId=22)  # H80 AI.2
    # ew = Engine(engineId=X, flightId=2, cycleId=X)      # H80 GE

    df = frDao.loadDf(engineId=ew.engineId, flightId=ew.flightId, cycleId=ew.cycleId, recType=RecordingType.FILTERED)

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
        print(f'[INFO] cruise {i} {cruise.start} -> {cruise.end}', )

    engineShutdownIntervals = detectEngineShutdowns(df)
    for i, shutdown in enumerate(engineShutdownIntervals):
        print(f'[INFO] engine shutdown {i} {shutdown.start} -> {shutdown.end}', )

    frDao.influx.stop()

    # iasKey = 'IAS' if 'IAS' in df.keys() else 'TAS'
    # df[['GS', iasKey, 'NG', 'NP', 'ALT']].plot()
    # plt.show()
    print('KOHEU.')

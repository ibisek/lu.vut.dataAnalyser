"""
influx:
    select * from flights where engine_id='2' and flight_id='2' and cycle_id='2' and type='fil' limit 10

TODO az na to budou data:
TODO (3) opakovany vzlet: IAS<80kt bez zastaveni
TODO (4) opakovane spousteni:  NG < 40% a pak zase NG na 60%; L410: NG=57% && NP <240-480>
"""

from collections import namedtuple
from datetime import timedelta
import numpy as np
from pandas import DataFrame, Series, Timestamp

import matplotlib.pyplot as plt
from typing import List

from dao.flightRecordingDao import FlightRecordingDao, RecordingType
from data.structures import Interval


def _findLandingAfter(df: DataFrame, afterIndexTs: Timestamp):
    """
    Finds next landing (IAS = 0) after specified index ts.

    :param df:
    :param afterIndexTs:
    :return: index ts
    """
    x = df.copy(deep=True)[afterIndexTs:]
    iasKey = 'IAS' if 'IAS' in df.keys() else 'TAS'
    landingTs = x.loc[x[iasKey] <= 0.1].index[0]    # == 0 does not work

    return landingTs


def detectTakeOff(df: DataFrame) -> List[Interval]:
    """
    Detection of TAKE-OFF window/interval.
    start: IAS (TAS) > 10 km/h
    end: NG = 0.98NG_max

    :param df:
    :return: takeoffStart index, takeoffEndIndex
    """

    x = df.copy(deep=True)

    TO_START_IAS_DELTA = 4       # [km/h]
    TO_START_IAS_THRESHOLD = 20  # [km/h]

    iasKey = 'IAS' if 'IAS' in df.keys() else 'TAS'

    tsTakeOffIndexStart = df.loc[df[iasKey] > TO_START_IAS_THRESHOLD].index[0]

    takeOffs: List[Interval] = list()
    doLoop = True
    while doLoop:
        x = x[tsTakeOffIndexStart:]  # df starting from the moment of takeoff

        ngMax = 0
        for index, row in x.iterrows():
            ng = row['NG']

            if ng > ngMax:
                ngMax = ng

            if ng < ngMax * 0.98:
                tsTakeOffIndexEnd = index

                interval = Interval(start=tsTakeOffIndexStart, end=tsTakeOffIndexEnd)
                takeOffs.append(interval)

                # plot the takeoff section:
                # x = x[:tsTakeOffIndexEnd]
                # x['dIAS'] = df[iasKey].diff() * 10
                # x['TO_dIAS'] = x['dIAS'].apply(lambda x: 1 if x > TO_START_IAS_DELTA else 0)
                # x['ALTx'] = x['ALT'] / 10
                # x['dALT'] = x['ALT'].diff() * 10
                # x['TO'] = x[iasKey].apply(lambda x: 100 if x > 0 else 0)
                # x[[iasKey, 'TO', 'NG', 'ALTx', 'dALT', 'dIAS']].plot()
                # plt.show()

                tsLanding = _findLandingAfter(x, tsTakeOffIndexEnd)   # start searching from this ts again
                x = x[tsLanding:]   # chop the previous data away
                xx = x.loc[x[iasKey] > TO_START_IAS_THRESHOLD]
                if len(xx.index) == 0:
                    doLoop = False
                else:
                    tsTakeOffIndexStart = xx.index[0]

                break

            if index == x.tail(1).index:     # we reached end of the dataframe with no endTime
                doLoop = False

    return takeOffs


def detectRepeatedTakeOff(df: DataFrame) -> Interval:
    """
    Detection of repeated TAKE-OFF window/interval.
    start: IAS (TAS) < 80kt && GS >> 0
    end: NG = 0.98NG_max

    :param df:
    :return: Interval
    """

    x = df.copy(deep=True)
    # x = x.drop(columns=['ts'])

    RTO_START_IAS_THRESHOLD = 80 * 1.852    # [kt] -> [km/h]

    iasKey = 'IAS' if 'IAS' in df.keys() else 'TAS'

    # speedBelowTs
    # x['x'] = df.loc[df[iasKey] < RTO_START_IAS_THRESHOLD]

    x['x'] = df[iasKey].apply(lambda x: 100 if x < RTO_START_IAS_THRESHOLD else 0)
    x[[iasKey, 'x']].plot()
    plt.show()

    # TODO xxx

    return Interval(start=None, end=None)


def detectTaxi(df: DataFrame) -> List[Interval]:
    """
    Detection of TAXIing.
    GS in <min, max>
    len >= 20s

    :param df:
    :return:
    """

    x = df.copy(deep=True)

    TAXI_LOW_SPEED_THR = 2    # [km/h]
    TAXI_HIGH_SPEED_THR = 50  # [km/h]
    TAXI_MIN_DURATION = 20    # [s]

    x['TAXI_flag'] = x['GS'].apply(lambda x: 1 if TAXI_LOW_SPEED_THR < x < TAXI_HIGH_SPEED_THR else 0)
    x['TAXI_state_change'] = x['TAXI_flag'].diff()      # mark where taxiing changes (stopped 2 taxiing | taxiing to stop)
    changesInGS: Series = x.loc[x['TAXI_state_change'] != 0]['TAXI_state_change']    # select only rows with changes
    changesInGS = changesInGS.dropna()

    taxiIntervals = list()
    taxiStart = None
    for index, item in changesInGS.iteritems():
        if item == 1:   # TAXI start
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

    NG_LOW_THR = 30     # [%]
    ENGINE_STARTUP_DURATION_MAX = 60    # [s]

    ngBelowTh: Series = x['NG'].loc[x['NG'] < NG_LOW_THR].diff().dropna()
    if len(ngBelowTh) == 0:
        return None

    engineStartupStart = ngBelowTh.loc[ngBelowTh > 0].index[0]

    x['dNG'] = x['NG'].diff()

    engineStartupEndEst = engineStartupStart + timedelta(0, ENGINE_STARTUP_DURATION_MAX)    # estimate startup time no longer than thr
    engineStartupSeries = x[engineStartupStart:engineStartupEndEst]['dNG']

    engineStartupEnd = engineStartupSeries.loc[engineStartupSeries <= 0].index[0]   # first row where dNG <= 0

    # plot startup section:
    # x['NGx'] = x['NG'] * 10
    # x['dNGx'] = x['dNG'] * 100
    # x['dNPx'] = x['NP'].diff() * 10
    # x[engineStartupStart:engineStartupEndEst][['NGx', 'NP', 'dNGx', 'dNPx']].plot()
    # plt.show()

    return Interval(start=engineStartupStart, end=engineStartupEnd)


if __name__ == '__main__':

    frDao = FlightRecordingDao()

    Engine = namedtuple('Engine', ['engineId', 'flightId', 'cycle_id'])

    # e = Engine(engineId=1, flightId=1, cycle_id=1)      # PT6
    # e = Engine(engineId=2, flightId=2, cycle_id=2)      # H80 #1
    e = Engine(engineId=3, flightId=2, cycle_id=3)      # H80 #2

    df = frDao.loadDf(engineId=e.engineId, flightId=e.flightId, cycleId=e.cycle_id, recType=RecordingType.FILTERED)

    takeoffs = detectTakeOff(df)
    for i, takeoff in enumerate(takeoffs):
        print(f'[INFO] takeoff #{i} START:', takeoff.start)
        print(f'[INFO] takeoff #{i} END:  ', takeoff.end)

    repeatedTakeoff = detectRepeatedTakeOff(df)
    print('[INFO] rpt. takeoff START:', repeatedTakeoff.start)
    print('[INFO] rpt. takeoff END:  ', repeatedTakeoff.end)

    taxiIntervals = detectTaxi(df)
    for interval in taxiIntervals:
        dur = (interval.end - interval.start).seconds
        print(f"[INFO] taxi {interval.start} -> {interval.end}; dur: {dur}s")

    engineStartup = detectEngineStartup(df)
    if engineStartup:
        print('[INFO] engine startup START:', engineStartup.start)
        print('[INFO] engine startup   END:', engineStartup.start)

    frDao.influx.stop()
    print('KOHEU.')

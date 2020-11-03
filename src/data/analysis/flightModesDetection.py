
import numpy as np
from pandas import DataFrame, Series
import matplotlib.pyplot as plt
from typing import List

from dao.flightRecordingDao import FlightRecordingDao, RecordingType
from data.structures import Interval


def detectTakeOff(df: DataFrame) -> Interval:
    """
    Detection of TAKE-OFF window/interval.
    start: IAS (TAS) > 0
    end: NG = 0.98NG_max

    :param df:
    :return: takeoffStart index, takeoffEndIndex
    """

    x = df.copy(deep=True)

    TO_START_IAS_DELTA = 4      # [km/h]
    TO_START_IAS_THRESHOLD = 0  # [km/h]

    iasKey = 'IAS' if 'IAS' in df.keys() else 'TAS'

    tsTakeOffIndexStart = df.loc[df[iasKey] > TO_START_IAS_THRESHOLD].index[0]
    x = x[tsTakeOffIndexStart:]  # df starting from the moment of takeoff

    ngMax = 0
    for index, row in x.iterrows():
        ng = row['NG']

        if ng > ngMax:
            ngMax = ng

        if ng < ngMax * 0.98:
            tsTakeOffIndexEnd = index
            break

    # plot the takeoff section:
    # x = x[:tsTakeOffIndexEnd]
    # x['dIAS'] = df[iasKey].diff()*10
    # x['TO_dIAS'] = x['dIAS'].apply(lambda x: 1 if x > TO_START_IAS_DELTA else 0)
    # x['ALTx'] = x['ALT']/10
    # x['dALT'] = x['ALT'].diff()*10
    # x['TO'] = x[iasKey].apply(lambda x: 100 if x > 0 else 0)
    # x[[iasKey, 'TO', 'NG', 'ALTx', 'dALT', 'dIAS']].plot()
    # plt.show()

    return Interval(start=tsTakeOffIndexStart, end=tsTakeOffIndexEnd)


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


if __name__ == '__main__':

    frDao = FlightRecordingDao()

    engineId = 1
    flightId = 1
    cycle_id = 1
    df = frDao.loadDf(engineId=engineId, flightId=flightId, cycleId=cycle_id, recType=RecordingType.FILTERED)

    takeoff = detectTakeOff(df)
    print('[INFO] takeoff START:', takeoff.start)
    print('[INFO] takeoff END:  ', takeoff.end)

    taxiIntervals = detectTaxi(df)
    for interval in taxiIntervals:
        dur = (interval.end - interval.start).seconds
        print(f"[INFO] taxi {interval.start} -> {interval.end}; dur: {dur}s")

    frDao.influx.stop()
    print('KOHEU.')

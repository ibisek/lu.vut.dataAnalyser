"""
All over-limit checks implemented here.
"""

from typing import List
import numpy as np
from pandas import DataFrame, Series

from configuration import NOMINAL_DATA
from data.structures import FlightMode, Interval
from dao.engineLimits import EngineLimits
from db.dao.enginesDao import EnginesDao
from db.dao.logbookDao import Logbook
from flow.utils import _min, _max
from flow.notifications import Notifications, NotificationType
from data.analysis.limits.limitsBase import Zone
from data.analysis.limits.ngLimits import NgLimits
from data.analysis.limits.tqLimits import TqLimits


def _checkNG(df: DataFrame, flightMode: FlightMode, cycle):
    df = df.copy()

    ngl = NgLimits()
    df['ZONE'] = df.apply(lambda x: ngl.check(oat=x.T0, ng=x.NG), axis=1)
    if len(df.loc[df['ZONE'] != Zone.A]) == 0:  # no data above limit
        return  # all OK

    cycle.NGlimL = _max(cycle.NGlimL, 1)    # set flag on cycle

    # flag above limit data points:
    df['lim'] = df['ZONE'].apply(lambda x: 0 if x == Zone.A else 1)
    intervals: List[Interval] = __findIntervals(df['lim'], 0, 1)

    for interval in intervals:
        maxNG = max(df['NG'].loc[interval.start: interval.end])

        duration = (interval.end - interval.start).seconds
        engine = EnginesDao().getOne(id=cycle.engine_id)
        Notifications.valAboveLim(dbEntity=engine, message=f'NG above limits with max value of {maxNG:.1f}% for {duration} seconds.')

        startT = interval.end.strftime('%Y-%m-%d %H:%M')
        endT = interval.start.strftime('%Y-%m-%d %H:%M')
        msg = f'NG above limits with max value of {maxNG:.1f}% between {startT} and {endT}'
        Logbook.add(ts=interval.start.timestamp(), entry=msg, engineId=cycle.engine_id)


def __findIntervals(s: Series, aboveVal, minDuration: int = 0) -> Interval:
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


def _checkNP(df: DataFrame, flightMode: FlightMode, cycle):
    maxNP = max(df['NP'])
    if maxNP <= EngineLimits.H80[flightMode]['NPLimCr']:    # 2080
        return  # we're fine

    cycle.NPlimL = _max(cycle.NPlimL, 1)   # NP overspeed detected

    notifMsgTemplate = "Propeller overspeed ({0:.0f} rpm for {1} s) detected! Refer to the Propeller Operation Manual."
    logbookMsgTemplate = "Propeller overspeed limit ({0} rpm) exceeded by value of {1:.0f} rpm for {2} s!"
    minDuration = 10    # [s]

    if maxNP > EngineLimits.H80[flightMode]['NPLimCrB']:  # > 2400
        overNpIntervals: List[Interval] = __findIntervals(s=df['NP'], aboveVal=EngineLimits.H80[flightMode]['NPLimCrB'], minDuration=minDuration)
        for i in overNpIntervals:
            duration = max([(i.end - i.start).seconds for i in overNpIntervals])

            msg = logbookMsgTemplate.format(EngineLimits.H80[flightMode]['NPLimCrB'], maxNP, duration)
            Logbook.add(ts=i[0].timestamp(), entry=msg, engineId=cycle.engine_id)

            Notifications.urgent(cycle, f'Propeller overspeed of {maxNP:.0f} rpm detected. Return the engine to overhaul facility for inspection/repair!')

    elif EngineLimits.H80[flightMode]['NPLimCrA'] < maxNP <= EngineLimits.H80[flightMode]['NPLimCrB']:  # 2300-2400 (zone B)
        overNpIntervals: List[Interval] = __findIntervals(s=df['NP'], aboveVal=EngineLimits.H80[flightMode]['NPLimCrA'], minDuration=minDuration)
        if len(overNpIntervals) > 0:
            enginesDao = EnginesDao()
            engine = enginesDao.getOne(id=cycle.engine_id)

            for i in overNpIntervals:
                duration = max([(i.end - i.start).seconds for i in overNpIntervals])

                msg = logbookMsgTemplate.format(EngineLimits.H80[flightMode]['NPLimCrA'], maxNP, duration)
                Logbook.add(ts=i[0].timestamp(), entry=msg, engineId=cycle.engine_id)

                Notifications.warning(cycle, notifMsgTemplate.format(maxNP, duration))

                engine.EngNumNPExcB += 1
                enginesDao.save(engine)
                if engine.EngNumNPExcB > EngineLimits.H80['EngNumNPExcB']:  # if propeller overspeeding number is greather then the limit
                    Notifications.urgent(engine, f"Num of NP excesses ({engine.EngNumNPExcB}) over limit ({EngineLimits.H80['EngNumNPExcB']})!")

    elif EngineLimits.H80[flightMode]['NPLimCr2'] < maxNP <= EngineLimits.H80[flightMode]['NPLimCrA']:  # 2200-2300 (zone A)
        overNpIntervals: List[Interval] = __findIntervals(s=df['NP'], aboveVal=EngineLimits.H80[flightMode]['NPLimCr2'], minDuration=minDuration)
        if len(overNpIntervals) > 0:
            enginesDao = EnginesDao()
            engine = enginesDao.getOne(id=cycle.engine_id)

            for i in overNpIntervals:
                duration = (i.end - i.start).seconds

                msg = logbookMsgTemplate.format(EngineLimits.H80[flightMode]['NPLimCr2'], maxNP, duration)
                Logbook.add(ts=i[0].timestamp(), entry=msg, engineId=cycle.engine_id)

                if duration < 20:
                    Notifications.warning(cycle, notifMsgTemplate.format(maxNP, duration))
                else:  # > 20s
                    Notifications.urgent(cycle, notifMsgTemplate.format(maxNP, duration))

                engine.EngNumNPExcA += 1
                enginesDao.save(engine)
                if engine.EngNumNPExcA > EngineLimits.H80['EngNumNPExcA']:  # if propeller overspeeding number is greather then the limit
                    Notifications.urgent(engine, f"Num of NP excesses ({engine.EngNumNPExcA}) over limit ({EngineLimits.H80['EngNumNPExcA']})!")


def _checkITT(df: DataFrame, flightMode: FlightMode, cycle):
    # TODO
    pass


def _checkTQ(df: DataFrame, flightMode: FlightMode, cycle):
    df = df.copy()
    # TODO TEMP remove!!
    df['TQ'] = df['TQ'] * 1.23

    if max(df['TQ']) < EngineLimits.H80['TQLim']:
        return

    cycle.TQlimL = _max(cycle.TQlimL, 1)  # set flag on cycle
    zone = None

    df['TQpct'] = df['TQ'] / NOMINAL_DATA['TQ'] * 100
    if max(df['TQpct']) > 108:
        zone = Zone.C

    else:
        tql = TqLimits()

        intervals = __findIntervals(df['TQpct'], 100, 1)
        for interval in intervals:
            zone = None
            df['TQpct'].loc[interval.start:interval.end].plot()     # TODO remove

            # TQ over 106.6:
            int1066 = __findIntervals(s=df['TQpct'].loc[interval.start:interval.end], aboveVal=106.6, minDuration=1)
            if len(int1066) > 0:
                dur1066 = sum([(i.end - i.start).seconds for i in int1066])
                if dur1066 > EngineLimits.H80[FlightMode.CRUISE]['TQLimTotTime']:
                    zone = Zone.C
                else:
                    zone = Zone.B

            # TQ between 106-106.6:
            if not zone:
                int106 = __findIntervals(s=df['TQpct'].loc[interval.start:interval.end], aboveVal=106.0, minDuration=1)
                if len(int106) > 0:
                    dur106 = sum([(i.end - i.start).seconds for i in int106])
                    x = df.loc[interval.start:interval.end].loc[df['TQpct'] > 106].loc[df['TQpct'] <= 106.6]
                    zone = tql.check(duration=dur106, torque=np.mean(x['TQpct']))

            # TQ between 100 and 106:
            if not zone:
                # int106 = __findIntervals(s=df['TQpct'].loc[interval.start:interval.end], aboveVal=106.0, minDuration=1)
                s: Series = df.loc[interval.start:interval.end].loc[df['TQpct'] > 100].loc[df['TQpct'] < 106]['TQpct']
                zone = tql.check(duration=len(s), torque=np.average(s))

            print(666)

    # TODO mame zonu, tak ted neco s tim udelat

    # # flag above limit data points:
    # df['lim'] = df['ZONE'].apply(lambda x: 0 if x == Zone.A else 1)
    # intervals: List[Interval] = __findIntervals(df['lim'], 0, 1)
    #
    # for interval in intervals:
    #     maxNG = max(df['NG'].loc[interval.start: interval.end])
    #
    #     duration = (interval.end - interval.start).seconds
    #     engine = EnginesDao().getOne(id=cycle.engine_id)
    #     Notifications.valAboveLim(dbEntity=engine, message=f'NG above limits with max value of {maxNG:.1f}% for {duration} seconds.')
    #
    #     startT = interval.end.strftime('%Y-%m-%d %H:%M')
    #     endT = interval.start.strftime('%Y-%m-%d %H:%M')
    #     msg = f'NG above limits with max value of {maxNG:.1f}% between {startT} and {endT}'
    #     Logbook.add(ts=interval.start.timestamp(), entry=msg, engineId=cycle.engine_id)


def _checkOILP(df: DataFrame, flightMode: FlightMode, cycle):
    """
    @see Appendix 3 – Minimum Oil Pressure
    :param df:
    :param flightMode:
    :param cycle:
    :return:
    """

    # calculate actual deltaPoil as it shall be for each particular NG:
    minOilP: Series = 0.000038 * np.power(df['NG'], 2) - 0.00225 * df['NG'] + 0.12

    deltaOILP: Series = (df['OILP'] * 1e06) - minOilP   # [Pa] -> [MPa]
    underPressureValues = deltaOILP[deltaOILP < 0]
    if len(underPressureValues):
        cycle.OilPlimL = 1  # set the flag

        dt = underPressureValues.index[0].strftime('%Y-%m-%d %H:%M')
        Notifications.valBelowLim(cycle, f'Low oil pressure during {flightMode.value} on {dt}')


def _checkOILT(df: DataFrame, flightMode: FlightMode, cycle):

    if flightMode is FlightMode.ENG_STARTUP:
        if cycle.OilTBe < EngineLimits.H80['OilTeLim']:
            Notifications.valBelowLim(cycle, f'Oil temperature before engine startup: {cycle.OilTBe} deg.C')

    elif flightMode is FlightMode.CRUISE:
        minLimit = EngineLimits.H80[flightMode]['OilTLimMin']
        maxLimit = EngineLimits.H80[flightMode]['OilTLimMax']

        minValue = np.min(df['OILT'])
        maxValue = np.max(df['OILT'])

        if minValue < minLimit:
            Notifications.valBelowLim(cycle, f'Oil temperature below limit ({minLimit} deg.C) during {flightMode.value}: {minValue} deg.C')

        if maxValue > maxLimit:
            Notifications.valAboveLim(cycle, f'Oil temperature above limit ({maxLimit} deg.C) during {flightMode.value}: {maxValue} deg.C')


def _checkFUELP(df: DataFrame, flightMode: FlightMode, cycle):
    # TODO perhaps one sunny day..
    pass


def checkCruiseLimits(df: DataFrame, cycle):
    _checkNG(df, FlightMode.CRUISE, cycle)
    _checkNP(df, FlightMode.CRUISE, cycle)
    _checkTQ(df, FlightMode.CRUISE, cycle)
    _checkITT(df, FlightMode.CRUISE, cycle)
    _checkOILP(df, FlightMode.CRUISE, cycle)
    _checkOILT(df, FlightMode.CRUISE, cycle)
    _checkFUELP(df, FlightMode.CRUISE, cycle)


def checkEngineIdleLimits(df: DataFrame, cycle):
    cycle.NGlimL = _max(cycle.NGlimL, 1 if max(df['NG']) > EngineLimits.H80['NGLimIdle'] else 0)

    maxITT = max(df['ITT'])
    ittLim = 1 if maxITT > EngineLimits.H80['ITTLimIdle'] else 0
    if ittLim:
        cycle.ITTlimL = _max(cycle.ITTlimL, ittLim)
        Notifications.valAboveLim(cycle, f'ITT during engine idle: {maxITT} deg.C')


def checkEngineStartupLimits(df: DataFrame, cycle):
    # ground engine start-up:
    if cycle.TimeSUg > EngineLimits.H80['TimeLimSUg']:
        Notifications.valAboveLim(cycle, f'Time to ignition: {cycle.TimeSUg} s')

    if cycle.TimeSUgIdle > EngineLimits.H80['TimeLimSUgIdle']:
        Notifications.valAboveLim(cycle, f'Time to idle: {cycle.TimeSUgIdle} s')

    if cycle.ITTSUg > EngineLimits.H80['ITTLimSUg']:
        cycle.ITTlimL &= 1
        Notifications.valAboveLim(cycle, f'Altitude during engine startup: {cycle.ITTlimL} deg.C')

    if cycle.ALTSUg > EngineLimits.H80['ALTLimSUg']:
        Notifications.valAboveLim(cycle, f'Altitude during engine startup: {cycle.ALTSUg} m')

    _checkOILP(df, FlightMode.ENG_STARTUP, cycle)
    _checkOILT(df, FlightMode.ENG_STARTUP, cycle)

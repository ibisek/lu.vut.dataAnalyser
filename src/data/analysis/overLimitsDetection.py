"""
All over-limit checks implemented here.
"""
from typing import List
from pandas import DataFrame, Series

from data.structures import FlightMode, Interval
from dao.engineLimits import EngineLimits
from db.dao.logbooksDao import Logbook
from flow.utils import _min, _max
from flow.notifications import Notifications, NotificationType


def _checkNG(df: DataFrame, flightMode: FlightMode, cycle):
    # TODO
    pass


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
    # if maxNP <= 2200:
    #     return  # we're fine
    #
    # cycle.NPlimL |= 1   # NP overspeed detected

    # TODO propeller overspeeding number?
    # TODO muze byt logbook i k necemu jinemu nez k motoru?
    # TODO v jakem formatu zapisovat do vsechno logbooku? Je to textove/nebo strojne zpracovatelne uloziste?

    msgTemplate = f'Propeller overspeed ({maxNP:.0f} rpm for {0} s) detected! Refer to the Propeller Operation Manual.'
    minDuration = 10    # [s]

    if maxNP > 2400:
        overNpIntervals: List[Interval] = __findIntervals(s=df['NP'], aboveVal=2400, minDuration=minDuration)
        for i in overNpIntervals:
            duration = max([(i.end - i.start).seconds for i in overNpIntervals])

            d = {'channel': 'NP', 'value': maxNP, 'duration': duration}
            Logbook.add(ts=i[0].timestamp(), entry=d, engineId=cycle.engine_id)

            Notifications.urgent(cycle, f'Propeller overspeed of {maxNP:.0f} rpm detected. Return the engine to overhaul facility for inspection/repair!')

    elif 2300 < maxNP <= 2400:
        overNpIntervals: List[Interval] = __findIntervals(s=df['NP'], aboveVal=2300, minDuration=minDuration)
        for i in overNpIntervals:
            duration = max([(i.end - i.start).seconds for i in overNpIntervals])

            d = {'channel': 'NP', 'value': maxNP, 'duration': duration}
            Logbook.add(ts=i[0].timestamp(), entry=d, engineId=cycle.engine_id)

            Notifications.urgent(cycle, msgTemplate.format(duration))

    elif 2200 < maxNP <= 2300:
        overNpIntervals: List[Interval] = __findIntervals(s=df['NP'], aboveVal=2200, minDuration=minDuration)
        for i in overNpIntervals:
            duration = (i.end - i.start).seconds

            d = {'channel': 'NP', 'value': maxNP, 'duration': duration}
            Logbook.add(ts=i[0].timestamp(), entry=d, engineId=cycle.engine_id)

            if duration < 20:
                Notifications.warning(cycle, msgTemplate.format(duration))
            else:  # > 20s
                Notifications.urgent(cycle, msgTemplate.format(duration))


def _checkITT(df: DataFrame, flightMode: FlightMode, cycle):
    # TODO
    pass


def _checkTQ(df: DataFrame, flightMode: FlightMode, cycle):
    # TODO
    pass


def _checkOILP(df: DataFrame, flightMode: FlightMode, cycle):
    # TODO
    pass


def _checkOILT(df: DataFrame, flightMode: FlightMode, cycle):
    # TODO
    pass


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

    if cycle.OilP < EngineLimits.H80['OilPLim']:
        Notifications.valBelowLim(cycle, f'Oil pressure before engine startup: {cycle.OilP} Pa')

    if cycle.OilTBe < EngineLimits.H80['OilTeLim']:
        Notifications.valBelowLim(cycle, f'Oil temperature before engine startup: {cycle.OilTBe} deg.C')

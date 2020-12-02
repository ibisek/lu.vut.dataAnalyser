"""
All over-limits check implementation implemented here.
"""
from pandas import DataFrame

from data.structures import FlightMode
from dao.engineLimits import EngineLimits
from flow.processing import _min, _max
from flow.notifications import Notifications, NotificationType


def _checkNG(df: DataFrame, flightMode: FlightMode, cycle):
    # TODO
    pass


def _checkNP(df: DataFrame, flightMode: FlightMode, cycle):
    # TODO
    pass


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

    ittLim = 1 if max(df['ITT']) > EngineLimits.H80['ITTLimIdle'] else 0
    if ittLim:
        cycle.ITTlimL = _max(cycle.ITTlimL, ittLim)
        Notifications.createValAboveLim(f'ITT during engine idle: {cycle.ITTlimL} deg.C')


def checkEngineStartupLimits(df: DataFrame, cycle):
    # ground engine start-up:
    if cycle.TimeSUg > EngineLimits.H80['TimeLimSUg']:
        Notifications.createValAboveLim(f'Time to ignition: {cycle.TimeSUg} s')

    if cycle.TimeSUgIdle > EngineLimits.H80['TimeLimSUgIdle']:
        Notifications.createValAboveLim(f'Time to idle: {cycle.TimeSUgIdle} s')

    if cycle.ITTSUg > EngineLimits.H80['ITTLimSUg']:
        cycle.ITTlimL &= 1
        Notifications.createValAboveLim(f'Altitude during engine startup: {cycle.ITTlimL} deg.C')

    if cycle.ALTSUg > EngineLimits.H80['ALTLimSUg']:
        Notifications.createValAboveLim(f'Altitude during engine startup: {cycle.ALTSUg} m')

    if cycle.OilP < EngineLimits.H80['OilPLim']:
        Notifications.createValBelowLim(NotificationType.VALUE_BELOW_LIMIT, f'Oil pressure before engine startup: {cycle.OilP} Pa')

    if cycle.OilTBe < EngineLimits.H80['OilTeLim']:
        Notifications.createValBelowLim(f'Oil temperature before engine startup: {cycle.OilTBe} deg.C')


"""
Step #2:
    * detects flight modes
    * excercises required analyses within those intervals and stores results into DB
"""

from typing import List

from pandas import DataFrame

from data.structures import EngineWork, Interval
from data.analysis.flightModesDetection import detectTakeOffs, detectClimbs, detectRepeatedTakeOffs, detectTaxi, detectEngineStartup, detectEngineIdles, detectEngineCruises
from dao.flightRecordingDao import FlightRecordingDao, RecordingType
from db.dao.cyclesDao import CyclesDao


def _max(a, b):
    if not a:
        return b
    if not b:
        return a
    return max(a, b)


def _min(a, b):
    if not a:
        return b
    if not b:
        return a
    return min(a, b)


class Processing:

    def __init__(self):
        self.frDao = FlightRecordingDao()
        self.cyclesDao = CyclesDao()

    def __del__(self):
        self.frDao.influx.stop()

    # @staticmethod
    # def _checkOverLimitsContravention(self, df: DataFrame, cycle):
    #     """
    #     Checks the entire flight for limits contravention.
    #     :param self:
    #     :param df:
    #     :param cycle:
    #     :return:
    #     """
    #     cycle.NGlimL = True
    #     cycle.NPlimL = True
    #     cycle.ITTlimL = True
    #
    #     cycle.TQlimL = True
    #     cycle.OilPlimL = True
    #     cycle.FuelPlimL = True
    #     cycle.FireWarning = True

    @staticmethod
    def _analyseClimbInterval(df: DataFrame, cycle):
        startTs = df.head(1)['ts'][0]
        endTs = df.tail(1)['ts'][0]
        duration = endTs - startTs

        cycle.BeTimeClim = startTs
        cycle.TimeClim = duration   # TODO is really needed when it can be calculated?
        cycle.NGRClim = _max(cycle.NGRClim, max(df['NG']))
        cycle.NPClim = _max(cycle.NPClim, max(df['NP']))
        cycle.TQClim = _max(cycle.TQClim, max(df['TQ']))
        cycle.ITTClim = _max(cycle.ITTClim, max(df['ITT']))
        cycle.ALTClim = _max(cycle.ALTClim, max(df['ALT']))
        cycle.OilPMinClim = _min(cycle.OilPMinClim, min(df['OILP']))
        cycle.OilPMaxClim = _max(cycle.OilPMaxClim, max(df['OILP']))
        cycle.OilTMaxClim = _max(cycle.OilTMaxClim, max(df['OILT']))
        # cycle.FuelPMinClim = _min(, min(df['X']))     # TODO not in data!
        # cycle.FuelPMaxClim = _max(, max(df['X']))     # TODO not in data!
        cycle.EndTimeClim = endTs

    @staticmethod
    def _analyseEngineCruiseInterval(df: DataFrame, cycle):
        startTs = df.head(1)['ts'][0]
        endTs = df.tail(1)['ts'][0]

        cycle.BeTimeCruis = startTs
        cycle.NGCruis = _max(cycle.NGCruis, max(df['NG']))
        cycle.NPCruis = _max(cycle.NPCruis, max(df['NP']))
        cycle.TQCruis = _max(cycle.TQCruis, max(df['TQ']))
        cycle.ITTCruis = _max(cycle.ITTCruis, max(df['ITT']))
        cycle.AltCruis = _max(cycle.AltCruis, max(df['ALT']))
        cycle.OilPMinCruis = _min(cycle.OilPMinCruis, min(df['OILP']))
        cycle.OilPMaxCruis = _max(cycle.OilPMaxCruis, max(df['OILP']))
        cycle.OilTMaxCruis = _max(cycle.OilTMaxCruis, max(df['OILT']))
        # cycle.FuelPMinCruis = _min(cycle.FuelPMinCruis, min(df['X']))     # TODO not in data!
        # cycle.FuelPMaxCruis = _max(cycle.FuelPMaxCruis, max(df['X']))     # TODO not in data!
        cycle.EndTimeCruis = endTs

    @staticmethod
    def _analyseIdleInterval(df: DataFrame, cycle):
        startTs = df.head(1)['ts'][0]
        endTs = df.tail(1)['ts'][0]

        cycle.BeTimeIdle = startTs
        # cycle.TimeIdle = 666              # TODO wtf?!
        # cycle.TimeIdleHyPumpIdle = 666    # TODO wtf?!
        cycle.NGIdle = _max(cycle.NGIdle, max(df['NG']))
        cycle.ITTIdle = _max(cycle.ITTIdle, max(df['ITT']))
        cycle.AltIdle = _max(cycle.AltIdle, max(df['ALT']))
        cycle.OilPMinIdle = _min(cycle.OilPMinIdle, min(df['OILP']))
        cycle.OilPMaxIdle = _max(cycle.OilPMaxIdle, max(df['OILP']))
        cycle.OilTMaxIdle = _max(cycle.OilTMaxIdle, max(df['OILT']))
        # cycle.FuelPMinIdle = _min(cycle.FuelPMinIdle, min(df['X']))     # TODO not in data!
        # cycle.FuelPMaxIdle = _max(cycle.FuelPMaxIdle, max(df['X']))     # TODO not in data!
        cycle.EndTimeIdle = endTs

    def _detectPhases(self, df: DataFrame):
        self.takeoffIntervals = detectTakeOffs(df)
        for i, takeoff in enumerate(self.takeoffIntervals):
            print(f'[INFO] takeoff #{i} {takeoff.start} -> {takeoff.end}')

        self.climbIntervals = detectClimbs(df)
        for i, climb in enumerate(self.climbIntervals):
            print(f'[INFO] climb #{i} {climb.start} -> {climb.end}:')

        self.repeatedTakeoffIntervals = detectRepeatedTakeOffs(df, self.climbIntervals)
        for i, interval in enumerate(self.repeatedTakeoffIntervals):
            print(f'[INFO] Repeated takeoff #{i} {interval.start} -> {interval.end}')

        self.taxiIntervals = detectTaxi(df)
        for i, interval in enumerate(self.taxiIntervals):
            dur = (interval.end - interval.start).seconds
            print(f"[INFO] taxi #{i} {interval.start} -> {interval.end}; dur: {dur}s")

        self.engineStartup = detectEngineStartup(df)  # TODO startup-S? can there be more than one?
        if self.engineStartup:
            print(f'[INFO] engine startup {self.engineStartup.start} -> {self.engineStartup.end}:', )

        self.engineIdles = detectEngineIdles(df)
        for i, idle in enumerate(self.engineIdles):
            print(f'[INFO] engine idle #{i} {idle.start} -> {idle.end}', )

        self.engineCruiseIntervals = detectEngineCruises(df)
        for i, cruise in enumerate(self.engineCruiseIntervals):
            print(f'[INFO] cruise #{i} {cruise.start} -> {cruise.end}', )

    def process(self, engineWork: EngineWork):
        print(f'[INFO] Processing flight data for engineId={ew.engineId}; flightId={ew.flightId}; cycleId={ew.cycleId}')
        df = self.frDao.loadDf(engineId=engineWork.engineId, flightId=engineWork.flightId, cycleId=engineWork.cycleId, recType=RecordingType.FILTERED)
        self._detectPhases(df)

        cycle = self.cyclesDao.getOne(id=ew.cycleId)

        # self._analyseEngineStartup()  # TODO xxx

        for climbInterval in self.climbIntervals:
            self._analyseClimbInterval(df[climbInterval.start:climbInterval.end], cycle)

        for engCruiseInterval in self.engineCruiseIntervals:
            self._analyseEngineCruiseInterval(df[engCruiseInterval.start:engCruiseInterval.end], cycle)

        for idleInterval in self.engineIdles:
            self._analyseIdleInterval(df[idleInterval.start:idleInterval.end], cycle)

        print('Y')
        # self.cyclesDao.save()


if __name__ == '__main__':
    ew = EngineWork(engineId=1, flightId=1, cycleId=10)  # PT6
    # ew = Engine(engineId=2, flightId=2, cycleId=2)      # H80 AI
    # ew = Engine(engineId=3, flightId=2, cycleId=3)      # H80 GE

    p = Processing()
    p.process(ew)

    print('KOHEU.')

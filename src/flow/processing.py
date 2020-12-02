"""
Step #2:
    * detects flight modes
    * excercises required analyses within those intervals and stores results into DB
"""

from typing import List

from pandas import DataFrame

from data.structures import EngineWork, Interval
from data.analysis.flightModesDetection import detectTakeOffs, detectClimbs, detectRepeatedTakeOffs, \
    detectTaxi, detectEngineStartups, detectEngineIdles, detectEngineCruises
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
    def _analyseEngineStartup(dfStartup: DataFrame, dfFull: DataFrame, cycle):
        startTs = dfStartup.head(1)['ts'][0]
        endTs = dfStartup.tail(1)['ts'][0]
        duration = int(endTs - startTs)

        cycle.BeTimeSU = startTs

        # time to engine ignition:
        dITT = dfStartup['ITT'].diff().dropna()
        ittRaisingTs = dITT.loc[dITT > 0].head(1).index[0].timestamp()
        cycle.TimeSUg = int(ittRaisingTs - startTs)

        # start-up time till idle:
        cycle.TimeSUgIdle = duration

        # time from engine start-up till NG >= 60 (for how long was the engine idling after start-up):
        x = dfFull.loc[dfStartup.tail(1).index[0]:]
        ngRaisingTs = x['NG'][x['NG'] >= 60].head(1).index[0].timestamp()
        cycle.TimePeHeat = int(ngRaisingTs - endTs)

        cycle.ITTSUg = _max(cycle.ITTSUg, max(dfStartup['ITT']))
        cycle.ALTSUg = _max(cycle.ALTSUg, max(dfStartup['ALT']))
        cycle.OilP = dfStartup['OILP'].head(1)[0]
        cycle.OilTBe = dfStartup['OILT'].head(1)[0]
        cycle.FuelP = _max(cycle.FuelP, min(dfStartup['FUELP']))  # TODO min/max?

        iasKey = 'IAS' if 'IAS' in dfStartup.keys() else 'TAS'
        cycle.CASmax = _max(cycle.CASmax, max(dfStartup[iasKey]))

        cycle.EndTimeSU = endTs

        # max ITT during ignition:
        cycle.ITTSUmax = _max(cycle.ITTSUmax, max(dfStartup['ITT']))
        # max ITT startup gradient:
        cycle.ITTSUgrad = _max(cycle.ITTSUgrad, max(dfStartup['ITT'].diff().dropna()))  # assumes samples in 1s interval!!

    @staticmethod
    def _analyseTakeOffInterval(df: DataFrame, cycle):
        startTs = df.head(1)['ts'][0]
        endTs = df.tail(1)['ts'][0]
        duration = endTs - startTs

        cycle.BeTimeTO = startTs
        cycle.TimeTO = duration
        cycle.NGTO = _max(cycle.NGTO, max(df['NG']))
        cycle.NPTO = _max(cycle.NPTO, max(df['NP']))
        cycle.TQTO = _max(cycle.TQTO, max(df['TQ']))
        cycle.ITTTO = _max(cycle.ITTTO, max(df['ITT']))
        cycle.AltTO = _max(cycle.AltTO, max(df['ALT']))
        cycle.OilPMinTO = _min(cycle.OilPMinTO, min(df['OILP']))
        cycle.OilPMaxTO = _max(cycle.OilPMaxTO, max(df['OILP']))
        cycle.OilTMaxTO = _max(cycle.OilTMaxTO, max(df['OILT']))
        cycle.FuelPMinTO = _min(cycle.FuelPMinTO, min(df['FUELP']))
        cycle.FuelPMaxTO = _max(cycle.FuelPMaxTO, max(df['FUELP']))
        cycle.EndTimeTO = endTs

    @staticmethod
    def _analyseClimbInterval(df: DataFrame, cycle):
        startTs = df.head(1)['ts'][0]
        endTs = df.tail(1)['ts'][0]
        duration = endTs - startTs

        cycle.BeTimeClim = startTs
        cycle.TimeClim = duration
        cycle.NGRClim = _max(cycle.NGRClim, max(df['NG']))
        cycle.NPClim = _max(cycle.NPClim, max(df['NP']))
        cycle.TQClim = _max(cycle.TQClim, max(df['TQ']))
        cycle.ITTClim = _max(cycle.ITTClim, max(df['ITT']))
        cycle.ALTClim = _max(cycle.ALTClim, max(df['ALT']))
        cycle.OilPMinClim = _min(cycle.OilPMinClim, min(df['OILP']))
        cycle.OilPMaxClim = _max(cycle.OilPMaxClim, max(df['OILP']))
        cycle.OilTMaxClim = _max(cycle.OilTMaxClim, max(df['OILT']))
        cycle.FuelPMinClim = _min(cycle.FuelPMinClim, min(df['FUELP']))
        cycle.FuelPMaxClim = _max(cycle.FuelPMaxClim, max(df['FUELP']))
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
        cycle.FuelPMinCruis = _min(cycle.FuelPMinCruis, min(df['FUELP']))
        cycle.FuelPMaxCruis = _max(cycle.FuelPMaxCruis, max(df['FUELP']))
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
        cycle.FuelPMinIdle = _min(cycle.FuelPMinIdle, min(df['FUELP']))
        cycle.FuelPMaxIdle = _max(cycle.FuelPMaxIdle, max(df['FUELP']))
        cycle.EndTimeIdle = endTs

    def _detectPhases(self, df: DataFrame):
        self.engineStartupIntervals = detectEngineStartups(df)
        for i, engineStartup in enumerate(self.engineStartupIntervals):
            print(f'[INFO] engine startup #{i} {engineStartup.start} -> {engineStartup.end}')
        # TODO in case of multiple -> crate subcycles; hell yeah! Master is the first, subs are the consequent ones; detection by NG only

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

        self.engineIdles = detectEngineIdles(df)
        for i, idle in enumerate(self.engineIdles):
            print(f'[INFO] engine idle #{i} {idle.start} -> {idle.end}', )

        self.engineCruiseIntervals = detectEngineCruises(df)
        for i, cruise in enumerate(self.engineCruiseIntervals):
            print(f'[INFO] cruise #{i} {cruise.start} -> {cruise.end}', )

    @staticmethod
    def _analyseEntireFlightParams(df: DataFrame, cycle):
        cycle.ITTOpMax = _max(cycle.ITTOpMax, max(df['ITT']))
        print('X')

    def process(self, engineWork: EngineWork):
        print(f'[INFO] Processing flight data for engineId={ew.engineId}; flightId={ew.flightId}; cycleId={ew.cycleId}')
        df = self.frDao.loadDf(engineId=engineWork.engineId, flightId=engineWork.flightId, cycleId=engineWork.cycleId, recType=RecordingType.FILTERED)
        self._detectPhases(df)

        cycle = self.cyclesDao.getOne(id=ew.cycleId)

        for engStartup in self.engineStartupIntervals:
            self._analyseEngineStartup(dfStartup=df[engStartup.start:engStartup.end], dfFull=df, cycle=cycle)

        for takeoffInterval in self.takeoffIntervals:
            self._analyseTakeOffInterval(df[takeoffInterval.start:takeoffInterval.end], cycle)

        for climbInterval in self.climbIntervals:
            self._analyseClimbInterval(df[climbInterval.start:climbInterval.end], cycle)

        for engCruiseInterval in self.engineCruiseIntervals:
            self._analyseEngineCruiseInterval(df[engCruiseInterval.start:engCruiseInterval.end], cycle)

        for idleInterval in self.engineIdles:
            self._analyseIdleInterval(df[idleInterval.start:idleInterval.end], cycle)

        self._analyseEntireFlightParams(df=df, cycle=cycle)

        # TODO uncomment!
        # self.cyclesDao.save()


if __name__ == '__main__':
    # ew = EngineWork(engineId=1, flightId=1, cycleId=10)     # PT6
    ew = EngineWork(engineId=2, flightId=2, cycleId=12)     # H80 AI.1
    # ew = EngineWork(engineId=3, flightId=2, cycleId=13)     # H80 AI.2
    # ew = Engine(engineId=3, flightId=2, cycleId=3)          # H80 GE

    p = Processing()
    p.process(ew)

    print('KOHEU.')

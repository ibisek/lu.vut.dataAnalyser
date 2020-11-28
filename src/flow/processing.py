"""
Step #2:
    * detects flight modes
    * excercises required analyses within those intervals and stores results into DB
"""

from typing import List

from pandas import DataFrame

from data.structures import EngineWork, Interval
from data.analysis.flightModesDetection import detectTakeOff, detectClimbs, detectRepeatedTakeOffs, detectTaxi, detectEngineStartup, detectEngineIdles
from dao.flightRecordingDao import FlightRecordingDao, RecordingType
from db.dao.cyclesDao import CyclesDao


class Processing:

    def __init__(self):
        self.frDao = FlightRecordingDao()
        self.cyclesDao = CyclesDao()

    def __del__(self):
        self.frDao.influx.stop()

    @staticmethod
    def _analyseClimbInterval(df: DataFrame, cycle):
        startTs = df.head(1)['ts'][0]
        endTs = df.tail(1)['ts'][0]
        duration = endTs - startTs

        cycle.BeTimeClim = startTs
        cycle.TimeClim = duration
        cycle.NGRClim = max(df['NG'])
        cycle.NPClim = max(df['NP'])
        cycle.TQClim = max(df['TQ'])
        cycle.ITTClim = max(df['ITT'])
        cycle.ALTClim = max(df['ALT'])
        cycle.OilPMinClim = min(df['OILP'])
        cycle.OilPMaxClim = max(df['OILP'])
        cycle.OilTMaxClim = max(df['OILT'])
        # cycle.FuelPMinClim = min(df['X'])     # TODO not in data!
        # cycle.FuelPMaxClim = max(df['X'])     # TODO not in data!
        cycle.EndTimeClim = endTs

    def _detectPhases(self, df: DataFrame):
        self.takeoffs = detectTakeOff(df)
        for i, takeoff in enumerate(self.takeoffs):
            print(f'[INFO] takeoff #{i} {takeoff.start} -> {takeoff.end}')

        self.climbIntervals = detectClimbs(df)
        for i, climb in enumerate(self.climbIntervals):
            print(f'[INFO] climb #{i} {climb.start} -> {climb.end}:')

        self.repeatedTakeoffs = detectRepeatedTakeOffs(df, self.climbIntervals)
        for i, interval in enumerate(self.repeatedTakeoffs):
            print(f'[INFO] Repeated takeoff #{i} {interval.start} -> {interval.end}')

        self.taxiIntervals = detectTaxi(df)
        for interval in self.taxiIntervals:
            dur = (interval.end - interval.start).seconds
            print(f"[INFO] taxi {interval.start} -> {interval.end}; dur: {dur}s")

        self.engineStartup = detectEngineStartup(df)  # TODO startup-S?
        if self.engineStartup:
            print(f'[INFO] engine startup {self.engineStartup.start} -> {self.engineStartup.end}:', )

        self.engineIdles = detectEngineIdles(df)
        for idle in self.engineIdles:
            print(f'[INFO] engine idle {idle.start} -> {idle.end}', )


def process(self, engineWork: EngineWork):
        print(f'[INFO] Processing flight data for engineId={ew.engineId}; flightId={ew.flightId}; cycleId={ew.cycleId}')
        df = self.frDao.loadDf(engineId=engineWork.engineId, flightId=engineWork.flightId, cycleId=engineWork.cycleId, recType=RecordingType.FILTERED)
        self._detectPhases(df)

        cycle = self.cyclesDao.getOne(id=ew.cycleId)

        # self._analyseEngineStartup()

        for climbInterval in self.climbIntervals:
            self._analyseClimbInterval(df[climbInterval.start:climbInterval.end], cycle)

        # self._analyseCruise()

        # self._analyseIdle()

        print('Y')
        # self.cyclesDao.save()


if __name__ == '__main__':
    ew = EngineWork(engineId=1, flightId=1, cycleId=10)  # PT6
    # ew = Engine(engineId=2, flightId=2, cycleId=2)      # H80 AI
    # ew = Engine(engineId=3, flightId=2, cycleId=3)      # H80 GE

    p = Processing()
    p.process(ew)

    print('KOHEU.')

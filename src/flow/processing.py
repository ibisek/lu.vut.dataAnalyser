"""
Step #2:
    * detects flight modes
    * excercises required analyses within those intervals and stores results into DB
"""

from typing import List

from pandas import DataFrame

from data.structures import EngineWork, Interval
from data.analysis.flightModesDetection import detectTakeOffs, detectClimbs, detectRepeatedTakeOffs, \
    detectTaxi, detectEngineStartups, detectEngineIdles, detectEngineCruises, detectEngineShutdowns, detectFlights
from data.analysis.overLimitsDetection import checkCruiseLimits, checkEngineIdleLimits, checkEngineStartupLimits, \
    checkEngineTakeoffLimits, checkEngineClimbLimits, checkEngineShutdownLimits
from dao.flightRecordingDao import FlightRecordingDao, RecordingType
from dao.engineLimits import EngineLimits
from db.dao.flightsDao import FlightsDao
from db.dao.cyclesDao import CyclesDao
from flow.utils import _min, _max


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
        cycle.OilP = dfStartup['OILP'].tail(1)[0]  # oil pressure at the end of startup
        cycle.OilTBe = dfStartup['OILT'].head(1)[0]
        cycle.FuelP = dfStartup['FUELP'].tail(1)[0]  # fuel pressure at the end of startup

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

    @staticmethod
    def _analyseEngineShutdownInterval(df: DataFrame, cycle):
        startTs = df.head(1)['ts'][0]
        endTs = df.tail(1)['ts'][0]

        cycle.BeTimeSD = startTs
        # cycle.TimeEnCool  TODO once we have the data available
        # cycle.TimeNGSD    TODO once we have the data available
        cycle.EndTimeSD = endTs

    def _detectPhases(self, df: DataFrame):
        self.engineStartupIntervals = detectEngineStartups(df)
        for i, engineStartup in enumerate(self.engineStartupIntervals):
            print(f'[INFO] engine startup #{i} {engineStartup.start} -> {engineStartup.end}')
        # TODO in case of multiple -> crate subcycles; detection by NG only

        self.flightIntervals = detectFlights(df)
        for i, flightInterval in enumerate(self.flightIntervals):
            print(f'[INFO] flight #{i} {flightInterval.start} -> {flightInterval.end}')

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

        self.engineShutdownIntervals = detectEngineShutdowns(df)
        for i, shutdown in enumerate(self.engineShutdownIntervals):
            print(f'[INFO] engine shutdown {i} {shutdown.start} -> {shutdown.end}', )

    lim = EngineLimits()

    @staticmethod
    def _analyseEntireFlightParams(df: DataFrame, cycle):
        # max ITT, NG, NP, TQ during the whole flight:
        cycle.ITTOpMax = _max(cycle.ITTOpMax, max(df['ITT']))
        cycle.TQlimL = _max(cycle.TQlimL, max(df['TQ']) > EngineLimits.H80['TQLim'])
        # fire warning
        cycle.FireWarning = _max(cycle.FireWarning, 1 if max(df['FIRE']) > 0 else 0)

    def _processFlight(self, engineWork: EngineWork, df: DataFrame = None):
        """
        Core of (sub)flight processing.
        :param engineWork:
        :param df
        :return:
        """
        print(f'[INFO] Processing flight data for engineId={ew.engineId}:'
              f'\n\tflight id={ew.flightId}; idx={ew.flightIdx} '
              f'\n\tcycle id={ew.cycleId}; idx={ew.cycleIdx}')

        if not df:
            df = self.frDao.loadDf(engineId=engineWork.engineId, flightId=engineWork.flightId, flightIdx=engineWork.flightIdx,
                                   cycleId=engineWork.cycleId, cycleIdx=engineWork.cycleIdx, recType=RecordingType.FILTERED)

        self._detectPhases(df)

        cycle = self.cyclesDao.getOne(id=ew.cycleId, idx=ew.cycleIdx)

        for engStartup in self.engineStartupIntervals:
            startupDf = df[engStartup.start:engStartup.end]
            self._analyseEngineStartup(dfStartup=startupDf, dfFull=df, cycle=cycle)
            checkEngineStartupLimits(df=startupDf, cycle=cycle)

        for takeoffInterval in self.takeoffIntervals:
            takeoffDf = df[takeoffInterval.start:takeoffInterval.end]
            self._analyseTakeOffInterval(takeoffDf, cycle)
            checkEngineTakeoffLimits(df=takeoffDf, cycle=cycle)

        for climbInterval in self.climbIntervals:
            climbDf = df[climbInterval.start:climbInterval.end]
            self._analyseClimbInterval(climbDf, cycle)
            checkEngineClimbLimits(df=climbDf, cycle=cycle)

        for engCruiseInterval in self.engineCruiseIntervals:
            cruiseDf = df[engCruiseInterval.start:engCruiseInterval.end]
            self._analyseEngineCruiseInterval(df=cruiseDf, cycle=cycle)
            checkCruiseLimits(df=cruiseDf, cycle=cycle)

        for idleInterval in self.engineIdles:
            idleDf = df[idleInterval.start:idleInterval.end]
            self._analyseIdleInterval(df=idleDf, cycle=cycle)
            checkEngineIdleLimits(df=idleDf, cycle=cycle)

        for sdInterval in self.engineShutdownIntervals:
            sdDf = df[sdInterval.start: sdInterval.end]
            self._analyseEngineShutdownInterval(df=sdDf, cycle=cycle)
            checkEngineShutdownLimits(df=sdDf, cycle=cycle)

        self._analyseEntireFlightParams(df=df, cycle=cycle)

        self.cyclesDao.prepareForSave(cycle)
        self.cyclesDao.save(cycle)

    def __populateFlightFields(self, flight, df: DataFrame, takeoffTs: int, landingTs:int):
        flight.takeoff_ts = takeoffTs
        flight.landing_ts = landingTs
        flight.flight_time = (flight.landing_ts - flight.takeoff_ts)
        flight.LNDCount = 1

        if 'lat' in df.keys() and 'lon' in df.keys():
            flight.takeoff_lat = df['lat'].head(1)[0]
            flight.takeoff_lon = df['lon'].head(1)[0]
            # flight.takeoff_icao = 'xxx'    # TODO location lookup
            flight.landing_lat = df['lat'].tail(1)[0]
            flight.landing_lon = df['lon'].tail(1)[0]
            # flight.landing_icao = 'xxx'    # TODO location lookup

    def _extractSubFlights(self, df: DataFrame, rootFlightId: int):
        """
        Extracts flight sections into sub-flights.
        :param df:
        :param rootFlightId
        :return:
        """
        if len(self.flightIntervals) > 1:
            flightsDao = FlightsDao()
            frDao = FlightRecordingDao()

            for idx, flightInterval in enumerate(self.flightIntervals, start=1):    # idx starts from 1
                print(f'[INFO] extracting sub-flight #{idx} {flightInterval.start} -> {flightInterval.end}')
                subDf = df[flightInterval.start: flightInterval.end]

                subFlight = flightsDao.getOne(root_id=ew.flightId, idx=idx)  # check for existence
                if not subFlight:
                    rootFlight = flightsDao.getOne(id=ew.flightId, idx=0)
                    assert rootFlight

                    subFlight = flightsDao.createNew()
                    subFlight.root_id = rootFlightId
                    subFlight.idx = idx
                    subFlight.airplane_id = rootFlight.airplane_id

                    toTs = int(flightInterval.start.timestamp())
                    laTs = int(flightInterval.end.timestamp())
                    self.__populateFlightFields(subFlight, subDf, takeoffTs=toTs, landingTs=laTs)
                    flightsDao.save(subFlight)

                    frDao.storeDf(engineId=ew.engineId, flightId=subFlight.id, flightIdx=subFlight.idx,
                                  cycleId=ew.cycleId, cycleIdx=ew.cycleIdx,
                                  df=subDf, recType=RecordingType.FILTERED)

    def process(self, engineWork: EngineWork):
        """
        Processes raw flights - with cycle- and flight-idx == 0.
        :param engineWork:
        :return:
        """

        print(f'[INFO] Processing initial flight data for engineId={ew.engineId}:'
              f'\n\tflight id={ew.flightId}; idx={ew.flightIdx} '
              f'\n\tcycle id={ew.cycleId}; idx={ew.cycleIdx}')
        df = self.frDao.loadDf(engineId=engineWork.engineId, flightId=engineWork.flightId, flightIdx=engineWork.flightIdx,
                               cycleId=engineWork.cycleId, cycleIdx=engineWork.cycleIdx, recType=RecordingType.FILTERED)

        # analyse the entire record as one flight:
        self._processFlight(engineWork=engineWork)

        # extract separate sub-flights (if any):
        self._extractSubFlights(df=df, rootFlightId=engineWork.flightId)


if __name__ == '__main__':
    # ew = EngineWork(engineId=1, flightId=1, flightIdx=0, cycleId=20, cycleIdx=0)     # PT6
    ew = EngineWork(engineId=2, flightId=2, flightIdx=0, cycleId=21, cycleIdx=0)  # H80 AI.1
    # ew = EngineWork(engineId=3, flightId=2, flightIdx=0, cycleId=22, cycleIdx=0)     # H80 AI.2
    # ew = Engine(engineId=3, flightId=2, flightIdx=0, cycleId=X, cycleIdx=0)          # H80 GE

    p = Processing()
    p.process(ew)

    print('KOHEU.')

"""
Step #2:
    * detects flight modes
    * excercises required analyses within those intervals and stores results into DB
"""

from typing import List

from pandas import DataFrame

from data.structures import EngineWork, Interval
from data.analysis.flightModesDetection import detectTakeOffs, detectClimbs, detectRepeatedTakeOffs, \
    detectTaxi, detectEngineStartups, detectEngineIdles, detectEngineCruises, detectEngineShutdowns, detectFlights, detectPropellerFeatheringIntervals
from data.analysis.overLimitsDetection import checkCruiseLimits, checkEngineIdleLimits, checkEngineStartupLimits, \
    checkEngineTakeoffLimits, checkEngineClimbLimits, checkEngineShutdownLimits
from dao.flightRecordingDao import FlightRecordingDao, RecordingType
from dao.engineLimits import EngineLimits
from dao.componentLimits import ComponentLimits, ComponentLimit
from db.dao.flightsDao import FlightsDao
from db.dao.cyclesDao import CyclesDao
from db.dao.enginesDao import EnginesDao
from db.dao.equipmentDao import EquipmentDao
from db.dao.componentsDao import ComponentsDao
from db.dao.cyclesFlightsDao import CyclesFlightsDao, CycleFlight
from flow.npUtils import _min, _max
from flow.notifications import Notifications


class Processing:

    def __init__(self):
        self.frDao = FlightRecordingDao()
        self.cyclesDao = CyclesDao()
        self.flightsDao = FlightsDao()
        self.frDao = FlightRecordingDao()
        self.enginesDao = EnginesDao()
        self.componentsDao = ComponentsDao()
        self.equipmentDao = EquipmentDao()
        self.cyclesFlightsDao = CyclesFlightsDao()

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

        if cycle.BeTimeIdle == 0:
            cycle.BeTimeIdle = startTs
        # cycle.TimeIdle = 666              # TODO accumulated time without hydr. pump
        # cycle.TimeIdleHyPumpIdle = 666    # TODO accumulated time with hydr. pump
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
        # TODO in case of multiple -> create sub-cycles; detection purely by NG

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

        self.propInFeatherPosIntervals = detectPropellerFeatheringIntervals(df)
        for i, feather in enumerate(self.propInFeatherPosIntervals):
            print(f'[INFO] prop. feather #{i} {feather.start} -> {feather.end}', )

        self.engineShutdownIntervals = detectEngineShutdowns(df)
        for i, shutdown in enumerate(self.engineShutdownIntervals):
            print(f'[INFO] engine shutdown {i} {shutdown.start} -> {shutdown.end}', )

    @staticmethod
    def _analyseEntireFlightParams(df: DataFrame, cycle):
        # max ITT, NG, NP, TQ during the whole flight:
        cycle.ITTOpMax = _max(cycle.ITTOpMax, max(df['ITT']))
        cycle.TQlimL = _max(cycle.TQlimL, max(df['TQ']) > EngineLimits.H80['TQLim'])
        # fire warning
        cycle.FireWarning = _max(cycle.FireWarning, 1 if max(df['FIRE']) > 0 else 0)

    def _processFlight(self, engineWork: EngineWork, df: DataFrame):
        """
        Core of (sub)flight processing.
        :param engineWork:
        :param df
        :return:
        """
        print(f'[INFO] Processing flight data for\n\tengineId={engineWork.engineId}'
              f'\n\tflight id={engineWork.flightId}; idx={engineWork.flightIdx} '
              f'\n\tcycle id={engineWork.cycleId}; idx={engineWork.cycleIdx}')

        cycle = self.cyclesDao.getOne(id=engineWork.cycleId, idx=engineWork.cycleIdx)
        flight = self.flightsDao.getOne(id=engineWork.flightId, idx=engineWork.flightIdx)
        if not cycle or not flight:
            print(f"[ERROR] Missing cycle or flight:\n\tcycle: {cycle}\n\tflight: {flight}!", str(engineWork))
        assert cycle and flight     # both must already exist

        self._detectPhases(df)

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

        toTs = self.flightIntervals[0].start.timestamp()
        laTs = self.flightIntervals[len(self.flightIntervals) - 1].end.timestamp()
        self.__populateFlightFields(flight=flight, df=df, takeoffTs=toTs, landingTs=laTs)

        self.flightsDao.save(flight)

        self.cyclesDao.prepareForSave(cycle)
        self.cyclesDao.save(cycle)

    def __populateFlightFields(self, flight, df: DataFrame, takeoffTs: int, landingTs:int):
        taxiingSeconds = sum([(x.end - x.start).seconds for x in self.taxiIntervals])

        flight.takeoff_ts = takeoffTs
        flight.landing_ts = landingTs

        flight.operation_time = (flight.landing_ts - flight.takeoff_ts)  # time in the air

        # flight time ~ from first taxiing till the last one:   (this is bullshit but they call it flight time - what can I do?)
        if self.taxiIntervals and len(self.taxiIntervals) > 0:
            flight.flight_time_start = self.taxiIntervals[0].end.timestamp()                         # beginning of first taxiing
            flight.flight_time_end = self.taxiIntervals[len(self.taxiIntervals)-1].end.timestamp()   # end of last taxiing
            flight.flight_time = flight.flight_time_end - flight.flight_time_start  # time in the air and moving on the ground - toto vymyslela nejaka urednicka <|>
        else:
            flight.flight_time = taxiingSeconds + flight.operation_time     # time in the air and moving on the ground - toto vymyslela nejaka urednicka <|>

        flight.LNDCount = 1
        flight.NoSUL = flight.NoSUR = len(self.engineStartupIntervals)
        flight.NoTOAll = 1
        flight.NoTORep = 0  # TODO once we can detect such state

        airborneDf = df.loc[df['TAS'] > 100]    # [km/h]
        if not airborneDf.empty:
            if 'LAT' in airborneDf.keys():
                flight.takeoff_lat = airborneDf['LAT'].head(1)[0]
                flight.takeoff_lon = airborneDf['LON'].head(1)[0]
                # flight.takeoff_icao = 'xxx'    # TODO location lookup
            if 'LON' in airborneDf.keys():
                flight.landing_lat = airborneDf['LAT'].tail(1)[0]
                flight.landing_lon = airborneDf['LON'].tail(1)[0]
                # flight.landing_icao = 'xxx'    # TODO location lookup

    def _splitIntoSubflights(self, df: DataFrame, engineWork: EngineWork):
        """
        Splits one record into multiple flights (if there are many)
        :param df:
        :param engineWork:
        :return: list of EngineWorks representing each sub-flight
        """
        if len(self.flightIntervals) == 1:
            return [engineWork]

        cycle = self.cyclesDao.getOne(id=engineWork.cycleId, idx=engineWork.cycleIdx)

        works = []
        numIntervals = len(self.flightIntervals)
        for i in range(numIntervals):
            flightInterval = self.flightIntervals[i]
            # get the right df-slice for the interval:
            if i == 0:                              # for first flight take df data..
                subDf = df[:flightInterval.end]     # from the very beginning of the record till the end of the actual flight as detected
            elif i == numIntervals-1:               # for last flight..
                subDf = df[self.flightIntervals[i-1].end:]   # take everything from the previous interval end till end of the df
            else:
                subDf = df[self.flightIntervals[i-1].end: flightInterval.end]   # from the previous interval end (incl.taxiing)

            # check for existence (idx) - it might have been created by the other engine's data record:
            subFlight = self.flightsDao.getOne(engine_id=engineWork.engineId, root_id=engineWork.flightId, idx=i + 1)
            if not subFlight:
                print(f'[INFO] extracting sub-flight #{i + 1} {flightInterval.start} -> {flightInterval.end}')
                rootFlight = self.flightsDao.getOne(id=engineWork.flightId, idx=0)
                assert rootFlight

                subFlight = self.flightsDao.createNew()
                subFlight.root_id = engineWork.flightId
                subFlight.idx = i + 1  # idx starts from 1
                subFlight.airplane_id = rootFlight.airplane_id
                subFlight.engine_id = engineWork.engineId

                toTs = int(flightInterval.start.timestamp())
                laTs = int(flightInterval.end.timestamp())
                self.__populateFlightFields(subFlight, subDf, takeoffTs=toTs, landingTs=laTs)
                self.flightsDao.save(subFlight)
                print(f'[INFO] created new sub-flight id={subFlight.id}')

                # create link from current cycle to the newly created subFlight:
                if not self.cyclesFlightsDao.exists(cycleId=engineWork.cycleId, flightId=subFlight.id):
                    self.cyclesFlightsDao.save(CycleFlight(cycleId=engineWork.cycleId, flightId=subFlight.id))

            print(f"[INFO] storing sub-flight data into influx for: engineId:{subFlight.engine_id}; "
                  f"sub-flightId:{subFlight.id}; sub-flightIdx:{subFlight.idx}; cycleId:{engineWork.cycleId}; cycleIdx:{engineWork.cycleId}")
            self.frDao.storeDf(engineId=subFlight.engine_id, flightId=subFlight.id, flightIdx=subFlight.idx,
                               cycleId=engineWork.cycleId, cycleIdx=engineWork.cycleIdx,
                               df=subDf, recType=RecordingType.FILTERED)
            self.frDao.flush()

            newEw = EngineWork(engineId=engineWork.engineId,
                               flightId=subFlight.id, flightIdx=subFlight.idx,
                               cycleId=engineWork.cycleId, cycleIdx=engineWork.cycleIdx,
                               df=subDf)    # subDf to avoid re-loading the DF from influx
            works.append(newEw)

        return works

    def _processCycle(self, engineWork: EngineWork, df: DataFrame):
        """
        Needs to be called in the same loop-step as the _processFlight() method!
        It uses the same flight phases for this particular engineWork are detected for the fligth.
        :param engineWork:
        :param df
        :return:
        """
        cycle = self.cyclesDao.getOne(id=engineWork.cycleId, idx=engineWork.cycleIdx)

        # NOTE: climb (after TO (take-off)) intervals are ('incorrectly') used instead of takeoffs
        # as the definition of TO is useless and there are hardly any TO intervals..
        # flags:
        engStartup = True if len(self.engineStartupIntervals) > 0 else False
        takeoff = True if len(self.climbIntervals) > 0 else False
        engStartupFollowedByTO = True if engStartup and takeoff and len(self.takeoffIntervals) > 0 and self.engineStartupIntervals[0].before(self.takeoffIntervals[0]) else False

        propFeather = True if len(self.propInFeatherPosIntervals) > 0 else False
        propFeatherBeforeTO = False
        if propFeather and self.propInFeatherPosIntervals[0].before(self.climbIntervals[0]):
            propFeatherBeforeTO = True

        cycle.TOflag = 1 if takeoff else 0
        cycle.NoSU = 1 if engStartupFollowedByTO else 0
        cycle.RTOflag = 1 if propFeatherBeforeTO and not engStartup else 0  # repeated-TO has no prior engine start-up(!)

        self.cyclesDao.save(cycle)

        # Calculate ENGINE indicators:
        engine = self.enginesDao.getOne(id=cycle.engine_id)

        #  time counter when the engine was up and running (even idling); NG>20%:
        secs = len(df['NG'].loc[df['NG'] > 20])  # assuming sampling perios 1s. This will NOT work if there is change in sampling period(!)
        engine.cycle_hours += secs

        for takeoffInterval in self.takeoffIntervals:
            engine.takeoff_hours += (takeoffInterval.end - takeoffInterval.start).seconds
        if engStartupFollowedByTO:
            engine.CYCLENo += 1
        if cycle.TOflag:
            engine.CYCLENoTO += 1
        if cycle.RTOflag:
            engine.CYCLERep += 1
        self.enginesDao.save(engine)

        # set components' cycle hours:
        components = self.componentsDao.list(engine.id)
        for component in components:
            component.cycle_hrs += secs
        self.componentsDao.save()

    def _calcEquivalentFlightCycles(self, engineWork: EngineWork):
        """
        Calculates simplifed & full number of equivalent flight cycles for engine's components
        according to section 3 from the specs document.
        :param engineWork: master record for flights+cycles
        :return:
        """

        masterCycle = self.cyclesDao.getOne(id=engineWork.cycleId)
        subCycles = [c for c in self.cyclesDao.get(root_id=masterCycle.id)]

        if len(subCycles) == 0:
            Ns = masterCycle.NoSU       # number of engine starts followed by take-off
            Np = masterCycle.RTOflag    # number of repeated take-offs with prior prop. feathering
            Nv = masterCycle.TOflag     # number of all take-offs
        else:
            Ns = sum([cycle.NoSU for cycle in subCycles])       # number of engine starts followed by take-off
            Np = sum([cycle.RTOflag for cycle in subCycles])    # number of repeated take-offs with prior prop. feathering
            Nv = sum([cycle.TOflag for cycle in subCycles])     # number of all take-offs

        print(f'[INFO] EQ cycle values for cycle id {masterCycle.id}: Ns={Ns}; Nv={Nv}; Np={Np};')

        # determine engine type and lookup its components limits:
        engine = self.enginesDao.getOne(id=engineWork.engineId)
        engineType, _ = self.enginesDao.getProperty(engine=engine, key='type')
        if not engineType: engineType = 'H80'  # better something than nothing, right? ;P
        cLimits = getattr(ComponentLimits, engineType)

        components = self.componentsDao.list(engineId=engineWork.engineId)
        for component in components:
            equipment = self.equipmentDao.getOne(id=component.equipment_id)
            lim: ComponentLimit = cLimits[equipment.part_no]

            if type(lim) is ComponentLimit:     # calculate equivalent cycle value:
                eqCycleSim = (Ns + lim.Ap * (Nv - Ns)) * lim.L
                eqCycleFull = (Ns + lim.Av * (Nv - Ns - Np) + lim.Ap * Np) * lim.L
                component.eq_cycles_sim += eqCycleSim
                component.eq_cycles += eqCycleFull
                print(f"[INFO] Equivalent cycles for component id {component.id}: full {eqCycleFull:.2f}; simplified: {eqCycleSim:.2f}")

        self.componentsDao.save()   # save per component would lose the content for other components in the db session

    def _checkLimits(self, engineWork: EngineWork):
        """
        Compare engine/component limits and raise notification when remaining below 10%.
        """
        LIMITING_THR = 0.9  # above remaining 10% of the limits

        engine = self.enginesDao.getOne(id=engineWork.engineId)
        # check engine's remaining cycle hours:
        engCycleHours = engine.cycle_hours / 3600   # [s] -> [h]
        engCycleHoursLim = EngineLimits.H80['CycleHour']
        if engCycleHours >= engCycleHoursLim * LIMITING_THR:  # exceeds X% of the limit
            Notifications.valAboveLim(engine, f'Engine cycle hours above {LIMITING_THR*100:.0f}% of its limit ({engCycleHoursLim} h): {engCycleHours:.1f} h.')

        # check engine remaining cycles:
        nCycles = engine.CYCLENo + engine.CYCLENoTO
        if nCycles >= EngineLimits.H80['CYCLElim'] * LIMITING_THR:       # exceeds X% of the limit
            Notifications.valAboveLim(engine, f"Engine cycles count above {LIMITING_THR*100:.0f}% of its limit ({EngineLimits.H80['CYCLElim']}): {nCycles:1f}.")

        # check engine's remaining take-off hours:
        takeoffHrs = engine.takeoff_hours / 3600    # [s] -> [h]
        if takeoffHrs >= engCycleHoursLim * LIMITING_THR * 0.025:  # exceeds X% which is max 2.5% of the total hours
            Notifications.valAboveLim(engine, f'Engine take-off hours above {LIMITING_THR * 100:.0f}% of its 2.5% limit ({(engCycleHoursLim*0.025):.0f} h) : {takeoffHrs:.1f} h.')

        # check all engine's components:
        engineType, _ = self.enginesDao.getProperty(engine=engine, key='type')
        if not engineType: engineType = 'H80'  # better something than nothing, right? ;P
        cLimits = getattr(ComponentLimits, engineType)
        components = self.componentsDao.list(engineId=engineWork.engineId)
        for c in components:
            equipment = self.equipmentDao.getOne(id=c.equipment_id)
            limitVal = cLimits.get(equipment.part_no, None)
            if type(limitVal) is ComponentLimit:    # ..is an object type, not a number
                limitVal = limitVal.N
            if c.eq_cycles >= limitVal * LIMITING_THR or c.eq_cycles_sim >= limitVal * LIMITING_THR:
                Notifications.valAboveLim(c, f"Component's equivalent cycles above {LIMITING_THR*100:.0f}% of its limit ({limitVal}): {c.eq_cycles:.1f}.")

    def process(self, engineWork: EngineWork):
        """
        Processes raw flights - with cycle- and flight-idx == 0.
        :param engineWork:
        :return: True if things went well
        """

        print(f'[INFO] Processing initial flight data for\n\tengineId={engineWork.engineId}'
              f'\n\tflight id={engineWork.flightId}; idx={engineWork.flightIdx} '
              f'\n\tcycle id={engineWork.cycleId}; idx={engineWork.cycleIdx}')
        df = self.frDao.loadDf(engineId=engineWork.engineId, flightId=engineWork.flightId, flightIdx=engineWork.flightIdx,
                               cycleId=engineWork.cycleId, cycleIdx=engineWork.cycleIdx, recType=RecordingType.FILTERED)

        if df.empty:
            print(f"[WARN] No flight recording stored for", engineWork)
            return False

        self._detectPhases(df)  # on the entire dataset

        works: List[EngineWork] = self._splitIntoSubflights(df=df, engineWork=engineWork)
        for work in works:
            if hasattr(work, 'df') and work.df is not None:
                workDf = work.df
            else:
                workDf = self.frDao.loadDf(engineId=work.engineId, flightId=work.flightId, flightIdx=work.flightIdx,
                                           cycleId=work.cycleId, cycleIdx=work.cycleIdx, recType=RecordingType.FILTERED)

            self._processFlight(engineWork=work, df=workDf)    # these two need to be executed in this exact order!
            self._processCycle(engineWork=work, df=workDf)     # these two need to be executed in this exact order!
            self._checkLimits(engineWork=work)

        # calculate equivalent flight-cycles for engine components affected by the 'root' (not partials) engineWork:
        self._calcEquivalentFlightCycles(engineWork)

        return True


if __name__ == '__main__':
    # ew = EngineWork(engineId=1, flightId=1, flightIdx=0, cycleId=20, cycleIdx=0)     # PT6
    # ew = EngineWork(engineId=2, flightId=2, flightIdx=0, cycleId=21, cycleIdx=0)  # H80 AI.1
    # ew = EngineWork(engineId=3, flightId=2, flightIdx=0, cycleId=22, cycleIdx=0)     # H80 AI.2
    # ew = Engine(engineId=3, flightId=2, flightIdx=0, cycleId=X, cycleIdx=0)          # H80 GE

    ew = EngineWork(engineId=2, flightId=1696, flightIdx=0, cycleId=3766, cycleIdx=0)     # DEBUG L410

    p = Processing()
    p.process(ew)

    print('KOHEU.')

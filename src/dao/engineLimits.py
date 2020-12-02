from collections import defaultdict

from configuration import NOMINAL_DATA
from data.structures import FlightMode


class EngineLimits:
    H80 = defaultdict()

    def __init__(self):
        self.initH80limits()

    def initH80limits(self):
        # engine limits:
        self.H80['CycleHour'] = 3600 * 60 * 60  # [hours] -> [seconds]
        self.H80['CYCLElim'] = 50000  # [-]

        # Cruise-mode limits
        self.H80[FlightMode.CRUISE]['ALT'] = 6100  # [m]
        # NP:
        self.H80[FlightMode.CRUISE]['NGRLimCr'] = 97.8  # [%]
        self.H80[FlightMode.CRUISE]['NGRLimCrbp'] = -32.2  # [deg.C]
        self.H80[FlightMode.CRUISE]['NGRLimCrgrad'] = 0.215827338129496  # [st.C]
        # NP:
        self.H80[FlightMode.CRUISE]['NPLimCr'] = 2080  # [1/min]
        self.H80[FlightMode.CRUISE]['NPLimCr2'] = 2200  # [1/min]
        self.H80[FlightMode.CRUISE]['NPLimCrA'] = 2300  # [1/min]
        self.H80[FlightMode.CRUISE]['NPlimCrB'] = 2400  # [1/min]
        # TQ:
        self.H80[FlightMode.CRUISE]['TQLim'] = 100 * NOMINAL_DATA['TQ']  # [%] -> [Nm]
        self.H80[FlightMode.CRUISE]['TQLimA'] = 106  # [%]
        self.H80[FlightMode.CRUISE]['TQLimATime'] = 30  # [s]
        self.H80[FlightMode.CRUISE]['TQLimA0'] = 60  # [s]
        self.H80[FlightMode.CRUISE]['TQLimTot'] = 108  # [%]
        self.H80[FlightMode.CRUISE]['TQLimTotTime'] = 10  # [s]
        self.H80[FlightMode.CRUISE]['TQLimB'] = 106.5  # [%]
        self.H80[FlightMode.CRUISE]['TQLimBTime'] = 60  # [s]
        self.H80[FlightMode.CRUISE]['TQLimBTime0'] = 300  # [s]
        # ITT:
        self.H80[FlightMode.CRUISE]['ITTLim'] = 720  # [deg.C]
        self.H80[FlightMode.CRUISE]['ITTLimTot'] = 810  # [deg.C]
        self.H80[FlightMode.CRUISE]['ITTLimTimeATot'] = 200 * 60  # [s]
        self.H80[FlightMode.CRUISE]['ITTLimTimeA'] = 90  # [s]
        self.H80[FlightMode.CRUISE]['ITTLimTimeBTot'] = 30 * 60  # [s]
        self.H80[FlightMode.CRUISE]['ITTLimTimeB'] = 90  # [s]

        # oil:
        self.H80[FlightMode.CRUISE]['OilPLim'] = 0.12 * 1000 * 1000  # [Pa]
        self.H80[FlightMode.CRUISE]['OilPLimA'] = 3.8E-05 * 1e06  # [Pa]
        self.H80[FlightMode.CRUISE]['OilPLimB'] = -0.00225 * 1e06  # [Pa]
        self.H80[FlightMode.CRUISE]['OilTLimMax'] = 85  # [deg.C]
        self.H80[FlightMode.CRUISE]['OilTLimMin'] = 20  # [deg.C]
        # fuel:
        self.H80[FlightMode.CRUISE]['FuelPLimMinOptim'] = 49 * 1000  # [Pa]
        self.H80[FlightMode.CRUISE]['FuelPLimMin'] = 20 * 1000      # [Pa]
        self.H80[FlightMode.CRUISE]['FuelPLimMinHA'] = 70 * 1000    # [Pa]
        self.H80[FlightMode.CRUISE]['FuelPLimMaxHA'] = 250 * 1000   # [Pa]
        self.H80[FlightMode.CRUISE]['FuelPLimMax'] = 300 * 1000     # [Pa]
        # self.H80[FlightMode.CRUISE]['PfuelMinFceB'] = 0  # []     # TODO not defined
        # self.H80[FlightMode.CRUISE]['PfuelMaxFce'] = 0  # []      # TODO not defined

        # Idle-mode limits
        self.H80[FlightMode.IDLE]['NGRLimIdle'] = 60  # [%]
        self.H80[FlightMode.IDLE]['ITTLimIdle'] = 550  # [deg.C]

        # Component limits:
        self.H80['ACD1-AV'] = 0.1  # []
        self.H80['ACD1-AP'] = 0.1  # []
        self.H80['ACD1-L'] = 1.46  # []
        self.H80['ACD1-N'] = 28000  # []
        self.H80['ACD2-AV'] = 0.1  # []
        self.H80['ACD2-AP'] = 0.1  # []
        self.H80['ACD2-L'] = 1.57  # []
        self.H80['ACD2-N'] = 50000  # []
        self.H80['Imp-AV'] = 0.39  # []
        self.H80['Imp-AP'] = 0.39  # []
        self.H80['Imp-L'] = 1.14  # []
        self.H80['Imp-N'] = 18300  # []
        self.H80['Imp-AV'] = 0.32  # []
        self.H80['Imp-AP'] = 0.32  # []
        self.H80['Imp-L'] = 1.21  # []
        self.H80['Imp-N'] = 16000  # []
        self.H80['FSR-AV'] = 0.42  # []
        self.H80['FSR-AP'] = 0.42  # []
        self.H80['FST-L'] = 1.07  # []
        self.H80['FSR-N'] = 22600  # []
        self.H80['CTD-AV'] = 0.44  # []
        self.H80['CDR-AP'] = 0.44  # []
        self.H80['CDR-L'] = 1.04  # []
        self.H80['CDR-N'] = 17300  # []
        self.H80['RShaft-AV'] = 0.32  # []
        self.H80['RShaft-AP'] = 0.32  # []
        self.H80['RShaft-L'] = 1.06  # []
        self.H80['RShaft-N'] = 10450  # []
        self.H80['FTC-AV'] = 0.59  # []
        self.H80['FTC-AP'] = 0.93  # []
        self.H80['FTC-L'] = 0.82  # []
        self.H80['FTC-N'] = 8820  # []
        self.H80['FShaft-AV'] = 0.46  # []
        self.H80['FShaft-AP'] = 0.9  # []
        self.H80['FShaft-L'] = 0.87  # []
        self.H80['FShaft-N'] = 11100  # []
        self.H80['Pshaft-N'] = 12000  # []

        # self.H80[''] =

from collections import defaultdict

from configuration import NOMINAL_DATA
from data.structures import FlightMode


class EngineLimits:
    limits = defaultdict()

    H80 = defaultdict()
    H80['CycleHour'] = 3600 * 60 * 60  # [hours] -> [seconds]

    # engine limits:
    H80['CycleHour'] = 3600 * 60 * 60  # [hours] -> [seconds]
    H80['CYCLElim'] = 50000  # [-]

    H80['TQLim'] = NOMINAL_DATA['TQ']  # [Nm]

    # Cruise-mode limits
    H80[FlightMode.CRUISE] = defaultdict()
    H80[FlightMode.CRUISE]['ALT'] = 6100  # [m]
    # NP:
    H80[FlightMode.CRUISE]['NGLimCr'] = 97.8  # [%]
    H80[FlightMode.CRUISE]['NGLimCrbp'] = -32.2  # [deg.C]
    H80[FlightMode.CRUISE]['NGLimCrgrad'] = 0.215827338129496  # [st.C]
    # NP:
    H80[FlightMode.CRUISE]['NPLimCr'] = 2080  # [1/min]
    H80[FlightMode.CRUISE]['NPLimCr2'] = 2200  # [1/min]
    H80[FlightMode.CRUISE]['NPLimCrA'] = 2300  # [1/min]
    H80[FlightMode.CRUISE]['NPlimCrB'] = 2400  # [1/min]
    # TQ:
    H80[FlightMode.CRUISE]['TQLim'] = NOMINAL_DATA['TQ']  # [Nm]
    H80[FlightMode.CRUISE]['TQLimA'] = 106  # [%]
    H80[FlightMode.CRUISE]['TQLimATime'] = 30  # [s]
    H80[FlightMode.CRUISE]['TQLimA0'] = 60  # [s]
    H80[FlightMode.CRUISE]['TQLimTot'] = 108  # [%]
    H80[FlightMode.CRUISE]['TQLimTotTime'] = 10  # [s]
    H80[FlightMode.CRUISE]['TQLimB'] = 106.5  # [%]
    H80[FlightMode.CRUISE]['TQLimBTime'] = 60  # [s]
    H80[FlightMode.CRUISE]['TQLimBTime0'] = 300  # [s]
    # ITT:
    H80[FlightMode.CRUISE]['ITTLim'] = 720  # [deg.C]
    H80[FlightMode.CRUISE]['ITTLimTot'] = 810  # [deg.C]
    H80[FlightMode.CRUISE]['ITTLimTimeATot'] = 200 * 60  # [s]
    H80[FlightMode.CRUISE]['ITTLimTimeA'] = 90  # [s]
    H80[FlightMode.CRUISE]['ITTLimTimeBTot'] = 30 * 60  # [s]
    H80[FlightMode.CRUISE]['ITTLimTimeB'] = 90  # [s]

    # oil:
    H80[FlightMode.CRUISE]['OilPLim'] = 0.12 * 1000 * 1000  # [Pa]
    H80[FlightMode.CRUISE]['OilPLimA'] = 3.8E-05 * 1e06  # [Pa]
    H80[FlightMode.CRUISE]['OilPLimB'] = -0.00225 * 1e06  # [Pa]
    H80[FlightMode.CRUISE]['OilTLimMax'] = 85  # [deg.C]
    H80[FlightMode.CRUISE]['OilTLimMin'] = 20  # [deg.C]
    # fuel:
    H80[FlightMode.CRUISE]['FuelPLimMinOptim'] = 49 * 1000  # [Pa]
    H80[FlightMode.CRUISE]['FuelPLimMin'] = 20 * 1000      # [Pa]
    H80[FlightMode.CRUISE]['FuelPLimMinHA'] = 70 * 1000    # [Pa]
    H80[FlightMode.CRUISE]['FuelPLimMaxHA'] = 250 * 1000   # [Pa]
    H80[FlightMode.CRUISE]['FuelPLimMax'] = 300 * 1000     # [Pa]
    # H80[FlightMode.CRUISE]['PfuelMinFceB'] = 0  # []     # TODO not defined
    # H80[FlightMode.CRUISE]['PfuelMaxFce'] = 0  # []      # TODO not defined

    # Idle-mode limits:
    H80['NGLimIdle'] = 60      # [%]
    H80['ITTLimIdle'] = 550    # [deg.C]

    # engine start-up ground without support limits:
    H80['TimeLimSUg'] = 10          # [s]
    H80['TimeLimSUgIdle'] = 45      # [s]
    H80['ITTLimSUg'] = 730          # [deg.C]
    H80['ALTLimSUg'] = 4000         # [m]
    H80['OilPLim'] = 0.35 * 1e06    # [Pa]
    H80['OilTeLim'] = -20           # [deg.C]

    # Component limits:
    H80['ACD1-AV'] = 0.1  # []
    H80['ACD1-AP'] = 0.1  # []
    H80['ACD1-L'] = 1.46  # []
    H80['ACD1-N'] = 28000  # []
    H80['ACD2-AV'] = 0.1  # []
    H80['ACD2-AP'] = 0.1  # []
    H80['ACD2-L'] = 1.57  # []
    H80['ACD2-N'] = 50000  # []
    H80['Imp-AV'] = 0.39  # []
    H80['Imp-AP'] = 0.39  # []
    H80['Imp-L'] = 1.14  # []
    H80['Imp-N'] = 18300  # []
    H80['Imp-AV'] = 0.32  # []
    H80['Imp-AP'] = 0.32  # []
    H80['Imp-L'] = 1.21  # []
    H80['Imp-N'] = 16000  # []
    H80['FSR-AV'] = 0.42  # []
    H80['FSR-AP'] = 0.42  # []
    H80['FST-L'] = 1.07  # []
    H80['FSR-N'] = 22600  # []
    H80['CTD-AV'] = 0.44  # []
    H80['CDR-AP'] = 0.44  # []
    H80['CDR-L'] = 1.04  # []
    H80['CDR-N'] = 17300  # []
    H80['RShaft-AV'] = 0.32  # []
    H80['RShaft-AP'] = 0.32  # []
    H80['RShaft-L'] = 1.06  # []
    H80['RShaft-N'] = 10450  # []
    H80['FTC-AV'] = 0.59  # []
    H80['FTC-AP'] = 0.93  # []
    H80['FTC-L'] = 0.82  # []
    H80['FTC-N'] = 8820  # []
    H80['FShaft-AV'] = 0.46  # []
    H80['FShaft-AP'] = 0.9  # []
    H80['FShaft-L'] = 0.87  # []
    H80['FShaft-N'] = 11100  # []
    H80['Pshaft-N'] = 12000  # []

    # H80[''] =

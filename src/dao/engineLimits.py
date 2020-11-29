
from collections import defaultdict

from configuration import NOMINAL_DATA


class EngineLimits:
    H80 = defaultdict()

    def __init__(self):
        self.initH80limits()

    def initH80limits(self):

        # engine limits:
        self.H80['CycleHour'] = 3600 * 60*60    # [hours] -> [seconds]
        self.H80['CICLElim'] = 50000            # [-]

        # Cruise-mode limits
        self.H80['cruise']['NGRLimCr'] = 97.8                   # [%]
        self.H80['cruise']['NGRLimCrbp'] = 32.2                 # [deg.C]
        self.H80['cruise']['NGRLimCrgrad'] = 0.215827338129496  # [st.C?] TODO?
        self.H80['cruise']['NPLimCr'] = 2080                    # [1/min]
        self.H80['cruise']['NPLimCr2'] = 2200                   # [1/min]
        self.H80['cruise']['NPLimCrA'] = 2300                   # [1/min]
        self.H80['cruise']['NPlimCrB'] = 2400                   # [1/min]
        self.H80['cruise']['ALT'] = 6100                        # [m]
        self.H80['cruise']['OilPLim'] = 0.12 * 1000*1000        # [Pa]
        self.H80['cruise']['OilTLimMax'] = 85                   # [deg.C]
        self.H80['cruise']['TQLim'] = 100 * NOMINAL_DATA['TQ']  # [%] -> [Nm]

        # Idle-mode limits
        self.H80['idle']['NGRLimIdle'] = 60     # [%]
        self.H80['idle']['ITTLimIdle'] = 550    # [deg.C]

        # Component limits:
        self.H80['ACD1-AV'] = 0.1   # []
        self.H80['ACD1-AP'] = 0.1   # []
        self.H80['ACD1-L'] = 1.46   # []
        self.H80['ACD1-N'] = 28000  # []
        self.H80['ACD2-AV'] = 0.1   # []
        self.H80['ACD2-AP'] = 0.1   # []
        self.H80['ACD2-L'] = 1.57   # []
        self.H80['ACD2-N'] = 50000  # []
        self.H80['Imp-AV'] = 0.39   # []
        self.H80['Imp-AP'] = 0.39   # []
        self.H80['Imp-L'] = 1.14    # []
        self.H80['Imp-N'] = 18300   # []
        self.H80['Imp-AV'] = 0.32   # []
        self.H80['Imp-AP'] = 0.32   # []
        self.H80['Imp-L'] = 1.21    # []
        self.H80['Imp-N'] = 16000   # []
        self.H80['FSR-AV'] = 0.42   # []
        self.H80['FSR-AP'] = 0.42   # []
        self.H80['FST-L'] = 1.07    # []
        self.H80['FSR-N'] = 22600   # []
        self.H80['CTD-AV'] = 0.44   # []
        self.H80['CDR-AP'] = 0.44   # []
        self.H80['CDR-L'] = 1.04    # []
        self.H80['CDR-N'] = 17300   # []
        self.H80['RShaft-AV'] = 0.32    # []
        self.H80['RShaft-AP'] = 0.32    # []
        self.H80['RShaft-L'] = 1.06     # []
        self.H80['RShaft-N'] = 10450    # []
        self.H80['FTC-AV'] = 0.59   # []
        self.H80['FTC-AP'] = 0.93   # []
        self.H80['FTC-L'] = 0.82    # []
        self.H80['FTC-N'] = 8820    # []
        self.H80['FShaft-AV'] = 0.46    # []
        self.H80['FShaft-AP'] = 0.9     # []
        self.H80['FShaft-L'] = 0.87     # []
        self.H80['FShaft-N'] = 11100    # []
        self.H80['Pshaft-N'] = 12000    # []

        # self.H80[''] =

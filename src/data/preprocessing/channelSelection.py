import math
import sys
import pandas as pd
import numpy as np
from configuration import NOMINAL_DATA, OUT_PATH
from pandas import DataFrame

from ..structures import FileFormat

from fileUtils import composeFilename2

FILE_SET_1 = ['SN131014_AT.csv', 'SN132014_AT.csv', 'SN132018_AT.csv', 'SN133005_AT.csv', 'SN141015_AT.csv',
              'SN141016_AT.csv', 'SN131014_OH.csv', 'SN132014_OH.csv', 'SN132018_OH.csv', 'SN133005_OH.csv',
              'SN141015_OH.csv', 'SN141016_OH.csv', 'SN-H025P.csv', '300615x124010H85-200_BC04.csv']

FILE_SET_2 = ['log_191023_091554.csv', 'log_191024_090031.csv', 'log_191115_082634.csv']


def _getKey(keys, k: str):
    for key in keys:
        if key.startswith(k):
            return key

    return None


def _processFS1(df: DataFrame) -> pd.DataFrame:
    # Kanaly ze zkusebnovych dat:
    # [0] Ng
    # [2] Tq / Mk
    # [3]  FF / Q prutok paliva
    # [15] t4 = ITT
    # [21] p0 vnejsi tlak
    # [26] pt tlak na turbine
    # --
    # [?] alt - vyska letu
    # [?] indikovana rychlost
    # --
    # [O] t1 (°C) - teplota okolniho vzduchu
    # [AH] Povv (kPa) - odpousteci ventil

    # keys = ['nG (%)', 'Mk (Nm)', 'Qp (l/hod)', 't4 (°C)', 'P0 (kPa)', 'Pt (kPa)', 't1 (°C)', 'Povv (kPa)']
    # keys = ['nG (%)', 'Mk (Nm)', 'Qp (l/hod)', 't4 (ˇC)', 'P0 (kPa)', 'Pt (kPa)', 't1 (ˇC)', 'Povv (kPa)']
    # dataFrame = df[keys]
    # print("## NARROW-DOWN HEAD:\n", dataFrame.head())

    # obcas je v tech datech pekny bordel..
    # v SN132014_OH.csv SN133005_OH.csv SN141015_OH.csv vubec neni t2 a/nebo p2!!
    key_t2 = None
    for key in ['t2c (řC)', 't2c (°C)', 't2c(°C)', 't2c (ˇC)', 't2c (ďż˝C)',
                't3c (řC)', 't3c (°C)', 't3c(°C)', 't3c (ˇC)']:
        if key in df.keys():
            key_t2 = key
            break

    if not key_t2:
        print("## T2 KEYz:", df.keys()[10:20])
        print("## P2 KEYz:", df.keys()[20:30])

    ndf = DataFrame(index=df.index)
    ndf = ndf.assign(NG=df['nG (%)'])
    ndf = ndf.assign(TQ=df['Mk (Nm)'])  # ft lbs -> Nm; * 1.3558
    ndf = ndf.assign(FC=df['Qp (l/hod)'])
    ndf = ndf.assign(ITT=df[_getKey(df.keys(), 't4')])  ## t4 (°C) | t4 (ˇC)
    ndf = ndf.assign(P0=df.get('P0 (kPa)', NOMINAL_DATA['P0'] / 1000))  # tlak okolniho vzduchu [kPa]
    ndf = ndf.assign(PT=df['Pt (kPa)'])  # tlak v torkmetru, tj. v meraku krouticiho momentu [kPa]
    ndf = ndf.assign(T0=df.get(_getKey(df.keys(), 't1'), NOMINAL_DATA['T0']))  # teplota okolniho vzduchu
    ndf = ndf.assign(NP=df['nV (1/min)'])  # tocky vrtule
    if key_t2:
        ndf = ndf.assign(T2=df[key_t2])  # teplota na vystupu z kompresoru
    if 'P2 (kPa)' in df.keys():
        ndf = ndf.assign(P2=df['P2 (kPa)'])  # staticky tlak za kompresorem [Pa]
    # ndf = ndf.assign(povv=df['Povv (kPa)'])  # tlak odpousteciho ventilu [kPa]

    ndf = ndf.astype(float)

    ndf['P0'] = ndf['P0'] * 1000  # [kPa] -> [Pa]
    ndf['PT'] = ndf['PT'] * 1000  # [kPa] -> [Pa]
    if 'P2' in ndf.keys():
        ndf['P2'] = ndf['P2'] * 1000  # [kPa] -> [Pa]
    # ndf['povv'] = ndf['povv'] * 1000  # [Pa]

    # Calculated Shaft Power - SP [W]:
    ndf['SP'] = ndf['TQ'] * 2 * math.pi * ndf['NP'] / 60

    # zero velocity for test-bench data:
    ndf['TAS'] = 0

    # elevation of the test-bench location (LKHK):
    ndf['ALT'] = 241

    if 'P2' in ndf.keys():
        ndf['PK0C'] = ndf['P2'] / ndf['P0']

    if 'T2' in ndf.keys():
        ndf['T2R'] = (ndf['T2'] + 273.15) * ((15 + 273.15) / (ndf['T0'] + 273.15)) - 273.15

    return [ndf]


def _processFD1(df: DataFrame) -> pd.DataFrame:
    """
    Flight data 1.
    :param df:
    :return:
    """

    # drop columns containing text;
    dropCols = [0, 1, 30, 44, 45, 49]
    if len(dropCols) > 0:
        df = df.drop(axis=1, columns=df.keys()[dropCols])

    ndf = DataFrame(index=df.index)
    ndf = ndf.assign(NG=df[df.keys()[24]])
    ndf = ndf.assign(TQ=df[df.keys()[22]])  # ft lbs -> Nm; * 1.3558
    ndf = ndf.assign(FC=df[df.keys()[19]])
    ndf = ndf.assign(ITT=df[df.keys()[25]])
    ndf = ndf.assign(P0=101325)  # tlak v turbine neni v let. datech! -> 1013.25hPa; inch -> Pa * 0.3220074 + 0.00000075682566
    ndf = ndf.assign(PT=1079000)  # tlak v turbine neni v let. datech! -> nominalni tlak 1079 kPa
    ndf = ndf.assign(T0=df[df.keys()[5]])  # teplota okolniho vzduchu
    ndf = ndf.assign(NP=df[df.keys()[23]])  # otacky vrtule

    ndf = ndf.astype(float)

    ndf['TQ'] = ndf['TQ'] * 1.3558  # [Nm]
    ndf['FC'] = ndf['FC'] * 3.7854  # [US gph] -> [kg/h] pyca, to jsou ale jednotky!!

    ftAmsl = df[df.keys()[4]].astype(float)
    baroPressPreset = df[df.keys()[3]].astype(float)

    mAmsl = ftAmsl * 0.3048  # ft -> m
    baroPressPresetPa = (0.3220074 * baroPressPreset + 0.00000075682566) * 10000
    ambientPress = baroPressPresetPa * np.power(1 - mAmsl.values / 44330, 5.255)
    ndf['P0'] = ambientPress  # [Pa]

    return [ndf]


def _processPT6(df: DataFrame) -> pd.DataFrame:
    """
    Flight data 2.
    :param df:
    :return:
    """

    ndf = DataFrame(index=df.index)
    ndf = ndf.assign(NG=df['E1NG'])
    ndf = ndf.assign(TQ=df['E1Torq'])  # [ft lbs]; ft lbs -> Nm; * 1.3558
    ndf = ndf.assign(FC=df['E1FFlow'])
    ndf = ndf.assign(ITT=df['E1ITT'])
    ndf = ndf.assign(P0=101325)  # tlak okolniho vzduchu neni v let. datech! -> 1013.25hPa; inch -> Pa * 0.3220074 + 0.00000075682566
    ndf = ndf.assign(PT=1079000)  # tlak v turbine neni v let. datech! -> nominalni tlak 1079 kPa
    ndf = ndf.assign(T0=df['OAT'])  # teplota okolniho vzduchu
    ndf = ndf.assign(NP=df['E1NP'])  # otacky vrtule
    ndf = ndf.assign(OILT=df['E1OilT'])  # [deg.F]
    ndf = ndf.assign(OILP=df['E1OilP'])  # [psi]
    ndf = ndf.assign(GS=df['GndSpd'] * 1.852)  # [kt] -> [km/h]

    # extra channels:
    ndf = ndf.assign(TAS=df['TAS'])  # [kt]

    ndf = ndf.astype(float)

    ndf['TQ'] = ndf['TQ'] * 1.3558  # [Nm]
    ndf['FC'] = ndf['FC'] * 3.7854  # [US gph] -> [kg/h] pyca, to jsou ale jednotky!!
    ndf['OILT'] = (ndf['OILT'] - 32) * 5 / 9  # [deg.F] -> [deg.C]
    ndf['OILP'] = ndf['OILP'] * 6894.76  # [psi] -> [Pa]

    # Calculated Shaft Power - SP [W]:
    ndf['SP'] = ndf['TQ'] * 2 * math.pi * ndf['NP'] / 60

    ftAmsl = df['AltB'].astype(float)
    mAmsl = ftAmsl * 0.3048  # [ft] -> [m]
    ambientPress = 101325 * np.power(1 - mAmsl.values / 44330, 5.255)
    ndf['P0'] = ambientPress  # [Pa]

    # extra channels:
    ndf['ALT'] = mAmsl  # alt AMSL [m]
    ndf['TAS'] = ndf['TAS'] * 1.852  # [kt] -> [km/h]

    return [ndf]


def _processH80AI(df: DataFrame) -> pd.DataFrame:
    """
    H80 dev data
    :param df:
    :return:
    """

    ndf1 = DataFrame(index=df.index)  # left engine (#1)
    ndf2 = DataFrame(index=df.index)  # right engine (#2)

    ndf1['IAS'] = ndf2['IAS'] = df['IAS_LH'] * 1.852  # [kt] -> [km/h]
    ndf1['ALT'] = ndf2['ALT'] = df['Pressure_Alt'] * 0.3048  # [ft] -> [m] AMSL

    ndf1['NG'] = df['Engine_LH_NG']  # [%]
    ndf1['ITT'] = df['Engine_LH_ITT']  # [deg.C]
    ndf1['NP'] = df['Engine_LH_NP']  # [1/min]
    ndf1['TQ'] = df['Engine_LH_TQ'] / 100 * NOMINAL_DATA['TQ']  # [%] - > [Nm]
    ndf1['FC'] = df['Engine_LH_FF']  # [kg/h]

    ndf2['NG'] = df['Engine_RH_NG']  # [%]
    ndf2['ITT'] = df['Engine_RH_ITT']  # [deg.C]
    ndf2['NP'] = df['Engine_RH_NP']  # [1/min]
    ndf2['TQ'] = df['Engine_RH_TQ'] / 100 * NOMINAL_DATA['TQ']  # [%] - > [Nm]
    ndf2['FC'] = df['Engine_RH_FF']  # [kg/h]

    mAmsl = ndf1['ALT'].astype(float)
    ambientPress = 101325 * np.power(1 - mAmsl.values / 44330, 5.255)
    ndf1['P0'] = ndf2['P0'] = ambientPress  # [Pa]

    # TODO 'PT' channel not in data file!!
    # TODO 'T0' channel not in data file!!
    # TODO 'OILT' channel not in data file!!
    # TODO 'OILP' channel not in data file!!
    # TODO 'GS' channel not in data file!!
    ndf1['PT'] = ndf2['PT'] = NOMINAL_DATA['PT']  # tlak v turbine neni v let. datech! -> nominalni tlak 1079 kPa
    ndf1['T0'] = ndf2['T0'] = NOMINAL_DATA['T0']  # [deg.C] teplota okolniho vzduchu
    ndf1['OILT'] = ndf2['OILT'] = 0  # [deg.C]
    ndf1['OILP'] = ndf2['OILP'] = 0  # [Pa]
    ndf1['GS'] = ndf2['GS'] = 0  # [km/h]

    # TAS = IAS / sqrt(288.15 / (T + 273.15) * (P / 1013.25))
    ndf1['TAS'] = ndf2['TAS'] = ndf1['IAS'] / np.sqrt(288.15 / (ndf1['T0'] + 273.15) * (ndf1['P0'] / 101325))  # [km/h]

    # Calculated Shaft Power - SP [W]:
    ndf1['SP'] = ndf1['TQ'] * 2 * math.pi * ndf1['NP'] / 60
    ndf2['SP'] = ndf2['TQ'] * 2 * math.pi * ndf2['NP'] / 60

    return [ndf1, ndf2]


def _processH80GE(df: DataFrame) -> pd.DataFrame:
    raise NotImplementedError("!! H80GE is errorneus. Do not use. !!")

    # throw away all rows where TAT = 1000 or -1001
    df = df.loc[df['TAT'] > -512].loc[df['TAT'] < 512]

    # colNames = ['Counter', 'PressureAltitude', 'EngLFireWarn', 'ALTcoarse', 'ALTfine', 'TAT', 'IAS', 'EngRn1', 'EngLn1', 'EngLn2', 'EngRn2',
    #             'ColdJunctionTemp', 'EngLFuelFlow', 'EngLittAux', 'EngRFuelFlow', 'EngRFireWarn', 'EngRittAux', 'EngLtorque', 'EngRtorque', 'dummy']

    ndf1 = DataFrame(index=df.index)  # left engine (#1)
    ndf2 = DataFrame(index=df.index)  # right engine (#2)

    # TODO 'PT' channel not in data file!!
    # TODO 'T0' channel not in data file!!
    # TODO 'OILT' channel not in data file!!
    # TODO 'OILP' channel not in data file!!
    # TODO 'GS' channel not in data file!!
    ndf1['ALT'] = ndf2['ALT'] = df['PressureAltitude'] * 0.3048  # ft -> m AMSL
    ndf1['T0'] = ndf2['T0'] = df['TAT'] * 0.5  # [deg.C] TODO T0 - neni jak prepocitat
    df['CJT'] = df['ColdJunctionTemp'] * 0.2442 - 550.38  # [deg.C] ..to be added to ITT aux values

    df['IAS'] = df['IAS'].apply(lambda x: x * 0.1)  # TODO/TEMP remove after the original data is FIXED(!)
    ndf1['IAS'] = ndf2['IAS'] = df['IAS']  # [km/h] TODO IAS - neni jak prepocitat

    # LEFT engine (#1):
    ndf1['ITT'] = df['EngLittAux'] * 0.2901 + 0.2707  # + df['CJT']   # [deg.C]
    ndf1['FF'] = -8.207194079247e-7 * np.power(df['EngLFuelFlow'], 3) + 0.00581486577412 * np.power(df['EngLFuelFlow'], 2) - 13.1871100950172 * df[
        'EngLFuelFlow'] + 9668.6259  # [l/h]
    ndf1['NP'] = 295772517.415887 * np.power(df['EngLn1'], -1) - 1.00006952  # [1/n]
    ndf1['NG'] = 14258778.7402233 * np.power(df['EngLn2'], -1) - 0.999844712  # [%]
    A = -4.1517624037479
    B = 2.86510393611708E-02
    C = 3.90324915407452E-06
    D = -4.58481385951965E-10
    ndf1['TQ'] = A + B * df['EngLtorque'] + C * np.power(df['EngLtorque'], 2) + D * np.power(df['EngLtorque'], 3)  # [%]
    ndf1['TQ'] = ndf1['TQ'] / 100 * NOMINAL_DATA['TQ']  # [Nm]

    # RIGHT engine (#2):
    df['EngRittAux'] = df['EngRittAux'].apply(lambda x: x if x >= 0 else x + 4096)  # TODO/TEMP remove after the original data is FIXED(!)
    ndf2['ITT'] = df['EngRittAux'] * 0.2901 + 0.2707  # + df['CJT']   # [deg.C]
    ndf2['FF'] = -5.895989847309e-7 * np.power(df['EngRFuelFlow'], 3) + 0.00052145591727 * np.power(df['EngRFuelFlow'], 2) + 0.378941513499262 * df[
        'EngRFuelFlow'] + 0.069354256168146  # [l/h]
    ndf2['NP'] = 295772517.415887 * np.power(df['EngRn1'], -1) - 1.00006952  # [1/n]
    ndf2['NG'] = 14258778.7402233 * np.power(df['EngRn2'], -1) - 0.999844712  # [%]
    A = -7.37001679409291
    B = 0.030284844582199
    C = 1.66519454993229E-06
    D = 9.00251689374884E-11
    ndf2['TQ'] = A + B * df['EngRtorque'] + C * np.power(df['EngRtorque'], 2) + D * np.power(df['EngRtorque'], 3)  # [%]
    ndf2['TQ'] = ndf2['TQ'] / 100 * NOMINAL_DATA['TQ']  # [Nm]


def channelSelection(fileFormat: FileFormat, dataFrame, originalFileName, outPath=OUT_PATH):
    # dataFrame = dataFrame.fillna(0)
    # dataFrame.interpolate()  # fill missing values

    if originalFileName in FILE_SET_1:
        dataFrames = _processFS1(dataFrame)
    elif originalFileName in FILE_SET_2:
        dataFrames = _processFD1(dataFrame)
    elif fileFormat == FileFormat.PT6:
        dataFrames = _processPT6(dataFrame)
    elif fileFormat == FileFormat.H80AI:
        dataFrames = _processH80AI(dataFrame)
    elif fileFormat == FileFormat.H80GE:
        dataFrames = _processH80GE(dataFrame)
    else:
        raise NotImplementedError(f'[FATAL] UNKNOWN file format {fileFormat} - unable to choose processing method!\n originalFileName: {originalFileName}')

    # throw away empty dataframes:
    nonZeroLengthDataFrames = []
    for df in dataFrames:
        if len(df) > 0:
            nonZeroLengthDataFrames.append(df)
    dataFrames = nonZeroLengthDataFrames

    for engineIndex, dataFrame in enumerate(dataFrames, start=1):
        # drop rows where p0 == 0 (causes inf/zero division in dataStandardisation):
        # dataFrame = dataFrame.replace(0, np.nan)

        # drop empty data
        dataFrame = dataFrame.dropna()
        # fill missing values:
        # dataFrame.interpolate()

        # add unix timestamp column:
        dataFrame['ts'] = dataFrame.index[0].value / 1e9

        dataFrame = _populateMissingChannels(dataFrame)

        fn = composeFilename2(originalFileName, 'selectedChannelsRaw', 'csv', engineIndex=engineIndex)
        fp = f"{outPath}/{fn}"
        print(f"[INFO] Writing selected channels to '{fn}'")
        dataFrame.to_csv(fp, sep=';', encoding='utf_8')

        dataFrames[engineIndex-1] = dataFrame   # reinsert this df back to the list (we are working with a copy in the loop) (!)

    return dataFrames


def _populateMissingChannels(dataFrame: DataFrame) -> DataFrame:
    """
    :param dataFrame:
    :return: dataFrame with populated missing channels with zeros
    """
    if 'GS' not in dataFrame:  # ground speed
        dataFrame['GS'] = 0
    if 'T0' not in dataFrame:  # OAT outside air temperature
        dataFrame['T0'] = 0
    if 'P0' not in dataFrame:  # ambient pressure
        dataFrame['P0'] = 0
    if 'PT' not in dataFrame:  # turbine pressure
        dataFrame['PT'] = 0
    if 'T2' not in dataFrame:
        dataFrame['T2'] = 0
    if 'P2' not in dataFrame:
        dataFrame['P2'] = 0
    if 'FUELP' not in dataFrame:  # fuel pressure
        dataFrame['FUELP'] = 0
    if 'FIRE' not in dataFrame:  # engine on fire indication
        dataFrame['FIRE'] = int(0)

    return dataFrame

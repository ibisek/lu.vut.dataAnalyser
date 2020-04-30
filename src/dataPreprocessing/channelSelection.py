import math
import sys
import pandas as pd
import numpy as np
from configuration import NOMINAL_DATA
from pandas import DataFrame

from fileUtils import composeFilename

FILE_SET_1 = ['SN131014_AT.csv', 'SN132014_AT.csv', 'SN132018_AT.csv', 'SN133005_AT.csv', 'SN141015_AT.csv', 'SN141016_AT.csv', 'SN131014_OH.csv', 'SN132014_OH.csv', 'SN132018_OH.csv', 'SN133005_OH.csv', 'SN141015_OH.csv',
              'SN141016_OH.csv', 'SN-H025P.csv', '300615x124010H85-200_BC04.csv']

FILE_SET_2 = ['log_191023_091554.csv', 'log_191024_090031.csv', 'log_191115_082634.csv']


def _getKey(keys, k: str):
    for key in keys:
        if key.startswith(k):
            return key

    return None


def _processFS1(df):
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

    ndf = DataFrame(index=df.index)
    ndf = ndf.assign(NG=df['nG (%)'])
    ndf = ndf.assign(TQ=df['Mk (Nm)'])  # ft lbs -> Nm; * 1.3558
    ndf = ndf.assign(FC=df['Qp (l/hod)'])
    ndf = ndf.assign(ITT=df[_getKey(df.keys(), 't4')])  ## t4 (°C) | t4 (ˇC)
    ndf = ndf.assign(P0=df.get('P0 (kPa)', NOMINAL_DATA['P0']/1000))  # tlak okolniho vzduchu [kPa]
    ndf = ndf.assign(PT=df['Pt (kPa)'])  # tlak v torkmetru, tj. v meraku krouticiho momentu [kPa]
    ndf = ndf.assign(T0=df.get(_getKey(df.keys(), 't1'), NOMINAL_DATA['t0']))  # teplota okolniho vzduchu
    ndf = ndf.assign(NP=df['nV (1/min)'])  # tocky vrtule
    # ndf = ndf.assign(povv=df['Povv (kPa)'])  # tlak odpousteciho ventilu [kPa]

    ndf = ndf.astype(float)

    ndf['P0'] = ndf['P0'] * 1000  # [Pa]
    ndf['PT'] = ndf['PT'] * 1000  # [Pa]
    # ndf['povv'] = ndf['povv'] * 1000  # [Pa]

    return ndf


def _processFD1(df):
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

    return ndf


def _processFD2(df):
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
    ndf = ndf.assign(P0=101325)  # tlak v turbine neni v let. datech! -> 1013.25hPa; inch -> Pa * 0.3220074 + 0.00000075682566
    ndf = ndf.assign(PT=1079000)  # tlak v turbine neni v let. datech! -> nominalni tlak 1079 kPa
    ndf = ndf.assign(T0=df['OAT'])  # teplota okolniho vzduchu
    ndf = ndf.assign(NP=df['E1NP'])  # otacky vrtule

    # extra channels:
    ndf = ndf.assign(TAS=df['TAS'])  # [kt]

    ndf = ndf.astype(float)

    ndf['TQ'] = ndf['TQ'] * 1.3558  # [Nm]
    ndf['FC'] = ndf['FC'] * 3.7854  # [US gph] -> [kg/h] pyca, to jsou ale jednotky!!

    # Calculated Shaft Power - SP [W]:
    ndf['SP'] = ndf['TQ'] * 2 * math.pi * ndf['NP'] / 60

    ftAmsl = df['AltB'].astype(float)
    mAmsl = ftAmsl * 0.3048  # [ft] -> [m]
    ambientPress = 101325 * np.power(1 - mAmsl.values / 44330, 5.255)
    ndf['P0'] = ambientPress  # [Pa]

    # extra channels:
    ndf['ALT'] = mAmsl  # alt AMSL [m]
    ndf['TAS'] = ndf['TAS'] * 1.852     # [kt] -> [km/h]

    return ndf


def channelSelection(dataFrame, originalFileName):
    # dataFrame = dataFrame.fillna(0)
    # dataFrame.interpolate()  # fill missing values

    if originalFileName in FILE_SET_1:
        dataFrame = _processFS1(dataFrame)
    elif originalFileName in FILE_SET_2:
        dataFrame = _processFD1(dataFrame)
    # else:
    #     print('[FATAL] UNKNOWN file - unable to choose processing method!')
    #     sys.exit(0)
    else:
        # "flight-data 2"
        dataFrame = _processFD2(dataFrame)

    # drop rows where p0 == 0 (causes inf/zero division in dataStandardisation):
    dataFrame = dataFrame.replace(0, np.nan)

    # drop empty data
    dataFrame = dataFrame.dropna()
    # fill missing values:
    # dataFrame.interpolate()

    fn = composeFilename(originalFileName, 'selectedChannelsRaw', 'csv')
    print(f"[INFO] Writing selected channels to '{fn}'")
    dataFrame.to_csv(fn, sep=';', encoding='utf_8')

    return dataFrame

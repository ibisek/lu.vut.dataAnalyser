import math
import numpy as np

from fileUtils import composeFilename
from configuration import OUT_PATH, FUEL_DENSITY


def standardiseData(dataFrame, originalFileName):
    """
    :param dataFrame: filtered data
    :param originalFileName
    :return: data recalculated to 0m  MSA
    """

    dataFrame = dataFrame.copy()    # we need to make a copy otherwise the original dataFrame gets overwritten

    # print(dataFrame.keys())
    # data1: ['nG (%)', 'Mk (Nm)', 'Qp (l/hod)', 't4 (°C)', 'P0 (kPa)', 'Pt (kPa)', 't1 (°C)', 'Povv (kPa)']
    # data2: ['nG (%)', 'Mk (Nm)', 'Qp (l/hod)', 't4 (<A1>C)', 'P0 (kPa)', 'Pt (kPa)', 't1 (°C)', 'Povv (kPa)']
    # flight data: ['NG', 'TQ', 'FF', 'ITT', 'P0', 'PT', 'T0', 'NP']

    # dataFrame['tISA'] = (15 - 0.0065 * dataFrame['ALT'])

    # ITT:
    dataFrame['ITT'] = (dataFrame['ITT'] + 273.15) * ((273.15 + 15) / (273.15 + dataFrame['T0'])) - 273.15

    # NG:
    # dataFrame['NG'] = dataFrame['NG'] * np.sqrt((273.15 + 15) / (273.15 + dataFrame['T0']))

    # NP:
    dataFrame['NP'] = dataFrame['NP'] * np.sqrt((273.15 + 15) / (273.15 + dataFrame['T0']))

    # Mk / TQ:
    dataFrame['TQ'] = dataFrame['TQ'] * (101325 / (dataFrame['P0']))

    # Calculated power [W]:
    dataFrame['P'] = dataFrame['TQ'] * 2 * math.pi * dataFrame['NP']/60
    # Reduced power [W]:
    dataFrame['P'] = dataFrame['P'] * (101325 / dataFrame['P0']) * ((15+273.15) / (dataFrame['T0'] + 273.15))

    # FC / FF / QQ / Qp:
    dataFrame['FC'] = dataFrame['FC'] * FUEL_DENSITY * (101325 / (dataFrame['P0'])) * ((15 + 273.15) / (dataFrame['T0'] + 273.15))

    dataFrame = dataFrame.dropna()  # drop rows with missing values
    # dataFrame = dataFrame.interpolate()  # fill missing values

    fn = composeFilename(originalFileName, 'reduced', 'csv')
    print(f"[INFO] Writing standardised data to '{fn}'")
    dataFrame.to_csv(fn, sep=';', encoding='utf_8')

    return dataFrame

import math
import numpy as np

from fileUtils import composeFilename
from configuration import OUT_PATH, FUEL_DENSITY, CONST_R


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

    # temperature compensated to speed:
    dataFrame['T0C'] = ((dataFrame['T0'] + 273.15) + np.power(dataFrame['TAS'] / 3.6, 2) / (2 * 10004.675)) - 273.15

    # ambient pressure compensated to speed:
    dataFrame['P0C'] = dataFrame['P0'] * (1 + np.power(dataFrame['TAS'] / 3.6, 2) / (2 * CONST_R * (dataFrame['T0C'] + 273.15)))

    # import matplotlib.pyplot as plt
    # dataFrame[['P0', 'P0C']].plot()
    # plt.savefig('/tmp/00/p0c.png', dpi=200)

    # ITT:
    dataFrame['ITTR'] = (dataFrame['ITT'] + 273.15) * ((273.15 + 15) / (273.15 + dataFrame['T0C'])) - 273.15

    # NG:
    dataFrame['NGR'] = dataFrame['NG'] * np.sqrt((273.15 + 15) / (273.15 + dataFrame['T0C']))

    # NP:
    dataFrame['NPR'] = dataFrame['NP'] * np.sqrt((273.15 + 15) / (273.15 + dataFrame['T0C']))

    # Mk / TQ:
    # dataFrame['TQR'] = dataFrame['TQ'] * (101325 / (dataFrame['P0C']))

    # Reduced Shaft Power [W]:
    dataFrame['SPR'] = dataFrame['SP'] * (101325 / dataFrame['P0C']) * ((15 + 273.15) / (dataFrame['T0C'] + 273.15))

    # FC / FF / QQ / Qp:
    dataFrame['FCR'] = dataFrame['FC'] * FUEL_DENSITY * (101325 / (dataFrame['P0C'])) * np.sqrt((15 + 273.15) / (273.15 + dataFrame['T0C']))

    dataFrame = dataFrame.dropna()  # drop rows with missing values
    # dataFrame = dataFrame.interpolate()  # fill missing values

    fn = composeFilename(originalFileName, 'reduced', 'csv')
    print(f"[INFO] Writing standardised data to '{fn}'")
    dataFrame.to_csv(fn, sep=';', encoding='utf_8')

    return dataFrame

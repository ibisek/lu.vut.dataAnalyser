"""
Plots selected channels of interest
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from configuration import OUT_PATH
from fileUtils import composeFilename, loadSteadyStates
from dataAnalysis.steadyStatesUtils import rowWithinSteadyState

from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA

from fileUtils import composeFilename2


def plotChannelsOfInterest(dataFrame, originalFileName, suffix=''):

    # old: ['nG (%)', 'Mk (Nm)', 'Qp (l/hod)', 't4 (°C)', 'P0 (kPa)', 'Pt (kPa)', 't1 (°C)', 'Povv (kPa)']
    # new: ['NG', 'TQ', 'FF', 'ITT', 'p0', 'pt', 't1']
    # keyIndexes = (0, 1, 2, 3, 4, 5, 6)
    # keyIndexes = [0]  # NG
    # keyIndexes = [3]  # ITT
    # keyIndexes = [1]  # Mk
    # keyIndexes = [2]  # Qp/FF
    # keyIndexes = [7]  # Povv
    # keyIndexes = (0, 7)     # NG + Povv

    # try:
    #     keys = [dataFrame.keys()[i] for i in keyIndexes]
    # except Exception:
    #     print("[ERROR] Some key(s) are missing!")
    #     return

    # keys = dataFrame.keys()     # plot all
    keys = ['ALT', 'TAS', 'NG', 'P']

    # ax = dataFrame.plot(x=dataFrame.index, y=keys[0], figsize=(20, 15))
    ax = dataFrame[keys].plot(figsize=(20, 15))

    plt.legend(fontsize=20)
    plt.xlabel('date-time', fontsize=20)
    # plt.ylabel('values')
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
    # axes.set_xlim([xmin, xmax])
    # ax.set_ylim([90, 100])    # NG 90-100
    plt.xticks(rotation=90)
    # plt.show()

    fn = composeFilename(originalFileName, suffix, 'png')
    plt.savefig(fn)

    plt.close()


def plotChannelsOfInterestMultiY(dataFrame, originalFileName, suffix='', reducedChannels=False, outPath=OUT_PATH):
    red = '' if not reducedChannels else 'R'

    keys = ['ALT', 'TAS', 'NG'+red, 'TQ'+red, 'NP'+red, 'ITT'+red, 'FC'+red, 'SP'+red, 'SS']
    yLabels = ['ALT [m] AMSL', 'TAS [km/h]', 'NG [%]', 'TQ [Nm]', 'NP [1/min]', 'ITT [deg.C]', 'FC [kg/hod]', 'SP [kW]', 'SS - steady states']
    yRanges = [[0, 5000], [0, 500], [60, 110], [0, 3500], [0, 2200], [0, 800], [0, 300], [0, 600], [-0.05, 1.05]]
    multipliers = [1, 1, 1, 1, 1, 1, 1, 1000, 1]
    legendLabels = keys

    # steady state indication:
    intervals = loadSteadyStates(originalFileName, ssDir=outPath)
    numRows = len(dataFrame)
    arr = np.zeros([numRows])
    for i in range(numRows):
        arr[i] = 1 if rowWithinSteadyState(intervals, dataFrame.iloc[i]) else 0
    dataFrame = dataFrame.assign(SS=arr)

    plt.figure(figsize=[18, 10])

    host = host_subplot(111,  axes_class=AA.Axes)
    plt.subplots_adjust(left=0.05, right=0.74)     # 0.04-0.84 for 5 keys; 0.05-0.80 for 6 keys; 0.05-0.76 for 7 keys
    plt.legend(fontsize=20)

    host.set_xlabel("dateTime")

    for i in range(0, len(keys)):
        if i == 0:
            host.set_ylabel(yLabels[0])
            host.set_ylim(yRanges[i])

            p0, = host.plot(dataFrame.index, dataFrame['ALT'], label=legendLabels[0])

        else:
            par1 = host.twinx()

            offset = (i-1) * 50
            new_fixed_axis1 = par1.get_grid_helper().new_fixed_axis
            par1.axis["right"] = new_fixed_axis1(loc="right", axes=par1, offset=(offset, 0))

            par1.set_ylabel(yLabels[i])
            par1.set_ylim(yRanges[i])

            p1, = par1.plot(dataFrame.index, dataFrame[keys[i]]/multipliers[i], label=legendLabels[i])

    host.legend(loc='lower center')
    plt.title(f"{originalFileName}")
    plt.draw()
    # plt.show()

    fn = composeFilename2(originalFileName, suffix, 'png')
    fp = f"{outPath}/{fn}"
    plt.savefig(fp, dpi=200)

    plt.close()

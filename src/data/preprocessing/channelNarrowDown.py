# !! OBSOLETE !!
# replaced by channelSelection.py
#
# import pandas as pd
# from configuration import OUT_PATH
#
#
# def channelNarrowDown(dataFrame, originalFileName):
#     # Kanaly ze zkusebnovych dat:
#     # [0] Ng
#     # [2] Tq / Mk
#     # [3]  FF / Q prutok paliva
#     # [15] t4 = ITT
#     # [21] p0 vnejsi tlak
#     # [26] pt tlak na turbine
#     # --
#     # [?] alt - vyska letu
#     # [?] indikovana rychlost
#     # --
#     # [O] t1 (°C) - teplota okolniho vzduchu
#     # [AH] Povv (kPa) - odpousteci ventil
#
#     keys = ['nG (%)', 'Mk (Nm)', 'Qp (l/hod)', 't4 (°C)', 'P0 (kPa)', 'Pt (kPa)', 't1 (°C)', 'Povv (kPa)']
#
#     dataFrame = dataFrame[keys]
#
#     # print("## NARROW-DOWN HEAD:\n", dataFrame.head())
#
#     dataFrame = dataFrame.dropna()  # drop empty data
#
#     fn = OUT_PATH + originalFileName[:originalFileName.rindex('.')] + '-selectedChannels.csv'
#     print(f"[INFO] Writing selected channels to '{fn}'")
#     dataFrame.to_csv(fn, sep=';', encoding='utf_8')
#
#     return dataFrame

"""
Loads data from configured DB and creates df.index as datetime.
"""


import pandas as pd


def loadDBData(todo):
    pass


if __name__ == '__main__':
    dataFrame = loadDBData("TODO")

    print("## DATAFILE HEAD:\n", dataFrame.head())


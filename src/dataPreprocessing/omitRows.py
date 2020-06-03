from pandas import DataFrame

from configuration import NG_THRESHOLD, SP_THRESHOLD


def omitRowsBelowThresholds(dataFrame: DataFrame, originalFileName: str, ngThreshold=NG_THRESHOLD, spThreshold=SP_THRESHOLD):
    # drop rows where NG < 90 %
    if 'NG' not in dataFrame.keys():
        print(f"[WARN] 'NG' column not present in data file '{originalFileName}'!")
        return dataFrame

    indexNames = dataFrame[(dataFrame['NG'] < ngThreshold)].index
    if len(indexNames) > 0:
        dataFrame = dataFrame.drop(indexNames)

    indexNames = dataFrame[(dataFrame['SP'] < spThreshold)].index
    if len(indexNames) > 0:
        dataFrame = dataFrame.drop(indexNames)

    return dataFrame

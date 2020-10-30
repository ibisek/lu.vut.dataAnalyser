"""
Raw data filtering.
"""

from configuration import OUT_PATH
from fileUtils import composeFilename, composeFilename2


def filterData(rawDataFrame, originalFileName, channels=None, windowWidth=10, outPath=OUT_PATH, engineIndex = 1):
    """
    Removes high firequency noise.
    :param rawDataFrame:
    :param channels: list of channels of interest
    :return: filteredDataFrame
    """

    # remove high-frequency noise:
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.resample.html
    # df[["nv", "Mk"]].resample("10S").median().plot(figsize=(20, 10))    # 10 seconds/ median / mean
    # filteredDf = df[channelsOfInterest].rolling(10).mean()

    filteredDf = None
    if channels:
        # filteredDf = rawDataFrame[channels].rolling(windowWidth).median()
        filteredDf = rawDataFrame.rolling(windowWidth, center=True).mean()

    else:
        # filteredDf = rawDataFrame.rolling(windowWidth).median()
        filteredDf = rawDataFrame.rolling(windowWidth, center=True).mean()

    filteredDf = filteredDf.dropna()
    # filteredDf.interpolate()  # fill missing values

    fn = composeFilename2(originalFileName, 'selectedChannelsFiltered', 'csv', engineIndex=engineIndex)
    fp = f"{outPath}/{fn}"

    print(f"[INFO] Writing filtered data to '{fn}'")
    filteredDf.to_csv(fp, sep=';', encoding='utf_8')

    return filteredDf

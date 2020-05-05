
from pandas.core.series import Series


def rowWithinSteadyState(intervals: list, row: Series):
    """
    :param intervals:
    :param row:
    :return: True if index falls within a steady state
    """

    for interval in intervals:
        a = interval['startIndex']
        b = interval['endIndex']

        # if a <= index <= b:
        #     return True

        if interval['startTime'] < row.name < interval['endTime']:
            return True

    return False


def indexWithinSteadyState(intervals:list, index:int):
    """
    :param intervals:
    :param index:
    :return: True if index falls within a steady state
    """

    for interval in intervals:
        a = interval['startIndex']
        b = interval['endIndex']

        if a <= index <= b:
            return True

    return False

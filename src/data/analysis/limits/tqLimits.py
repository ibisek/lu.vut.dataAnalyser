"""
Over-torque limits.
Refer to Appendix 6 of the specification document.
"""

from data.analysis.limits.limitsBase import LimitsBase, Zone


class TqLimits(LimitsBase):
    FILE_PATH = 'images/tqLimits.png'
    X_RANGE = (0, 300)  # [s]
    Y_RANGE = (100.1, 108)  # [%]

    def __init__(self):
        super().__init__()

    def check(self, duration: int, torque: float) -> Zone:
        """
        :param duration:    duration in seconds
        :param torque:  TQ in %
        :return: Zone.A ~ OK, Zone.B ~ warning, Zone.C ~ severe problem detected
        """

        if torque < 100.1:
            return Zone.A
        elif torque >= 108:
            return Zone.C
        else:
            return self.getZone(xVal=duration, yVal=torque)


if __name__ == '__main__':
    tql = TqLimits()

    time = 300  # [s]    # v zelenem
    tq = 98  # [%]
    zone = tql.check(duration=time, torque=tq)
    print(time, tq, zone, zone == Zone.A)

    # inside the image polygons:

    time = 25  # [s]    # v zelenem
    tq = 105  # [%]
    zone = tql.check(duration=time, torque=tq)
    print(time, tq, zone, zone == Zone.A)

    time = 13  # [s]    # na hrane modreho a cerveneho
    tq = 107  # [%]
    zone = tql.check(duration=time, torque=tq)
    print(time, tq, zone, zone == Zone.C)

    time = 12  # [s]    # v modrem
    tq = 107  # [%]
    zone = tql.check(duration=time, torque=tq)
    print(time, tq, zone, zone == Zone.B)

    time = 61  # [s]
    tq = 102  # [%]
    zone = tql.check(duration=time, torque=tq)
    print(time, tq, zone, zone == Zone.B)

    time = 250  # [s]
    tq = 101  # [%]
    zone = tql.check(duration=time, torque=tq)
    print(time, tq, zone, zone == Zone.B)

    time = 30  # [s]
    tq = 107  # [%]
    zone = tql.check(duration=time, torque=tq)
    print(time, tq, zone, zone == Zone.C)

    time = 120  # [s]
    tq = 106  # [%]
    zone = tql.check(duration=time, torque=tq)
    print(time, tq, zone, zone == Zone.C)

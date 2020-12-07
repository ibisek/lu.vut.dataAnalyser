"""
Gas generator operating limits.
Refer to Appendix 2 of the specification document.
"""

from data.analysis.limits.limitsBase import LimitsBase, Zone


class NgLimits(LimitsBase):
    FILE_PATH = 'images/ngLimits.png'
    X_RANGE = (-60, 50)     # [deg.C]
    Y_RANGE = (90, 101.5)  # [%]

    def __init__(self):
        super().__init__()

    def check(self, oat: float, ng: float) -> Zone:
        """
        :param ng:    outside air temperature in deg.C
        :param oat:      NG in %
        :return: Zone.A ~ OK, Zone.B ~ above limit
        """

        if ng < 95.5 or (oat > -32.2 and ng < self.Y_RANGE[1]):
            return Zone.A
        elif ng >= self.Y_RANGE[1]:
            return Zone.B
        else:
            return self.getZone(xVal=oat, yVal=ng)


if __name__ == '__main__':
    tql = NgLimits()

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

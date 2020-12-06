"""
OTT Limits for engine operation.
Refer to Appendix 9 of the specification document.
"""

from data.analysis.limits.limitsBase import LimitsBase, Zone


class IttEngOpsLimits(LimitsBase):
    FILE_PATH = 'images/ittEngOpsLimits.png'
    X_RANGE = (0, 90)  # [s]
    Y_RANGE = (740, 809)  # [%]

    def __init__(self):
        super().__init__()

    def check(self, duration: int, itt: float) -> Zone:
        """
        :param duration:    duration in seconds
        :param itt:         ITT in deg.C
        :return:            ZONE.NONE ~ OK, Zone.A ~ warning 1, Zone.B ~ warning 2, Zone.C ~ severe problem detected
        """

        if itt < 780:
            return Zone.A
        elif itt >= 809:
            return Zone.D
        else:
            return self.getZone(xVal=time, yVal=itt)


if __name__ == '__main__':
    ittLimits = IttEngOpsLimits()

    time = 50  # [s]    # v zelenem
    itt = 770  # [def.C]
    zone = ittLimits.check(duration=time, itt=itt)
    print(time, itt, zone, zone == Zone.A)

    time = 50  # [s]    # nahore nad
    itt = 810  # [def.C]
    zone = ittLimits.check(duration=time, itt=itt)
    print(time, itt, zone, zone == Zone.D)

    # inside the image polygons:

    time = 50  # [s]
    itt = 785  # [def.C]
    zone = ittLimits.check(duration=time, itt=itt)
    print(time, itt, zone, zone == Zone.B)

    time = 50  # [s]
    itt = 800  # [def.C]
    zone = ittLimits.check(duration=time, itt=itt)
    print(time, itt, zone, zone == Zone.C)

    time = 10  # [s]
    itt = 808  # [def.C]
    zone = ittLimits.check(duration=time, itt=itt)
    print(time, itt, zone, zone == Zone.C)

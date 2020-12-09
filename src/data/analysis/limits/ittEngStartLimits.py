"""
OTT Limits for engine operation.
Refer to Appendix 9 of the specification document.
"""

from data.analysis.limits.limitsBase import LimitsBase, Zone


class IttEngStartLimits(LimitsBase):
    FILE_PATH = 'images/ittEngStartLimits.png'
    X_RANGE = (0, 30)     # [s]
    Y_RANGE = (729, 780)  # [deg.C]

    def __init__(self):
        super().__init__()

    def check(self, duration: int, itt: float) -> Zone:
        """
        :param duration:    duration in seconds
        :param itt:         ITT in deg.C
        :return:            ZONE.NONE ~ OK, Zone.A ~ Area A, Zone.B ~ Area B, Zone.C ~ return for overhaul
        """

        if itt < self.Y_RANGE[0]:
            return Zone.NONE
        elif itt >= self.Y_RANGE[1]:
            return Zone.D
        else:
            return self.getZone(xVal=duration, yVal=itt)


if __name__ == '__main__':
    ittLimits = IttEngStartLimits()

    time = 10  # [s]    # v zelenem
    itt = 725  # [def.C]
    zone = ittLimits.check(duration=time, itt=itt)
    print(time, itt, zone, zone == Zone.NONE)

    time = 10  # [s]    # nahore nad
    itt = 760  # [def.C]
    zone = ittLimits.check(duration=time, itt=itt)
    print(time, itt, zone, zone == Zone.C)

    # inside the image polygons:

    time = 10  # [s]
    itt = 732  # [def.C]
    zone = ittLimits.check(duration=time, itt=itt)
    print(time, itt, zone, zone == Zone.A)

    time = 10  # [s]
    itt = 750  # [def.C]
    zone = ittLimits.check(duration=time, itt=itt)
    print(time, itt, zone, zone == Zone.B)

    time = 4  # [s]
    itt = 779  # [def.C]
    zone = ittLimits.check(duration=time, itt=itt)
    print(time, itt, zone, zone == Zone.B)

    time = 5  # [s]
    itt = 779  # [def.C]
    zone = ittLimits.check(duration=time, itt=itt)
    print(time, itt, zone, zone == Zone.C)

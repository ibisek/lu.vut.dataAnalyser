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
    ngl = NgLimits()

    oat = 0     # [deg.C]    # v zelenem
    ng = 90    # [%]
    zone = ngl.check(oat=oat, ng=ng)
    print(oat, ng, zone, zone == Zone.A)

    # inside the image polygons:

    oat = 0  # [deg.C]    # v zelenem
    ng = 100  # [%]
    zone = ngl.check(oat=oat, ng=ng)
    print(oat, ng, zone, zone == Zone.A)

    oat = 0  # [deg.C]    # nad
    ng = 102  # [%]
    zone = ngl.check(oat=oat, ng=ng)
    print(oat, ng, zone, zone == Zone.B)

    oat = -50  # [deg.C]    # nad
    ng = 99  # [%]
    zone = ngl.check(oat=oat, ng=ng)
    print(oat, ng, zone, zone == Zone.B)

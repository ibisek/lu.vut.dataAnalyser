"""
Component coefficients and limits.
@see specs. Table 1. page 14+15
"""

from copy import deepcopy
from collections import namedtuple

ComponentLimit = namedtuple('ComponentLimit', ['Av', 'Ap', 'L', 'N'])


class ComponentLimits:
    H80 = dict()    # H75-100, H75-200, H80, H80-100, H80-200 and H85-100
    # axial compressor disc stage 1:
    H80['XM601-1021.3'] = ComponentLimit(Av=0.1, Ap=0.1, L=1.46, N=28000)
    # axial compressor disc stage 2:
    H80['XM601-1022.3'] = ComponentLimit(Av=0.1, Ap=0.1, L=1.57, N=50000)
    # impeller:
    H80['XM601-1023.3'] = ComponentLimit(Av=0.39, Ap=0.39, L=1.14, N=18300)
    H80['XM601-1023.31'] = ComponentLimit(Av=0.39, Ap=0.39, L=1.14, N=18300)
    # main shaft:
    H80['M601-1017.75'] = ComponentLimit(Av=0.32, Ap=0.32, L=1.21, N=16000)
    # fuel spray ring:
    H80['M601-2058.5'] = ComponentLimit(Av=0.42, Ap=0.42, L=1.07, N=22600)
    H80['M601-2068.5'] = ComponentLimit(Av=0.42, Ap=0.42, L=1.07, N=22600)
    # compressor turbine disc:
    H80['M601-3335.5'] = ComponentLimit(Av=0.44, Ap=0.44, L=1.04, N=17300)
    # rear shaft:
    H80['M601-3156.9'] = ComponentLimit(Av=0.32, Ap=0.32, L=1.06, N=10450)
    H80['M601-3156.5'] = ComponentLimit(Av=0.32, Ap=0.32, L=1.06, N=10450)
    # free turbine disc:
    H80['M601-3220.5'] = ComponentLimit(Av=0.59, Ap=0.93, L=0.82, N=8820)
    # free turbine disc*:
    H80['M601-3220.8'] = ComponentLimit(Av=0.69, Ap=0.95, L=0.75, N=10500)
    # free turbine shaft:
    H80['M601-4004.7'] = ComponentLimit(Av=0.46, Ap=0.90, L=0.87, N=11100)
    H80['M601-4004.5'] = ComponentLimit(Av=0.46, Ap=0.90, L=0.87, N=11100)
    # propeller shaft:
    H80['M601-6081.2'] = 12000
    H80['M601-6081.5'] = 12000

    H85 = dict()    # H85-200-BC04 (H85-200)
    # axial compressor disc stage 1:
    H85['XM601-1021.3'] = ComponentLimit(Av=0.1, Ap=0.1, L=1.46, N=28000)
    # axial compressor disc stage 2:
    H85['XM601-1022.3'] = ComponentLimit(Av=0.1, Ap=0.1, L=1.57, N=50000)
    # impeller:
    H85['XM601-1023.3'] = ComponentLimit(Av=0.39, Ap=0.39, L=1.14, N=18300)
    H85['XM601-1023.31'] = ComponentLimit(Av=0.39, Ap=0.39, L=1.14, N=18300)
    # main shaft:
    H85['XM601-1017.75'] = ComponentLimit(Av=0.32, Ap=0.32, L=1.21, N=16000)
    # fuel spray ring:
    H85['M601-2058.5'] = ComponentLimit(Av=0.42, Ap=0.42, L=1.07, N=22600)
    H85['M601-2068.5'] = ComponentLimit(Av=0.42, Ap=0.42, L=1.07, N=22600)
    # compressor turbine disc:
    H85['M601-3335.5'] = ComponentLimit(Av=0.44, Ap=0.44, L=1.04, N=17300)
    # rear shaft:
    H85['M601-3156.9'] = ComponentLimit(Av=0.32, Ap=0.32, L=1.06, N=10450)
    H85['M601-3156.5'] = ComponentLimit(Av=0.32, Ap=0.32, L=1.06, N=10450)
    # free turbine disc:
    H85['M601-3220.5'] = ComponentLimit(Av=0.66, Ap=0.94, L=1.28, N=8820)
    # free turbine shaft:
    H85['M601-4004.7'] = ComponentLimit(Av=0.37, Ap=0.88, L=1.46, N=11100)
    H85['M601-4004.5'] = ComponentLimit(Av=0.37, Ap=0.88, L=1.46, N=11100)
    # propeller shaft:
    H85['M601-6081.2'] = 12000
    H85['M601-6081.5'] = 12000

    PT6 = deepcopy(H80)     # TODO: TEMP ale asi nafurt ;)

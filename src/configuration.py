
IN_PATH = '/home/ibisek/wqz/prog/python/lu.vut.dataAnalyser/data/in/'
OUT_PATH = '/home/ibisek/wqz/prog/python/lu.vut.dataAnalyser/data/out/'

# flight data 2:
# IN_PATH = '/home/ibisek/wqz/prog/python/lu.vut.dataAnalyser/data/in/2019'

OUT_PATH_TEMPLATE = "/home/ibisek/wqz/prog/python/lu.vut.dataAnalyser/data/out/{}/{}"

NG_THRESHOLD = 80

STEADY_STATE_WINDOW_LEN = 99  # [s]
STEADY_STATE_DVAL = 0.01      # [%/100]

CSV_DELIMITER = ';'
# CSV_DELIMITER = ','

FUEL_DENSITY = 0.798    # hodnota pouzivana v excelovskych datech

NOMINAL_DATA = {
    't0': 15,           # [deg.C]
    'P0': 101325,       # [Pa]
    'NG': 95,           # [%]   97.8% | 95%
    'NP': 2086,         # [1/min]
    'FC': 215.52,       # [kg/h]
    'ITT': 674,         # [deg.C]
    'TQ': 2740,         # [Nm]
    'PT': 1079*1000,    # [Pa]
    'P': 425000,        # [W]   597000W | 425000w
}

UNITS = {
    't0': 'deg.C',
    'P0': 'Pa',
    'NG': '%',
    'NP': '1/min',
    'FC': 'kg/h',
    'ITT': 'deg.C',
    'TQ': 'Nm',
    'PT': 'Pa',
    'P': 'W',
    'IAS': 'km/h',
    'TAS': 'km/h',
}

# ['NG', 'TQ', 'FC', 'ITT', 'P0', 'PT', 'T1', 'NP']
KEYS_FOR_STEADY_STATE_DETECTION = ['NG', 'TQ', 'FC', 'ITT', 'P0', 'PT']


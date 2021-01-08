import os

DEV_MODE = True

IN_PATH = '/home/ibisek/wqz/prog/python/lu.vut.dataAnalyser/data/in/'
OUT_PATH = '/home/ibisek/wqz/prog/python/lu.vut.dataAnalyser/data/out/'

if DEV_MODE:
    IMG_PATH = '/home/ibisek/wqz/prog/python/lu.vut.dataAnalyser/images/'
else:
    IMG_PATH = 'images/'

NG_THRESHOLD = 80           # [%] N Generator (RPM)
SP_THRESHOLD = 150*1000     # [W] Shaft Power

STEADY_STATE_WINDOW_LEN = 99  # [s]
STEADY_STATE_DVAL = 0.01      # [%/100]

CSV_DELIMITER = ';'
# CSV_DELIMITER = ','

FUEL_DENSITY = 0.797  # hodnota pouzivana v excelovskych datech

CONST_R = 287.03    # universal gas constant [J/kg/K]

NOMINAL_DATA = {
    'T0': 15,           # [deg.C]
    'P0': 101325,       # [Pa]
    'NG': 91,           # [%]   97.8% | 95%
    'NP': 2086,         # [1/min]
    'FC': 215.52,       # [kg/h]
    'ITT': 674,         # [deg.C]
    'TQ': 2740,         # [Nm]
    'PT': 1079*1000,    # [Pa]
    'SP': 425000,       # [W]   597000W | 425000w
}
NOMINAL_DATA['ITTR'] = NOMINAL_DATA['ITT']
NOMINAL_DATA['SPR'] = NOMINAL_DATA['SP']
NOMINAL_DATA['NGR'] = NOMINAL_DATA['NG']
NOMINAL_DATA['FCR'] = NOMINAL_DATA['FC']
NOMINAL_DATA['TQR'] = NOMINAL_DATA['TQ']

UNITS = {
    'T0': 'deg.C',
    'T2': 'deg.C',
    'P0': 'Pa',
    'P2': 'Pa',
    'NG': '%',
    'NP': '1/min',
    'FC': 'kg/h',
    'ITT': 'deg.C',
    'TQ': 'Nm',
    'PT': 'Pa',
    'SP': 'W',
    'IAS': 'km/h',
    'TAS': 'km/h',
    'PK0C': '-',
    'OILT': 'deg.C',
    'OILP': 'Pa',

    'T2R': 'deg.C',
    'ITTR': 'deg.C',
    'NPR': '1/min',
    'FCR': 'kg/h',
    'SPR': 'W',
    'NGR': '%',
}


KEYS_FOR_STEADY_STATE_DETECTION = ['NG', 'TQ', 'FC', 'ITT', 'P0', 'PT']
KEYS_FOR_AVG_IN_SSs = ['T0', 'NP', 'OILT', 'OILP', 'TAS', 'SP', 'ALT']


DB_HOST = '10.8.0.30'   # radec
DB_PORT = 3306
DB_NAME = 'radec'
# DB_NAME = 'radec_dev' if DEV_MODE else 'radec'
DB_USER = 'ibisek'
DB_PASSWORD = 'heslo'
dbConnectionInfo = (DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD)

if DB_PASSWORD != '**':
    os.environ.setdefault('DB_HOST', DB_HOST)
    os.environ.setdefault('DB_PORT', str(DB_PORT))
    os.environ.setdefault('DB_NAME', DB_NAME)
    os.environ.setdefault('DB_USER', DB_USER)
    os.environ.setdefault('DB_PASSWORD', DB_PASSWORD)

INFLUX_DB_NAME = DB_NAME
INFLUX_DB_HOST = DB_HOST

SQLALCHEMY_DB_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

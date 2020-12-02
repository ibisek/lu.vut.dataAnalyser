
from enum import Enum
from collections import namedtuple


class FileFormat(Enum):
    UNDEFINED = 0
    PT6 = 1
    H80AI = 2
    H80GE = 3
    UNKNOWN = 255


Interval = namedtuple('Interval', ['start', 'end'])

# engine-flight-cycle work to be further done after initial preprocessing
EngineWork = namedtuple('EngineWork', ['engineId', 'flightId', 'cycleId'])

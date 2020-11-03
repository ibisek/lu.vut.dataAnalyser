
from enum import Enum
from collections import namedtuple


class RawDataFileFormat(Enum):
    PT6 = 'PT6'
    H80 = 'H80'


Interval = namedtuple('Interval', ['start', 'end'])


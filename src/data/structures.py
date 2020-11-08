
from enum import Enum
from collections import namedtuple


class RawDataFileFormat(Enum):
    PT6 = 'PT6'
    H80AI = 'H80AI'
    H80GE = 'H80GE'


Interval = namedtuple('Interval', ['start', 'end'])


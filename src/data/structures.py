from enum import Enum
from collections import namedtuple


class FileFormat(Enum):
    UNDEFINED = 0
    PT6 = 1
    H80AI = 2
    H80GE = 3
    UNKNOWN = 255

    def translate(self, escape_table) -> int:
        return self.value

    def __str__(self):
        return f'#FileFormat: {self.name} ({self.value})'


class FlightMode(Enum):
    TAXI = 'taxi'
    ENG_IDLE = 'idle'
    ENG_STARTUP = 'startup'
    TAKE_OFF = 'take-off'
    CLIMB = 'climb'
    CRUISE = 'cruise'

    def __str__(self):
        return self.value


# Interval = namedtuple('Interval', ['start', 'end'])
class Interval:

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __str__(self):
        return f'Interval {self.start} -> {self.end}'

    def before(self, other):
        """
        :param other:
        :return: True if this interval is before the other interval
        """
        if self.end < other.start:
            return True
        else:
            return False


# engine-flight-cycle work to be further done after initial preprocessing
# EngineWork = namedtuple('EngineWork', ['engineId', 'flightId', 'flightIdx', 'cycleId', 'cycleIdx'])
class EngineWork:
    def __init__(self, engineId: int, flightId: int, flightIdx: int, cycleId: int, cycleIdx: int):
        self.engineId = engineId
        self.flightId = flightId
        self.flightIdx = flightIdx
        self.cycleId = cycleId
        self.cycleIdx = cycleIdx

    def __str__(self):
        return f"#EngineWork: engineId={self.engineId}; " \
            f"flightId={self.flightId}; flightIdx={self.flightIdx}; " \
            f"cycleId={self.cycleId}; cycleIdx={self.cycleIdx}; "

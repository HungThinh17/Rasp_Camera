
from enum import Enum

class SystemState(Enum):
    INIT = 1
    READY = 2
    ERROR = 3
    RUNNING = 4
    STOP = 5
    PAUSED = 6
    IDLING_STOP = 7

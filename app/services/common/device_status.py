from enum import Enum

class DeviceState(Enum):
    INIT = 1
    READY = 2
    ERROR = 3
    RUNNING = 4
    STOP = 5
    PAUSE = 6
    IDLING_STOP = 7

class dbDeviceState:
    def __init__(self) -> None:
        self.state = DeviceState.INIT
        self.idling_ena = True

    def set_state(self, val: DeviceState):
            self.state = val

    def get_state(self) -> DeviceState:
        return self.state

    def set_idling(self, val: bool):
        self.idling_ena = val

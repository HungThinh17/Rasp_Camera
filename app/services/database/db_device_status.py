

class dbDeviceState:
    def __init__(self) -> None:
        self.state = 1   # init: 1; ready: 2; error: 3; running: 4; stop: 5; pause: 6; idling stop: 7
        self.idling_ena = True 

    def set_state(self, val):
        self.state = val
        return
    
    def get_state(self):
        return self.state
    
    def set_idling(self, val):
        self.idling_ena = val
        return
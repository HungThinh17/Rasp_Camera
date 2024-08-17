import time
import keyboard
from services.common.shared_keys import SharedKey
from services.common.system_store import SystemStore

class KeyboardController:
    def __init__(self, shared_obj):
        self.shared_obj = shared_obj
        self.system_store: SystemStore = self.shared_obj[SharedKey.SYSTEM_STORE]
        self.stop_event = self.shared_obj[SharedKey.STOP_EVENT]

    def run(self):
        while not self.stop_event:
            # check keyboard input
            kb = keyboard.read_key()
            self.system_store.set_kbCtrl(kb)
            
            time.sleep(0.2)

def keyboard_contoller_worker(shared_obj):
    keyboard_controller = KeyboardController(shared_obj)
    keyboard_controller.run()

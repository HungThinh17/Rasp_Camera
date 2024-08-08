import keyboard
import time
from module.db_main import dbSLI

def kbCtrl(stop, db: dbSLI):
    while True:
        if stop():
                break
       
        # check keyboard input
        kb = keyboard.read_key()
        db.set_kbCtrl(kb)
        
        time.sleep(0.2)

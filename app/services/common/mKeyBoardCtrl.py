import keyboard
import time
from services.database.db_main import dbSLI

def kbCtrl(stop, db: dbSLI):
    while True:
        if stop():
                break
       
        # check keyboard input
        kb = keyboard.read_key()
        db.set_kbCtrl(kb)
        
        time.sleep(0.2)

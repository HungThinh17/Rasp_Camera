
from __future__ import annotations
import time
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from module.db_main import dbSLI


class cFP:
    def __init__(self):
        self.flag = False
        self.output = False

    def FP(self, RLO):
        self.output = False
        if RLO == True and self.flag == False:
            self.flag = True
            self.output = True
        if RLO == False and self.flag == True:
            self.flag = False
            self.output = False
        return self.output

def sysTimer(stop, db: 'dbSLI'):
    dt=0
    tn = time.perf_counter()
    tn1 = tn

    while 1:
        tn = time.perf_counter()
        dt = 1000 * (tn - tn1)
        db.set_dt(dt)
        db.set_msec_now(db.msec_now + dt)
        tn1 = tn

        # reset gps milisec
        if db.reset_msec:
            db.set_msec_now(0)
            db.set_reset_msec(False)

        # default pulse cycle 250 ms
        db.p250.pulse(dt, 125, 125)
        db.p250.start()

        # default pulse cycle 500 ms
        db.p500.pulse(dt, 250, 250)
        db.p500.start()
        
        # default pulse cycle 1000 ms
        db.p800.pulse(dt, 400, 400)
        db.p800.start()

        # default pulse cycle 1000 ms
        db.p1000.pulse(dt, 500, 500)
        db.p1000.start()
        
        # default pulse cycle 1200 ms
        db.p1200.pulse(dt, 600, 600)
        db.p1200.start()

        # default pulse cycle 1500 ms
        db.p1500.pulse(dt, 750, 750)
        db.p1500.start()

        # default pulse cycle 2500 ms
        db.p2500.pulse(dt, 1250, 1250)
        db.p2500.start()
        
        # default pulse cycle 5000 ms
        db.p5000.pulse(dt, 2500, 2500)
        db.p5000.start()        
        
        # default pulse cycle 10000 ms
        db.p10000.pulse(dt, 5000, 5000)
        db.p10000.start()
        
        # idling time
        db.timer_idling.timer_ON(dt, 2000)

        if stop():
            break

        time.sleep(0.001)

    return


from __future__ import annotations

import time
from services.common.shared_keys import SharedKey
from services.common.system_store import SystemStore

class TimerService:
    def __init__(self, system_store, stop_event):
        self.system_store: SystemStore = system_store
        self.stop_event = stop_event
    
    def run(self):
        dt=0
        tn = time.perf_counter()
        tn1 = tn

        while not self.stop_event:
            tn = time.perf_counter()
            dt = 1000 * (tn - tn1)

            # self.system_store.set_dt(dt)
            time_data = self.system_store.get_gps_captured_data()
            time_data.set_msec_now(time_data.get_msec_now() + dt)
            tn1 = tn

            # reset gps milisec
            if self.system_store.gps_captured_data.reset_msec:
                self.system_store.gps_captured_data.set_msec_now(0)
                self.system_store.gps_captured_data.set_reset_msec(False)
            
            self.system_store.set_gps_captured_data(time_data) # update milisecond

            # default pulse cycle 250 ms
            self.system_store.p250.pulse(dt, 125, 125)
            self.system_store.p250.start()

            # default pulse cycle 500 ms
            self.system_store.p500.pulse(dt, 250, 250)
            self.system_store.p500.start()
            
            # default pulse cycle 1000 ms
            self.system_store.p800.pulse(dt, 400, 400)
            self.system_store.p800.start()

            # default pulse cycle 1000 ms
            self.system_store.p1000.pulse(dt, 500, 500)
            self.system_store.p1000.start()
            
            # default pulse cycle 1200 ms
            self.system_store.p1200.pulse(dt, 600, 600)
            self.system_store.p1200.start()

            # default pulse cycle 1500 ms
            self.system_store.p1500.pulse(dt, 750, 750)
            self.system_store.p1500.start()

            # default pulse cycle 2500 ms
            self.system_store.p2500.pulse(dt, 1250, 1250)
            self.system_store.p2500.start()
            
            # default pulse cycle 5000 ms
            self.system_store.p5000.pulse(dt, 2500, 2500)
            self.system_store.p5000.start()        
            
            # default pulse cycle 10000 ms
            self.system_store.p10000.pulse(dt, 5000, 5000)
            self.system_store.p10000.start()
            
            # idling time
            self.system_store.timer_idling.timer_ON(dt, 2000)
            time.sleep(0.001)
        return

def timer_service_worker(system_store, stop_event):
    timer_service = TimerService(system_store, stop_event)
    timer_service.run()

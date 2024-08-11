#!/usr/bin/python

# =============================================
# For debugging ...
# =============================================
import sys
if len(sys.argv) > 1:
    if sys.argv[1] == "debug":
        import debugpy
        debugpy.listen(("0.0.0.0", 5678))
        print("Waiting for debugger attach...")
        debugpy.wait_for_client()
        debugpy.breakpoint()
        print("Debugger is attached!")
# =============================================

import time
import math
import numpy as np
import queue
import keyboard
import threading
import os.path
#import datetime


from threading import Thread
from module.mCamera import run_picamera, convert_array_to_file, auto_gain_PID
from module.mGps import run_GPS
from module.mKeyBoardCtrl import kbCtrl
from module.mCommon import sysTimer
# from pynput.keyboard import Key
from module.mSQL import run_add_data
from module.db_main import dbSLI
from module.mGUI import display_GUI, mainGUI

##=====================================================
# define a main function
##=====================================================
def main():    

    db_SLI = dbSLI()

    print("Hello test camera")

    db_SLI.sysState.set_state(1) # init
    
    stop_threads = False
    
    # 1. Define thread
    # Thread: system timer
    t0 = Thread(target=sysTimer, args =(lambda : stop_threads, db_SLI, ))
    # Thread: capture camera
    t1 = Thread(target=run_picamera, args =(lambda : stop_threads, db_SLI, ))
    # Thread: save image array to file
    t2 = Thread(target=convert_array_to_file, args =(lambda : stop_threads, db_SLI, ))
    # Thread: PID control analog gain
    t3 = Thread(target=auto_gain_PID, args =(lambda : stop_threads, 110, db_SLI, ))
    # Thread: run GPS
    t4 = Thread(target=run_GPS, args =(lambda : stop_threads, db_SLI, ))
    # Thread: keyboard control
    # t5 = Thread(target=kbCtrl, args =(lambda : stop_threads, db_SLI))
    # Thread: input database
    t6 = Thread(target=run_add_data, args =(lambda : stop_threads, db_SLI))
    # Thread: GUI display
    #t10 = Thread(target=update_GUI_parameter, args =(lambda : stop_threads, db_SLI))
    # Thread: GUI display
    t11 = Thread(target=mainGUI, args=(db_SLI, ))
    
    # 2. Run thread
    t0.start()
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    # t5.start()
    t6.start()
    #t10.start()
    t11.start()
    
    # print cpu serial number
    print("CPU serial number: ", db_SLI.CPU_serial)
    
    # 3. Control program status by keyboard
    while True:
        camState = db_SLI.cameraState.get_state()
        gpsState = db_SLI.GpsState.get_state()
        dataBaseState = db_SLI.DataBaseState.get_state()
        sysState = db_SLI.sysState.get_state()
        
        if camState == 4: # camera ready
            # auto gain
            db_SLI.fpAutoGain.FP(db_SLI.p5000.Output)

            if db_SLI.fpAutoGain.output:
                db_SLI.set_camera_gain_sample()

        # system ready
        if camState == 4 and gpsState == 4 and sysState != 4 and sysState != 7 and sysState != 6: # and db_SLI.DataBaseState == 2: 
            db_SLI.sysState.set_state(2) # system ready, waiting for run command
            #print("system ready")

        # system error
        if camState == 3 or gpsState == 3: # or db_SLI.DataBaseState == 3: 
            db_SLI.sysState.set_state(3) # system error, atleast one module error
            #print("system error")
 
        # system running
        if sysState == 4:
            # auto capture interval
            db_SLI.fpAutoCapture.FP(db_SLI.p800.Output)

            if db_SLI.fpAutoCapture.output == True and db_SLI.capture_interval_mode == True:
                db_SLI.set_camera_ctrl_signal()
                print("Auto capture interval")

            # auto capture distance
            #print (sysState)

        # idling stop
        if db_SLI.speed_now <= 2: 
            db_SLI.timer_idling.start()
        else: 
            db_SLI.timer_idling.stop()
        
        #db_SLI.timer_idling.timer_ON(db_SLI.dt, 200)
            

        # keyboard control
        #if db_SLI.kb == "r" or db_SLI.imgGUI.btn_GUI_capture_auto == True:
        # system run transition
        if ((db_SLI.kb == "r" or db_SLI.imgGUI.btn_GUI_capture_auto == True) and (sysState == 2 or sysState == 6)) or (sysState == 7 and (db_SLI.timer_idling.Output == False or db_SLI.imgGUI.btn_GUI_Idling_cmd == False)):
            db_SLI.sysState.set_state(4) # system run 
            db_SLI.clear_kbCtrl()
            db_SLI.imgGUI.set_btn_GUI_capture_auto(False)
            print("system run trasition")
        
        # system pause transition
        if (db_SLI.kb == "r" or db_SLI.imgGUI.btn_GUI_capture_auto == True) and (sysState == 4 or sysState ==7): # stop 
            db_SLI.sysState.set_state(6) # system pause 
            db_SLI.clear_kbCtrl()
            db_SLI.imgGUI.set_btn_GUI_capture_auto(False)
            print("system pause")

        # system idling transition
        if db_SLI.timer_idling.Output == True and db_SLI.imgGUI.btn_GUI_Idling_cmd == True and sysState == 4:
            db_SLI.sysState.set_state(7) # system idling stop 
            print("system idling")


            #db_SLI.clear_kbCtrl()
            #db_SLI.imgGUI.set_btn_GUI_capture_auto(False)

        if db_SLI.kb == "a" or db_SLI.imgGUI.btn_GUI_capture_single == True:
            db_SLI.set_camera_ctrl_signal()
            db_SLI.clear_kbCtrl()
            db_SLI.imgGUI.set_btn_GUI_capture_single(False)
                
        if db_SLI.kb == "c" or db_SLI.imgGUI.btn_GUI_exit == True:
            print("Closing all thread")
            db_SLI.clear_kbCtrl()
            db_SLI.imgGUI.set_btn_GUI_exit(False)
            stop_threads = True
            break
            
        time.sleep(0.02)

        #print(cycle_elapse)
       
       

    # 4. waiting thread finish
    t0.join()
    print("t0 closed")
    t1.join()
    print("t1 closed")
    t2.join()
    print("t2 closed")
    t3.join()
    print("t3 closed")
    t4.join()
    print("t4 closed")
    # t5.join()
    # print("t5 closed")
    t6.join()
    print("t6 closed")
    #t10.join()
    t11.join()
    print("t11 closed")

    print ("all thread close")
  

##=====================================================
if __name__ == "__main__":
    main()

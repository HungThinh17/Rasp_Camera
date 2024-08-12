import sys
import time
import signal

# =============================================
# For debugging ...
# =============================================
if len(sys.argv) > 1:
    import debugpy

    if sys.argv[1] == "debug":
        debugpy.listen(("0.0.0.0", 5678))
        print("Waiting for debugger attach...")
        debugpy.wait_for_client()
        debugpy.breakpoint()
        print("Debugger is attached!")
    
    def signal_handler(sig, frame):
        print('Signal received, closing app...')
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

# =============================================

from threading import Thread, Event
from concurrent.futures import ThreadPoolExecutor
from enum import Enum

from module.db_main import dbSLI
from module.mCamera import auto_gain_PID, convert_array_to_file, run_picamera
from module.mCommon import sysTimer
from module.mGUI import mainGUI
from module.mGps import run_GPS
from module.mSQL import run_add_data

# Global list to hold thread objects
gThreads = []

class SystemState(Enum):
    INIT = 1
    READY = 2
    ERROR = 3
    RUNNING = 4
    IDLING_STOP = 7
    PAUSED = 6

def initialize_system(db_SLI):
    db_SLI.sysState.set_state(SystemState.INIT)  # init
    print("Hello SLI Image !")

def start_threads(db_SLI, stop_event):
    threads = []

    # Thread: system timer
    timer_thread = Thread(target=sysTimer, args=(stop_event, db_SLI))
    threads.append(timer_thread)

    # Thread: capture camera
    camera_thread = Thread(target=run_picamera, args=(stop_event, db_SLI))
    threads.append(camera_thread)

    # Thread: save image array to file
    file_thread = Thread(target=convert_array_to_file, args=(stop_event, db_SLI))
    threads.append(file_thread)

    # Thread: PID control analog gain
    gain_thread = Thread(target=auto_gain_PID, args=(stop_event, 110, db_SLI))
    threads.append(gain_thread)

    # Thread: run GPS
    gps_thread = Thread(target=run_GPS, args=(stop_event, db_SLI))
    threads.append(gps_thread)

    # Thread: input database
    data_thread = Thread(target=run_add_data, args=(stop_event, db_SLI))
    threads.append(data_thread)

    # Thread: GUI display
    gui_thread = Thread(target=mainGUI, args=(db_SLI,))
    threads.append(gui_thread)

    # Start all threads
    for thread in threads:
        thread.start()

    return threads

def control_program_flow(db_SLI):
    while True:
        system_state = handle_system_state(db_SLI)
        handle_camera_state(db_SLI, system_state)
        handle_user_input(db_SLI, system_state)
        handle_idling(db_SLI, system_state)
        time.sleep(0.02)

def handle_system_state(db_SLI):
    cam_state = db_SLI.cameraState.get_state()
    gps_state = db_SLI.GpsState.get_state()
    data_base_state = db_SLI.DataBaseState.get_state()
    sys_state = db_SLI.sysState.get_state()

    if cam_state == SystemState.RUNNING and gps_state == SystemState.RUNNING and \
       sys_state != SystemState.RUNNING and sys_state != SystemState.IDLING_STOP and \
       sys_state != SystemState.PAUSED:
        db_SLI.sysState.set_state(SystemState.READY)  # system ready, waiting for run command

    if cam_state == SystemState.ERROR or gps_state == SystemState.ERROR:
        db_SLI.sysState.set_state(SystemState.ERROR)  # system error, at least one module error

    return sys_state

def handle_camera_state(db_SLI, system_state):
    if system_state == SystemState.RUNNING:
        db_SLI.fpAutoCapture.FP(db_SLI.p800.Output)
        if db_SLI.fpAutoCapture.output and db_SLI.capture_interval_mode:
            db_SLI.set_camera_ctrl_signal()
            print("Auto capture interval")

def handle_user_input(db_SLI, system_state):
    if (db_SLI.kb == "r" or db_SLI.imgGUI.btn_GUI_capture_auto) and (system_state == SystemState.READY or system_state == SystemState.PAUSED):
        transition_to_run_state(db_SLI)
    elif (db_SLI.kb == "r" or db_SLI.imgGUI.btn_GUI_capture_auto) and (system_state == SystemState.RUNNING or system_state == SystemState.IDLING_STOP):
        transition_to_pause_state(db_SLI)
    elif db_SLI.kb == "a" or db_SLI.imgGUI.btn_GUI_capture_single:
        db_SLI.set_camera_ctrl_signal()
        db_SLI.clear_kbCtrl()
        db_SLI.imgGUI.set_btn_GUI_capture_single(False)
    elif db_SLI.kb == "c" or db_SLI.imgGUI.btn_GUI_exit:
        stop_threads(db_SLI, gThreads)

def transition_to_run_state(db_SLI):
    db_SLI.sysState.set_state(SystemState.RUNNING)  # system run
    db_SLI.clear_kbCtrl()
    db_SLI.imgGUI.set_btn_GUI_capture_auto(False)
    print("system run transition")

def transition_to_pause_state(db_SLI):
    db_SLI.sysState.set_state(SystemState.PAUSED)  # system pause
    db_SLI.clear_kbCtrl()
    db_SLI.imgGUI.set_btn_GUI_capture_auto(False)
    print("system pause")

def handle_idling(db_SLI, system_state):
    if db_SLI.speed_now <= 2:
        db_SLI.timer_idling.start()
    else:
        db_SLI.timer_idling.stop()

    if db_SLI.timer_idling.Output and db_SLI.imgGUI.btn_GUI_Idling_cmd and system_state == 4:
        db_SLI.sysState.set_state(SystemState.IDLING_STOP)  # system idling stop
        print("system idling")

def stop_threads(db_SLI, threads):
    print("Closing all threads")
    db_SLI.clear_kbCtrl()
    db_SLI.imgGUI.set_btn_GUI_exit(False)

    # Stop and join threads here
    for thread in threads:
        thread.join()

def main():
    db_SLI = dbSLI()
    initialize_system(db_SLI)

    stop_event = lambda:False 
    try:
        gThreads = start_threads(db_SLI, stop_event)
        print("CPU serial number: ", db_SLI.CPU_serial)
    except any as e:
        print("Error starting threads:", e)

    try:
        control_program_flow(db_SLI)
    except KeyboardInterrupt:
        stop_event.set()
    finally:
        stop_threads(db_SLI, gThreads)
        print("All threads closed")

if __name__ == "__main__":
    main()
import os
import sys
import time

# =============================================
# For debugging ...
# =============================================
if '--debug' in sys.argv:
    import debugpy
    debugpy.listen(("0.0.0.0", 5678))
    print("Waiting for debugger attach...")
    debugpy.wait_for_client()
    debugpy.breakpoint()
    print("Debugger is attached!")
# =============================================

# =============================================
# For changing cwd ... 
# =============================================
try:
    os.chdir(os.path.dirname(__file__))
    print(f"Current working directory changed to {os.getcwd()}")
except OSError as e:
    print(f"Error: {e}")
# =============================================

from threading import Thread, Event
from services.common.system_store import SystemStore
from services.common.system_status import SystemState
from services.devTools.logger import Logger

from services.timer.timer_service import timer_service_worker
from services.gps.gps_service import gps_service_worker
from services.database.database_service import database_service_worker
from services.camera.cameraService import camera_controller_worker
from services.image.imageService import image_processor_worker

if '--headless' in sys.argv:
    from services.web.webService import web_service_worker
else:
    from services.gui.guiService import gui_service_worker


class System:

    def __init__(self):
        self.threads = []
        self.processes = {}

        # Create a shared dictionary to store the database connection
        self.system_store: SystemStore = None
        self.stop_event = Event()
        self.logger = None

    def initialize_system(self):
        """
        Initialize the system components (camera, image processor, and GUI controller).
        """
        self.system_store = SystemStore()
        self.system_store.logger = Logger(os.path.join(os.getcwd(), "archives/logs"), "sli_image.log").get_logger()
        self.logger = self.system_store.logger

        self.system_store.set_cpu_serial(self.getserial())
        self.system_store.sysState.set_state(SystemState.INIT)  # init
        self.logger.info(f"{__class__.__name__}: Hello SLI Image !")

    def set_stop_event(self):
        self.stop_event.set()

    def start_app(self):
        """
        Start the application by creating and starting threads and processes for various tasks.
        """
        self.threads = []

        # Thread: system timer
        timer_thread = Thread(name='Timer Service', target=timer_service_worker, args=(self.system_store, self.stop_event,))
        self.threads.append(timer_thread)

        # Thread: run GPS
        gps_thread = Thread(name='GPS Service', target=gps_service_worker, args=(self.system_store, self.stop_event,))
        self.threads.append(gps_thread)

        # Thread: GUI display
        if '--headless' in sys.argv:
            web_thread = Thread(name='Web Service', target=web_service_worker, args=(self.system_store, self.stop_event))
            self.threads.append(web_thread)
        else:
            gui_thread = Thread(name='GUI Service', target=gui_service_worker, args=(self.system_store, self.stop_event,))
            self.threads.append(gui_thread)

        # Thread: input database
        data_thread = Thread(name='Database Service', target=database_service_worker, args=(self.system_store, self.stop_event))
        self.threads.append(data_thread)

        # capture camera
        camera_thread = Thread(name='Camera Service', target=camera_controller_worker, args=(self.system_store, self.stop_event))
        self.threads.append(camera_thread)


        # save image array to file
        image_thread = Thread(name='Image Service', target=image_processor_worker, args=(self.system_store, self.stop_event))
        self.threads.append(image_thread)

        # Start all threads
        for thread in self.threads:
            thread.start()


    def handle_system_state(self):
        """
        Handle the system state based on the camera and GPS states.
        """
        cam_state = self.system_store.cameraState.get_state()
        gps_state = self.system_store.GpsState.get_state()
        sys_state = self.system_store.sysState.get_state()

        if cam_state == SystemState.RUNNING and gps_state == SystemState.RUNNING and \
           sys_state != SystemState.RUNNING and sys_state != SystemState.IDLING_STOP and \
           sys_state != SystemState.PAUSED:
            self.system_store.sysState.set_state(SystemState.READY)  # system ready, waiting for run command

        if cam_state == SystemState.ERROR or gps_state == SystemState.ERROR:
            self.system_store.sysState.set_state(SystemState.ERROR)  # system error, at least one module error

        return sys_state

    def handle_camera_state(self, system_state):
        """
        Handle the camera state based on the system state and capture interval mode.
        """
        if system_state == SystemState.RUNNING:
            self.system_store.fpAutoCapture.FP(self.system_store.p800.Output)
            if self.system_store.fpAutoCapture.output and self.system_store.capture_interval_mode:
                self.system_store.set_camera_ctrl_signal()
                self.logger.info(f"{__class__.__name__}: Auto capture interval")

    def handle_user_input(self, system_state):
        """
        Handle user input (keyboard or GUI) to transition between system states or capture images.
        """
        if (self.system_store.keyboardControl == "r" or self.system_store.imgGUI.request_auto_capture) and \
           (system_state == SystemState.READY or system_state == SystemState.PAUSED):
            self.transition_to_run_state(self.system_store)

        elif (self.system_store.keyboardControl == "r" or self.system_store.imgGUI.request_auto_capture) and \
             (system_state == SystemState.RUNNING or system_state == SystemState.IDLING_STOP):
            self.transition_to_pause_state(self.system_store)

        elif self.system_store.keyboardControl == "a" or self.system_store.imgGUI.request_single_capture:
            self.system_store.set_camera_ctrl_signal()
            self.system_store.clear_kbCtrl()
            self.system_store.imgGUI.set_btn_GUI_capture_single(False)

        elif self.system_store.keyboardControl == "c" or self.system_store.imgGUI.request_exit_app:
            self.stop_app()

    def transition_to_run_state(self):
        """
        Transition the system to the RUNNING state.
        """
        self.system_store.sysState.set_state(SystemState.RUNNING)  # system run
        self.system_store.clear_kbCtrl()
        self.system_store.imgGUI.set_btn_GUI_capture_auto(False)
        self.logger.info(f"{__class__.__name__}: system run transition")

    def transition_to_pause_state(self):
        """
        Transition the system to the PAUSED state.
        """
        self.system_store.sysState.set_state(SystemState.PAUSED)  # system pause
        self.system_store.clear_kbCtrl()
        self.system_store.imgGUI.set_btn_GUI_capture_auto(False)
        self.logger.info(f"{__class__.__name__}: system pause")

    def handle_idling(self, system_state):
        """
        Handle the idling state based on the vehicle speed and user input.
        """
        if self.system_store.gps_captured_data.speed_now <= 2:
            self.system_store.timer_idling.start()

        else:
            self.system_store.timer_idling.stop()

        if self.system_store.timer_idling.Output and self.system_store.imgGUI.request_idling and system_state == 4:
            self.system_store.sysState.set_state(SystemState.IDLING_STOP)  # system idling stop
            self.logger.info(f"{__class__.__name__}: system idling")

    def stop_app(self):
        """
        Stop the application by joining all threads and processes.
        """
        self.logger.info(f"{__class__.__name__}: Closing all threads and processes")
        self.system_store.clear_kbCtrl()
        self.system_store.imgGUI.set_btn_GUI_exit(False)
        self.set_stop_event()

        for thread in self.threads:
            thread.join()

        for process in self.processes.values():
            process.join()

    def control_program_flow(self):
        """
        Control the program flow by handling system state, camera state, user input, and idling state.
        """
        while not self.stop_event.is_set():
            system_state = self.handle_system_state()
            self.handle_camera_state(system_state)
            self.handle_user_input(system_state)
            self.handle_idling(system_state)
            time.sleep(0.02)

    def getserial(self):
        cpuserial = "0000000000000000"
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if line.startswith('Serial'):
                        cpuserial = line.split(':')[1].strip()
                        break
        except:
            cpuserial = "ERROR000000000"

        return cpuserial

def main():
    """
    Main function to initialize and run the application.
    """
    try:
        system = System()
        system.initialize_system()
        system.start_app()
        system.logger.info(f"CPU serial number: {system.system_store.CPU_serial}")
        system.control_program_flow()

    except Exception as e:
        system.logger.error(f"Error starting threads: {e}")

    except KeyboardInterrupt:
        system.stop_app()

    finally:
        system.logger.info("All threads closed")
        sys.exit(0)

if __name__ == "__main__":
    main()

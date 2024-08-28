import sys
import time
import numpy as np
from simple_pid import PID
from picamera2 import Picamera2
from threading import Event
from multiprocessing import Queue, Manager, Process
from services.devTools.profilingService import Profiler
from services.common.system_store import SystemStore
from services.image.img_metadata import RawImageData
from services.camera.camera_manager import CameraManager
from services.camera.camera_store import CameraStore
from services.web.guiService import image_streamer_worker
from services.camera.camera_controller import capture_process_worker

# PID controller parameters
PID_KP = 0.02
PID_KI = 0.005
PID_KD = 0.01
PID_SETPOINT = 40  # Desired grayscale brightness value

tuning = Picamera2.load_tuning_file("imx477.json")

class CameraService:
    def __init__(self, system_store: SystemStore, stop_event: Event):
        self.camera_store: CameraStore = system_store.camera_store
        self.system_store = system_store
        self.stop_event = stop_event
        self.logger = system_store.logger
        self.camera_manager = CameraManager()

        self.camera_store.get_preview_img = self.camera_manager.capture_preview_image

        self.pid = PID(PID_KP, PID_KI, PID_KD, setpoint=PID_SETPOINT)
        self.pid.output_limits = (1, 200)
        self.pid.proportional_on_measurement = True
        self.pid.sample_time = 0.01

    def capture_image(self):
        with Profiler(function_call="captureImage"):
            self.logger.info(f"{__class__.__name__}:Capturing image...")
            start_time = time.perf_counter()

            # image_arr = self.camera_manager.capture_image()
            # self.system_store.imgGUI.set_lastImg(image_arr)
            # self.system_store.imgGUI.set_newImg(True)

            image_arr = self.camera_manager.capture_still_image()
            gps_captured_data = self.system_store.get_gps_captured_data()
            img_raw_data = RawImageData(image_arr, gps_captured_data)
            self.camera_store.put_img_raw_to_queue(img_raw_data)

            end_time = time.perf_counter()
            capture_time = end_time - start_time
            self.logger.info(
                f"{__class__.__name__}:"
                f"Image captured. Brightness: {self.system_store.get_last_img_grey_brightness()}, "
                f"Gain: {self.system_store.camPara.AnalogGain}, Time: {capture_time:.6f} seconds"
            )

    def auto_gain_adjustment(self):
        last_img = self.camera_store.get_gain_sample_img()
        grey_brightness = self.image_brightness_grey(last_img)
        self.system_store.set_last_img_grey_brightness(grey_brightness)

        new_gain = self.pid(grey_brightness)
        self.system_store.camPara.set_analog_gain(new_gain)
        self.system_store.camPara.set_update()

        self.logger.info(f"{__class__.__name__}: Brightness: {grey_brightness}, Gain: {new_gain}")

    def image_brightness_grey(self, img: np.ndarray) -> float:
        roi = img[:4056, 1216:3040, :]  # 1216 = 3040*2/5
        grey_img = np.mean(roi, axis=2)
        return np.average(grey_img)

    def run(self):
        self.system_store.cameraState.set_state(1)  # init
        self.logger.info(f"{__class__.__name__}: Initializing Camera Service...")
        self.camera_manager.start_camera_process(capture_process_worker)
        time.sleep(1)
        self.system_store.cameraState.set_state(2)  # ready

        self.logger.info(f"{__class__.__name__}:Ready... Waiting for capture signal...")
        while not self.stop_event.is_set():
            self.system_store.cameraState.set_state(4)  # running

            if self.system_store.camPara.update:
                self.camera_manager.update_controls(self.system_store.camPara.AnalogGain)
                self.system_store.camPara.clear_update()

            if self.system_store.camera_gain_sample:
                self.system_store.clear_camera_gain_sample()
                image_arr = self.camera_manager.capture_image()
                self.camera_store.put_gain_sample_img(image_arr)

            if self.system_store.get_camera_ctrl_signal():
                self.capture_image()
                self.system_store.clear_camera_ctrl_signal()

            if self.system_store.camera_store.request_streamer['run']:
                self.camera_manager.set_capture_mode(CameraManager.CaptureMode.STREAMING)
                while not self.stop_event.is_set():
                    pass

            if self.system_store.imgGUI.request_auto_capture:
                self.camera_manager.set_capture_mode(CameraManager.CaptureMode.COLLECTING)
                while self.system_store.imgGUI.request_auto_capture:
                    self.capture_image()

            if not self.camera_store.check_gain_sample_img_empty():
                self.auto_gain_adjustment()

            time.sleep(self.system_store.THREAD_SLEEP_1US)

        self.camera_manager.stop_camera_process()
        self.system_store.cameraState.set_state(5)  # stop

def camera_controller_worker(system_store, stop_event):
    try:
        camera_controller = CameraService(system_store, stop_event)
        camera_controller.run()
    except Exception as e:
        system_store.logger.error(f"Error in camera controller worker: {e}")


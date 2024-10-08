import logging
import time
import numpy as np
from simple_pid import PID
from picamera2 import Picamera2
from typing import Tuple, Optional
from threading import Event
from services.devTools.profilingService import Profiler
from services.common.system_store import SystemStore
from services.image.img_metadata import RawImageData

# PID controller parameters
PID_KP = 0.02
PID_KI = 0.005
PID_KD = 0.01
PID_SETPOINT = 40  # Desired grayscale brightness value

tuning = Picamera2.load_tuning_file("imx477.json")

class CameraController:
    def __init__(self, system_store: SystemStore, stop_event: Event):
        self.camera_store = system_store.camear_store
        self.system_store = system_store
        self.stop_event = stop_event
        self.logger = system_store.logger

        self.camera = None
        self.pid = PID(PID_KP, PID_KI, PID_KD, setpoint=PID_SETPOINT)
        self.pid.output_limits = (1, 200)
        self.pid.proportional_on_measurement = True
        self.pid.sample_time = 0.01

    def start(self):
        self.camera = Picamera2(tuning=tuning)
        config = self.camera.create_still_configuration()
        self.camera.configure(config)
        # TODO - this might caused the camera capture slower !!
        # self.camera.set_controls({"ExposureTime": self.system_store.camPara.ExposureTime, "AnalogueGain": self.system_store.camPara.AnalogGain})
        self.camera.start()
        self.logger.info(f"{__class__.__name__}:Camera initialized and ready for capture.")

    def stop(self):
        self.camera.stop()
        self.camera = None
        self.logger.info(f"{__class__.__name__}:Camera stopped.")

    def capture_image(self) -> Optional[Tuple[np.ndarray, float]]:
        with Profiler(function_call="captureImage"):
            self.logger.info(f"{__class__.__name__}:Capturing image...")
            start_time = time.perf_counter()
            image_arr = self.camera.capture_array()

            gps_captured_data = self.system_store.get_gps_captured_data()
            img_raw_data = RawImageData(image_arr, gps_captured_data)
            self.camera_store.put_img_raw_to_queue(img_raw_data)

            self.system_store.imgGUI.set_lastImg(image_arr)
            self.system_store.imgGUI.set_newImg(True)

            end_time = time.perf_counter()
            capture_time = end_time - start_time
            self.logger.info(
                f"{__class__.__name__}:"
                f"Image captured. Brightness: {self.system_store.get_last_img_grey_brightness()}, "
                f"Gain: {self.system_store.camPara.AnalogGain}, Time: {capture_time:.6f} seconds"
            )

            return image_arr

    def auto_gain_adjustment(self):
        if not self.camera_store.check_gain_sample_img_empty():
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
        self.start()
        self.system_store.cameraState.set_state(1)  # init
        time.sleep(1)
        self.system_store.cameraState.set_state(2)  # ready

        self.logger.info(f"{__class__.__name__}:Waiting for capture signal...")

        while not self.stop_event.is_set():
            self.system_store.cameraState.set_state(4)  # running

            if self.system_store.camPara.update:
                self.camera.set_controls({"AnalogueGain": self.system_store.camPara.AnalogGain})
                self.system_store.camPara.clear_update()

            if self.system_store.camera_gain_sample:
                self.system_store.clear_camera_gain_sample()
                image_arr = self.camera.capture_array()
                self.camera_store.put_gain_sample_img(image_arr)

            if self.system_store.get_camera_ctrl_signal():
                self.capture_image()
                self.system_store.clear_camera_ctrl_signal()

            self.auto_gain_adjustment()

            time.sleep(0.01)

        self.stop()
        self.system_store.cameraState.set_state(5)  # stop

def camera_controller_worker(system_store, stop_event):
    try:
        camera_controller = CameraController(system_store, stop_event)
        camera_controller.run()
    except Exception as e:
        system_store.logger.error(f"Error in camera controller worker: {e}")
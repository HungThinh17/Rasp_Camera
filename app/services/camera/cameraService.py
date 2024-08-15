
import os
import time
import logging
import numpy as np
from typing import Tuple, Optional
from datetime import datetime, timezone
from PIL import Image
from picamera2 import Picamera2
from simple_pid import PID
from services.database.db_main import dbSLI
from services.devTools.profilingService import Profiler

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load camera tuning file
TUNING_FILE = "imx477.json"
tuning = Picamera2.load_tuning_file(TUNING_FILE)

# PID controller parameters
PID_KP = 0.02
PID_KI = 0.005
PID_KD = 0.01
PID_SETPOINT = 40  # Desired grayscale brightness value

# Image storage directory
IMAGES_DIR = os.path.join(os.getcwd(), "storeImages")


class CameraController:
    _instance = None

    def __new__(cls, db: dbSLI):
        if cls._instance is None:
            cls._instance = super(CameraController, cls).__new__(cls)
            cls._instance.db = db
            cls._instance.camera = None

            cls._instance.pid = PID(PID_KP, PID_KI, PID_KD, setpoint=PID_SETPOINT)
            cls._instance.pid.output_limits = (1, 200)
            cls._instance.pid.proportional_on_measurement = True
            cls._instance.pid.sample_time = 0.01
        return cls._instance

    def start(self):
        # TODO - need to figure out why use this configuration.
        # self.camera = Picamera2(tuning=tuning)
        # config = self.camera.create_still_configuration()
        # self.camera.configure(config)
        # self.camera.set_controls({"ExposureTime": self.db.camPara.ExposureTime,
        #                            "AnalogueGain": self.db.camPara.AnalogGain})
        self.camera = Picamera2()
        self.camera.start()
        logger.info("Camera initialized and ready for capture.")

    def stop(self):
        if self.camera:
            self.camera.stop()
            self.camera = None
        logger.info("Camera stopped.")

    def capture_image(self) -> Optional[Tuple[np.ndarray, float]]:
        with Profiler(function_call="capture_image"):
            if not self.camera:
                logger.error("Camera not initialized.")
                return None, 0.0

            logger.info("Capturing image...")
            start_time = time.perf_counter()

            try:
                image_arr = self.camera.capture_array()
            except Exception as e:
                logger.error(f"Error capturing image: {e}")
                return None, 0.0

            self.db.clear_camera_ctrl_signal()
            self.db.set_img_data(
                img_arr=image_arr,
                year=self.db.year_now,
                month=self.db.month_now,
                day=self.db.day_now,
                hour=self.db.hour_now,
                min=self.db.minute_now,
                sec=self.db.second_now,
                msec=int(self.db.msec_now / 10),
                lat=self.db.lat_now,
                lon=self.db.lon_now,
                alt=self.db.alt_now,
                numSat=self.db.numsat_now,
            )

            self.db.imgGUI.set_lastImg(image_arr)
            self.db.imgGUI.set_newImg(True)

            end_time = time.perf_counter()
            capture_time = end_time - start_time
            logger.info(
                f"Image captured. Brightness: {self.db.get_last_img_grey_brightness()}, "
                f"Gain: {self.db.camPara.AnalogGain}, Time: {capture_time:.6f} seconds"
            )

            return image_arr, capture_time

    def auto_gain_adjustment(self):
        if not self.camera:
            logger.error("Camera not initialized.")
            return

        if not self.db.check_gain_sample_img_empty():
            last_img = self.db.get_gain_sample_img()
            grey_brightness = self.image_brightness_grey(last_img)
            self.db.set_last_img_grey_brightness(grey_brightness)

            new_gain = self.pid(grey_brightness)
            self.db.camPara.set_analog_gain(new_gain)
            self.db.camPara.set_update()

            logger.info(f"Brightness: {grey_brightness}, Gain: {new_gain}")

    def image_brightness_grey(self, img: np.ndarray) -> float:
        roi = img[:4056, 1216:3040, :]  # 1216 = 3040*2/5
        grey_img = np.mean(roi, axis=2)
        return np.average(grey_img)

    def run(self, stop_event):
        self.start()
        self.db.cameraState.set_state(1)  # init
        time.sleep(1)
        self.db.cameraState.set_state(2)  # ready

        logger.info("Waiting for capture signal...")

        while not stop_event():
            self.db.cameraState.set_state(4)  # running

            if self.db.camPara.update:
                self.camera.set_controls({"AnalogueGain": self.db.camPara.AnalogGain})
                self.db.camPara.clear_update()

            if self.db.camera_gain_sample:
                self.db.clear_camera_gain_sample()
                image_arr = self.camera.capture_array()
                self.db.put_gain_sample_img(image_arr)

            if self.db.get_camera_ctrl_signal():
                self.capture_image()

            self.auto_gain_adjustment()

            time.sleep(0.01)

        self.stop()
        self.db.cameraState.set_state(5)  # stop

    def save_image_to_file(self, img_data):
        with Profiler(function_call="saveToFileStoreToDb"):
            current_date = datetime.now(timezone.utc)
            dirname1 = current_date.strftime("%Y%m%d")
            dirname2 = f"{img_data.img_hour:02d}{img_data.img_min:02d}{img_data.img_sec:02d}{img_data.img_msec:02d}"
            filename = f"{dirname1}{dirname2}"

            image_dir = os.path.join(IMAGES_DIR, dirname1)
            os.makedirs(image_dir, exist_ok=True)

            image_path = os.path.join(image_dir, f"{filename}.jpeg")
            pil_image = Image.fromarray(img_data.img_arr)
            
            # Check if the image mode is RGBA and convert to RGB if necessary
            if pil_image.mode == 'RGBA':
                pil_image = pil_image.convert('RGB')
            pil_image.save(image_path, format='JPEG', optimize=True, quality=80)

            self.db.set_img_data_db(
                self.db.CPU_serial,
                filename,
                dirname1,
                dirname2,
                img_data.img_lat,
                img_data.img_lon,
                img_data.img_alt,
                img_data.img_numSat,
            )

    def convert_array_to_file(self, stop_event):
        logger.info("Starting image conversion and saving...")

        while not stop_event():
            if self.db.year_now != 0 and not self.db.check_img_data_empty():
                img_data = self.db.get_img_data_0()
                self.save_image_to_file(img_data)

            time.sleep(0.1)

        logger.info("Image conversion and saving stopped.")

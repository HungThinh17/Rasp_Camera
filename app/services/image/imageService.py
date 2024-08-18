import os
import time
import logging
from threading import Event
from datetime import datetime, timezone
from PIL import Image
from services.common.system_store import SystemStore
from services.common.shared_keys import SharedKey
from services.image.img_filedata import FileImageData
from services.camera.camera_store import CameraStore
from services.devTools.profilingService import Profiler

logger = logging.getLogger(__name__)

# Image storage directory
IMAGES_DIR = os.path.join(os.getcwd(), "storeImages")

class ImageProcessor:
    def __init__(self, system_store: SystemStore, stop_event):
        self.system_store = system_store
        self.stop_event: Event = stop_event
        self.cameraStore: CameraStore = system_store.camear_store

    def save_image_to_file(self, img_data):
        with Profiler(function_call="saveToFileStoreToDb"):
            current_date = datetime.now(timezone.utc)
            dirname1 = current_date.strftime("%Y%m%d")
            dirname2 = f"{img_data.img_hour:02d}{img_data.img_min:02d}{img_data.img_sec:02d}{img_data.img_msec:0f}"
            filename = f"{dirname1}{dirname2}"

            image_dir = os.path.join(IMAGES_DIR, dirname1)
            os.makedirs(image_dir, exist_ok=True)

            image_path = os.path.join(image_dir, f"{filename}.jpeg")
            pil_image = Image.fromarray(img_data.img_arr)

            # Check if the image mode is RGBA and convert to RGB if necessary
            if pil_image.mode == 'RGBA':
                pil_image = pil_image.convert('RGB')
            pil_image.save(image_path, format='JPEG', optimize=True, quality=80)

            image_data = FileImageData(
                self.system_store.CPU_serial,
                filename,
                dirname1,
                dirname2,
                img_data.img_lat,
                img_data.img_lon,
                img_data.img_alt,
                img_data.img_numSat,
            )

            self.cameraStore.put_img_file_to_queue(image_data)

    def run(self):
        logger.info("Starting image conversion and saving...")
        while not self.stop_event.is_set():
            if self.system_store.gps_captured_data.year_now != 0 and not self.cameraStore.is_img_raw_db_empty():
                img_data = self.cameraStore.get_first_img_raw_from_queue()
                self.save_image_to_file(img_data)

            time.sleep(0.1)

        logger.info("Image conversion and saving stopped.")

def image_processor_worker(system_store, stop_event):
    try:
        image_processor = ImageProcessor(system_store, stop_event)
        image_processor.run()
    except Exception as e:
        logger.error(f"Error in image_processor_worker: {e}")
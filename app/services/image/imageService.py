import os
import time
import logging
from multiprocessing import Queue
from datetime import datetime, timezone
from PIL import Image
from services.common.shared_keys import SharedKey
from services.image.img_filedata import FileImageData
from services.camera.camera_store import CameraStore
from services.common.system_store import SystemStore
from services.devTools.profilingService import Profiler

logger = logging.getLogger(__name__)

# Image storage directory
IMAGES_DIR = os.path.join(os.getcwd(), "storeImages")

class ImageProcessor:
    def __init__(self, shared_obj, camera_store, shared_data_queue):
        self.shared_obj = shared_obj
        self.system_store: SystemStore = self.shared_obj[SharedKey.SYSTEM_STORE]
        self.stop_event = self.shared_obj[SharedKey.STOP_EVENT]
        self.cameraStore: CameraStore = camera_store
        self.shared_data_queue: Queue = shared_data_queue

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

            self.shared_data_queue.put(image_data)

    def run(self):
        logger.info("Starting image conversion and saving...")
        while not self.stop_event:
            if self.system_store.gps_captured_data.year_now != 0 and not self.cameraStore.is_img_raw_db_empty():
                img_data = self.cameraStore.get_first_img_raw_from_queue()
                self.save_image_to_file(img_data)

            time.sleep(0.1)

        logger.info("Image conversion and saving stopped.")

def image_processor_worker(shared_obj, camera_store, shared_data_queue):
    image_processor = ImageProcessor(shared_obj, camera_store, shared_data_queue)
    image_processor.run()
import os
import time
from threading import Event
from datetime import datetime, timezone
from PIL import Image
from services.common.system_store import SystemStore
from services.image.img_filedata import FileImageData
from services.camera.camera_store import CameraStore
from services.devTools.profilingService import Profiler

# Image storage directory
IMAGES_DIR = os.path.join(os.getcwd(), "storeImages")

class ImageProcessor:
    def __init__(self, system_store: SystemStore, stop_event):
        self.system_store = system_store
        self.stop_event: Event = stop_event
        self.cameraStore: CameraStore = system_store.camera_store
        self.logger = system_store.logger

    def save_image_to_file(self, img_data):
        with Profiler(function_call="saveToFileStoreToDb"):
            current_date = datetime.now(timezone.utc)
            dirname1 = current_date.strftime("%Y%m%d")
            dirname2 = f"{img_data.img_hour:02d}{img_data.img_min:02d}{img_data.img_sec:02d}{img_data.img_msec:03.0f}"
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
                image_path
            )

            self.cameraStore.put_img_file_to_queue(image_data)

    def clear_images_directory(self):
        for root, dirs, files in os.walk(IMAGES_DIR, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        
        print(f"All contents of {IMAGES_DIR} have been removed.")

    def run(self):
        self.logger.info(f"{__class__.__name__}:Start image processing service")
        while not self.stop_event.is_set():
            if not self.cameraStore.is_img_raw_db_empty():
                self.logger.info(f"{__class__.__name__}:Saving image...")
                img_data = self.cameraStore.get_first_img_raw_from_queue()
                self.save_image_to_file(img_data)
                self.logger.info(f"{__class__.__name__}:Done!")

            if self.system_store.imgGUI.request_clean_up:
                self.system_store.imgGUI.set_btn_GUI_clean(False)
                self.clear_images_directory()
                self.system_store.sli_database.remove_all_items()
            
            time.sleep(self.system_store.THREAD_SLEEP_1US)

        self.logger.info(f"{__class__.__name__}:Image conversion and saving stopped.")

def image_processor_worker(system_store, stop_event):
    try:
        image_processor = ImageProcessor(system_store, stop_event)
        image_processor.run()
    except Exception as e:
        system_store.logger.error(f"Error in image_processor_worker: {e}")
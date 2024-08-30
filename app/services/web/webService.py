import time
from multiprocessing import Process, Queue, Manager
from typing import List
from services.image.img_filedata import FileImageData
from services.common.system_store import SystemStore
from services.web.webServer import UserRequest, web_server_worker
from threading import Thread
from PIL import Image, ImageTk, ImageFile

class WebService:
    def __init__(self, system_store: SystemStore, stop_event):
        self.system_store = system_store
        self.camera_store = system_store.camera_store
        self.stop_event = stop_event
        self.image_queue = None
        self.request_streamer = None
        self.server_process = None
        self.user_request_dict = None

        self.preview_mode = False
        self.available_images: List[FileImageData] = None
        self.current_image_idx = 0

    def initialize(self):
        # Wait for resources to be available
        while (not self.camera_store.get_preview_img or not self.camera_store.preview_image_queue)\
                and not self.stop_event.is_set():
            time.sleep(0.1)

        self.image_queue: Queue = self.camera_store.preview_image_queue
        self.request_streamer = self.camera_store.request_streamer
        self.user_request_dict = Manager().dict()

    def start_server(self):
        self.server_process = Process(target=web_server_worker, args=(self.image_queue, self.user_request_dict, 8000))
        self.server_process.start()

    def stop_server(self):
        if self.server_process:
            self.server_process.terminate()
            self.server_process.join()

    def update_info(self):
        captured_time = self.system_store.get_gps_captured_data()
        number_of_captured_images = self.system_store.sli_database.get_number_of_items()
        time_str = "{:02d}-{:02d}-{:04d} {:02d}:{:02d}:{:02d}".format(
            captured_time.day_now,
            captured_time.month_now,
            captured_time.year_now,
            captured_time.hour_now,
            captured_time.minute_now,
            captured_time.second_now
        )
        info_text = (
            f"Time: {time_str}\n"
            f"Lat: {captured_time.lat_now:.6f}\n"
            f"Lon: {captured_time.lon_now:.6f}\n"
            f"Alt: {captured_time.alt_now}\n"
            f"Satellite: {captured_time.numsat_now}\n"
            f"Speed: {captured_time.speed_now:.2f} Km/h\n"
            f"Captured Images: {number_of_captured_images}"
        )
        return info_text
    
    def setupStreamingProcess(self):
        def feedingImgage(camera_store, image_queue, request_streamer, stop_event):
            while not stop_event.is_set():
                if request_streamer.get('run'):
                    image_queue.put(camera_store.get_preview_img())
                else:
                    time.sleep(1)
        Thread(target=feedingImgage, args=(self.camera_store, self.image_queue, self.request_streamer, self.stop_event)).start()

    def load_preview_mode(self):
        self.preview_mode = True
        self.available_images = self.system_store.sli_database.get_all_items_as_img_data()
        self.current_image_idx = 0 # reset index

    def load_preview_image(self, idx):
        img_path = self.available_images[idx].file_path
        self.user_request_dict['img_path'] = img_path


    def run(self):
        try:
            self.initialize()
            self.start_server()
            self.setupStreamingProcess()

            while not self.stop_event.is_set():
                if self.user_request_dict.get(UserRequest.STREAMING):
                    self.request_streamer['run'] = self.user_request_dict.get(UserRequest.STREAMING)
                    while not self.image_queue.empty(): self.image_queue.get_nowait() # clear queue
                    self.user_request_dict[UserRequest.STREAMING] = False # reset streaming request

                if self.user_request_dict.get(UserRequest.STOP_STREAMING):
                    self.request_streamer['run'] = False
                    self.user_request_dict[UserRequest.STOP_STREAMING] = False

                if self.user_request_dict.get(UserRequest.UPDATE_INFO):
                    self.user_request_dict['info'] = self.update_info()
                    self.user_request_dict[UserRequest.UPDATE_INFO] = False

                if self.user_request_dict.get(UserRequest.CLEAN):
                    self.system_store.imgGUI.request_clean_up = True
                    self.user_request_dict[UserRequest.CLEAN] = False

                if self.user_request_dict.get(UserRequest.SINGLE_CAPTURE):
                    self.system_store.imgGUI.request_single_capture = True
                    self.user_request_dict[UserRequest.SINGLE_CAPTURE] = False

                if self.user_request_dict.get(UserRequest.AUTO_CAPTURE):
                    self.system_store.imgGUI.request_auto_capture = True
                    self.user_request_dict[UserRequest.AUTO_CAPTURE] = False

                if self.user_request_dict.get(UserRequest.STOP_AUTO_CAPTURE):
                    self.system_store.imgGUI.request_auto_capture = False
                    self.user_request_dict[UserRequest.STOP_AUTO_CAPTURE] = False

                if self.user_request_dict.get(UserRequest.PREVIEW):
                    self.load_preview_mode()
                    self.load_preview_image(self.current_image_idx)
                    self.user_request_dict[UserRequest.PREVIEW] = False

                if self.user_request_dict.get(UserRequest.NEXT):
                    if self.current_image_idx < len(self.available_images) - 1:
                        self.current_image_idx += 1
                    self.load_preview_image(self.current_image_idx)
                    self.user_request_dict[UserRequest.NEXT] = False

                if self.user_request_dict.get(UserRequest.PREVIOUS):
                    if self.current_image_idx > 0:
                        self.current_image_idx -= 1
                    self.load_preview_image(self.current_image_idx)
                    self.user_request_dict[UserRequest.PREVIOUS] = False

        except Exception as e:
            print(f"Error in web service worker: {e}")
        finally:
            self.stop_server()

def web_service_worker(system_store, stop_event):
    try:
        web_service = WebService(system_store, stop_event)
        web_service.run()
    except Exception as e:
        print(f"Error in web service worker: {e}")
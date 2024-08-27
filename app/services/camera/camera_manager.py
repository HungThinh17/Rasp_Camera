import time
from enum import Enum
from threading import Lock
from multiprocessing import Queue, Process, Manager
from services.camera.camera_config import CameraConfig
from services.camera.camera_controller import CameraRequests

class CameraManager:
    CAMERA_INITIALIZE_TIME = 1 # seconds

    class CaptureMode(Enum):
        COLLECTING = 1
        STREAMING = 2

    def __init__(self):
        self.camera_queue = Queue()
        self.camera_requests = Manager().dict()
        self.camera_process = None
        self.request_capture = Lock()

        self.camera_requests[CameraRequests.START] = False
        self.camera_requests[CameraRequests.STOP] = False
        self.camera_requests[CameraRequests.CAPTURE] = False
        self.camera_requests[CameraRequests.UPDATE_CONTROLS] = False
        self.camera_requests[CameraRequests.UPDATE_CONFIG] = False

    def start_camera_process(self, capture_process_worker):
        self.camera_process = Process(target=capture_process_worker, args=(self.camera_requests, self.camera_queue))
        self.camera_process.start()
        time.sleep(self.CAMERA_INITIALIZE_TIME)
        self.camera_requests[CameraRequests.START] = True


    def stop_camera_process(self):
        self.camera_requests[CameraRequests.STOP] = True
        if self.camera_process:
            self.camera_process.terminate()
            self.camera_process.join()
            self.camera_process = None

    def set_capture_mode(self, mode:CaptureMode):
        if mode == self.CaptureMode.COLLECTING:
            self.camera_requests['config'] = CameraConfig.STILL
        elif mode == self.CaptureMode.STREAMING:
            self.camera_requests['config'] = CameraConfig.PREVIEW
        self.camera_requests[CameraRequests.UPDATE_CONFIG] = True

    def capture_preview_image(self):
        with self.request_capture:
            self.camera_requests['config'] = CameraConfig.PREVIEW
            self.camera_requests[CameraRequests.CAPTURE] = True
            return self.camera_queue.get()
    
    def capture_still_image(self):
        with self.request_capture:
            self.camera_requests['config'] = CameraConfig.STILL
            self.camera_requests[CameraRequests.CAPTURE] = True
            return self.camera_queue.get()

    def update_controls(self, analog_gain):
        self.camera_requests['AnalogGain'] = analog_gain
        self.camera_requests[CameraRequests.UPDATE_CONTROLS] = True

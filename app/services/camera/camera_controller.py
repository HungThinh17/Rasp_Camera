
from enum import Enum
from picamera2 import Picamera2

class CameraRequests(Enum):
    START = 0
    CAPTURE = 1
    STOP = 2
    UPDATE_CONTROLS = 3
    RECORD = 4

class CameraConfig(Enum):
    STILL = 0
    PREVIEW = 1
    VIDEO = 2

class CameraController:
    TUNING_FILE = "imx477.json"

    def __init__(self, camera_requests, camera_data_queue):
        tuning = Picamera2.load_tuning_file(CameraController.TUNING_FILE) # type: ignore
        self.camera = Picamera2(tuning=tuning)

        self.camera_requests = camera_requests
        self.camera_data_queue = camera_data_queue

        self.still_config = None
        self.preview_config = None
        self.video_config = None
        self.default_config = CameraConfig.PREVIEW

        self.init_config()

    def start(self):
        # config = self.camera.create_still_configuration()
        # self.camera.configure(config)
        self.camera_config(CameraConfig.PREVIEW)
        self.camera.start()
        print(self.camera.camera_configuration())

    def stop(self):
        if self.camera:
            self.camera.stop()
            self.camera = None

    def init_config(self):
        self.still_config = self.camera.create_still_configuration()
        self.preview_config = self.camera.create_preview_configuration()
        self.video_config = self.camera.create_video_configuration()

    def camera_config(self, camera_config: CameraConfig):
        memoi = self.camera.started
        if memoi:
            self.stop()

        if camera_config == CameraConfig.STILL:
            self.camera.configure(self.still_config)
        elif camera_config == CameraConfig.PREVIEW:
            self.camera.configure(self.preview_config)
        elif camera_config == CameraConfig.VIDEO:
            self.camera.configure(self.video_config)

        if memoi:
            self.start()

    def update_controls(self):
        self.camera.set_controls({"AnalogueGain": self.camera_requests["AnalogueGain"]})
        pass

    def capture_image(self, camera_config: CameraConfig = None):
        if camera_config  != None:
            self.camera_config(camera_config)
            
        image_arr = self.camera.capture_array()
        self.camera_data_queue.put(image_arr)

    def run(self):
        while True:
            if self.camera_requests[CameraRequests.START]:
                self.camera_requests[CameraRequests.START] = False
                self.start()

            elif self.camera_requests[CameraRequests.STOP]:
                self.camera_requests[CameraRequests.STOP] = False
                self.stop()

            elif self.camera_requests[CameraRequests.CAPTURE]:
                self.camera_requests[CameraRequests.CAPTURE] = False
                self.capture_image()

            elif self.camera_requests[CameraRequests.UPDATE_CONTROLS]:
                self.camera_requests[CameraRequests.UPDATE_CONTROLS] = False
                self.update_controls()
            else:
                pass


def capture_process_worker(capture_requests, capture_data_queue):
    try:
        capture_controller = CameraController(capture_requests, capture_data_queue)
        capture_controller.run()
    except Exception as e:
        print(f"Error in camera controller worker: {e}")

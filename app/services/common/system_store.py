import threading
from services.database.my_sql_database import MySliDatabase
from services.camera.camera_store import CameraStore
from services.gps.gps_data import GPSCaptureData
from services.camera.cam_parameter import dbCamPara
from services.timer.custom_timer import CustomTimer, cFP
from services.common.device_status import dbDeviceState
from services.gui.gui_param import GuiParams


class SystemStore:
    # Constants
    THREAD_SLEEP_1US = 0.001
    THREAD_SLEEP_10US = 0.01

    def __init__(self):
        # instance variable
        self.lock = threading.Lock()
        self.CPU_serial = None
        self.keyboardControl = None
        
        self.imgGUI = GuiParams()
        self.camPara = dbCamPara()

        self.sysState = dbDeviceState()
        self.cameraState = dbDeviceState()
        self.GpsState = dbDeviceState()
        self.ImuState = dbDeviceState()
        self.DataBaseState = dbDeviceState()

        self.gps_captured_data = GPSCaptureData()
        self.camera_store = CameraStore()
        self.sli_database = MySliDatabase()

        self.camera_ctrl_signal = False
        self.camera_status_signal = False
        self.camera_ctrl_signal_flag = False
        self.camera_gain_sample = False
        self.camera_gain_sample_flag = False
        self.last_img_grey_brightness = 0
        self.capture_interval_mode = True

        # default timer pulse
        self.p250 = CustomTimer()
        self.p500 = CustomTimer()
        self.p800 = CustomTimer()
        self.p1000 = CustomTimer()
        self.p1200 = CustomTimer()
        self.p1500 = CustomTimer()
        self.p2500 = CustomTimer()
        self.p5000 = CustomTimer()
        self.p10000 = CustomTimer()

        self.gain_pulse_interval = CustomTimer()
        self.capture_interval = CustomTimer()
        self.timer_idling = CustomTimer()

        # positive pulse flag
        self.fp250 = cFP()
        self.fp500 = cFP()
        self.fp800 = cFP()
        self.fp1000 = cFP()
        self.fp1200 = cFP()
        self.fp1500 = cFP()
        self.fp2500 = cFP()
        self.fp5000 = cFP()
        self.fp10000 = cFP()

        self.fpAutoGain = cFP()
        self.fpAutoCapture = cFP()
        self.fpUpdatePic = cFP()

        # system logger
        self.logger = None

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['lock']  # Remove the non-picklable lock object
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.lock = threading.Lock()  # Recreate the lock object


    def set_cpu_serial(self, cpu_serial):
        with self.lock:
            self.CPU_serial = cpu_serial
        return

    # Handle for GPS Captured Data
    def set_gps_captured_data(self, data: GPSCaptureData):
        with self.lock:
            self.gps_captured_data = data
        return

    def get_gps_captured_data(self):
        with self.lock:
            return self.gps_captured_data

    # Handle for Camera params
    # ===========================
    def set_camera_ctrl_signal(self):
        with self.lock:
            self.camera_ctrl_signal = True
        return self.camera_ctrl_signal

    def clear_camera_ctrl_signal(self):
        with self.lock:
            self.camera_ctrl_signal = False
        return self.camera_ctrl_signal

    def get_camera_ctrl_signal(self):
        with self.lock:
            return self.camera_ctrl_signal

    def get_last_img_grey_brightness(self):
        with self.lock:
            return self.last_img_grey_brightness

    def set_last_img_grey_brightness(self, value):
        with self.lock:
            self.last_img_grey_brightness = value
        return

    def set_kbCtrl(self, value):
        with self.lock:
            self.keyboardControl = value
        return

    def clear_kbCtrl(self):
        with self.lock:
            self.keyboardControl = ''
        return

    def get_kbCtrl(self):
        with self.lock:
            return self.keyboardControl

    def set_camera_gain_sample(self):
        with self.lock:
            self.camera_gain_sample = True
        return

    def clear_camera_gain_sample(self):
        with self.lock:
            self.camera_gain_sample = False
        return

    def set_camera_gain_sample_flag(self, val=True):
        with self.lock:
            self.camera_gain_sample_flag = val
        return

    def clear_camera_gain_sample_flag(self):
        with self.lock:
            self.camera_gain_sample_flag = False
        return

    def set_camera_capture_flag(self):
        with self.lock:
            self.camera_ctrl_signal_flag = True
        return

    def clear_camera_capture_flag(self):
        with self.lock:
            self.camera_ctrl_signal_flag = False
        return

    def get_capture_interval_mode(self):
        with self.lock:
            return self.capture_interval_mode

    def set_capture_interval_mode(self):
        with self.lock:
            self.capture_interval_mode = True
        return

    def clear_capture_interval_mode(self):
        with self.lock:
            self.capture_interval_mode = False
        return

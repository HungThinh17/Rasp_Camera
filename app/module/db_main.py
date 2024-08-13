import queue
import time
from module.db_cam_parameter import dbCamPara
from module.mTimer import db_timer
from module.db_img_metadata import dbImgMetadata
from module.mCommon import cFP
from module.db_device_status import dbDeviceState
from module.mSQL import m_SQL, dbSQL
from module.mGUI import dbGUI

def getserial():
    # Extract serial from cpuinfo file
    cpuserial = "0000000000000000"
    try:
        f = open('/proc/cpuinfo','r')
        for line in f:
            if line[0:6]=='Serial':
                cpuserial = line[10:26]
                print(cpuserial)
        f.close()
    except:
        cpuserial = "ERROR000000000"

    return cpuserial

class dbSLI:
    # contructor
    def __init__(self):

        # instance variable
        self.CPU_serial = getserial()
        
        self.sysState = dbDeviceState()
        self.cameraState = dbDeviceState()
        self.GpsState = dbDeviceState()
        self.ImuState = dbDeviceState()
        self.DataBaseState = dbDeviceState()
        
        #self.img_data: List[dbImgMetadata] = [] # list of dbImgMetadata of cam1
        self.img_data: "queue.Queue[dbImgMetadata]" = queue.Queue()

        self.sliSQL = m_SQL()
        #self.img_data_db: List[dbSQL] = [] # list of data add to database of cam1
        self.img_data_db: "queue.Queue[dbSQL]" = queue.Queue()
        
        self.imgGUI = dbGUI()

        self.queue_image_array = queue.Queue()
        self.queue_image_ID = queue.Queue()
        self.queue_gps = queue.Queue()

        self.image_ID = 0

        self.camera_ctrl_signal = False
        self.camera_status_signal = False
        self.camera_ctrl_signal_flag = False

        self.camera_gain_sample = False
        self.camera_gain_sample_flag = False
        self.gain_sample_img = queue.Queue()

        self.camPara = dbCamPara()
        self.last_img_grey_brightness = 0

        self.t0 = time.perf_counter()   # time at system start
        self.t_last = self.t0           # time at last cycle
        self.t_now = 0                  # current time
        self.dt = 0                     # time elapse each cycle in main thread in milisecond

        self.Gain_pulse_interval = db_timer()

        self.capture_interval = db_timer()
        self.capture_interval_mode = True # False: disable interval mode; True: enable intervalmode

        self.kb = ''

        #self.date_now = datetime()
        self.year_now = 0
        self.month_now = 0
        self.day_now = 0
        self.hour_now = 0
        self.minute_now = 0
        self.second_now = 0
        self.msec_now = 0
        self.lat_now = 0
        self.lon_now = 0
        self.alt_now = 0
        self.numsat_now = 0
        self.reset_msec = False
        self.speed_now = 0

        self.image_file_time = ''
        self.image_file_order_in_1_second = 0

        # default timer pulse
        self.p250 = db_timer()
        self.p500 = db_timer()
        self.p800 = db_timer()
        self.p1000 = db_timer()
        self.p1200 = db_timer()
        self.p1500 = db_timer()
        self.p2500 = db_timer()
        self.p5000 = db_timer()
        self.p10000 = db_timer()

        self.timer_idling = db_timer()

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

    

    def set_img_data(self, img_arr, year, month, day , hour, min, sec, msec, lat, lon, alt, numSat):
        data = dbImgMetadata()

        data.set_img_arr(img_arr)
        data.set_img_year(year)
        data.set_img_month(month)
        data.set_img_day(day)
        data.set_img_hour(hour)
        data.set_img_min(min)
        data.set_img_sec(sec)
        data.set_img_msec(msec)
        data.set_img_lat(lat)
        data.set_img_lon(lon)
        data.set_img_alt(alt)
        data.set_img_numSat(numSat)

        #self.img_data.append(data)
        self.img_data.put(data)
        
        del data

        return
    
    def check_img_data_empty(self):
        """
        if len(self.img_data) > 0:
            return False
        else:
            return True
        """
        return self.img_data.empty()
            
    def get_img_data_0(self):
        #return self.img_data.pop(0)
        return self.img_data.get(0)
    
    def set_img_data_db(self, deviceID, imgID, imgDate, imgTime , lat, lon, alt, numSat):
        data = dbSQL()

        data.set_deviceID(deviceID)
        data.set_imgID(imgID)
        data.set_imgDate(imgDate)
        data.set_imgTime(imgTime)
        data.set_lat(lat)
        data.set_lon(lon)
        data.set_alt(alt)
        data.set_numSat(numSat)

        #self.img_data_db.append(data)
        self.img_data_db.put(data)

        del data

        return
    
    def check_img_data_db_empty(self):
        """
        if len(self.img_data_db) > 0:
            return False
        else:
            return True
        """
        return self.img_data_db.empty()
            
    def get_img_data_db_0(self):
        #return self.img_data_db.pop(0)
        return self.img_data_db.get(0)
    
    def put_image_array_to_queue(self, value):
        self.queue_image_array.put(value)
        return
    
    def check_image_array_empty(self):
        return self.queue_image_array.empty()
    
    def get_image_array_from_queue(self):
        return self.queue_image_array.get(0)
    
    def put_image_ID_to_queue(self, value):
        self.queue_image_ID.put(value)
        return
    
    def check_image_ID_empty(self):
        return self.queue_image_ID.empty()
    
    def get_image_ID_from_queue(self):
        return self.queue_image_ID.get(0)
    
    def set_camera_ctrl_signal(self):
        self.camera_ctrl_signal = True
        return self.camera_ctrl_signal
    
    def clear_camera_ctrl_signal(self):
        self.camera_ctrl_signal = False
        return self.camera_ctrl_signal
    
    def get_camera_ctrl_signal(self):
        return self.camera_ctrl_signal
    
    def get_img_ID(self):
        return self.image_ID
    
    def increse_img_ID(self, value):
        self.image_ID += value
        return 

    def get_last_img_grey_brightness(self):
        return self.last_img_grey_brightness

    def set_last_img_grey_brightness(self, value):
        self.last_img_grey_brightness = value
        return
    
    def get_t0(self):
        return self.t0
    
    def system_time_elapse_calc(self):
        self.t_now = time.perf_counter()
        self.dt = 1000 * (self.t_now - self.t_last)
        self.t_last = self.t_now
        return self.dt

    def set_dt(self, value):
        self.dt = value
        return 
    
    def set_kbCtrl(self, value):
        self.kb = value
        return

    def clear_kbCtrl(self):
        self.kb = ''
        return
    
    def get_kbCtrl(self, value):
        return self.kb
    
    def set_camera_gain_sample(self):
        self.camera_gain_sample = True
        return
    
    def clear_camera_gain_sample(self):
        self.camera_gain_sample = False
        return
    
    def set_camera_gain_sample_flag(self, val = True):
        self.camera_gain_sample_flag = val
        return
    
    def clear_camera_gain_sample_flag(self):
        self.camera_gain_sample_flag = False
        return
    
    def set_camera_capture_flag(self):
        self.camera_ctrl_signal_flag = True
        return
    
    def clear_camera_capture_flag(self):
        self.camera_ctrl_signal_flag = False
        return
    
    def put_gain_sample_img(self, value):
        self.gain_sample_img.put(value)
        return
    
    def check_gain_sample_img_empty(self):
        return self.gain_sample_img.empty()
    
    def get_gain_sample_img(self):
        return self.gain_sample_img.get(0)
   
    def get_year_now(self):
        return self.year_now

    def set_year_now(self, value):
        self.year_now = value
        return
    
    def get_month_now(self):
        return self.month_now

    def set_month_now(self, value):
        self.month_now = value
        return
    
    def get_day_now(self):
        return self.day_now

    def set_day_now(self, value):
        self.day_now = value
        return
    
    def get_hour_now(self):
        return self.hour_now

    def set_hour_now(self, value):
        self.hour_now = value
        return

    def get_minute_now(self):
        return self.minute_now

    def set_minute_now(self, value):
        self.minute_now = value
        return
    
    def get_second_now(self):
        return self.second_now

    def set_second_now(self, value):
        self.second_now = value
        return
    
    def set_msec_now(self, val):
        self.msec_now = val
        return
    
    def get_lat_now(self):
        return self.lat_now

    def set_lat_now(self, value):
        self.lat_now = value
        return

    def get_lon_now(self):
        return self.lon_now

    def set_lon_now(self, value):
        self.lon_now = value
        return
    
    def get_alt_now(self):
        return self.alt_now

    def set_alt_now(self, value):
        self.alt_now = value
        return
    
    def get_numsat_now(self):
        return self.numsat_now

    def set_numsat_now(self, value):
        self.numsat_now = value
        return
    
    def set_speed_now(self, value):
        self.speed_now = value
        return
    
    def get_capture_interval_mode(self):
        return self.capture_interval_mode

    def set_capture_interval_mode(self):
        self.capture_interval_mode = True
        return
    
    def clear_capture_interval_mode(self):
        self.capture_interval_mode = False
        return

    def set_image_file_time(self, value):
        self.image_file_time = value
        return

    def set_image_file_order_in_1_second(self, value):
        self.image_file_order_in_1_second = value
        return  
    
    def set_reset_msec(self, val):
        self.reset_msec = val
        return
    

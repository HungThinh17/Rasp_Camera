from services.gps.gps_data import GPSCaptureData

class RawImageData:
    # contructor
    def __init__(self, img_arr, gps_captured_data: GPSCaptureData):
        
        # instance variable
        self.img_arr = img_arr      # image as array form
        self.img_ID = 0             # ID aka Name of the image
        self.img_device = ""        # device capture image

        # retreive data from gps data
        self.img_year = gps_captured_data.year_now      # year capture image
        self.img_month = gps_captured_data.month_now
        self.img_day = gps_captured_data.day_now 
        self.img_hour = gps_captured_data.hour_now
        self.img_min = gps_captured_data.minute_now
        self.img_sec = gps_captured_data.second_now
        self.img_msec = gps_captured_data.msec_now      # image order if same time
        self.img_lat = gps_captured_data.lat_now        # coor capture image
        self.img_lon = gps_captured_data.lon_now
        self.img_alt = gps_captured_data.alt_now
        self.img_numSat = gps_captured_data.numsat_now  # number of satalite capture image

    def __del__(self):
        return
    
    def set_img_arr(self, value):
        self.img_arr = value
        return
    
    def set_img_ID(self, value):
        self.img_ID = value
        return
    
    def set_img_device(self, value):
        self.img_device = value
        return
    
    def set_gps_captured_data(self, gps_captured_data):
        self.img_year = gps_captured_data.year_now      # year capture image
        self.img_month = gps_captured_data.month_now
        self.img_day = gps_captured_data.day_now 
        self.img_hour = gps_captured_data.hour_now
        self.img_min = gps_captured_data.minute_now
        self.img_sec = gps_captured_data.second_now
        self.img_msec = gps_captured_data.msec_now      # image order if same time

        self.img_lat = gps_captured_data.lat_now        # coor capture image
        self.img_lon = gps_captured_data.lon_now
        self.img_alt = gps_captured_data.alt_now
        self.img_numSat = gps_captured_data.numsat_now  # number of satalite capture image
        return
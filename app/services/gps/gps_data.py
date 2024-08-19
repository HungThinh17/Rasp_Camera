
class GPSCaptureData:

    # contructor
    def __init__(self):
        self.year_now = 0
        self.month_now = 0
        self.day_now = 0
        self.hour_now = 0
        self.minute_now = 0
        self.second_now = 0
        self.msec_now = 0           # Initialize msec_now to a default value
        self.lat_now = 0
        self.lon_now = 0
        self.alt_now = 0
        self.numsat_now = 0
        self.reset_msec = False
        self.speed_now = 0

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
    
    def get_msec_now(self):
        return self.msec_now
    
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
    
    def set_reset_msec(self, val):
        self.reset_msec = val
        return
    
    def get_reset_msec(self):
        return self.reset_msec
        
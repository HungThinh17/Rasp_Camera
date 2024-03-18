

class dbImgMetadata:
    # contructor
    def __init__(self):
        
        # instance variable
        self.img_arr = []           # image as array form
        self.img_ID = 0             # ID aka Name of the image
        self.img_device = ""        # device capture image

        self.img_year = 0           # year capture image
        self.img_month = 0
        self.img_day = 0
        self.img_hour = 0
        self.img_min = 0
        self.img_sec = 0
        self.img_msec = 0           # image order if same time

        self.img_lat = None         # coor capture image
        self.img_lon = None
        self.img_alt = None
        self.img_numSat = 0         # number of satalite capture image

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
    
    def set_img_year(self, value):
        self.img_year = value
        return
    
    def set_img_month(self, value):
        self.img_month = value
        return
    
    def set_img_day(self, value):
        self.img_day = value
        return
    
    def set_img_hour(self, value):
        self.img_hour = value
        return
    
    def set_img_min(self, value):
        self.img_min = value
        return
    
    def set_img_sec(self, value):
        self.img_sec = value
        return
    
    def set_img_msec(self, value):
        self.img_msec = value
        return
    
    def set_img_lat(self, value):
        self.img_lat = value
        return
    
    def set_img_lon(self, value):
        self.img_lon = value
        return
    
    def set_img_alt(self, value):
        self.img_alt = value
        return

    def set_img_numSat(self, value):
        self.img_numSat = value
        return
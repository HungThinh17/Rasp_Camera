class dbCamPara:
    # contructor
    def __init__(self):
        
        # instance variable
        self.ExposureTime = 2000 # microsecond
        self.AnalogGain = 1
        self.update = False
        self.measure_Gain_interval_time = 5000 # milisecond

    def get_exposure_time(self):
        return self.ExposureTime
    
    def set_exposure_time(self, value):
        self.ExposureTime = value
        return
    
    def get_analog_gain(self):
        return self.AnalogGain
    
    def set_analog_gain(self, value):
        self.AnalogGain = value
        return
    
    def set_update(self):
        self.update = True
        return
    
    def clear_update(self):
        self.update = False
        return
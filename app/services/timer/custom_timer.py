
class cFP:
    def __init__(self):
        self.flag = False
        self.output = False

    def FP(self, RLO):
        self.output = False
        if RLO == True and self.flag == False:
            self.flag = True
            self.output = True
        if RLO == False and self.flag == True:
            self.flag = False
            self.output = False
        return self.output


class CustomTimer:
    # contructor
    def __init__(self):
        self.timerData = 0      # timer data 
        self.t_start = 0
        self.dt_ON = 0
        self.dt_OFF = 0
        self.TON = False
        self.TOFF = True
        self.trigger_bit = False        # trigger timer
        self.Output = False
        self.up_flag = False

    def timer_ON(self, dt, ON_val):
        
        if self.trigger_bit == False:
            self.timerData = ON_val
            #return False
            self.Output = False
        else:
            self.timerData -= dt
            if self.timerData <= 0:
                self.Output = True               
            else:
                self.Output = False
                

        return self.Output

    

    def pulse(self, dt, ON_val, OFF_val):
        if self.trigger_bit == False:
            self.timerData = ON_val
            return False
        else:
            self.timerData -= dt
            if self.Output == False and self.timerData <= 0:              
                self.Output = True
                self.timerData = OFF_val
                return self.Output
            elif self.Output == True and self.timerData <= 0:
                self.Output = False
                self.timerData = ON_val
                return self.Output
            

    def start(self):
        self.trigger_bit = True
        return
    
    def stop(self):
        self.trigger_bit = False
        return
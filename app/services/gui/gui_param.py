
class GuiParams():
    def __init__(self) -> None:
        self.lastImg = None     # last img array was captured
        self.newImg = False     # flat: lastImg array change

        # buttons 
        self.btn_GUI_exit = False               # True: exit whole program
        self.btn_GUI_capture_single = False     # True: trigger one capture; False: no capture
        self.btn_GUI_capture_auto = False       # True: change to auto capture; False: pause auto capture
        self.btn_GUI_Idling_cmd = True
        self.btn_GUI_clean = False

    def set_lastImg(self, val):
        self.lastImg = val
        return
    
    def set_newImg(self, val):
        self.newImg = val
        return
    
    def set_btn_GUI_exit(self, val):
        self.btn_GUI_exit = val
        return
    
    def set_btn_GUI_capture_single(self, val):
        self.btn_GUI_capture_single = val
        return
    
    def set_btn_GUI_capture_auto(self, val):
        self.btn_GUI_capture_auto = val
        return

    def set_btn_GUI_Idling_cmd(self, val):
        self.btn_GUI_Idling_cmd = val
        return
    
    def set_btn_GUI_clean(self, val):
        self.btn_GUI_clean = val
        return
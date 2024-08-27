
class GuiParams():
    def __init__(self) -> None:
        self.lastImg = None     # last img array was captured
        self.newImg = False     # flat: lastImg array change

        # buttons 
        self.request_exit_app = False               # True: exit whole program
        self.request_single_capture = False     # True: trigger one capture; False: no capture
        self.request_auto_capture = False       # True: change to auto capture; False: pause auto capture
        self.request_idling = True
        self.request_clean_up = False
        self.request_streaming = False

    def set_lastImg(self, val):
        self.lastImg = val
        return
    
    def set_newImg(self, val):
        self.newImg = val
        return
    
    def set_btn_GUI_exit(self, val):
        self.request_exit_app = val
        return
    
    def set_btn_GUI_capture_single(self, val):
        self.request_single_capture = val
        return
    
    def set_btn_GUI_capture_auto(self, val):
        self.request_auto_capture = val
        return

    def set_btn_GUI_Idling_cmd(self, val):
        self.request_idling = val
        return
    
    def set_btn_GUI_clean(self, val):
        self.request_clean_up = val
        return
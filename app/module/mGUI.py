from __future__ import annotations
from tkinter import *
from PIL import Image, ImageTk
from functools import partial
from typing import TYPE_CHECKING
import tkinter as tk
import time
import numpy as np
import os

if TYPE_CHECKING:
    from module.db_main import dbSLI

class dbGUI():
    def __init__(self) -> None:
        
        self.lastImg = None     # last img array was captured
        self.newImg = False     # flat: lastImg array change

        # 
        self.btn_GUI_exit = False               # True: exit whole program
        self.btn_GUI_capture_single = False     # True: trigger one capture; False: no capture
        self.btn_GUI_capture_auto = False       # True: change to auto capture; False: pause auto capture
        self.btn_GUI_Idling_cmd = True
        # label status parameter
        self.lbl_status_txt = "System status: "
        self.lbl_status_bg = "gold"
        
        # label time parameter
        self.lbl_time_txt = "Time: "
        
        # label lat parameter
        self.lbl_lat_txt = "Lat: "
        
        # label lon parameter
        self.lbl_lon_txt = "Lon: "
        
        # label alt parameter
        self.lbl_alt_txt = "Alt: "
        
        # label number of satalite parameter
        self.lbl_numSat_txt = "Satellite: "
        
        # label idling
        self.lbl_idling_txt = "Idling ON"

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
    
    def set_lbl_status_txt(self, val):
        self.lbl_status_txt = val
        return
    
    def set_lbl_status_bg(self, val):
        self.lbl_status_bg = val
        return
    
    def set_lbl_time_txt(self, val):
        self.lbl_time_txt = val
        return
    
    def set_lbl_lat_txt(self, val):
        self.lbl_lat_txt = val
        return
    
    def set_lbl_lon_txt(self, val):
        self.lbl_lon_txt = val
        return
    
    def set_lbl_alt_txt(self, val):
        self.lbl_alt_txt = val
        return
    
    def set_lbl_numSat_txt(self, val):
        self.lbl_numSat_txt = val
        return

    def set_lbl_idling_txt(self, val):
        self.lbl_idling_txt = val
        return
    
    def set_btn_capture_auto_img(self, val):
        self.btn_capture_auto_img = val
        return

    def set_btn_GUI_Idling_cmd(self, val):
        self.btn_GUI_Idling_cmd = val
        return
    


    

class classGUI:
    def __init__(self, parent, db:'dbSLI') -> None:

        # root window title and dimension
        parent.title("Mini SLI")
        
        # Set geometry (widthxheight)
        parent.geometry('1024x530')

        self.frame = Frame(parent)
        self.frame.pack()
        # create default backgroud img
        # image capturec
        self.bg_img = Image.open(os.path.join(os.path.dirname(__file__),"../Digime.jpeg"))
        self.bg_img = self.bg_img.resize((1024, 530), Image.Resampling.LANCZOS) #1024x600
        self.bg_img = ImageTk.PhotoImage(self.bg_img)
        
        # button widget with image captured
        self.btn_img = tk.Button(parent, image = self.bg_img, command = lambda: self.btn_img_cmd(db))
        self.btn_img.place(x=0, y=0)

        
        self.label_status = tk.Label(parent, anchor="w", text="Initializing", width = 500,
                                        font =("Courier", 13, "bold"), bg = "gold", fg = "black") # Create a text label
        self.label_status.place(x=0, y=0)
        
        # label for time, lat, lon, alt, satellite
        self.label_time = tk.Label(parent, anchor="w", text= "Time: \nLat: \nLon: \nAlt: \nSatellite: \nSpeed: ", justify=LEFT,
                                    font =("Courier", 13, "bold"), bg = "black", fg = "lime") # Create a text label
        self.label_time.place(x=0, y=20)
        
        
        
        # button exit
        self.btn_exit = tk.Button(parent, text = "Exit", font = ("Courier", 10, "bold"),
                                    bg = "red", fg = "white", height = 1, width = 3, command = lambda: self.btn_exit_cmd(db, parent))
        self.btn_exit.place(x=974, y=0)
        
      
        # button capture
        self.btn_man_cap = tk.Button(parent, text = "Capture", font = ("Courier", 13, "bold"),
                                    bg = "lime", fg = "black", height = 3, width = 10, command = lambda: self.btn_man_cap_cmd(db))
        self.btn_man_cap.place(x=900, y=465)

        # button idling enable
        self.btn_idling_enable = tk.Button(parent, text = "Idling", font = ("Courier", 13, "bold"),
                                    bg = "lime", fg = "black", height = 3, width = 10, command = lambda: self.btn_idling_cmd(db))
        self.btn_idling_enable.place(x=0, y=465)

        # callback
        self._interval = self.btn_img.after(200, lambda: self.update_GUI_parameter(db))

    def btn_img_cmd(self, db:'dbSLI'):
        db.imgGUI.set_btn_GUI_capture_auto(True)
        #db.imgGUI.set_btn_GUI_capture_auto(not db.imgGUI.btn_capture_auto_img)
        return
    
    # button is manual capture command
    def btn_man_cap_cmd(self, db:'dbSLI'):
        db.imgGUI.set_btn_GUI_capture_single(True)
        return
    
    # button 
    def btn_idling_cmd(self, db:'dbSLI'):
        db.imgGUI.set_btn_GUI_Idling_cmd(not db.imgGUI.btn_GUI_Idling_cmd)
        return
    
    # button is exit command
    def btn_exit_cmd(self, db:'dbSLI', mainroot):
        db.imgGUI.set_btn_GUI_exit(True)
        self.stop_interval(mainroot)
        mainroot.destroy()
        mainroot.quit()
        return
    
    def stop_interval(self, root):
        if self._interval is not None:
            root.after_cancel(self._interval)
            self._interval = None
        return

    
    def update_GUI_parameter(self, db:'dbSLI'= None):
    
        sysState = db.sysState.get_state()
        sysStateStr = str(sysState)

        db.fpUpdatePic.FP(db.p1000.Output)
        # update new image capture
        if db.imgGUI.newImg and db.fpUpdatePic.output:
            print("new image must be show")
            db.imgGUI.set_newImg(False)

            #array = np.ones((40,40))*150
            self.bg_img = Image.fromarray(db.imgGUI.lastImg)
            self.bg_img = self.bg_img.resize((1024, 530), Image.Resampling.LANCZOS)
            #db.imgGUI.set_btn_capture_auto_img(ImageTk.PhotoImage(img))
            self.bg_img = ImageTk.PhotoImage(self.bg_img)
             # btn img
            self.btn_img.configure(image = self.bg_img)

        # label for status
        if sysState == 4:
            db.imgGUI.set_lbl_status_txt("System status " + sysStateStr + ": RECORDING")
            db.imgGUI.set_lbl_status_bg("lime")
        elif sysState == 3:
            db.imgGUI.set_lbl_status_txt("System status " + sysStateStr + ": ERROR")
            db.imgGUI.set_lbl_status_bg("red")
        elif sysState == 7:
            db.imgGUI.set_lbl_status_txt("System status " + sysStateStr + ": IDLING, speed < 2")
            db.imgGUI.set_lbl_status_bg("gold")
        else:
            db.imgGUI.set_lbl_status_txt("System status " + sysStateStr + ": PAUSE, waiting for run command")
            db.imgGUI.set_lbl_status_bg("gold")

        if db.imgGUI.btn_GUI_Idling_cmd == True:
            db.imgGUI.set_lbl_idling_txt("Idling ON")
        if db.imgGUI.btn_GUI_Idling_cmd == False:
            db.imgGUI.set_lbl_idling_txt("Idling OFF")
 
        # label for time
        dayGUI = str(db.day_now).zfill(2)
        monthGUI = str(db.month_now).zfill(2)
        yearGUI = str(db.year_now).zfill(2)
        hourGUI = str(db.hour_now).zfill(2)
        minGUI = str(db.minute_now).zfill(2)
        secGUI = str(db.second_now).zfill(2)
        timeGUI = dayGUI + "-" + monthGUI +"-" + yearGUI + " " + hourGUI + ":" + minGUI + ":" + secGUI
        
        latGUI = str(round(db.lat_now, 6))
        lonGUI = str(round(db.lon_now, 6))
        altGUI = str(db.alt_now)
        numSatGUI = str(db.numsat_now)
        speedGUI = str(round(db.speed_now, 2))
        
        lbl_info_txt = "Time: " + timeGUI + "\nLat: " + latGUI + "\nLon: " +  lonGUI + "\nAlt: " + altGUI + "\nSatellite: "  + numSatGUI + "\nSpeed: " + speedGUI + " Km/h"

        # update gui
      
        # status label
        self.label_status.configure(text = db.imgGUI.lbl_status_txt, bg = db.imgGUI.lbl_status_bg)
        # status +_*/
        self.label_time.configure(text = lbl_info_txt, anchor="w", justify=LEFT)      
        # status idlingan
        self.btn_idling_enable.configure(text = db.imgGUI.lbl_idling_txt)     



        self.btn_img.after(100, lambda: self.update_GUI_parameter(db))
        
def mainGUI(db:'dbSLI'):
    
    time.sleep(2)
    root = tk.Tk()
    GUIne = classGUI(root, db)

    time.sleep(1)
    GUIne.update_GUI_parameter(db)
    root.mainloop()

    return root


def display_GUI(stop, db: 'dbSLI'):
    db.imgGUI.btn_capture_auto_img = ImageTk.PhotoImage(db.imgGUI.btn_capture_auto_img)

    time.sleep(1)

    # root window title and dimension
    db.rootGUI.title("Mini SLI")
    
    # Set geometry (widthxheight)
    db.rootGUI.geometry('1024x530')

    

    statusVar = StringVar()
    timeVar = StringVar()
    latVar = StringVar()
    lonVar = StringVar()
    altVar = StringVar()
    numSatVar = StringVar()

    statusVar.set(db.imgGUI.lbl_status_txt)
    timeVar.set(db.imgGUI.lbl_time_txt)
    latVar.set(db.imgGUI.lbl_lat_txt)
    lonVar.set(db.imgGUI.lbl_lon_txt)
    altVar.set(db.imgGUI.lbl_alt_txt)
    numSatVar.set(db.imgGUI.lbl_numSat_txt)

    

    

    # function to change status of system pause to record and vice versa
    # button is clicked
    def btn_img_cmd():
        db.imgGUI.set_btn_GUI_capture_auto(True)
        return
    
    # button widget with image captured
    btn_img = tk.Button(db.imgGUI.root, image = db.imgGUI.btn_capture_auto_img, command = btn_img_cmd)
    btn_img.place(x=0, y=0)

    
    label_status = tk.Label(db.rootGUI, anchor="w", textvariable=db.imgGUI.lbl_status_txt, width = 500,
                                    font =("Courier", 13, "bold"), bg = db.imgGUI.lbl_status_bg, fg = "black") # Create a text label
    label_status.place(x=0, y=0)
    
    # label for time
    label_time = tk.Label(db.rootGUI, anchor="w", textvariable=timeVar,
                                font =("Courier", 13, "bold"), bg = "black", fg = "lime") # Create a text label
    label_time.place(x=0, y=20)
    
    # label for lat
    label_lat = tk.Label(db.rootGUI, anchor="w", textvariable=latVar,
                                font =("Courier", 13, "bold"), bg = "black", fg = "lime") # Create a text label
    label_lat.place(x=0, y=40)
    
    # label for lon
    label_lon = tk.Label(db.rootGUI, anchor="w", textvariable=lonVar,
                                font =("Courier", 13, "bold"), bg = "black", fg = "lime") # Create a text label
    label_lon.place(x=0, y=60)
    
    # label for alt
    
    label_alt = tk.Label(db.rootGUI, anchor="w", textvariable=altVar,
                                font =("Courier", 13, "bold"), bg = "black", fg = "lime") # Create a text label
    label_alt.place(x=0, y=80)
    
    # label for number of satalite
    label_numSat = tk.Label(db.rootGUI, anchor="w", textvariable=numSatVar,
                                    font =("Courier", 13, "bold"), bg = "black", fg = "lime") # Create a text label
    label_numSat.place(x=0, y=100)
    
    # button is exit command
    def btn_exit_cmd():
        db.imgGUI.set_btn_GUI_exit(True)
        db.imgGUI.root.quit()
        db.imgGUI.root.destroy()
        return
    # button exit
    btn_exit = tk.Button(db.rootGUI, text = "Exit", font = ("Courier", 10, "bold"),
                                bg = "red", fg = "white", height = 1, width = 3,
                                command = btn_exit_cmd)
    btn_exit.place(x=974, y=0)
    
    # button is manual capture command
    def btn_man_cap_cmd():
        db.imgGUI.set_btn_GUI_capture_single(True)
        return
    # button exit
    btn_man_cap = tk.Button(db.rootGUI, text = "Capture", font = ("Courier", 13, "bold"),
                                bg = "lime", fg = "black", height = 3, width = 10,
                                    command = btn_man_cap_cmd)
    btn_man_cap.place(x=900, y=465)
            

    """
    if stop():
        db.imgGUI.root.quit()
        db.imgGUI.root.destroy()
        break
    """

    db.rootGUI.after(250)

    #db.imgGUI.root.update()
    db.rootGUI.mainloop()


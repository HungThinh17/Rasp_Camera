import os
import time
import tkinter as tk
from PIL import Image, ImageTk
from typing import Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("gui.log"),
        logging.StreamHandler()
    ]
)

class dbGUI():
    def __init__(self) -> None:
        self.lastImg = None     # last img array was captured
        self.newImg = False     # flat: lastImg array change

        # buttons 
        self.btn_GUI_exit = False               # True: exit whole program
        self.btn_GUI_capture_single = False     # True: trigger one capture; False: no capture
        self.btn_GUI_capture_auto = False       # True: change to auto capture; False: pause auto capture
        self.btn_GUI_Idling_cmd = True

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

class GUIConfig:
    WINDOW_TITLE = "Mini SLI"
    WINDOW_WIDTH = 1024
    WINDOW_HEIGHT = 634
    FONT_FAMILY = "Courier"
    FONT_SIZE = 13
    FONT_WEIGHT = "bold"

class GUIPanel(tk.Frame):
    def __init__(self, parent, image_path, **kwargs):
        super().__init__(parent, **kwargs)
        self.image = ImageTk.PhotoImage(Image.open(image_path).resize((GUIConfig.WINDOW_WIDTH, GUIConfig.WINDOW_HEIGHT), Image.Resampling.LANCZOS))
        self.label = tk.Label(self, image=self.image)
        self.label.pack(fill=tk.BOTH, expand=True)
        logging.info(f"GUIPanel created with image: {image_path}")

    def config(self, **kwargs):
        self.label.config(**kwargs)


class GUIWidget:
    def __init__(self, parent):
        self.parent = parent
        self.widgets = {}

    def add_label(self, name, text, anchor="w", width=None, bg=None, fg=None, x=0, y=0, justify=None):
        label = GUILabel(self.parent, text, anchor=anchor, width=width, bg=bg, fg=fg)
        label.place(x=x, y=y)
        self.widgets[name] = label

    def add_button(self, name, text, command, bg=None, fg=None, height=None, width=None, x=None, y=None):
        button = GUIButton(self.parent, text, command, bg=bg, fg=fg, height=height, width=width)
        if x is not None and y is not None:
            button.place(x=x, y=y)
        self.widgets[name] = button

    def config(self, name, **kwargs):
        if name in self.widgets:
            self.widgets[name].config(**kwargs)

class GUILabel(tk.Label):
    def __init__(self, parent, text, **kwargs):
        super().__init__(
            parent,
            text=text,
            font=(GUIConfig.FONT_FAMILY, GUIConfig.FONT_SIZE, GUIConfig.FONT_WEIGHT),
            **kwargs
        )
        logging.info(f"GUILabel created with text: {text}")

class GUIButton(tk.Button):
    def __init__(self, parent, text, command, **kwargs):
        super().__init__(
            parent,
            text=text,
            font=(GUIConfig.FONT_FAMILY, GUIConfig.FONT_SIZE, GUIConfig.FONT_WEIGHT),
            command=command,
            **kwargs
        )
        logging.info(f"GUIButton created with text: {text}")

class GUIController:
    __instance = None

    def __new__(cls, db):
        if cls.__instance is None:
            cls.__instance = super(GUIController, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self, db):
        if self.__initialized:
            return
        self.__initialized = True
        self.parent = None
        self.db = db
        # self.init_gui()
        logging.info("GUI initialized")

    def init_gui(self):
        self.parent.title(GUIConfig.WINDOW_TITLE)
        self.parent.geometry(f"{GUIConfig.WINDOW_WIDTH}x{GUIConfig.WINDOW_HEIGHT}")
        logging.info(f"Window created with title: {GUIConfig.WINDOW_TITLE} and geometry: {GUIConfig.WINDOW_WIDTH}x{GUIConfig.WINDOW_HEIGHT}")

        # Create the background panel
        image_path = os.path.join(os.path.dirname(__file__), "../Digime.jpeg")
        self.bg_panel = GUIPanel(self.parent, image_path, width=GUIConfig.WINDOW_WIDTH, height=GUIConfig.WINDOW_HEIGHT)
        self.bg_panel.place(x=0, y=0)

        # Create a GUIWidget instance to manage GUI components
        self.gui_widget = GUIWidget(self.parent)

        # Add labels
        self.gui_widget.add_label("lbStatus", "Initializing", width=500, bg="gold", fg="black", x=0, y=0)
        self.gui_widget.add_label("lbInfo", "Time: \nLat: \nLon: \nAlt: \nSatellite: \nSpeed: ", anchor="w", justify=tk.LEFT, bg="black", fg="lime", x=0, y=20)

        # Add buttons
        self.gui_widget.add_button("btExit", "Exit", self.handle_exit_button_click, bg="red", fg="white", height=1, width=3, x=GUIConfig.WINDOW_WIDTH - 50, y=0)
        self.gui_widget.add_button("btCapture", "Capture", self.handle_capture_button_click, bg="lime", fg="black", height=3, width=10, x=GUIConfig.WINDOW_WIDTH - 130, y=GUIConfig.WINDOW_HEIGHT - 65)
        self.gui_widget.add_button("btIdling", "Idling", self.handle_idling_button_click, bg="lime", fg="black", height=3, width=10, x=0, y=GUIConfig.WINDOW_HEIGHT - 65)
        # self.update_gui()

    def handle_bg_image_button_click(self):
        self.db.imgGUI.set_btn_GUI_capture_auto(True)
        logging.info("Background image button clicked, setting capture auto mode")

    def handle_capture_button_click(self):
        self.db.imgGUI.set_btn_GUI_capture_single(True)
        logging.info("Capture button clicked, setting capture single mode")

    def handle_idling_button_click(self):
        self.db.imgGUI.set_btn_GUI_Idling_cmd(not self.db.imgGUI.btn_GUI_Idling_cmd)
        logging.info(f"Idling button clicked, setting idling mode to: {self.db.imgGUI.btn_GUI_Idling_cmd}")

    def handle_exit_button_click(self):
        self.db.imgGUI.set_btn_GUI_exit(True)
        self.parent.quit()
        self.parent.destroy()
        logging.info("Exit button clicked, closing the application")

    def update_gui(self):
        system_state = self.db.sysState.get_state()
        system_state_str = str(system_state)

        self.db.fpUpdatePic.FP(self.db.p500.Output)

        # Update new image capture
        if self.db.imgGUI.newImg and self.db.fpUpdatePic.output:
            self.db.imgGUI.set_newImg(False)

            self.bg_img = Image.fromarray(self.db.imgGUI.lastImg)
            # Check if the image mode is RGBA and convert to RGB if necessary
            if self.bg_img.mode == 'RGBA':
                self.bg_img = self.bg_img.convert('RGB')
            self.bg_img = self.bg_img.resize((GUIConfig.WINDOW_WIDTH, GUIConfig.WINDOW_HEIGHT), Image.Resampling.LANCZOS)
            self.bg_img = ImageTk.PhotoImage(self.bg_img)
            self.bg_panel.config(image=self.bg_img)

        # Update status label
        if system_state == 4:
            pass
        elif system_state == 3:
            self.gui_widget.config("lbStatus", text=f"System status {system_state_str}: ERROR", bg="red")
        elif system_state == 7:
            self.gui_widget.config("lbStatus", text=f"System status {system_state_str}: IDLING, speed < 2", bg="gold")
        else:
            self.gui_widget.config("lbStatus", text=f"System status {system_state_str}: PAUSE, waiting for run command", bg="gold")

        # Update idling button text
        if self.db.imgGUI.btn_GUI_Idling_cmd:
            self.gui_widget.config("btIdling", text="Idling ON")
        else:
            self.gui_widget.config("btIdling", text="Idling OFF")

        # Update time, location, and satellite information
        time_str = f"{str(self.db.day_now).zfill(2)}-{str(self.db.month_now).zfill(2)}-{str(self.db.year_now).zfill(2)} {str(self.db.hour_now).zfill(2)}:{str(self.db.minute_now).zfill(2)}:{str(self.db.second_now).zfill(2)}"
        lat_str = str(round(self.db.lat_now, 6))
        lon_str = str(round(self.db.lon_now, 6))
        alt_str = str(self.db.alt_now)
        numsat_str = str(self.db.numsat_now)
        speed_str = str(round(self.db.speed_now, 2))
        info_text = f"Time: {time_str}\nLat: {lat_str}\nLon: {lon_str}\nAlt: {alt_str}\nSatellite: {numsat_str}\nSpeed: {speed_str} Km/h"
        self.gui_widget.config("lbInfo",text=info_text)

        if self.stop_event():
            self.parent.quit()
        else:
            # Schedule the next update
            self.parent.after(100, self.update_gui)

    def run(self, stop_event):
        """Runs the GUI event loop."""
        self.stop_event = stop_event
        self.parent = tk.Tk()
        self.init_gui()

        self.update_gui()
        self.parent.mainloop()

def start_gui(gui_service, stop_event):
    gui_service.run(stop_event)
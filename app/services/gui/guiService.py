import os
import tkinter as tk
import logging
from PIL import Image, ImageTk
from services.common.shared_keys import SharedKey
from services.common.system_store import SystemStore
from services.gui.guiPanel import GUIPanel
from services.gui.guiConfig import GUIConfig
from services.gui.guiWidget import GUIWidget

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f'{os.getcwd()}/archives/logs/gui.log'),
        logging.StreamHandler()
    ]
)

class GUI_Service:
    def __init__(self, system_store, stop_event):
        self.system_store:SystemStore = system_store
        self.stop_event = stop_event
        self.bg_img = None

    def init_gui(self):
        self.parent.title(GUIConfig.WINDOW_TITLE)
        self.parent.geometry(f"{GUIConfig.WINDOW_WIDTH}x{GUIConfig.WINDOW_HEIGHT}")
        logging.info(f"Window created with title: {GUIConfig.WINDOW_TITLE} and geometry: {GUIConfig.WINDOW_WIDTH}x{GUIConfig.WINDOW_HEIGHT}")

        # Create the background panel
        image_path = os.path.join(os.getcwd(), "Digime.jpeg")
        self.bg_panel = GUIPanel(self.parent, image_path, width=GUIConfig.WINDOW_WIDTH, height=GUIConfig.WINDOW_HEIGHT)
        self.bg_panel.place(x=0, y=0)

        # Create a GUIWidget instance to manage GUI components
        self.gui_widget = GUIWidget(self.parent)

        # Add labels
        self.gui_widget.add_label("lbStatus", "Initializing", width=500, bg="gold", fg="black", x=0, y=0)
        self.gui_widget.add_label("lbInfo", "Time: \nLat: \nLon: \nAlt: \nSatellite: \nSpeed: ", anchor="w", justify=tk.LEFT, bg="black", fg="lime", x=0, y=20)

        # Add buttons
        self.gui_widget.add_button(
            "btExit", "Exit", self.handle_exit_button_click, \
            bg="red", fg="white", height=1, width=3, \
            x=GUIConfig.WINDOW_WIDTH - 50, y=0
        )
        self.gui_widget.add_button(
            "btCapture", "Capture", self.handle_capture_button_click, \
            bg="lime", fg="black", height=3, width=10, \
            x=GUIConfig.WINDOW_WIDTH - 130, y=GUIConfig.WINDOW_HEIGHT - 65
        )
        self.gui_widget.add_button(
            "btIdling", "Idling", self.handle_idling_button_click, \
            bg="lime", fg="black", height=3, width=10, \
            x=0, y=GUIConfig.WINDOW_HEIGHT - 65
        )

    def handle_bg_image_button_click(self):
        self.system_store.imgGUI.set_btn_GUI_capture_auto(True)
        logging.info("Background image button clicked, setting capture auto mode")

    def handle_capture_button_click(self):
        self.system_store.imgGUI.set_btn_GUI_capture_single(True)
        logging.info("Capture button clicked, setting capture single mode")

    def handle_idling_button_click(self):
        self.system_store.imgGUI.set_btn_GUI_Idling_cmd(not self.system_store.imgGUI.btn_GUI_Idling_cmd)
        logging.info(f"Idling button clicked, setting idling mode to: ??")

    def handle_exit_button_click(self):
        self.system_store.imgGUI.set_btn_GUI_exit(True)
        self.parent.quit()
        self.parent.destroy()
        logging.info("Exit button clicked, closing the application")

    def update_gui(self):
        system_state = self.system_store.sysState.get_state()
        system_state_str = str(system_state)

        # Update new image capture
        if self.system_store.imgGUI.newImg:
            self.system_store.imgGUI.set_newImg(False)

            self.bg_img = Image.fromarray(self.system_store.imgGUI.lastImg)
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
        if self.system_store.imgGUI.btn_GUI_Idling_cmd:
            self.gui_widget.config("btIdling", text="Idling ON")
        else:
            self.gui_widget.config("btIdling", text="Idling OFF")

        # Update time, location, and satellite information
        captured_time = self.system_store.get_gps_captured_data()
        time_str = "{:02d}-{:02d}-{:04d} {:02d}:{:02d}:{:02d}".format(
            captured_time.day_now,
            captured_time.month_now,
            captured_time.year_now,
            captured_time.hour_now,
            captured_time.minute_now,
            captured_time.second_now
        )
        info_text = (
            f"Time: {time_str}\n"
            f"Lat: {captured_time.lat_now:.6f}\n"
            f"Lon: {captured_time.lon_now:.6f}\n"
            f"Alt: {captured_time.alt_now}\n"
            f"Satellite: {captured_time.numsat_now}\n"
            f"Speed: {captured_time.speed_now:.2f} Km/h"
        )
        self.gui_widget.config("lbInfo", text=info_text)

        if self.stop_event:
            self.parent.quit()
        else:
            # Schedule the next update
            self.parent.after(100, self.update_gui)

    def run(self):
        self.parent = tk.Tk()
        self.init_gui()
        self.update_gui()
        self.parent.mainloop()

def gui_service_worker(system_store, stop_event):
    try:
        gui_service = GUI_Service(system_store, stop_event)
        gui_service.run()
    except Exception as e:
        logging.error(f"Error in GUI service: {e}")
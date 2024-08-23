import os
import time
import tkinter as tk
from typing import List
from PIL import Image, ImageTk, ImageFile
from threading import Event, Thread
from services.image.img_filedata import FileImageData
from services.common.system_status import SystemState
from services.common.system_store import SystemStore
from services.gui.guiPanel import GUIPanel
from services.gui.guiConfig import GUIConfig
from services.gui.guiWidget import GUIWidget
from services.gui.guiNotification import GUINotification

class GUI_Service:
    INITIALIZE_TIME = 3 # seconds
    SCAN_UPDATE_GUI_INTERVAL = 10 # miliseconds
    NOTIFICATION_DURATION = 1000 # milliseconds

    def __init__(self, system_store: SystemStore, stop_event: Event):
        self.parent = tk.Tk()
        self.system_store = system_store
        self.stop_event = stop_event
        self.logger = system_store.logger

        # Gui elements
        self.default_bg_img_path = os.path.join(os.getcwd(), "Digime.jpeg")
        self.background_img = None
        self.bg_panel = None
        self.gui_widget = None
        self.notification = None

        self.preview_mode = False
        self.available_images: List[FileImageData] = None
        self.current_image_idx = 0

    def stop_service(self):
        self.parent.quit()
        self.parent.destroy()

    def init_gui(self):
        self.parent.title(GUIConfig.WINDOW_TITLE)
        self.parent.geometry(f"{GUIConfig.WINDOW_WIDTH}x{GUIConfig.WINDOW_HEIGHT}")
        self.logger.info(f"{__class__.__name__}: Window created with title: {GUIConfig.WINDOW_TITLE} and geometry: {GUIConfig.WINDOW_WIDTH}x{GUIConfig.WINDOW_HEIGHT}")

        # Create the background panel
        self.bg_panel = GUIPanel(self.parent, self.default_bg_img_path, width=GUIConfig.WINDOW_WIDTH, height=GUIConfig.WINDOW_HEIGHT)
        # self.bg_panel.place(x=0, y=0)

        # Create the main widget
        self.create_main_widget()

        # Create the notification channel
        self.notification = GUINotification(self.parent)

    def create_main_widget(self):
        # Create a GUIWidget instance to manage GUI components
        self.gui_widget = GUIWidget(self.parent)

        # Add labels
        self.gui_widget.add_label("lbStatus", "Initializing", width=500, bg="gold", fg="black", x=0, y=0)
        self.gui_widget.add_label("lbInfo", "Time: \nLat: \nLon: \nAlt: \nSatellite: \nSpeed: ", anchor="w", justify=tk.LEFT, bg="dim gray", fg="lime", x=0, y=25)

        # Add buttons
        self.gui_widget.add_button(
            "btExit", "Exit", self.handle_exit_button_click, \
            bg="red", fg="white", height=1, width=3, \
            x=GUIConfig.WINDOW_WIDTH - 60, y=25
        )
        self.gui_widget.add_button(
            "btAuto", "Clean", self.handle_clean_button_click, \
            bg="lime", fg="black", height=3, width=10, \
            x=GUIConfig.WINDOW_WIDTH - 650, y=GUIConfig.WINDOW_HEIGHT - 65
        )
        self.gui_widget.add_button(
            "btAuto", "Auto", self.handle_auto_button_click, \
            bg="lime", fg="black", height=3, width=10, \
            x=GUIConfig.WINDOW_WIDTH - 520, y=GUIConfig.WINDOW_HEIGHT - 65
        )
        self.gui_widget.add_button(
            "btCapture", "Capture", self.handle_capture_button_click, \
            bg="lime", fg="black", height=3, width=10, \
            x=GUIConfig.WINDOW_WIDTH - 390, y=GUIConfig.WINDOW_HEIGHT - 65
        )
        self.gui_widget.add_button(
            "btStream", "Stream", self.handle_stream_button_click, \
            bg="lime", fg="black", height=3, width=10, \
            x=GUIConfig.WINDOW_WIDTH - 260, y=GUIConfig.WINDOW_HEIGHT - 65
        )
        self.gui_widget.add_button(
            "btPreview", "Preview", self.handle_preview_button_click, \
            bg="lime", fg="black", height=3, width=10, \
            x=GUIConfig.WINDOW_WIDTH - 130, y=GUIConfig.WINDOW_HEIGHT - 65
        )
        self.gui_widget.add_button(
            "btPrevious", "◀", self.handle_previous_button_click, \
            fg="black", bg='gray25', height=1, width=3, relief=tk.FLAT, \
            x=GUIConfig.WINDOW_WIDTH - 130, y=GUIConfig.WINDOW_HEIGHT - 100
        )
        self.gui_widget.add_button(
            "btNext", "▶", self.handle_next_button_click, \
            fg="black", bg='gray25', height=1, width=3, relief=tk.FLAT, \
            x=GUIConfig.WINDOW_WIDTH - 60, y=GUIConfig.WINDOW_HEIGHT - 100
        )
        self.gui_widget.add_button(
            "btIdling", "Idling", self.handle_idling_button_click, \
            bg="lime", fg="black", height=3, width=10, \
            x=0, y=GUIConfig.WINDOW_HEIGHT - 65
        )

    def handle_bg_image_button_click(self):
        self.system_store.imgGUI.set_btn_GUI_capture_auto(True)
        self.logger.info(f"{__class__.__name__}: Background image button clicked, setting capture auto mode")

    def handle_clean_button_click(self):
        self.system_store.imgGUI.set_btn_GUI_clean(True)
        self.logger.info(f"{__class__.__name__}: Clean button clicked")
        self.notification.show("Start clean data table...")

    def handle_auto_button_click(self):
        self.system_store.imgGUI.set_btn_GUI_capture_auto(
            not self.system_store.imgGUI.btn_GUI_capture_auto #  toggle
        )
        self.logger.info(f"{__class__.__name__}: Auto button clicked, setting capture auto mode")
        self.notification.show("Start auto capturing...")

    def handle_capture_button_click(self):
        self.system_store.imgGUI.set_btn_GUI_capture_single(True)
        self.logger.info(f"{__class__.__name__}: Capture button clicked, setting capture single mode")
        self.notification.show("Start capturing...")

    def handle_stream_button_click(self):
        self.system_store.camera_store.request_streamer['run'] = not self.system_store.camera_store.request_streamer['run']
        if self.system_store.camera_store.request_streamer['run']:
            self.logger.info(f"{__class__.__name__}: Stream button clicked, start streaming ...")
            self.notification.show("Start streaming...")
        else:
            self.logger.info(f"{__class__.__name__}: Stream button clicked, stop streaming !")
            self.notification.show("Stop streaming...")
        
    def handle_preview_button_click(self):
        if self.preview_mode:       # Toggle off
            self.preview_mode = False
            self.bg_panel.reset_to_default()
        else:                       # Toggle on 
            self.preview_mode = True
            self.load_preview_mode()
        # load image
        
        self.logger.info(f"{__class__.__name__}: Preview button clicked")
        self.notification.show("Preview Images.")

    def handle_previous_button_click(self):
        if self.current_image_idx > 0:
            self.current_image_idx -= 1
            self.load_and_display_preview_image(self.available_images[self.current_image_idx].file_path)
            self.notification.show(f'Displaying image: {self.available_images[self.current_image_idx].imgID}')
        else:
            self.notification.show("No more images to display.")
        self.logger.info(f"{__class__.__name__}: Previous button clicked")

    def handle_next_button_click(self):
        if self.current_image_idx < len(self.available_images) - 1:
            self.current_image_idx += 1
            self.load_and_display_preview_image(self.available_images[self.current_image_idx].file_path)
            self.notification.show(f'Displaying image: {self.available_images[self.current_image_idx].imgID}')
        else:
            self.notification.show("No more images to display.")
        self.logger.info(f"{__class__.__name__}: Next button clicked")

    def handle_idling_button_click(self):
        self.system_store.imgGUI.set_btn_GUI_Idling_cmd(not self.system_store.imgGUI.btn_GUI_Idling_cmd)
        self.logger.info(f"{__class__.__name__}: Idling button clicked, setting idling mode to: {self.system_store.imgGUI.btn_GUI_Idling_cmd}")
        if self.system_store.imgGUI.btn_GUI_Idling_cmd:
            self.notification.show("Idling mode ON")
        else:
            self.notification.show("Idling mode OFF")

    def handle_exit_button_click(self):
        self.system_store.imgGUI.set_btn_GUI_exit(True)
        self.stop_service()
        self.logger.info(f"{__class__.__name__}: Exit button clicked, closing the application")

    def update_gui(self):
        system_state = self.system_store.sysState.get_state()

        # Update status label
        if system_state == SystemState.RUNNING:
            pass
        elif system_state == SystemState.ERROR:
            self.gui_widget.config("lbStatus", text=f"System status {system_state.name}: ERROR", bg="red")
        elif system_state == SystemState.IDLING_STOP:
            self.gui_widget.config("lbStatus", text=f"System status {system_state.name}: IDLING, speed < 2", bg="gold")
        else:
            self.gui_widget.config("lbStatus", text=f"System status {system_state.name}: PAUSE, waiting for run command", bg="gold")

        # Update idling button text
        if self.system_store.imgGUI.btn_GUI_Idling_cmd:
            self.gui_widget.config("btIdling", text="Idling ON")
        else:
            self.gui_widget.config("btIdling", text="Idling OFF")

        # Update time, location, and satellite information
        captured_time = self.system_store.get_gps_captured_data()
        number_of_captured_images = self.system_store.sli_database.get_number_of_items()
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
            f"Speed: {captured_time.speed_now:.2f} Km/h\n"
            f"Captured Images: {number_of_captured_images}"
        )
        self.gui_widget.config("lbInfo", text=info_text)

        if self.stop_event.is_set():
            self.parent.quit()
        
        self.parent.after(self.SCAN_UPDATE_GUI_INTERVAL, self.update_gui)

    def load_preview_mode(self):
        self.load_images_from_db()
        self.current_image_idx = 0 # reset index
        if not self.available_images:
            self.logger.info(f"{__class__.__name__}: Preview button clicked, but no available images")
            self.notification.show("No available images")
            return
        self.load_and_display_preview_image(self.available_images[self.current_image_idx].file_path)
        self.notification.show(f'Displaying image: {self.available_images[self.current_image_idx].imgID}')


    def load_images_from_db(self):
        self.available_images = self.system_store.sli_database.get_all_items_as_img_data()

    def load_and_display_preview_image(self, image_path, size=(500, 500)):
        def load_image(self, image_path, size):
            ImageFile.LOAD_TRUNCATED_IMAGES = True
            with Image.open(image_path) as img:
                size = size
                img.thumbnail(size, Image.Resampling.LANCZOS)
                self.background_img = ImageTk.PhotoImage(img)
                self.bg_panel.config(image=self.background_img)
        Thread(target=load_image, args=(self, image_path, size)).start()


    def run(self):
        self.init_gui()
        self.update_gui()
        self.parent.mainloop()

def gui_service_worker(system_store, stop_event):
    try:
        gui_service = GUI_Service(system_store, stop_event)
        time.sleep(GUI_Service.INITIALIZE_TIME)
        gui_service.run()
    except Exception as e:
        system_store.logger.error(f"Error in GUI service: {e}")

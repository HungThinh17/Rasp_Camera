import logging
import tkinter as tk
from PIL import Image, ImageTk
from services.gui.guiConfig import GUIConfig

class GUIPanel(tk.Frame):
    def __init__(self, parent, image_path, **kwargs):
        super().__init__(parent, **kwargs)
        self.original_image_path = image_path
        self.setup_panel(image_path)
        logging.info(f"GUIPanel created with image: {image_path}")

    def setup_panel(self, image_path):
        self.image = Image.open(image_path)
        self.photo = ImageTk.PhotoImage(self.image.resize((GUIConfig.WINDOW_WIDTH, GUIConfig.WINDOW_HEIGHT), Image.Resampling.LANCZOS))
        self.label = tk.Label(self, image=self.photo)
        self.label.pack(expand=True)
        self.pack(fill=tk.BOTH, expand=True)
        self.update_idletasks()
        self.center_image()

    def center_image(self):
        frame_width = self.winfo_width()
        frame_height = self.winfo_height()
        image_width = self.photo.width()
        image_height = self.photo.height()
        x = (frame_width - image_width) // 2
        y = (frame_height - image_height) // 2
        self.label.place(x=x, y=y)

    def config(self, **kwargs):
        self.label.config(**kwargs)
        if 'image' in kwargs:
            self.photo = kwargs.pop('image')
            self.center_image()

    def reset_to_default(self):
        self.setup_panel(self.original_image_path)

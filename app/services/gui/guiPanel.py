
import logging
import tkinter as tk
from PIL import Image, ImageTk
from services.gui.guiConfig import GUIConfig

class GUIPanel(tk.Frame):
    def __init__(self, parent, image_path, **kwargs):
        super().__init__(parent, **kwargs)
        self.image = ImageTk.PhotoImage(Image.open(image_path).resize((GUIConfig.WINDOW_WIDTH, GUIConfig.WINDOW_HEIGHT), Image.Resampling.LANCZOS))
        self.label = tk.Label(self, image=self.image)
        self.label.pack(fill=tk.BOTH, expand=True)
        logging.info(f"GUIPanel created with image: {image_path}")

    def config(self, **kwargs):
        self.label.config(**kwargs)


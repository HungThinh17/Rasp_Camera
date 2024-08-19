import logging
import tkinter as tk
from services.gui.guiConfig import GUIConfig


class GUIWidget:
    def __init__(self, parent):
        self.parent = parent
        self.widgets = {}

    def add_label(self, name, text, anchor="w", width=None, bg="#262626", fg=None, x=0, y=0, justify="left"):
        label = GUILabel(self.parent, text, anchor=anchor, width=width, bg=bg, fg=fg, justify=justify)
        label.place(x=x, y=y)
        self.widgets[name] = label

    def add_button(self, name, text, command, bg=None, fg=None, height=None, width=None, x=None, y=None,):
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

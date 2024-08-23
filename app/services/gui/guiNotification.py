import tkinter as tk

class GUINotification:
    def __init__(self, parent, duration=2000):
        self.parent = parent
        self.duration = duration

        self.notification_window = tk.Toplevel(self.parent)
        self.notification_window.title("Notification")
        self.notification_window.attributes("-topmost", True)
        self.notification_window.overrideredirect(True)

        self.notification_window.update_idletasks()
        x = self.parent.winfo_x()
        y = self.parent.winfo_y()
        self.notification_window.geometry(f"+{x}+{y}")
        
        self.notification_window.withdraw()  # Hide the window initially

    def show(self, message):
        for widget in self.notification_window.winfo_children():
            widget.destroy()

        # Update position before showing
        x = self.parent.winfo_x()
        y = self.parent.winfo_y()
        self.notification_window.geometry(f"+{x}+{y}")
        
        label = tk.Label(self.notification_window, text=message, bg="black", fg="white", padx=20, pady=10)
        label.pack()
        
        self.notification_window.deiconify()
        self.notification_window.after(self.duration, self.hide)

    def hide(self):
        self.notification_window.withdraw()

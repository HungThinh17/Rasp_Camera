import tkinter as tk

class GUINotification:
    def __init__(self, parent, duration=1000):
        self.parent = parent
        self.duration = duration

    def show(self, message):
        notification_window = tk.Toplevel(self.parent)
        notification_window.title("Notification")
        notification_window.attributes("-topmost", True)  # Make the window stay on top
        notification_window.overrideredirect(True)  # Remove the window border and title bar

        label = tk.Label(notification_window, text=message, bg="black", fg="white", padx=20, pady=10)
        label.pack()

        # Align the notification window with the main application window
        notification_window.update_idletasks()
        x = self.parent.winfo_x()
        y = self.parent.winfo_y()
        notification_window.geometry(f"+{x}+{y}")

        # Show the notification window for the specified duration
        notification_window.after(self.duration, notification_window.destroy)
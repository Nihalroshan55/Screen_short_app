import tkinter as tk
from tkinter import ttk, simpledialog, filedialog
import requests
from PIL import Image, ImageTk
import io
import os
import datetime
import pyautogui
from plyer import notification
import time
import shutil
from dotenv import load_dotenv
load_dotenv()

class ScreenshotUploaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Screenshot Uploader")
        self.root.geometry('400x500')  # Increased height to accommodate the footer and additional button

        self.create_widgets()

    def create_widgets(self):
        self.btn_capture = ttk.Button(self.root, text="Capture Screenshot", command=self.capture_screenshot)
        self.btn_capture.pack(pady=10)

        self.btn_upload = ttk.Button(self.root, text="Upload to API", command=self.upload_to_api, state=tk.DISABLED)
        self.btn_upload.pack(pady=10)

        self.btn_save = ttk.Button(self.root, text="Save Screenshot", command=self.save_screenshot, state=tk.DISABLED)
        self.btn_save.pack(pady=10)

        # Entry field for remarks with a placeholder
        self.remarks_entry = ttk.Entry(self.root, width=40)
        self.remarks_entry.pack(pady=5)
        self.set_placeholder(self.remarks_entry, "Enter remarks")
        self.remarks_entry.bind("<FocusIn>", lambda event: self.clear_placeholder(event, "Enter remarks"))
        self.remarks_entry.bind("<FocusOut>", lambda event: self.set_placeholder_on_empty(event, "Enter remarks"))

        # Entry field for phone with a placeholder
        self.phone_entry = ttk.Entry(self.root, width=20)
        self.phone_entry.pack(pady=5)
        self.set_placeholder(self.phone_entry, "Enter phone")
        self.phone_entry.bind("<FocusIn>", lambda event: self.clear_placeholder(event, "Enter phone"))
        self.phone_entry.bind("<FocusOut>", lambda event: self.set_placeholder_on_empty(event, "Enter phone"))

        self.status_label = ttk.Label(self.root, text="")
        self.status_label.pack(pady=10)

        # Placeholder for the screenshot image
        self.screenshot_image = None
        self.screenshot_panel = ttk.Label(self.root)
        self.screenshot_panel.pack()

        # Footer
        footer_text = "Nihal Roshan App"
        self.footer_label = ttk.Label(self.root, text=footer_text, font=("Arial", 10, "italic"))
        self.footer_label.pack(side=tk.BOTTOM, pady=10)

    def set_placeholder(self, entry, placeholder):
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(foreground='grey')

    def clear_placeholder(self, event, placeholder):
        # Clear the placeholder when the entry field is clicked
        widget = event.widget
        if widget.get() == placeholder:
            widget.delete(0, tk.END)
            widget.config(foreground='black')

    def set_placeholder_on_empty(self, event, placeholder):
        # Set the placeholder if the entry field is empty
        widget = event.widget
        if not widget.get():
            widget.insert(0, placeholder)
            widget.config(foreground='grey')

    def capture_screenshot(self):
        # Hide the application window before taking the screenshot
        self.root.iconify()
        
        
        time.sleep(0.6)

        # Capture the screenshot excluding the UI of the application
        screenshot = pyautogui.screenshot()
        screenshot.save("screenshot.png")

        # Restore the application window after taking the screenshot
        self.root.deiconify()

        # Update the displayed screenshot in the UI
        self.update_screenshot("screenshot.png")
        self.btn_upload.config(state=tk.NORMAL)
        self.btn_save.config(state=tk.NORMAL)

    def update_screenshot(self, image_path):
        img = Image.open(image_path)
        img.thumbnail((300, 300))
        img = ImageTk.PhotoImage(img)

        # Update the displayed image
        self.screenshot_panel.configure(image=img)
        self.screenshot_panel.image = img

    def upload_to_api(self):
        api_url = os.getenv("API_URL")
        image_path = "screenshot.png"

        if not os.path.exists(image_path):
            self.status_label.config(text="Error: Screenshot not found")
            return

        remarks = self.remarks_entry.get()
        phone = self.phone_entry.get()

        if remarks == "Enter remarks" or phone == "Enter phone":
            self.status_label.config(text="Error: Remarks and phone are required")
            return

        files = {'image': open(image_path, 'rb')}
        data = {'remarks': remarks, 'phone': phone}
        
        try:
            response = requests.post(api_url, data=data, files=files)
            response_data = response.json()

            if response_data['status'] == 'success':
                file_path = response_data['data']['file_path']
                self.status_label.config(text=f"Upload successful!\nFile Path: {file_path}")
                self.show_notification("Upload successful", f"File uploaded successfully. File Path: {file_path}")
            else:
                self.status_label.config(text=f"Upload failed. Error: {response_data['message']}")

        except requests.RequestException as e:
            self.status_label.config(text=f"Error: {e}")

    def save_screenshot(self):
        initial_dir = os.path.expanduser('~')
        file_path = filedialog.asksaveasfilename(initialdir=initial_dir, defaultextension=".png", filetypes=[("PNG files", "*.png")])

        if file_path:
            screenshot_path = "screenshot.png"
            try:
                # Copy the captured screenshot to the chosen file path
                shutil.copy(screenshot_path, file_path)
                self.status_label.config(text=f"Screenshot saved to: {file_path}")
                self.show_notification("Screenshot Saved", f"Screenshot saved successfully to: {file_path}")
            except Exception as e:
                self.status_label.config(text=f"Error saving screenshot: {e}")

    def show_notification(self, title, message):
        notification.notify(
            title=title,
            message=message,
            app_name="Screenshot Uploader"
        )

if __name__ == "__main__":
    root = tk.Tk()

    app = ScreenshotUploaderApp(root)

    root.mainloop()
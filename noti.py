import os
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageGrab
from plyer import notification

BASE_DIR = os.path.join(os.getcwd(), "Screenshots")
os.makedirs(BASE_DIR, exist_ok=True)

def create_tray_icon():
    menu = Menu(
        MenuItem('Last Capture', show_last_capture),
        MenuItem('Open Folder', open_folder),
        Menu.SEPARATOR,
        MenuItem('Exit', exit_app)
    )
    image = Image.new('RGB', (64, 64), 'white')  # Tray icon
    icon = Icon("ss_manager", image, "Smart Screenshot Manager", menu)
    icon.run_detached()

def show_last_capture(icon, item):
    print("Show last capture - implement me!")

def open_folder(icon, item):
    os.startfile(BASE_DIR)

def exit_app(icon, item):
    icon.stop()
    os._exit(0)

def show_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        app_name="Smart Screenshot Manager",
        timeout=5
    )

def take_ss_and_save():
    screenshot = ImageGrab.grab()
    screenshot_path = os.path.join(BASE_DIR, "screenshot.png")
    screenshot.save(screenshot_path)
    show_notification("Screenshot Saved", 
    f"📂 Folder: Screenshots\n📍 {screenshot_path}")

if __name__ == "__main__":
    take_ss_and_save()  # Optional: capture once
    create_tray_icon()
    



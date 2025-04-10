import os, threading, keyboard, time
from pystray import Icon, Menu, MenuItem
from PIL import Image
from plyer import notification

from backend import take_ss_and_save

BASE_DIR = os.path.join(os.getcwd(), "Categorized_Screenshots")  # Match backend
os.makedirs(BASE_DIR, exist_ok=True)

def create_tray_icon():
    menu = Menu(
        MenuItem('Last Capture', show_last_capture),
        MenuItem('Open Folder', lambda: os.startfile(BASE_DIR)),
        Menu.SEPARATOR,
        MenuItem('Exit', exit_app)
    )
    image = Image.new('RGB', (64, 64), 'white')  # Tray icon
    icon = Icon("ss_manager", image, "Smart Screenshot Manager", menu)
    icon.run()
    
def show_last_capture(icon, item):
    try:
        all_files = []
        for root, _, files in os.walk(BASE_DIR):
            for file in files:
                if file.endswith(".png"):
                    all_files.append(os.path.join(root, file))

        if all_files:
            latest = max(all_files, key=os.path.getmtime)
            os.startfile(latest)
        else:
            show_notification("No Screenshots", "No screenshots have been captured yet.")
    except Exception as e:
        show_notification("Error", str(e))

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

def listen_hotkey():
    keyboard.add_hotkey("ctrl+shift+i", lambda: threading.Thread(target=take_ss_and_save).start())
    while True: 
        time.sleep(1)

def start_app():
    threading.Thread(target=listen_hotkey, daemon=True).start()
    create_tray_icon()

if __name__ == "__main__":
    start_app()

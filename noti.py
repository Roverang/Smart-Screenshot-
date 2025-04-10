import os,threading,keyboard,time
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
    icon.run()
    
def show_last_capture(icon, item):
    try:
        files = sorted(
            [f for f in os.listdir(BASE_DIR) if f.endswith(".png")],
            key=lambda x: os.path.getmtime(os.path.join(BASE_DIR, x)),
            reverse=True
        )
        if files:
            latest = os.path.join(BASE_DIR, files[0])
            os.startfile(latest)
        else:
            show_notification("No Screenshots", "No screenshots have been captured yet.")
    except Exception as e:
        show_notification("Error", str(e))


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
    try:
        screenshot = ImageGrab.grab()
        timestamp = time.strftime("%Y%m%d_%H%M%S_%f")[:-3]
        screenshot_path = os.path.join(BASE_DIR, f"screenshot_{timestamp}.png")
        screenshot.save(screenshot_path)
        show_notification("Screenshot Saved", 
        f"📂 Folder: Screenshots\n📍 {screenshot_path}")
    except Exception as e:
        show_notification("Capture Failed", str(e))

def listen_hotkey():
    keyboard.add_hotkey("ctrl+shift+i", take_ss_and_save)
    while True: 
        time.sleep(1)

def start_app():
    threading.Thread(target=listen_hotkey, daemon=True).start()

    create_tray_icon()

if __name__ == "__main__":
    start_app()



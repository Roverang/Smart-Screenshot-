import pytesseract
from PIL import ImageGrab
import keyboard
import threading
import os
import time
import win32gui
import win32process
import psutil

# Set your Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

BASE_DIR = os.path.join(os.getcwd(), "Categorized_Screenshots")
os.makedirs(BASE_DIR, exist_ok=True)

# -------- Get Active Window App Name --------
def get_foreground_app_name():
    try:
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        proc = psutil.Process(pid)
        return proc.name().lower()
    except Exception:
        return "unknown"

# -------- Improved Categorization --------
def categorize(text, app_name):
    text = text.lower()
    full_context = f"{text} {app_name}"

    tags = []

    if "whatsapp" in full_context or "telegram" in full_context:
        tags.append("Messaging/Chats_Stickers")
    elif "vscode" in full_context or "python" in full_context or "codeblocks" in full_context:
        tags.append("Programming/IDE_Language")
    elif "youtube" in full_context:
        tags.append("Media/YouTube_Shorts_Channels")
    elif "spotify" in full_context:
        tags.append("Media/Spotify_Playlist_Album")
    elif "chrome" in full_context or "edge" in full_context or "firefox" in full_context:
        if "drive" in full_context or "docs" in full_context:
            tags.append("Browser/Docs_Drive")
        elif "twitter" in full_context or "reddit" in full_context:
            tags.append("Browser/Social")
        elif "amazon" in full_context or "flipkart" in full_context:
            tags.append("Browser/Ecom")
        else:
            tags.append("Browser/Search_General")
    elif "explorer.exe" in app_name or "this pc" in full_context:
        tags.append("System/Folders_Disk_Explorer")
    elif "masterclass" in full_context or "study" in full_context:
        tags.append("Education/Lectures_Notes")
    else:
        tags.append("Uncategorized")

    return tags[0]  # Only use primary categorization

# -------- Screenshot + Categorize + Save --------
def take_ss_and_save():
    screenshot = ImageGrab.grab()
    app_name = get_foreground_app_name()

    config = r'--oem 3 --psm 6'
    extracted_text = pytesseract.image_to_string(screenshot, config=config)

    category_path = categorize(extracted_text, app_name)
    full_save_path = os.path.join(BASE_DIR, category_path)
    os.makedirs(full_save_path, exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    screenshot_filename = f"{timestamp}.png"
    screenshot_path = os.path.join(full_save_path, screenshot_filename)
    screenshot.save(screenshot_path)

    print(f"✅ Saved to: {screenshot_path}")

# -------- Hotkey Trigger --------
keyboard.add_hotkey('ctrl+shift+i', lambda: threading.Thread(target=take_ss_and_save).start())
print("🟢 Smart Screenshot Categorizer is running... Press Ctrl+Shift+I to capture and auto-organize.")
keyboard.wait()

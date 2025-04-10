import pytesseract
from PIL import ImageGrab
import os, time
import win32gui

# Path to your installed Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

BASE_DIR = os.path.join(os.getcwd(), "Categorized_Screenshots")
os.makedirs(BASE_DIR, exist_ok=True)

CATEGORY_RULES = {
    "whatsapp": ["Messaging", "WhatsApp"],
    "telegram": ["Messaging", "Telegram"],
    "vscode": ["Programming", "IDE"],
    "codeblocks": ["Programming", "IDE"],
    "python": ["Programming", "Language"],
    "arduino": ["Programming", "Language"],
    "git": ["Programming", "Tool"],
    "youtube": ["Media", "YouTube"],
    "anime": ["Media", "Anime"],
    "video": ["Media", "Video"],
    "shorts": ["Media", "YouTube"],
    "masterclass": ["Education", "Courses"],
    "learning": ["Education", "Courses"],
    "jee": ["Education", "ExamPrep"],
    "resources": ["Education", "Material"],
    ".zip": ["Downloads", "Archives"],
    "stickers": ["Downloads", "Stickers"],
    "downloads": ["Downloads", "General"],
    "emoji": ["Downloads", "Stickers"],
    "this pc": ["System", "Explorer"],
    "volume (c:)": ["System", "Disk"],
    "recycle bin": ["System", "Trash"],
    "spotify": ["Media", "Spotify"],
    "chrome": ["Browser", "Chrome"],
    "edge": ["Browser", "Edge"],
    "docs": ["Browser", "Docs"],
    "search": ["Browser", "Search"]
}

def get_active_window_title():
    return win32gui.GetWindowText(win32gui.GetForegroundWindow()).lower()

def categorize_window_title(title):
    for keyword, category in CATEGORY_RULES.items():
        if keyword in title:
            return os.path.join(*category)
    return os.path.join("Uncategorized")

def take_ss_and_save():
    screenshot = ImageGrab.grab()
    window_title = get_active_window_title()

    category_path = os.path.join(BASE_DIR, categorize_window_title(window_title))
    os.makedirs(category_path, exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    screenshot_filename = f"{timestamp}.png"
    screenshot_path = os.path.join(category_path, screenshot_filename)
    screenshot.save(screenshot_path)

    with open("ss_log.txt", "a", encoding="utf-8") as log:
        log.write(f"{timestamp} | {window_title} | {category_path}\n")

    print(f"✅ Saved to: {screenshot_path}")

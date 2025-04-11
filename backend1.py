import pytesseract
from PIL import ImageGrab, Image
import keyboard
import threading
import os
import time
import json
import tkinter as tk
import win32gui
import io
from cryptography.fernet import Fernet
from frontend import ask_user_to_save  # Link frontend popup

# --- Config Paths ---
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
BASE_DIR = os.path.join(os.getcwd(), "Categorized_Screenshots")
ENCRYPTED_DIR = os.path.join(BASE_DIR, "Encrypted")
SENSITIVE_KEYWORDS_FILE = "sensitive_keywords.json"
BLOCKED_LOG_FILE = "blocked_log.txt"
SS_LOG_FILE = "ss_log.txt"
KEY_FILE = "key.key"
SETTINGS_FILE = "settings.json"

# Create necessary dirs
os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(ENCRYPTED_DIR, exist_ok=True)

# --- Load settings ---
DEFAULT_SETTINGS = {"compression": True, "compression_quality": 85}
if not os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(DEFAULT_SETTINGS, f, indent=4)
with open(SETTINGS_FILE, "r") as f:
    SETTINGS = json.load(f)

# --- Load sensitive keywords ---
DEFAULT_SENSITIVE_KEYWORDS = ["password", "otp", "account number", "upi", "pin", "cvv", "pan"]
if not os.path.exists(SENSITIVE_KEYWORDS_FILE):
    with open(SENSITIVE_KEYWORDS_FILE, "w") as f:
        json.dump(DEFAULT_SENSITIVE_KEYWORDS, f, indent=4)
with open(SENSITIVE_KEYWORDS_FILE, "r") as f:
    SENSITIVE_KEYWORDS = json.load(f)

# --- Encryption key ---
def load_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
    return key
fernet = Fernet(load_key())

# --- Helpers ---
def get_active_window_title():
    return win32gui.GetWindowText(win32gui.GetForegroundWindow()).lower()

CATEGORY_RULES = {
    "whatsapp": ["Messaging", "WhatsApp"],
    "telegram": ["Messaging", "Telegram"],
    "vscode": ["Programming", "IDE"],
    "youtube": ["Media", "YouTube"],
    "shorts": ["Media", "YouTube"],
    "docs": ["Browser", "Docs"],
    "chrome": ["Browser", "Chrome"],
    "learning": ["Education", "Courses"],
    "downloads": ["Downloads", "General"]
}

def categorize_window_title(title):
    for keyword, category in CATEGORY_RULES.items():
        if keyword in title:
            return os.path.join(*category)
    return os.path.join("Uncategorized")

def contains_sensitive_keywords(text):
    return any(keyword.lower() in text.lower() for keyword in SENSITIVE_KEYWORDS)

def log_action(log_path, content):
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(content + "\n")

def save_encrypted(image, filename, text):
    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=True, quality=SETTINGS.get("compression_quality", 85))
    encrypted_data = fernet.encrypt(buffer.getvalue())
    image_path = os.path.join(ENCRYPTED_DIR, filename + ".enc")
    with open(image_path, "wb") as f:
        f.write(encrypted_data)
    with open(image_path + ".txt", "w", encoding="utf-8") as f:
        f.write(text)

# --- Screenshot capture ---
def take_ss_and_save():
    screenshot = ImageGrab.grab()
    window_title = get_active_window_title()
    text = pytesseract.image_to_string(screenshot)
    timestamp = time.strftime("%Y%m%d_%H%M%S")

    if contains_sensitive_keywords(text):
        user_choice = ask_user_to_save()
        if user_choice:
            save_encrypted(screenshot, timestamp, text)
            log_action(SS_LOG_FILE, f"{timestamp} | ENCRYPTED | {window_title} | Contains sensitive info")
            print(f"🔒 Encrypted and saved: {timestamp}.enc")
        else:
            log_action(BLOCKED_LOG_FILE, f"{timestamp} | BLOCKED | {window_title}")
            print("🚫 Screenshot blocked by user.")
        return

    category_path = os.path.join(BASE_DIR, categorize_window_title(window_title))
    os.makedirs(category_path, exist_ok=True)
    screenshot_path = os.path.join(category_path, f"{timestamp}.png")

    if SETTINGS.get("compression", True):
        screenshot.save(screenshot_path, optimize=True, quality=SETTINGS.get("compression_quality", 85))
    else:
        screenshot.save(screenshot_path)

    size_kb = os.path.getsize(screenshot_path) // 1024
    log_action(SS_LOG_FILE, f"{timestamp} | {window_title} | {screenshot_path} | Size: {size_kb} KB")
    print(f"✅ Saved: {screenshot_path} ({size_kb} KB)")

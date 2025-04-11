import os, time, io, json
from PIL import ImageGrab, Image
import pytesseract
import win32gui
from cryptography.fernet import Fernet

# --- Config ---
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
BASE_DIR = os.path.join(os.getcwd(), "Categorized_Screenshots")
ENCRYPTED_DIR = os.path.join(BASE_DIR, "Encrypted")
KEY_FILE = "key.key"
SENSITIVE_KEYWORDS_FILE = "sensitive_keywords.json"
SS_LOG_FILE = "ss_log.txt"
BLOCKED_LOG_FILE = "blocked_log.txt"
os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(ENCRYPTED_DIR, exist_ok=True)

# --- Load Key ---
def load_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
    return key

fernet = Fernet(load_key())

# --- Load Sensitive Keywords ---
DEFAULT_SENSITIVE_KEYWORDS = ["password", "otp", "account number", "upi", "pin", "cvv", "pan"]
if not os.path.exists(SENSITIVE_KEYWORDS_FILE):
    with open(SENSITIVE_KEYWORDS_FILE, "w") as f:
        json.dump(DEFAULT_SENSITIVE_KEYWORDS, f, indent=4)
with open(SENSITIVE_KEYWORDS_FILE, "r") as f:
    SENSITIVE_KEYWORDS = json.load(f)

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

def get_active_window_title():
    return win32gui.GetWindowText(win32gui.GetForegroundWindow()).lower()

def categorize_window_title(title):
    for keyword, category in CATEGORY_RULES.items():
        if keyword in title:
            return os.path.join(*category)
    return os.path.join("Uncategorized")

def contains_sensitive_keywords(text):
    return any(k.lower() in text.lower() for k in SENSITIVE_KEYWORDS)

def log_action(log_path, content):
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(content + "\n")

def compress_image(image, quality=75):
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=quality)
    buffer.seek(0)
    return Image.open(buffer)

def save_encrypted(image, filename, text):
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    encrypted_data = fernet.encrypt(buffer.getvalue())
    path = os.path.join(ENCRYPTED_DIR, filename + ".enc")
    with open(path, "wb") as f:
        f.write(encrypted_data)
    with open(path + ".txt", "w", encoding="utf-8") as f:
        f.write(text)

def take_ss_and_save(show_popup_fn=None, notify_fn=None):
    screenshot = ImageGrab.grab()
    window_title = get_active_window_title()
    text = pytesseract.image_to_string(screenshot)
    timestamp = time.strftime("%Y%m%d_%H%M%S")

    if contains_sensitive_keywords(text) and show_popup_fn:
        user_choice = show_popup_fn()
        if user_choice:
            save_encrypted(screenshot, timestamp, text)
            log_action(SS_LOG_FILE, f"{timestamp} | ENCRYPTED | {window_title}")
            if notify_fn:
                notify_fn("Screenshot Encrypted", f"Saved to Encrypted folder")
        else:
            log_action(BLOCKED_LOG_FILE, f"{timestamp} | BLOCKED | {window_title}")
        return

    category_path = os.path.join(BASE_DIR, categorize_window_title(window_title))
    os.makedirs(category_path, exist_ok=True)
    screenshot_path = os.path.join(category_path, f"{timestamp}.jpg")
    compressed = compress_image(screenshot)
    compressed.save(screenshot_path)
    log_action(SS_LOG_FILE, f"{timestamp} | {window_title} | {screenshot_path}")
    if notify_fn:
        notify_fn("Screenshot Saved", screenshot_path)

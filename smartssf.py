# --- REQUIRED INSTALLATION ---
# pip install pywin32 keyboard Pillow plyer pyyaml
# -----------------------------
import os
import time
import threading
import win32gui 
import keyboard 
from PIL import ImageGrab 
import tkinter as tk 
from tkinter import filedialog
import subprocess 
from plyer import notification 
import yaml 
import sys 

class Config:
    DEFAULT_BASE_DIR = os.path.join(os.path.expanduser('~'), 'Desktop', 'Categorized_Screenshots')
    HOTKEY = 'ctrl+shift+i'
    LOG_FILE = "ss_log.csv" 
    APP_NAME = "Smart Screenshot Categorizer"
    CONFIG_FILE = "ss_config.yaml" 

    DEFAULT_RULES = {
        "whatsapp": ["Messaging", "WhatsApp"],
        "telegram": ["Messaging", "Telegram"],
        "vscode": ["Programming", "IDE"],
        "python": ["Programming", "Language"],
        "youtube": ["Media", "YouTube"],
        "spotify": ["Media", "Spotify"],
        "chrome": ["Browser", "Chrome"],
        "edge": ["Browser", "Edge"],
    }
    
    @staticmethod
    def load_rules():
        if os.path.exists(Config.CONFIG_FILE):
            try:
                with open(Config.CONFIG_FILE, 'r') as f:
                    rules = yaml.safe_load(f)
                    if rules is None:
                        print(f"Warning: Config file '{Config.CONFIG_FILE}' is empty. Using default rules.")
                        return Config.DEFAULT_RULES
                    print(f"Configuration loaded from {Config.CONFIG_FILE}.")
                    return rules
            except Exception as e:
                print(f"Error loading config file: {e}. Using default rules.")
                return Config.DEFAULT_RULES
        else:
            try:
                with open(Config.CONFIG_FILE, 'w') as f:
                    yaml.dump(Config.DEFAULT_RULES, f, default_flow_style=False)
                print(f"Created default config file: {Config.CONFIG_FILE}. Please edit it to customize rules.")
            except Exception as e:
                print(f"Warning: Could not create config file: {e}")
            return Config.DEFAULT_RULES

Config.CATEGORY_RULES = Config.load_rules()


class ScreenshotTaker:

    def __init__(self):
        self.base_dir = self._select_base_directory()
        os.makedirs(self.base_dir, exist_ok=True)
        self._ensure_log_header() 
        print(f"Base directory set to: {self.base_dir}")

    def _select_base_directory(self) -> str:
        root = tk.Tk()
        root.withdraw()
        
        selected_dir = filedialog.askdirectory(
            initialdir=os.path.dirname(Config.DEFAULT_BASE_DIR),
            title="Select the Base Folder for Categorized Screenshots"
        )

        root.destroy()

        if selected_dir:
            final_dir = os.path.join(selected_dir, os.path.basename(Config.DEFAULT_BASE_DIR))
        else:
            final_dir = Config.DEFAULT_BASE_DIR
            print(f"Warning: Directory selection canceled. Using default location: {final_dir}")
            
        return final_dir

    def get_active_window_title(self) -> str:
        try:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                return win32gui.GetWindowText(hwnd) 
            return "unknown_window"
        except Exception as e:
            print(f"Error retrieving window title: {e}")
            return "error_retrieving_title"

    def categorize_window_title(self, title: str) -> str:
        lower_title = title.lower()
        for keyword, category in Config.CATEGORY_RULES.items():
            if keyword.lower() in lower_title:
                return os.path.join(*category)
        return "Uncategorized"

    def open_folder(self, folder_path: str):
        try:
            subprocess.Popen(f'explorer "{folder_path}"')
        except Exception as e:
            print(f"Error opening folder: {e}")
            
    def _ensure_log_header(self):
        if not os.path.exists(Config.LOG_FILE) or os.stat(Config.LOG_FILE).st_size == 0:
            with open(Config.LOG_FILE, "w", encoding="utf-8") as log:
                log.write("Timestamp,CategoryPath,ActiveWindowTitle,RelativeFilePath\n")

    def _log_action(self, timestamp, title, category_path, relative_file_path):
        try:
            safe_title = title.replace(',', ' ')
            log_entry = f"{timestamp},{category_path},{safe_title},{relative_file_path}\n"
            with open(Config.LOG_FILE, "a", encoding="utf-8") as log:
                log.write(log_entry)
        except Exception as e:
            print(f"Warning: Could not write to log file: {e}")

    def take_ss_and_save(self):
        try:
            screenshot = ImageGrab.grab()

            window_title = self.get_active_window_title()
            category_relative_path = self.categorize_window_title(window_title)
            
            category_path = os.path.join(self.base_dir, category_relative_path)
            os.makedirs(category_path, exist_ok=True)

            category_for_filename = category_relative_path.replace(os.sep, '_')
            
            title_snippet = window_title[:20].strip()
            illegal_chars = '<>:"/\\|?*\n'
            for char in illegal_chars:
                title_snippet = title_snippet.replace(char, '_')
            
            if not title_snippet:
                title_snippet = "No_Title"

            timestamp = time.strftime("%Y%m%d_%H%M%S")
            screenshot_filename = f"{timestamp}_{category_for_filename}_{title_snippet}.png"
            screenshot_path = os.path.join(category_path, screenshot_filename)
            
            screenshot.save(screenshot_path)

            relative_file_path = os.path.relpath(screenshot_path, self.base_dir)
            self._log_action(timestamp, window_title, category_relative_path, relative_file_path)

            print(f"\n\n✅ Saved to: {screenshot_path}")

            self._show_notification_and_prompt(category_relative_path, category_path)

        except Exception as e:
            print(f"❌ An error occurred during capture or saving: {e}")
            
    def _show_notification_and_prompt(self, category_name, folder_path):
        notification.notify(
            title=f"{Config.APP_NAME}: Screenshot Saved!",
            message=f"Category: {category_name}\nClick 'Open' in console to view.",
            app_name=Config.APP_NAME,
            timeout=5
        )
        
        print(f"\n\n📂 Screenshot saved to: {folder_path}")
        try:
            user_input = input("❓ Open folder now? (y/N): ").strip().lower()
            if user_input == 'y':
                self.open_folder(folder_path)
                print("Opening folder...")
            else:
                print("Folder not opened.")
        except EOFError:
            pass
        except Exception as e:
            print(f"Error handling prompt: {e}")

    def run(self):
        print("-" * 50)
        print(f"🟢 {Config.APP_NAME} running...")
        print(f"   Hotkey: {Config.HOTKEY.upper()}")
        print(f"   Base Dir: {self.base_dir}")
        print("-" * 50)
        print("Press 'ESC' key to stop the script.")
        
        keyboard.add_hotkey(Config.HOTKEY, lambda: threading.Thread(target=self.take_ss_and_save).start())
        
        keyboard.wait('esc')
        print("🛑 Script stopped.")

if __name__ == "__main__":
    try:
        app = ScreenshotTaker()
        app.run()
    except Exception as e:
        print(f"A fatal error occurred: {e}")
        sys.exit(1)
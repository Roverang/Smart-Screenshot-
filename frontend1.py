# frontend.py

import os, threading, keyboard, tkinter as tk
from tkinter import messagebox
from pystray import Icon, Menu, MenuItem
from PIL import Image
from plyer import notification
import pyperclip

from backend import BASE_DIR, take_ss_and_save, ENCRYPTED_DIR
import pytesseract
from PIL import Image as PILImage

# --- Notification ---
def show_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        app_name="Smart Screenshot Manager",
        timeout=5
    )

# --- Ask User to Save (Sensitive) ---
def ask_user_to_save():
    result = {"choice": None}
    def on_save(): result.update(choice=True); popup.destroy()
    def on_cancel(): result.update(choice=False); popup.destroy()
    popup = tk.Tk()
    popup.withdraw()
    popup.deiconify()
    popup.title("Sensitive Screenshot")
    tk.Label(popup, text="Sensitive content detected. Save this screenshot securely?").pack(padx=20, pady=10)
    tk.Button(popup, text="Yes (Encrypt & Save)", command=on_save).pack(pady=(0,5))
    tk.Button(popup, text="No (Discard)", command=on_cancel).pack()
    popup.mainloop()
    return result["choice"]

# --- GUI Search Window ---
def search_gui():
    def search():
        query = entry.get().lower()
        results.delete(0, tk.END)
        for root, dirs, files in os.walk(BASE_DIR):
            for file in files:
                if file.endswith(".png"):
                    path = os.path.join(root, file)
                    try:
                        text = pytesseract.image_to_string(PILImage.open(path)).lower()
                        if query in text:
                            results.insert(tk.END, path)
                    except:
                        pass
        for file in os.listdir(ENCRYPTED_DIR):
            if file.endswith(".txt"):
                path = os.path.join(ENCRYPTED_DIR, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        text = f.read().lower()
                        if query in text:
                            results.insert(tk.END, path.replace(".txt", ".enc"))
                except:
                    pass

    def show_image(event):
        selected = results.get(results.curselection())
        pyperclip.copy(selected)
        os.startfile(selected)

    window = tk.Tk()
    window.title("Search Screenshots")
    tk.Label(window, text="Search by Text:").pack()
    entry = tk.Entry(window, width=50)
    entry.pack()
    tk.Button(window, text="Search", command=search).pack()
    results = tk.Listbox(window, width=100, height=20)
    results.pack(pady=10)
    results.bind("<Double-Button-1>", show_image)
    window.mainloop()

# --- Tray Icon ---
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
            show_notification("No Screenshots", "No screenshots captured yet.")
    except Exception as e:
        show_notification("Error", str(e))

def exit_app(icon, item):
    icon.stop()
    os._exit(0)

def create_tray_icon():
    menu = Menu(
        MenuItem('Last Capture', show_last_capture),
        MenuItem('Open Folder', lambda: os.startfile(BASE_DIR)),
        MenuItem('Exit', exit_app)
    )
    image = Image.new('RGB', (64, 64), 'white')
    icon = Icon("ss_manager", image, "Smart Screenshot Manager", menu)
    icon.run()

# --- Hotkey Listeners ---
def listen_hotkey():
    keyboard.add_hotkey("ctrl+shift+i", lambda: threading.Thread(target=lambda: take_ss_and_save(ask_user_to_save, show_notification)).start())
    keyboard.add_hotkey("ctrl+shift+s", lambda: threading.Thread(target=search_gui).start())
    while True: 
        pass

# --- Launch App ---
def start_app():
    threading.Thread(target=listen_hotkey, daemon=True).start()
    create_tray_icon()

if __name__ == "__main__":
    start_app()

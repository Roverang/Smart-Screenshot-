import os, threading, time, keyboard
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from plyer import notification
from pystray import Icon, Menu, MenuItem
from backend import take_ss_and_save, BASE_DIR, ENCRYPTED_DIR
import pytesseract
import pyperclip

def show_notification(title, message):
    notification.notify(title=title, message=message, app_name="Smart Screenshot Manager", timeout=5)

def ask_user_to_save():
    result = {"choice": None}
    def on_save(): result.update(choice=True); popup.destroy()
    def on_cancel(): result.update(choice=False); popup.destroy()
    popup = tk.Tk()
    popup.title("Sensitive Screenshot")
    popup.geometry("300x120")
    tk.Label(popup, text="Sensitive content detected. Save securely?").pack(pady=10)
    tk.Button(popup, text="Yes (Encrypt)", command=on_save).pack(pady=2)
    tk.Button(popup, text="No (Discard)", command=on_cancel).pack(pady=2)
    popup.mainloop()
    return result["choice"]

def search_gui():
    def search():
        query = entry.get().lower()
        results.delete(0, tk.END)
        for root, _, files in os.walk(BASE_DIR):
            for file in files:
                if file.endswith(".jpg"):
                    path = os.path.join(root, file)
                    try:
                        text = pytesseract.image_to_string(Image.open(path)).lower()
                        if query in text:
                            results.insert(tk.END, path)
                    except:
                        pass
        for file in os.listdir(ENCRYPTED_DIR):
            if file.endswith(".txt"):
                path = os.path.join(ENCRYPTED_DIR, file)
                with open(path, "r", encoding="utf-8") as f:
                    if query in f.read().lower():
                        results.insert(tk.END, path.replace(".txt", ".enc"))

    def show_image(event):
        path = results.get(results.curselection())
        pyperclip.copy(path)
        os.startfile(path)

    window = tk.Tk()
    window.title("Search Screenshots")
    tk.Label(window, text="Search Text:").pack()
    entry = tk.Entry(window, width=50)
    entry.pack(pady=5)
    tk.Button(window, text="Search", command=search).pack()
    results = tk.Listbox(window, width=90, height=20)
    results.pack(pady=10)
    results.bind("<Double-1>", show_image)
    tk.Button(window, text="Exit", command=window.destroy).pack(pady=5)
    window.mainloop()

def listen_hotkeys():
    keyboard.add_hotkey("ctrl+shift+i", lambda: threading.Thread(target=take_ss_and_save, kwargs={
        "show_popup_fn": ask_user_to_save,
        "notify_fn": show_notification
    }).start())
    keyboard.add_hotkey("ctrl+shift+s", lambda: threading.Thread(target=search_gui).start())
    while True:
        time.sleep(1)

def create_tray_icon():
    def show_last(icon, item):
        all_files = [os.path.join(r, f) for r, _, fs in os.walk(BASE_DIR) for f in fs if f.endswith(".jpg")]
        if all_files:
            os.startfile(max(all_files, key=os.path.getmtime))
        else:
            show_notification("No Screenshots", "You haven't taken any screenshots yet.")

    def exit_app(icon, item):
        icon.stop()
        os._exit(0)

    menu = Menu(
        MenuItem("Last Capture", show_last),
        MenuItem("Open Folder", lambda: os.startfile(BASE_DIR)),
        Menu.SEPARATOR,
        MenuItem("Exit", exit_app)
    )
    icon = Icon("ss_manager", Image.new('RGB', (64, 64), 'white'), "Smart Screenshot Manager", menu)
    icon.run()

def start_app():
    threading.Thread(target=listen_hotkeys, daemon=True).start()
    create_tray_icon()

if __name__ == "__main__":
    start_app()

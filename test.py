import tkinter as tk
from tkinter import filedialog, messagebox,ttk

def upload_screenshot():
    # Open file dialog to select image
    file_path = filedialog.askopenfilename(
        title="Select Screenshot",
        filetypes=[("Image files", "*.png *.jpg *.jpeg")]
    )
    
    if file_path:
        messagebox.showinfo("Success", f"Selected: {file_path}")
        # later add code to process the screenshot
    else:
        messagebox.showwarning("Cancelled", "No file selected")

window = tk.Tk()
window.title("Smart Screenshot Manager")
window.geometry("600x400")

#tk.Button(window, text="Upload Screenshot", command=upload_screenshot).pack(pady=20)

window.mainloop()
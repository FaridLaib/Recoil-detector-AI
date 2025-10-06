# record/help_texts.py
import tkinter as tk
from tkinter import messagebox

def show_help(field):
    try:
        help_texts = {
            "text": "Select an image file (JPEG, JPG) showing a pattern to automatically detect impacts.",
            "image": "Select an image file (JPEG/PNG) showing a recoil pattern to automatically detect bullet impacts.",
            "weapon_name": "Enter the name of the weapon for saving the detected pattern. Required. Any non-empty string is valid.",
            "fire_rate": "Enter the weapon's fire rate in rounds per minute. Required. Must be a number between 0 and 2000. Click 'Show Fire Rates' for a list of Apex Legends weapons.",
            "import_recoil": "Select a JSON file containing a recoil pattern to test with anti-recoil.",
            "pattern_save_name": "Enter a name for saving an imported recoil pattern. Required. Any non-empty string is valid.",
            "vertical_recoil": "Set the vertical recoil adjustment for anti-recoil. Range: -5.0 to 5.0, default 1.0, increments of 0.05.",
            "horizontal_recoil": "Set the horizontal recoil adjustment for anti-recoil. Range: -5.0 to 5.0, default 1.0, increments of 0.05.",
            "zoom_factor": "Set the zoom correction factor for anti-recoil. Range: 0.0 to 5.0, default 1.0, increments of 0.05. If a screenshot was taken with a large scope (e.g., 4x-8x), adjust this value. If recoil pulls down too much, reduce zoom factor; if too little, increase it."
        }
        popup = tk.Toplevel()
        popup.title("Help")
        popup.geometry("300x150")
        popup.transient()
        popup.grab_set()
        frame = tk.Frame(popup)
        frame.pack(padx=10, pady=10, fill="both", expand=True)
        tk.Label(frame, text=help_texts.get(field, "No help available"), wraplength=280, justify="left").pack(padx=10, pady=10)
        tk.Button(frame, text="OK", command=popup.destroy).pack(pady=5)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to show help: {str(e)}")
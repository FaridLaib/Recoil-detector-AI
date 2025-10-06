import logging
import os
import json
import tkinter as tk
from datetime import datetime
import sys

# Use executable's directory if running as a PyInstaller bundle
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Points to project_root/

MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB in bytes
ERROR_LOG_FILE = os.path.join(BASE_DIR, "logs", "errors.log")

def setup_logging(enabled):
    os.makedirs(os.path.join(BASE_DIR, "logs"), exist_ok=True)
    
    error_handler = logging.FileHandler(ERROR_LOG_FILE, mode='a')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    
    if os.path.exists(ERROR_LOG_FILE) and os.path.getsize(ERROR_LOG_FILE) >= MAX_LOG_SIZE:
        with open(ERROR_LOG_FILE, 'w'):
            pass
    
    logging.getLogger('').addHandler(error_handler)
    
    if enabled:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = os.path.join(BASE_DIR, "logs", f"anti_recoil_{timestamp}.log")
        handler = logging.FileHandler(log_file)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter('%(asctime)s,%(msecs)d - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
        logging.getLogger('').addHandler(handler)
        logging.getLogger('').addHandler(logging.StreamHandler())
    else:
        for handler in logging.getLogger('').handlers[:]:
            if not isinstance(handler, logging.FileHandler) or handler.baseFilename != ERROR_LOG_FILE:
                logging.getLogger('').removeHandler(handler)

def save_to_json(points, filename, weapon_name, fire_rate, adjusted=False, **kwargs):
    try:
        if not points:
            print("No points to save.")
            return
        origin_x, origin_y = points[0]
        normalized = [(x - origin_x, y - origin_y) for x, y in points]
        data = {
            "weapon_name": weapon_name,
            "fire_rate": fire_rate,
            "x": [pt[0] for pt in normalized],
            "y": [pt[1] for pt in normalized]
        }
        if adjusted:
            data["vertical_recoil"] = round(kwargs.get("vertical_recoil", 1.0), 2)
            data["horizontal_recoil"] = round(kwargs.get("horizontal_recoil", 1.0), 2)
            data["zoom_correction_factor"] = round(kwargs.get("zoom_correction_factor", 1.0), 2)
        patterns_dir = os.path.join(BASE_DIR, "common", "patterns")  # Updated path
        os.makedirs(patterns_dir, exist_ok=True)
        filepath = os.path.join(patterns_dir, f"{filename}.json")
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Saved {len(points)} points to {filepath}")
    except Exception as e:
        logging.error(f"Failed to save JSON {filename}: {str(e)}")
        raise

def create_popup(root, title, size):
    # (Unchanged)
    try:
        popup = tk.Toplevel(root)
        popup.title(title)
        popup.geometry(size)
        popup.transient(root)
        popup.grab_set()
        frame = tk.Frame(popup)
        frame.pack(padx=10, pady=10, fill="both", expand=True)
        return popup, frame
    except Exception as e:
        logging.error(f"Failed to create popup {title}: {str(e)}")
        raise
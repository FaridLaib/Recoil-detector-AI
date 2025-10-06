# C:\REKOILX\launcher.py
import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import logging

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(os.path.join(os.path.dirname(__file__), 'logs', 'launcher_log.txt')), logging.StreamHandler()]
)

class REKOILXLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("REKOILX Launcher")
        self.root.geometry("400x300")  # Increased size
        self.root.resizable(False, False)

        # Main frame for grid layout
        main_frame = tk.Frame(root)
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # App name label
        tk.Label(
            main_frame,
            text="REKOILX",
            font=("Arial", 24, "bold")
        ).grid(row=0, column=0, pady=30, sticky="n")

        # Record/Adjust Patterns button
        tk.Button(
            main_frame,
            text="Record/Adjust Patterns",
            command=self.launch_record,
            width=25,
            font=("Arial", 10)
        ).grid(row=1, column=0, pady=15, sticky="n")

        # Detect Weapon and Apply Recoil button
        tk.Button(
            main_frame,
            text="Detect Weapon and Apply Recoil",
            command=self.launch_detection,
            width=25,
            font=("Arial", 10)
        ).grid(row=2, column=0, pady=15, sticky="n")

        # Exit button
        tk.Button(
            main_frame,
            text="Exit",
            command=self.exit_app,
            width=10,
            font=("Arial", 8)
        ).grid(row=3, column=0, pady=15, sticky="n")

    def launch_record(self):
        try:
            record_script = os.path.join(os.path.dirname(__file__), 'record', 'main.py')
            if not os.path.exists(record_script):
                raise FileNotFoundError(f"Record script not found: {record_script}")
            subprocess.run(['python', record_script], check=True)
            logging.info("Launched record/main.py")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Record/Adjust Patterns: {str(e)}")
            logging.error(f"Record launch failed: {e}")

    def launch_detection(self):
        try:
            detection_script = os.path.join(os.path.dirname(__file__), 'Detection', 'gui.py')
            if not os.path.exists(detection_script):
                raise FileNotFoundError(f"Detection script not found: {detection_script}")
            subprocess.run(['python', detection_script], check=True)
            logging.info("Launched Detection/gui.py")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Detect Weapon and Apply Recoil: {str(e)}")
            logging.error(f"Detection launch failed: {e}")

    def exit_app(self):
        logging.info("Exiting REKOILX Launcher")
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = REKOILXLauncher(root)
    root.mainloop()
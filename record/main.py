# record/main.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Adds C:\REKOILX to sys.path
import tkinter as tk
from main_gui import AutoRecoilPatternGUI
from record.utils import setup_logging

def main():
    root = tk.Tk()
    def toggle_logging(enabled):
        setup_logging(enabled)
    app = AutoRecoilPatternGUI(root, toggle_logging)
    root.mainloop()

if __name__ == "__main__":
    main()
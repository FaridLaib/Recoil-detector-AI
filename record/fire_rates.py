# record/fire_rates.py
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

def show_fire_rates():
    try:
        weapons = [
            {"name": "R-301 Carbine", "rpm": 810, "category": "Assault Rifle", "firing_type": "Full-Auto / Semi-Auto"},
            {"name": "VK-47 Flatline", "rpm": 600, "category": "Assault Rifle", "firing_type": "Full-Auto / Semi-Auto"},
            {"name": "Hemlok Burst AR", "rpm": 490, "category": "Assault Rifle", "firing_type": "3-Round Burst / Semi-Auto"},
            {"name": "HAVOC Rifle", "rpm": 672, "category": "Assault Rifle", "firing_type": "Full-Auto"},
            {"name": "R-99", "rpm": 1080, "category": "SMG", "firing_type": "Full-Auto"},
            {"name": "Alternator SMG", "rpm": 640, "category": "SMG", "firing_type": "Full-Auto"},
            {"name": "Prowler Burst PDW", "rpm": 800, "category": "SMG", "firing_type": "5-Round Burst / Full-Auto (with Hop-Up)"},
            {"name": "M600 Spitfire", "rpm": 512, "category": "LMG", "firing_type": "Full-Auto"},
            {"name": "Devotion LMG", "rpm": 900, "category": "LMG", "firing_type": "Full-Auto"},
            {"name": "Peacekeeper", "rpm": 58, "category": "Shotgun", "firing_type": "Lever-Action (Single Shot)"},
            {"name": "EVA-8 Auto", "rpm": 128, "category": "Shotgun", "firing_type": "Full-Auto"},
            {"name": "Mozambique", "rpm": 180, "category": "Shotgun", "firing_type": "Triple-Barrel (Single Shot)"},
            {"name": "Mastiff Shotgun", "rpm": 96, "category": "Shotgun", "firing_type": "Semi-Auto"},
            {"name": "Kraber .50-Cal", "rpm": 36, "category": "Sniper Rifle", "firing_type": "Bolt-Action"},
            {"name": "Longbow DMR", "rpm": 78, "category": "Sniper Rifle", "firing_type": "Semi-Auto"},
            {"name": "Triple Take", "rpm": 88, "category": "Sniper Rifle", "firing_type": "Semi-Auto"},
            {"name": "Sentinel", "rpm": 57, "category": "Sniper Rifle", "firing_type": "Bolt-Action"},
            {"name": "Wingman", "rpm": 205, "category": "Pistol", "firing_type": "Semi-Auto"},
            {"name": "RE-45 Auto", "rpm": 750, "category": "Pistol", "firing_type": "Full-Auto"},
            {"name": "P2020", "rpm": 430, "category": "Pistol", "firing_type": "Semi-Auto"}
        ]
        popup = tk.Toplevel()
        popup.title("Apex Legends Fire Rates")
        popup.geometry("600x400")
        popup.transient()
        popup.grab_set()
        tree = ttk.Treeview(popup, columns=("Name", "RPM", "Category", "Firing Type"), show="headings")
        tree.heading("Name", text="Weapon Name")
        tree.heading("RPM", text="Fire Rate (RPM)")
        tree.heading("Category", text="Category")
        tree.heading("Firing Type", text="Firing Type")
        tree.column("Name", width=150)
        tree.column("RPM", width=100)
        tree.column("Category", width=100)
        tree.column("Firing Type", width=200)
        for weapon in weapons:
            tree.insert("", "end", values=(weapon["name"], weapon["rpm"], weapon["category"], weapon["firing_type"]))
        tree.pack(padx=10, pady=10, fill="both", expand=True)
        tk.Button(popup, text="OK", command=popup.destroy).pack(pady=5)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to show fire rates: {str(e)}")
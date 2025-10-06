# record/gui_components.py
import tkinter as tk
from tkinter import ttk
import webbrowser
from record.fire_rates import show_fire_rates
from record.gui_utils import browse_image, browse_json, match_background_color, paint, pick_color, toggle_select_region_mode, save_image, toggle_adjust_mode, show_save_warning  # Add browse_json
from record.help_texts import show_help

class MainFrame:
    def __init__(self, app):
        self.app = app
        self.frame = tk.LabelFrame(self.app.root, text="Recoil Pattern Detector and Anti-Recoil")
        self.frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.setup_menu()

    def setup_menu(self):
        options_mb = tk.Menubutton(self.frame, text="Options", relief="raised")
        options_mb.grid(row=0, column=0, padx=2, pady=2, sticky="nw")
        options_menu = tk.Menu(options_mb, tearoff=0)
        options_mb.config(menu=options_menu)
        options_menu.add_command(label="Instructions", command=lambda: self.app.show_instructions())
        options_menu.add_command(label="Discord", command=lambda: webbrowser.open("https://discord.gg/A2EUcH7Q"))
        options_menu.add_command(label="Enable/Disable Logs", command=lambda: self.app.toggle_logging())
        options_menu.add_command(label="Exit", command=lambda: self.app.exit_app())

class DetectionControls:
    def __init__(self, parent, app):
        self.app = app
        self.frame = tk.LabelFrame(parent, text="Recoil Pattern Detection")
        self.frame.grid(row=1, column=0, padx=5, pady=5, sticky="nw")
        self.min_thresh_var = tk.IntVar(value=1)
        self.max_thresh_var = tk.IntVar(value=65)
        self.min_area_var = tk.DoubleVar(value=1.0)
        self.max_area_var = tk.DoubleVar(value=300.0)
        self.kernel_size_var = tk.IntVar(value=1)
        self.brush_size_var = tk.IntVar(value=5)
        self.overwrite_var = tk.BooleanVar(value=False)
        self.setup_controls()

    def setup_controls(self):
        controls = tk.Frame(self.frame)
        controls.grid(row=0, column=0, padx=2, pady=2, sticky="nw")

        tk.Label(controls, text="Image:").grid(row=0, column=0, padx=2, pady=2, sticky="w")
        tk.Label(controls, text="?", fg="blue", cursor="hand2").grid(row=0, column=1, padx=2, pady=2, sticky="w")
        controls.children['!label2'].bind("<Button-1>", lambda e: show_help("image"))
        self.image_entry = tk.Entry(controls, width=30)
        self.image_entry.grid(row=0, column=2, padx=2, pady=2, sticky="w")
        tk.Button(controls, text="Browse", command=lambda: browse_image(self.app)).grid(row=0, column=3, padx=2, pady=2, sticky="w")

        tk.Label(controls, text="Weapon Name:*").grid(row=1, column=0, padx=2, pady=2, sticky="w")
        tk.Label(controls, text="?", fg="blue", cursor="hand2").grid(row=1, column=1, padx=2, pady=2, sticky="w")
        controls.children['!label4'].bind("<Button-1>", lambda e: show_help("weapon_name"))
        self.weapon_entry = tk.Entry(controls, width=20)
        self.weapon_entry.grid(row=1, column=2, padx=2, pady=2, sticky="w")

        tk.Label(controls, text="Fire Rate (0-2000):*").grid(row=2, column=0, padx=2, pady=2, sticky="w")
        tk.Label(controls, text="?", fg="blue", cursor="hand2").grid(row=2, column=1, padx=2, pady=2, sticky="w")
        controls.children['!label6'].bind("<Button-1>", lambda e: show_help("fire_rate"))
        self.fire_rate_entry = tk.Entry(controls, width=10)
        self.fire_rate_entry.grid(row=2, column=2, padx=2, pady=2, sticky="w")
        tk.Button(controls, text="Show Fire Rates", command=show_fire_rates).grid(row=2, column=3, padx=2, pady=2, sticky="w")

        tk.Label(controls, text="Min Threshold:").grid(row=3, column=0, padx=2, pady=2, sticky="w")
        tk.Scale(controls, from_=0, to=100, orient="horizontal", variable=self.min_thresh_var).grid(row=3, column=2, padx=2, pady=2, sticky="w")

        tk.Label(controls, text="Max Threshold:").grid(row=4, column=0, padx=2, pady=2, sticky="w")
        tk.Scale(controls, from_=0, to=100, orient="horizontal", variable=self.max_thresh_var).grid(row=4, column=2, padx=2, pady=2, sticky="w")

        tk.Label(controls, text="Min Area:").grid(row=5, column=0, padx=2, pady=2, sticky="w")
        tk.Scale(controls, from_=0.0, to=10.0, resolution=0.5, orient="horizontal", variable=self.min_area_var).grid(row=5, column=2, padx=2, pady=2, sticky="w")

        tk.Label(controls, text="Max Area:").grid(row=6, column=0, padx=2, pady=2, sticky="w")
        tk.Scale(controls, from_=50.0, to=500.0, resolution=10.0, orient="horizontal", variable=self.max_area_var).grid(row=6, column=2, padx=2, pady=2, sticky="w")

        tk.Label(controls, text="Kernel Size:").grid(row=7, column=0, padx=2, pady=2, sticky="w")
        tk.Scale(controls, from_=1, to=7, resolution=1, orient="horizontal", variable=self.kernel_size_var).grid(row=7, column=2, padx=2, pady=2, sticky="w")

        tk.Label(controls, text="Brush Size:").grid(row=8, column=0, padx=2, pady=2, sticky="w")
        tk.Scale(controls, from_=1, to=20, orient="horizontal", variable=self.brush_size_var).grid(row=8, column=2, padx=2, pady=2, sticky="w")
        tk.Button(controls, text="Pick Color", command=lambda: pick_color(self.app)).grid(row=8, column=3, padx=2, pady=2, sticky="w")
        tk.Button(controls, text="Match Background", command=lambda: match_background_color(self.app)).grid(row=9, column=3, padx=2, pady=2, sticky="w")
        tk.Button(controls, text="Select Region to Match", command=lambda: toggle_select_region_mode(self.app)).grid(row=10, column=3, padx=2, pady=2, sticky="w")
        tk.Button(controls, text="Paint", command=lambda: paint(self.app)).grid(row=10, column=2, padx=2, pady=2, sticky="w")

        self.save_image_button = tk.Button(controls, text="Save Image", command=lambda: save_image(self.app))
        self.save_image_button.grid(row=11, column=3, padx=2, pady=2, sticky="w")
        self.save_image_button.grid_remove()
        self.overwrite_check = tk.Checkbutton(controls, text="Overwrite Original", variable=self.overwrite_var)
        self.overwrite_check.grid(row=11, column=2, padx=2, pady=2, sticky="w")
        self.overwrite_check.grid_remove()

        tk.Button(controls, text="Analyze Impacts", command=self.app.analyze_impacts).grid(row=10, column=0, padx=2, pady=2, sticky="w")
        tk.Button(controls, text="Adjust", command=lambda: toggle_adjust_mode(self.app, True)).grid(row=10, column=1, padx=2, pady=2, sticky="w")
        self.done_button = tk.Button(controls, text="Done", command=lambda: toggle_adjust_mode(self.app, False))
        self.done_button.grid(row=12, column=1, padx=2, pady=2, sticky="w")
        self.done_button.grid_remove()
        self.save_button = tk.Button(controls, text="Save", command=self.app.save_pattern)
        self.save_button.grid(row=12, column=0, padx=2, pady=2, sticky="w")
        save_warning_label = tk.Label(controls, text="!", fg="red", cursor="hand2")
        save_warning_label.grid(row=12, column=2, padx=0, pady=2, sticky="w")
        save_warning_label.bind("<Button-1>", lambda e: show_save_warning(self.app))
        tk.Button(controls, text="Reset", command=self.app.reset).grid(row=12, column=3, padx=2, pady=2, sticky="w")

class AntiRecoilControls:
    def __init__(self, parent, app):
        self.app = app
        self.frame = tk.LabelFrame(parent, text="Anti-Recoil Control")
        self.frame.grid(row=2, column=0, padx=5, pady=5, sticky="nw")
        self.vertical_recoil_var = tk.DoubleVar(value=1.0)
        self.horizontal_recoil_var = tk.DoubleVar(value=1.0)
        self.zoom_correction_var = tk.DoubleVar(value=1.0)
        self.json_path_var = tk.StringVar()
        self.pattern_save_name_var = tk.StringVar()
        self.setup_controls()

    def setup_controls(self):
        tk.Button(self.frame, text="Anti-Recoil", command=self.app.toggle_anti_recoil).grid(row=0, column=0, padx=2, pady=2, sticky="w")
        tk.Button(self.frame, text="Remap Trigger", command=self.app.remap_trigger).grid(row=0, column=1, padx=2, pady=2, sticky="w")

        tk.Label(self.frame, text="Import Recoil:").grid(row=1, column=0, padx=2, pady=2, sticky="w")
        tk.Label(self.frame, text="?", fg="blue", cursor="hand2").grid(row=1, column=1, padx=2, pady=2, sticky="w")
        self.frame.children['!label2'].bind("<Button-1>", lambda e: show_help("import_recoil"))
        self.json_path_entry = tk.Entry(self.frame, textvariable=self.json_path_var, width=20)
        self.json_path_entry.grid(row=1, column=2, padx=2, pady=2, sticky="w")
        tk.Button(self.frame, text="Browse", command=lambda: browse_json(self.app)).grid(row=2, column=0, padx=2, pady=2, sticky="w")
        tk.Button(self.frame, text="Import Recoil", command=self.app.import_recoil).grid(row=2, column=1, padx=2, pady=2, sticky="w")

        tk.Label(self.frame, text="Pattern Save Name:*").grid(row=3, column=0, padx=2, pady=2, sticky="w")
        tk.Label(self.frame, text="?", fg="blue", cursor="hand2").grid(row=3, column=1, padx=2, pady=2, sticky="w")
        self.frame.children['!label4'].bind("<Button-1>", lambda e: show_help("pattern_save_name"))
        self.pattern_save_name_entry = tk.Entry(self.frame, textvariable=self.pattern_save_name_var, width=20)
        self.pattern_save_name_entry.grid(row=3, column=2, padx=2, pady=2, sticky="w")
        tk.Button(self.frame, text="Save Imported", command=self.app.save_imported_pattern).grid(row=4, column=0, columnspan=2, padx=2, pady=2, sticky="w")

        tk.Label(self.frame, text="Vertical Recoil:").grid(row=5, column=0, padx=2, pady=2, sticky="w")
        tk.Label(self.frame, text="?", fg="blue", cursor="hand2").grid(row=5, column=1, padx=2, pady=2, sticky="w")
        self.frame.children['!label6'].bind("<Button-1>", lambda e: show_help("vertical_recoil"))
        vertical_frame = tk.Frame(self.frame)
        vertical_frame.grid(row=5, column=2, padx=2, pady=2, sticky="w")
        tk.Button(vertical_frame, text="−", command=lambda: self.app.increment_scale('vertical_recoil', -0.05)).grid(row=0, column=0, padx=2)
        tk.Button(vertical_frame, text="+", command=lambda: self.app.increment_scale('vertical_recoil', 0.05)).grid(row=0, column=1, padx=2)
        tk.Scale(vertical_frame, from_=-5.0, to=5.0, resolution=0.05, orient="horizontal", variable=self.vertical_recoil_var, length=150, command=lambda _: self.app.update_scales()).grid(row=1, column=0, columnspan=2)

        tk.Label(self.frame, text="Horizontal Recoil:").grid(row=6, column=0, padx=2, pady=2, sticky="w")
        tk.Label(self.frame, text="?", fg="blue", cursor="hand2").grid(row=6, column=1, padx=2, pady=2, sticky="w")
        self.frame.children['!label8'].bind("<Button-1>", lambda e: show_help("horizontal_recoil"))
        horizontal_frame = tk.Frame(self.frame)
        horizontal_frame.grid(row=6, column=2, padx=2, pady=2, sticky="w")
        tk.Button(horizontal_frame, text="−", command=lambda: self.app.increment_scale('horizontal_recoil', -0.05)).grid(row=0, column=0, padx=2)
        tk.Button(horizontal_frame, text="+", command=lambda: self.app.increment_scale('horizontal_recoil', 0.05)).grid(row=0, column=1, padx=2)
        tk.Scale(horizontal_frame, from_=-5.0, to=5.0, resolution=0.05, orient="horizontal", variable=self.horizontal_recoil_var, length=150, command=lambda _: self.app.update_scales()).grid(row=1, column=0, columnspan=2)

        tk.Label(self.frame, text="Zoom Factor:").grid(row=7, column=0, padx=2, pady=2, sticky="w")
        tk.Label(self.frame, text="?", fg="blue", cursor="hand2").grid(row=7, column=1, padx=2, pady=2, sticky="w")
        self.frame.children['!label10'].bind("<Button-1>", lambda e: show_help("zoom_factor"))
        zoom_frame = tk.Frame(self.frame)
        zoom_frame.grid(row=7, column=2, padx=2, pady=2, sticky="w")
        tk.Button(zoom_frame, text="−", command=lambda: self.app.increment_scale('zoom', -0.05)).grid(row=0, column=0, padx=2)
        tk.Button(zoom_frame, text="+", command=lambda: self.app.increment_scale('zoom', 0.05)).grid(row=0, column=1, padx=2)
        tk.Scale(zoom_frame, from_=0.0, to=5.0, resolution=0.05, orient="horizontal", variable=self.zoom_correction_var, length=150, command=lambda _: self.app.update_scales()).grid(row=1, column=0, columnspan=2)

        tk.Button(self.frame, text="Save Modified Recoil", command=self.app.save_modified_recoil).grid(row=8, column=0, columnspan=2, padx=2, pady=2, sticky="w")
        tk.Button(self.frame, text="Merge All Patterns", command=self.app.merge_patterns).grid(row=9, column=0, columnspan=2, padx=2, pady=2, sticky="w")

class PatternCanvas:
    def __init__(self, parent, app):
        self.app = app
        self.canvas = tk.Canvas(parent, width=400, height=800, bg="gray")
        self.canvas.grid(row=1, column=1, rowspan=2, padx=5, pady=5, sticky="ne")
        tk.Label(parent, text="Recoil Pattern Visualization").grid(row=3, column=1, padx=5, pady=2, sticky="n")
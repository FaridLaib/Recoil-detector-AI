# detection/gui.py
import tkinter as tk
from tkinter import messagebox
import yaml
import os
import logging
from weapon_detection import detect_weapons  # Fix: Correct import
#from common.anti_recoil import AntiRecoil  # Fix: Correct import
from common.absolute import AntiRecoil  # New
import json
import vgamepad as vg
import threading
import time

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(os.path.join(os.path.dirname(__file__), '..', 'logs', 'gui_log.txt')), logging.StreamHandler()]
)

class DetectionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Weapon Detection & Anti-Recoil")
        self.root.geometry("400x450")
        self.running = False
        self.anti_recoil = None
        self.gamepad = vg.VX360Gamepad()
        logging.info("Virtual controller initialized")
        self.patterns_path = os.path.join(os.path.dirname(__file__), '..', 'common', 'patterns')  # Fix: Correct path
        self.config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')  # Fix: Correct path
        self.current_weapon = "None"
        self.current_slot = "Unknown"
        self.current_magazine_type = None
        self.current_pattern = None
        self.current_recoil_params = None
        self.rt_thread_running = False
        self.rt_thread = None
        self.zoom_correction_factor = 1.0

        self.magazine_mapping = {
            "R-99": {
                "Base": "R99diagn.json",
                "Purple/Gold": "R99diagn.json"
            }
        }
        logging.info("Magazine mappings initialized")

        # GUI elements
        self.label_status = tk.Label(root, text="Status: Stopped", font=("Arial", 12))
        self.label_status.pack(pady=10)

        self.label_weapon = tk.Label(root, text="Weapon: None", font=("Arial", 12))
        self.label_weapon.pack(pady=5)

        self.label_slot = tk.Label(root, text="Slot: Unknown", font=("Arial", 12))
        self.label_slot.pack(pady=5)

        self.label_magazine = tk.Label(root, text="Magazine: Unknown", font=("Arial", 12))
        self.label_magazine.pack(pady=5)

        self.label_zoom = tk.Label(root, text="Zoom Correction Factor: 1.0", font=("Arial", 12))
        self.label_zoom.pack(pady=5)
        self.zoom_slider = tk.Scale(
            root,
            from_=0.0,
            to=4.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            length=200,
            command=self.update_zoom_factor
        )
        self.zoom_slider.set(1.0)
        self.zoom_slider.pack(pady=10)

        self.btn_start = tk.Button(root, text="Start Detection", command=self.start_detection)
        self.btn_start.pack(pady=5)

        self.btn_stop = tk.Button(root, text="Stop Detection", command=self.stop_detection, state="disabled")
        self.btn_stop.pack(pady=5)

        self.btn_config = tk.Button(root, text="Configure", command=self.open_config)
        self.btn_config.pack(pady=5)

        try:
            with open(self.config_path, "r") as f:
                self.config = yaml.safe_load(f)
            logging.info("Configuration loaded from config.yaml")
        except FileNotFoundError:
            self.config = {}
            self.save_config()
            logging.warning("No config.yaml found, created new config")

    def update_zoom_factor(self, value):
        self.zoom_correction_factor = float(value)
        self.label_zoom.config(text=f"Zoom Correction Factor: {self.zoom_correction_factor:.1f}")
        logging.debug(f"Zoom correction factor updated to {self.zoom_correction_factor}")

    def save_config(self):
        try:
            with open(self.config_path, "w") as f:
                yaml.dump(self.config, f, default_flow_style=False)
            logging.info("Configuration saved to config.yaml")
        except Exception as e:
            logging.error(f"Failed to save config: {e}")

    def open_config(self):
        config_window = tk.Toplevel(self.root)
        config_window.title("Configuration")
        config_window.geometry("300x500")

        tk.Label(config_window, text="Weapon 1 Scan (left,top,width,height):").pack()
        entry_w1 = tk.Entry(config_window)
        entry_w1.pack()
        entry_w1.insert(0, str(self.config.get("scan_coord_one", {})))

        tk.Label(config_window, text="Weapon 2 Scan (left,top,width,height):").pack()
        entry_w2 = tk.Entry(config_window)
        entry_w2.pack()
        entry_w2.insert(0, str(self.config.get("scan_coord_two", {})))

        tk.Label(config_window, text="Attachment Scan (left,top,width,height):").pack()
        entry_att = tk.Entry(config_window)
        entry_att.pack()
        entry_att.insert(0, str(self.config.get("scan_coord_attachment", {})))

        tk.Label(config_window, text="Ammo Scan (left,top,width,height):").pack()
        entry_ammo = tk.Entry(config_window)
        entry_ammo.pack()
        entry_ammo.insert(0, str(self.config.get("scan_coord_ammo", {})))

        tk.Label(config_window, text="Magazine Icon Scan (left,top,width,height):").pack()
        entry_mag_icon = tk.Entry(config_window)
        entry_mag_icon.pack()
        entry_mag_icon.insert(0, str(self.config.get("scan_coord_mag_icon", {})))

        tk.Label(config_window, text="Modifier Value:").pack()
        entry_mod = tk.Entry(config_window)
        entry_mod.pack()
        entry_mod.insert(0, str(self.config.get("modifier_value", 10.0)))

        def save():
            try:
                self.config["scan_coord_one"] = eval(entry_w1.get())
                self.config["scan_coord_two"] = eval(entry_w2.get())
                self.config["scan_coord_attachment"] = eval(entry_att.get())
                self.config["scan_coord_ammo"] = eval(entry_ammo.get())
                self.config["scan_coord_mag_icon"] = eval(entry_mag_icon.get())
                self.config["modifier_value"] = float(entry_mod.get())
                self.save_config()
                messagebox.showinfo("Success", "Configuration saved!")
                config_window.destroy()
            except Exception as e:
                logging.error(f"Config save error: {e}")
                messagebox.showerror("Error", f"Invalid input: {e}")

        tk.Button(config_window, text="Save", command=save).pack(pady=10)

    def load_pattern(self, weapon, magazine_type=None):
        weapon_to_json = {
            "R-99": "R99diagn.json",
            "R-301": "R-301_Blank_v1.json",
            "FLATLINE": "Flatline_Blank_v1.json",
            "ALTERNATOR": "Alternator_Blank_v1.json",
            "VOLT": "Volt_Blank_v1.json"
        }
        json_filename = weapon_to_json.get(weapon, f"{weapon}.json")
        if weapon in self.magazine_mapping and magazine_type in self.magazine_mapping[weapon]:
            json_filename = self.magazine_mapping[weapon][magazine_type]
            logging.info(f"Selected magazine-specific JSON for {weapon} ({magazine_type}): {json_filename}")
        else:
            logging.warning(f"Using default JSON for {weapon}: {json_filename} (magazine_type={magazine_type})")

        json_path = os.path.join(self.patterns_path, json_filename)
        try:
            with open(json_path, "r") as f:
                data = json.load(f)
            logging.info(f"Loaded JSON from {json_path}")

            if "x" in data and "y" in data and "fire_rate" in data:
                pattern = list(zip(data["x"], data["y"]))
                if not all(isinstance(p, tuple) and len(p) == 2 for p in pattern):
                    logging.error(f"Invalid pattern format in {json_path}")
                    return None, None
                try:
                    recoil_params = {
                        "fire_rate": data["fire_rate"],
                        "vertical_recoil": float(data.get("vertical_recoil", 1.0)),
                        "horizontal_recoil": float(data.get("horizontal_recoil", 1.0)),
                        "zoom_correction_factor": float(data.get("zoom_correction_factor", 1.0))
                    }
                except (ValueError, TypeError) as e:
                    logging.error(f"Invalid recoil parameters in {json_path}: {e}")
                    return None, None
                logging.info(f"Converted pattern for {weapon}: {pattern[:5]}...")
                logging.info(f"Recoil parameters for {weapon}: {recoil_params}")
                return pattern, recoil_params
            else:
                logging.error(f"Invalid JSON structure in {json_path}")
                return None, None
        except FileNotFoundError:
            logging.error(f"No pattern found at {json_path}")
            return None, None
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in {json_path}: {e}")
            return None, None

    def rt_detection_loop(self):
        while self.rt_thread_running:
            if self.current_weapon != "None" and AntiRecoil.is_trigger_pressed_static() and self.current_pattern:
                logging.info(f"RT pressed, applying anti-recoil for {self.current_weapon} ({self.current_magazine_type})")
                self.anti_recoil = AntiRecoil(
                    pattern=self.current_pattern,
                    fire_rate=self.current_recoil_params["fire_rate"],
                    zoom_correction_factor=self.current_recoil_params.get("zoom_correction_factor", self.zoom_correction_factor),
                    y_scale=self.current_recoil_params.get("vertical_recoil", 1.0),
                    x_scale=self.current_recoil_params.get("horizontal_recoil", 1.0),
                    gamepad=self.gamepad
                )
                self.anti_recoil.apply_anti_recoil()
                self.anti_recoil = None
            time.sleep(0.01)

    def detection_loop(self):
        if not self.running:
            return

        weapon_info, _ = detect_weapons(active_slot_hint=self.current_slot)
        new_weapon = weapon_info["active_weapon"]["name"]
        new_magazine_type = weapon_info["active_weapon"]["magazine_type"]
        self.current_slot = weapon_info["active_weapon"]["slot"]

        if new_weapon != self.current_weapon or new_magazine_type != self.current_magazine_type:
            self.current_weapon = new_weapon
            self.current_magazine_type = new_magazine_type
            self.current_pattern = None
            self.current_recoil_params = None
            if self.current_weapon != "None":
                self.current_pattern, self.current_recoil_params = self.load_pattern(self.current_weapon, self.current_magazine_type)
                if self.current_pattern and self.current_recoil_params:
                    logging.info(f"Preloaded pattern for {self.current_weapon} ({self.current_magazine_type})")
                else:
                    logging.warning(f"Failed to preload pattern for {self.current_weapon} ({self.current_magazine_type})")

        self.label_weapon.config(text=f"Weapon: {self.current_weapon}")
        self.label_slot.config(text=f"Slot: {self.current_slot}")
        self.label_magazine.config(text=f"Magazine: {self.current_magazine_type or 'Unknown'}")
        self.root.update()
        logging.debug(f"GUI updated: Weapon={self.current_weapon}, Slot={self.current_slot}, Magazine={self.current_magazine_type}")

        self.root.after(500, self.detection_loop)

    def start_detection(self):
        if not self.running:
            self.running = True
            self.rt_thread_running = True
            self.label_status.config(text="Status: Running")
            self.btn_start.config(state="disabled")
            self.btn_stop.config(state="normal")
            self.rt_thread = threading.Thread(target=self.rt_detection_loop, daemon=True)
            self.rt_thread.start()
            self.detection_loop()
            logging.info("Detection started")

    def stop_detection(self):
        if self.running:
            self.running = False
            self.rt_thread_running = False
            if self.rt_thread:
                self.rt_thread.join(timeout=1.0)
            self.label_status.config(text="Status: Stopped")
            self.btn_start.config(state="normal")
            self.btn_stop.config(state="disabled")
            if self.anti_recoil:
                self.anti_recoil.reset_stick()
                self.anti_recoil = None
            self.current_pattern = None
            self.current_recoil_params = None
            self.current_magazine_type = None
            logging.info("Detection stopped")

    def run(self):
        try:
            self.root.mainloop()
        finally:
            if self.gamepad:
                self.gamepad.reset()
                logging.info("Virtual controller shut down")

if __name__ == "__main__":
    root = tk.Tk()
    app = DetectionGUI(root)
    app.run()
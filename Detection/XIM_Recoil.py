import tkinter as tk
from tkinter import messagebox
import yaml
import os
import logging
from weapon_detection import detect_weapons
import vgamepad as vg
import time
import pydirectinput

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), '..', 'logs', 'gui_log.txt')),
        logging.StreamHandler()
    ]
)

class DetectionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Weapon Detection")
        self.root.geometry("400x300")
        self.running = False
        self.gamepad = vg.VX360Gamepad()
        logging.info("Virtual controller initialized (assumed XInput index 0)")
        self.config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
        self.current_weapon = "None"
        self.current_slot = "Unknown"

        # Weapon-to-button mapping (only for weapons that trigger presses)
        self.button_mapping = {
            "R-301": "DPAD_UP",
            "C.A.R": "Y",
            "FLATLINE": "DPAD_DOWN",
            "HEMLOK": "DPAD_LEFT",
            "ALTERNATOR": "A",
            "R-99": "X",
            "VOLT": "LB",
            "SPITFIRE": "RB",
            "DEVOTION": "LT",
            "L-STAR": "RT",
            "HAVOC": "DPAD_RIGHT",
            "PROWLER": "DPAD_LEFT",
            "NEMESIS": "DPAD_LEFT"
        }
        logging.info("Button mappings initialized")

        # Weapons to ignore (no button presses)
        self.ignored_weapons = {
            "P2020", "RE-45", "G7 SCOUT", "30-30 REPEATER", "RAMPAGE", "KRABER",
            "SENTINEL", "WINGMAN", "MASTIFF", "EVA-8", "MOZAMBIQUE", "PEACEKEEPER",
            "LONGBOW", "BOCEK", "CHARGERIFLE"
        }
        logging.info("Ignored weapons initialized")

        # GUI elements
        self.label_status = tk.Label(root, text="Status: Stopped", font=("Arial", 12))
        self.label_status.pack(pady=10)
        self.label_weapon = tk.Label(root, text="Weapon: None", font=("Arial", 12))
        self.label_weapon.pack(pady=5)
        self.label_slot = tk.Label(root, text="Slot: Unknown", font=("Arial", 12))
        self.label_slot.pack(pady=5)
        self.btn_start = tk.Button(root, text="Start Detection", command=self.start_detection)
        self.btn_start.pack(pady=5)
        self.btn_stop = tk.Button(root, text="Stop Detection", command=self.stop_detection, state="disabled")
        self.btn_stop.pack(pady=5)
        self.btn_config = tk.Button(root, text="Configure", command=self.open_config)
        self.btn_config.pack(pady=5)

        # Load config
        try:
            with open(self.config_path, "r") as f:
                self.config = yaml.safe_load(f)
            logging.info("Configuration loaded from config.yaml")
        except FileNotFoundError:
            self.config = {}
            self.save_config()
            logging.warning("No config.yaml found, created new config")

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

    def press_button(self, button_type):
        try:
            if button_type == "DPAD_UP":  # R-301 uses keyboard simulation for XIM
                start_time = time.time()
                logging.debug(f"Simulating F1 key press for XIM D-pad Up at {start_time}")
                pydirectinput.press('f2')  # Simulates F1 press/release
                end_time = time.time()
                logging.info(f"Pressed F1 (XIM D-pad Up), duration: {(end_time - start_time) * 1000:.2f}ms")
            else:
                self.gamepad.reset()  # Clear controller state
                self.gamepad.update()
                start_time = time.time()
                logging.debug(f"Pressing {button_type} to XIM Matrix at {start_time}")
                if button_type == "LT":
                    self.gamepad.left_trigger_float(0.01)
                    self.gamepad.update()
                    time.sleep(0.1)
                    self.gamepad.left_trigger_float(0.0)
                elif button_type == "RT":
                    self.gamepad.right_trigger_float(0.01)
                    self.gamepad.update()
                    time.sleep(0.1)
                    self.gamepad.right_trigger_float(0.0)
                else:
                    button = {
                        "DPAD_UP": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
                        "DPAD_DOWN": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
                        "DPAD_LEFT": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
                        "DPAD_RIGHT": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
                        "Y": vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
                        "X": vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
                        "A": vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
                        "B": vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
                        "LB": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
                        "RB": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER
                    }[button_type]
                    self.gamepad.press_button(button=button)
                    self.gamepad.update()
                    time.sleep(0.1)
                    self.gamepad.release_button(button=button)
                self.gamepad.update()
                end_time = time.time()
                logging.info(f"Pressed {button_type} to XIM Matrix, duration: {(end_time - start_time) * 1000:.2f}ms")
        except Exception as e:
            logging.error(f"Failed to press {button_type}: {e}")

    def detection_loop(self):
        if not self.running:
            return

        weapon_info, _ = detect_weapons(active_slot_hint=self.current_slot)
        new_weapon = weapon_info["active_weapon"]["name"]
        new_slot = weapon_info["active_weapon"]["slot"]

        logging.debug(f"Detected: weapon={new_weapon}, slot={new_slot}, current_weapon={self.current_weapon}")

        # Press button for R-301 every detection cycle
        if new_weapon == "R-301" and new_weapon not in self.ignored_weapons:
            button_type = self.button_mapping["R-301"]
            logging.info(f"Detected R-301 in {new_slot}, pressing {button_type}")
            self.press_button(button_type)

        # Press button for other mapped, non-ignored weapons on change
        elif (new_weapon != "None" and 
              new_weapon != self.current_weapon and 
              new_weapon in self.button_mapping and 
              new_weapon not in self.ignored_weapons):
            button_type = self.button_mapping[new_weapon]
            logging.info(f"Detected {new_weapon} in {new_slot}, pressing {button_type}")
            self.press_button(button_type)

        self.current_weapon = new_weapon
        self.current_slot = new_slot
        self.label_weapon.config(text=f"Weapon: {self.current_weapon}")
        self.label_slot.config(text=f"Slot: {self.current_slot}")
        self.root.update()
        logging.debug(f"GUI updated: Weapon={self.current_weapon}, Slot={self.current_slot}")

        self.root.after(200, self.detection_loop)  # Run every 200ms

    def start_detection(self):
        if not self.running:
            self.running = True
            self.label_status.config(text="Status: Running")
            self.btn_start.config(state="disabled")
            self.btn_stop.config(state="normal")
            self.detection_loop()
            logging.info("Detection started")

    def stop_detection(self):
        if self.running:
            self.running = False
            self.label_status.config(text="Status: Stopped")
            self.btn_start.config(state="normal")
            self.btn_stop.config(state="disabled")
            logging.info("Detection stopped")

    def run(self):
        try:
            self.root.mainloop()
        finally:
            if self.gamepad:
                self.gamepad.reset()
                self.gamepad.update()
                logging.info("Virtual controller shut down")

if __name__ == "__main__":
    # Overwrite XIM_Recoil.py with the current script's source code
    script_path = r"C:\REKOILX - BEST\Detection\XIM_Recoil.py"
    try:
        with open(__file__, "r") as source_file:
            source_code = source_file.read()
        with open(script_path, "w") as target_file:
            target_file.write(source_code)
        logging.info(f"Script saved to {script_path}")
    except Exception as e:
        logging.error(f"Failed to save script to {script_path}: {e}")

    # Initialize pydirectinput
    pydirectinput.FAILSAFE = True  # Move mouse to upper-left to stop
    root = tk.Tk()
    app = DetectionGUI(root)
    app.run()
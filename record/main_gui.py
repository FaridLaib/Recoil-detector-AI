# record/main_gui.py
import sys
import os
import threading
import json
import time
import keyboard
import vgamepad as vg
import XInput
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
from common.anti_recoil import AntiRecoil
from record.utils import save_to_json, BASE_DIR
from record.gui_components import MainFrame, DetectionControls, AntiRecoilControls, PatternCanvas
from record.fire_rates import show_fire_rates
from record.help_texts import show_help
from record.gui_utils import (
    browse_image, browse_json, pick_color, match_background_color,
    toggle_select_region_mode, paint, save_image, toggle_adjust_mode,
    add_point, remove_point, show_instructions, show_save_warning
)

class AutoRecoilPatternGUI:
    def __init__(self, root, log_toggle_callback):
        self.root = root
        self.root.title("Automatic Recoil Pattern Detector and Anti-Recoil")
        self.root.geometry("900x900")
        self.image_path = None
        self.current_image = None
        self.points = []
        self.images = []
        self.thresh_image = None
        self.min_thresh_var = None
        self.max_thresh_var = None
        self.min_area_var = None
        self.max_area_var = None
        self.kernel_size_var = None
        self.brush_size_var = None
        self.overwrite_var = None
        self.adjust_mode = False
        self.paint_mode = False
        self.select_region_mode = False
        self.selected_color = (255, 0, 0)
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        self.vertical_recoil_var = None
        self.horizontal_recoil_var = None
        self.zoom_correction_var = None
        self.json_path_var = None
        self.pattern_save_name_var = None
        self.weapon_entry = None
        self.fire_rate_entry = None
        self.image_entry = None
        self.imported_pattern = None
        self.anti_recoil = None
        self.anti_recoil_thread = None
        self.anti_recoil_running = False
        self.last_weapon_name = None
        self.last_pattern_save_name = None
        self.log_toggle_callback = log_toggle_callback
        self.logging_enabled = False
        self.pending_trigger_button = None
        self.gamepad = vg.VX360Gamepad()
        self.canvas = None
        self.detection_controls = None
        self.setup_gui()

    def setup_gui(self):
        main_frame = MainFrame(self).frame
        self.detection_controls = DetectionControls(main_frame, self)
        anti_recoil_controls = AntiRecoilControls(main_frame, self)
        self.canvas = PatternCanvas(main_frame, self).canvas

        self.min_thresh_var = self.detection_controls.min_thresh_var
        self.max_thresh_var = self.detection_controls.max_thresh_var
        self.min_area_var = self.detection_controls.min_area_var
        self.max_area_var = self.detection_controls.max_area_var
        self.kernel_size_var = self.detection_controls.kernel_size_var
        self.brush_size_var = self.detection_controls.brush_size_var
        self.overwrite_var = self.detection_controls.overwrite_var
        self.vertical_recoil_var = anti_recoil_controls.vertical_recoil_var
        self.horizontal_recoil_var = anti_recoil_controls.horizontal_recoil_var
        self.zoom_correction_var = anti_recoil_controls.zoom_correction_var
        self.json_path_var = anti_recoil_controls.json_path_var
        self.pattern_save_name_var = anti_recoil_controls.pattern_save_name_var
        self.weapon_entry = self.detection_controls.weapon_entry
        self.fire_rate_entry = self.detection_controls.fire_rate_entry
        self.image_entry = self.detection_controls.image_entry

    def load_image(self, file):
        try:
            img = Image.open(file)
            img_width, img_height = img.size
            max_width, max_height = 400, 800
            canvas_width = min(img_width, max_width)
            canvas_height = min(img_height, max_height)
            if img_width > max_width or img_height > max_height:
                ratio = min(max_width / img_width, max_height / img_height)
                canvas_width = int(img_width * ratio)
                canvas_height = int(img_height * ratio)
                img = img.resize((canvas_width, canvas_height), Image.LANCZOS)
            self.canvas.config(width=canvas_width, height=canvas_height)
            photo = ImageTk.PhotoImage(img)
            self.images.append(photo)
            self.canvas.delete("all")
            self.image_id = self.canvas.create_image(0, 0, image=photo, anchor="nw")
            self.points = []
            self.current_image = cv2.imread(file)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")

    def visualize_points(self):
        self.canvas.delete("all")
        img_pil = Image.fromarray(cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB))
        img_width, img_height = img_pil.size
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        scale_x = canvas_width / img_width
        scale_y = canvas_height / img_height
        img_pil = img_pil.resize((canvas_width, canvas_height), Image.LANCZOS)
        self.images.append(ImageTk.PhotoImage(img_pil))
        self.canvas.create_image(0, 0, image=self.images[-1], anchor="nw")

        if self.thresh_image:
            self.canvas.create_image(0, 0, image=self.thresh_image, anchor="nw")

        proximity_threshold = 20
        for i, (x, y) in enumerate(self.points, 1):
            canvas_x = x * scale_x
            canvas_y = y * scale_y
            radius = 3
            self.canvas.create_oval(canvas_x - radius, canvas_y - radius,
                                    canvas_x + radius, canvas_y + radius,
                                    fill="green", tags="point")
            direction = "right"
            if i > 1:
                prev_x, prev_y = self.points[i - 2]
                y_diff = abs(y - prev_y)
                if y_diff < proximity_threshold:
                    prev_direction = "right" if (self.points[i - 2][0] < self.points[i - 2][0] + 20) else "left"
                    direction = "left" if prev_direction == "right" else "right"
            line_length = 20
            if direction == "right":
                line_end_x = canvas_x + line_length
                line_end_y = canvas_y
                text_x = line_end_x + 10
                text_y = line_end_y
            else:
                line_end_x = canvas_x - line_length
                line_end_y = canvas_y
                text_x = line_end_x - 10
                text_y = line_end_y
            self.canvas.create_line(canvas_x, canvas_y, line_end_x, line_end_y, fill="black", width=1, tags="point")
            self.canvas.create_text(text_x, text_y, text=str(i), fill="black", tags="point")

    def analyze_impacts(self):
        try:
            if not self.image_path:
                messagebox.showerror("Error", "Please select an image.")
                return

            img = cv2.imread(self.image_path)
            self.current_image = img.copy()
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)

            min_thresh = self.min_thresh_var.get()
            max_thresh = self.max_thresh_var.get()
            thresh_combined = np.zeros_like(gray)
            for thresh_val in range(min_thresh, max_thresh + 1, 5):
                _, thresh = cv2.threshold(blurred, thresh_val, 255, cv2.THRESH_BINARY_INV)
                thresh_combined = cv2.bitwise_or(thresh_combined, thresh)

            kernel_size = self.kernel_size_var.get()
            kernel = np.ones((kernel_size, kernel_size), np.uint8)
            thresh = cv2.morphologyEx(thresh_combined, cv2.MORPH_OPEN, kernel)
            thresh = cv2.dilate(thresh, kernel, iterations=1)

            cv2.imwrite("thresh.png", thresh)

            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            self.points = []
            min_area = self.min_area_var.get()
            max_area = self.max_area_var.get()
            for contour in contours:
                area = cv2.contourArea(contour)
                if min_area < area < max_area:
                    M = cv2.moments(contour)
                    if M["m00"] != 0:
                        cX = int(M["m10"] / M["m00"])
                        cY = int(M["m01"] / M["m00"])
                        self.points.append((cX, cY))

            if not self.points:
                messagebox.showerror("Error", "No bullet impacts detected. Try adjusting the parameters.")
                return

            self.points.sort(key=lambda p: p[1], reverse=True)

            annotated_img = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
            proximity_threshold = 20
            for i, (x, y) in enumerate(self.points, 1):
                cv2.circle(annotated_img, (x, y), 5, (0, 255, 0), -1)
                direction = "right"
                if i > 1:
                    prev_x, prev_y = self.points[i - 2]
                    y_diff = abs(y - prev_y)
                    if y_diff < proximity_threshold:
                        prev_direction = "right" if (self.points[i - 2][0] < self.points[i - 2][0] + 20) else "left"
                        direction = "left" if prev_direction == "right" else "right"
                line_length = 20
                if direction == "right":
                    line_end_x = x + line_length
                    line_end_y = y
                    text_x = line_end_x + 10
                    text_y = line_end_y
                else:
                    line_end_x = x - line_length
                    line_end_y = y
                    text_x = line_end_x - 10
                    text_y = line_end_y
                cv2.line(annotated_img, (x, y), (line_end_x, line_end_y), (0, 0, 0), 1)
                cv2.putText(annotated_img, str(i), (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            cv2.imwrite("annotated_thresh.png", annotated_img)

            self.visualize_points()

            messagebox.showinfo("Success", f"Detected and sorted {len(self.points)} bullet impacts. Annotated threshold image saved as 'annotated_thresh.png'.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to analyze impacts: {str(e)}")

    def save_pattern(self):
        try:
            weapon_name = self.weapon_entry.get().strip()
            fire_rate = self.fire_rate_entry.get().strip()

            if not weapon_name:
                messagebox.showerror("Error", "Please enter a weapon name.")
                return
            if not fire_rate.isdigit() or not (0 <= int(fire_rate) <= 2000):
                messagebox.showerror("Error", "Fire rate must be a number between 0 and 2000.")
                return
            if not self.points:
                messagebox.showerror("Error", "No bullet impacts detected. Analyze the image first.")
                return

            self.last_weapon_name = weapon_name
            save_to_json(self.points, weapon_name, weapon_name, int(fire_rate), adjusted=False)
            messagebox.showinfo("Success", f"Saved {weapon_name}.json.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save pattern: {str(e)}")

    def reset(self):
        try:
            self.image_entry.delete(0, tk.END)
            self.image_path = None
            self.current_image = None
            self.points = []
            self.canvas.delete("all")
            self.weapon_entry.delete(0, tk.END)
            self.fire_rate_entry.delete(0, tk.END)
            self.thresh_image = None
            self.adjust_mode = False
            self.paint_mode = False
            self.select_region_mode = False
            self.canvas.unbind("<Button-1>")
            self.canvas.unbind("<Button-3>")
            self.canvas.unbind("<B1-Motion>")
            self.canvas.unbind("<ButtonRelease-1>")
            if self.anti_recoil_running:
                self.toggle_anti_recoil()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reset: {str(e)}")

    def toggle_logging(self):
        try:
            self.logging_enabled = not self.logging_enabled
            self.log_toggle_callback(self.logging_enabled)
            status = "enabled" if self.logging_enabled else "disabled"
            messagebox.showinfo("Logging", f"Logging has been {status}.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to toggle logging: {str(e)}")

    def remap_trigger(self):
        try:
            def capture_button():
                try:
                    state = XInput.get_state(0)
                    buttons = state.Gamepad.wButtons
                    button_map = {
                        XInput.XINPUT_GAMEPAD_A: "A",
                        XInput.XINPUT_GAMEPAD_B: "B",
                        XInput.XINPUT_GAMEPAD_X: "X",
                        XInput.XINPUT_GAMEPAD_Y: "Y",
                        XInput.XINPUT_GAMEPAD_LEFT_SHOULDER: "Left Shoulder",
                        XInput.XINPUT_GAMEPAD_RIGHT_SHOULDER: "Right Shoulder",
                        XInput.XINPUT_GAMEPAD_BACK: "Back",
                        XInput.XINPUT_GAMEPAD_START: "Start",
                        XInput.XINPUT_GAMEPAD_LEFT_THUMB: "Left Thumb",
                        XInput.XINPUT_GAMEPAD_RIGHT_THUMB: "Right Thumb",
                        XInput.XINPUT_GAMEPAD_DPAD_UP: "D-Pad Up",
                        XInput.XINPUT_GAMEPAD_DPAD_DOWN: "D-Pad Down",
                        XInput.XINPUT_GAMEPAD_DPAD_LEFT: "D-Pad Left",
                        XINPUT.XINPUT_GAMEPAD_DPAD_RIGHT: "D-Pad Right"
                    }
                    for flag, name in button_map.items():
                        if buttons & flag:
                            if self.anti_recoil:
                                self.anti_recoil.set_trigger_button(flag)
                            else:
                                self.pending_trigger_button = flag
                            messagebox.showinfo("Success", f"Anti-recoil trigger set to: {name}")
                            popup.destroy()
                            return
                    self.root.after(100, capture_button)
                except XInput.XInputNotConnectedError:
                    messagebox.showerror("Error", "No controller detected.")
                    popup.destroy()

            popup = tk.Toplevel(self.root)
            popup.title("Remap Trigger")
            popup.geometry("300x150")
            popup.transient(self.root)
            popup.grab_set()
            tk.Label(popup, text="Press a controller button to set as the anti-recoil trigger.", wraplength=280).pack(padx=10, pady=10)
            tk.Button(popup, text="Cancel", command=popup.destroy).pack(pady=5)
            self.root.after(100, capture_button)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remap trigger: {str(e)}")

    def toggle_anti_recoil(self):
        try:
            if self.anti_recoil_running:
                self.anti_recoil_running = False
                if self.anti_recoil_thread:
                    self.anti_recoil_thread.join(timeout=1.0)
                if self.anti_recoil:
                    self.anti_recoil.reset_stick()
                self.anti_recoil = None
                print("Anti-recoil stopped.")
                return

            if not self.last_weapon_name and not self.last_pattern_save_name:
                messagebox.showerror("Error", "No pattern saved or imported. Save or import a pattern first.")
                return

            pattern_name = self.last_pattern_save_name or self.last_weapon_name
            json_path = os.path.join(BASE_DIR, "common", "patterns", f"{pattern_name}_Adjusted.json")
            if not os.path.exists(json_path):
                json_path = os.path.join(BASE_DIR, "common", "patterns", f"{pattern_name}.json")
                if not os.path.exists(json_path):
                    messagebox.showerror("Error", f"Pattern file for {pattern_name} not found at {json_path}.")
                    return

            with open(json_path, "r") as f:
                data = json.load(f)
                pattern = list(zip(data["x"], data["y"]))
                fire_rate = data["fire_rate"]
                vertical_recoil = data.get("vertical_recoil", self.vertical_recoil_var.get())
                horizontal_recoil = data.get("horizontal_recoil", self.horizontal_recoil_var.get())
                zoom_correction_factor = data.get("zoom_correction_factor", self.zoom_correction_var.get())
                self.vertical_recoil_var.set(vertical_recoil)
                self.horizontal_recoil_var.set(horizontal_recoil)
                self.zoom_correction_var.set(zoom_correction_factor)

            self.anti_recoil = AntiRecoil(
                pattern=pattern,
                fire_rate=fire_rate,
                zoom_correction_factor=zoom_correction_factor,
                y_scale=vertical_recoil,
                x_scale=horizontal_recoil,
                gamepad=self.gamepad
            )
            if hasattr(self, 'pending_trigger_button'):
                self.anti_recoil.set_trigger_button(self.pending_trigger_button)
                del self.pending_trigger_button
            self.anti_recoil_running = True

            def anti_recoil_loop():
                print("Hold the remapped controller button (default Right Trigger) to activate anti-recoil. Press ESC to stop.")
                was_pressed = False
                while self.anti_recoil_running and not keyboard.is_pressed('esc'):
                    is_pressed = self.anti_recoil.is_trigger_pressed()
                    if is_pressed:
                        self.anti_recoil.apply_anti_recoil()
                        was_pressed = True
                    elif was_pressed:
                        self.anti_recoil.reset_stick()
                        was_pressed = False
                    time.sleep(0.01)
                self.anti_recoil_running = False
                if self.anti_recoil:
                    self.anti_recoil.reset_stick()
                self.anti_recoil = None
                print("Anti-recoil stopped.")

            self.anti_recoil_thread = threading.Thread(target=anti_recoil_loop)
            self.anti_recoil_thread.start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to toggle anti-recoil: {str(e)}")

    def import_recoil(self):
        try:
            if self.anti_recoil_running:
                self.anti_recoil_running = False
                if self.anti_recoil_thread:
                    self.anti_recoil_thread.join(timeout=1.0)
                self.anti_recoil = None
                print("Anti-recoil stopped.")

            json_path = self.json_path_var.get()
            if not json_path or not os.path.exists(json_path):
                messagebox.showerror("Error", "Please select a valid JSON file.")
                return

            with open(json_path, "r") as f:
                data = json.load(f)
                self.imported_pattern = list(zip(data["x"], data["y"]))
                fire_rate = data["fire_rate"]
                vertical_recoil = data.get("vertical_recoil", self.vertical_recoil_var.get())
                horizontal_recoil = data.get("horizontal_recoil", self.horizontal_recoil_var.get())
                zoom_correction_factor = data.get("zoom_correction_factor", self.zoom_correction_var.get())
                self.vertical_recoil_var.set(vertical_recoil)
                self.horizontal_recoil_var.set(horizontal_recoil)
                self.zoom_correction_var.set(zoom_correction_factor)

            self.anti_recoil = AntiRecoil(
                pattern=self.imported_pattern,
                fire_rate=fire_rate,
                zoom_correction_factor=zoom_correction_factor,
                y_scale=vertical_recoil,
                x_scale=horizontal_recoil,
                gamepad=self.gamepad
            )
            if hasattr(self, 'pending_trigger_button'):
                self.anti_recoil.set_trigger_button(self.pending_trigger_button)
                del self.pending_trigger_button
            self.anti_recoil_running = True

            def anti_recoil_loop():
                print(f"Testing imported JSON pattern from {json_path}. Hold the remapped controller button (default Right Trigger) to activate anti-recoil. Press ESC to stop.")
                was_pressed = False
                while self.anti_recoil_running and not keyboard.is_pressed('esc'):
                    is_pressed = self.anti_recoil.is_trigger_pressed()
                    if is_pressed:
                        self.anti_recoil.apply_anti_recoil()
                        was_pressed = True
                    elif was_pressed:
                        self.anti_recoil.reset_stick()
                        was_pressed = False
                    time.sleep(0.01)
                self.anti_recoil_running = False
                if self.anti_recoil:
                    self.anti_recoil.reset_stick()
                self.anti_recoil = None
                print("Anti-recoil stopped.")

            self.anti_recoil_thread = threading.Thread(target=anti_recoil_loop)
            self.anti_recoil_thread.start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import recoil: {str(e)}")

    def save_imported_pattern(self):
        try:
            if not self.imported_pattern:
                messagebox.showerror("Error", "No imported pattern to save. Please import a JSON file first.")
                return

            pattern_save_name = self.pattern_save_name_var.get().strip()
            fire_rate = self.fire_rate_entry.get().strip()

            if not pattern_save_name:
                messagebox.showerror("Error", "Please enter a pattern save name.")
                return
            if not fire_rate.isdigit() or not (0 <= int(fire_rate) <= 2000):
                messagebox.showerror("Error", "Fire rate must be a number between 0 and 2000.")
                return

            self.last_pattern_save_name = pattern_save_name
            save_to_json(self.imported_pattern, pattern_save_name, pattern_save_name, int(fire_rate), adjusted=False)
            messagebox.showinfo("Success", f"Saved imported pattern as {pattern_save_name}.json")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save imported pattern: {str(e)}")

    def save_modified_recoil(self):
        try:
            pattern_name = self.last_pattern_save_name or self.last_weapon_name
            pattern = self.imported_pattern or self.points

            if not pattern_name or not pattern:
                messagebox.showerror("Error", "No pattern saved or imported. Save or import a pattern first.")
                return

            json_path = os.path.join(BASE_DIR, "common", "patterns", f"{pattern_name}.json")
            if not os.path.exists(json_path):
                messagebox.showerror("Error", f"Pattern file for {pattern_name} not found at {json_path}.")
                return

            with open(json_path, "r") as f:
                data = json.load(f)
                fire_rate = data["fire_rate"]

            save_to_json(
                pattern,
                f"{pattern_name}_Adjusted",
                pattern_name,
                fire_rate,
                adjusted=True,
                vertical_recoil=self.vertical_recoil_var.get(),
                horizontal_recoil=self.horizontal_recoil_var.get(),
                zoom_correction_factor=self.zoom_correction_var.get()
            )
            messagebox.showinfo("Success", f"Saved {pattern_name}_Adjusted.json with modified settings.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save modified recoil: {str(e)}")

    def increment_scale(self, scale_type, delta):
        try:
            if scale_type == 'vertical_recoil':
                current = self.vertical_recoil_var.get()
                new_value = min(max(current + delta, -5.0), 5.0)
                self.vertical_recoil_var.set(round(new_value, 2))
            elif scale_type == 'horizontal_recoil':
                current = self.horizontal_recoil_var.get()
                new_value = min(max(current + delta, -5.0), 5.0)
                self.horizontal_recoil_var.set(round(new_value, 2))
            elif scale_type == 'zoom':
                current = self.zoom_correction_var.get()
                new_value = min(max(current + delta, 0.0), 5.0)
                self.zoom_correction_var.set(round(new_value, 2))
            self.update_scales()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to increment scale: {str(e)}")

    def update_scales(self, *args):
        try:
            if self.anti_recoil:
                self.anti_recoil.y_scale = self.vertical_recoil_var.get()
                self.anti_recoil.x_scale = self.horizontal_recoil_var.get()
                self.anti_recoil.zoom_correction_factor = self.zoom_correction_var.get()
                print(f"Updated scales: vertical_recoil={self.anti_recoil.y_scale}, horizontal_recoil={self.anti_recoil.x_scale}, zoom_correction_factor={self.anti_recoil.zoom_correction_factor}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update scales: {str(e)}")

    def merge_patterns(self):
        try:
            weapon_name = self.weapon_entry.get().strip()
            if not weapon_name:
                messagebox.showerror("Error", "Please enter a weapon name for merging.")
                return
            files = filedialog.askopenfilenames(
                filetypes=[("JSON Files", "*.json")],
                initialdir=os.path.join(BASE_DIR, "common", "patterns"),
                title="Select up to 3 JSON files"
            )
            if not files:
                messagebox.showerror("Error", "No files selected.")
                return
            if len(files) > 3:
                messagebox.showerror("Error", "Please select up to 3 files.")
                return
            messagebox.showinfo("Placeholder", f"Merging {len(files)} files for {weapon_name}. To be implemented with merging.py")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to merge patterns: {str(e)}")

    def show_instructions(self):
        try:
            instructions = """
How to Use the Automatic Recoil Pattern Detector for Apex Legends:

1. **Capture a Recoil Pattern**:
   - Go to the Apex Legends firing range and find a flat wall.
   - Stand 5–20 meters away from the wall.
   - Choose a weapon (e.g., R-301 Carbine) and aim at a fixed point on the wall.
   - Fire the entire magazine without moving your joystick to create a recoil pattern.
   - Equip a sniper rifle with 4x–8x zoom, stand at the same distance, and zoom in to capture the entire pattern.
   - Take a screenshot of the pattern using a tool like Windows Snipping Tool (free).
   - Example: See 'Flatline_Example.png' in the same folder for a sample pattern.

2. **Analyze the Pattern**:
   - Click 'Browse' under 'Image' to import your screenshot.
   - Enter the weapon name and fire rate (click 'Show Fire Rates' for a list).
   - Adjust parameters (Min/Max Threshold, Min/Max Area, Kernel Size) if needed.
   - Click 'Analyze Impacts' to automatically detect and sort bullet impacts (bottom to top).
   - Use 'Adjust' to manually add (left-click) or remove (right-click) points.
   - Use 'Paint' to edit the image (e.g., remove noise) with a selected color.

3. **Save the Pattern**:
   - Click 'Save' to save the pattern as '<Weapon Name>.json'.
   - Use 'Merge All Patterns' to combine up to 3 patterns to reduce randomization (placeholder).

4. **Test Anti-Recoil**:
   - Click 'Anti-Recoil' to apply the saved pattern.
   - Click 'Remap Trigger' to choose a controller button (default: Right Trigger).
   - Browse and import a saved '.json' pattern via 'Import Recoil'.
   - Adjust 'Vertical Recoil' (-5.0 to 5.0), 'Horizontal Recoil' (-5.0 to 5.0), and 'Zoom Factor' (0.0 to 5.0).
   - Click 'Save Modified Recoil' to save as '<Weapon Name>_Adjusted.json'.
   - Save imported patterns with a 'Pattern Save Name' via 'Save Imported'.

5. **Tips**:
   - Use '?' buttons for help.
   - Hold the remapped controller button to activate anti-recoil; press ESC to stop.
   - Save adjusted patterns for later use.
"""
            popup = tk.Toplevel(self.root)
            popup.title("Instructions")
            popup.geometry("600x500")
            popup.transient(self.root)
            popup.grab_set()
            canvas = tk.Canvas(popup)
            scrollbar = tk.Scrollbar(popup, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas)
            scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            text = tk.Text(scrollable_frame, wrap="word", height=25, width=70)
            text.insert("1.0", instructions)
            text.config(state="disabled")
            text.pack(padx=10, pady=10)
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            tk.Button(popup, text="OK", command=popup.destroy).pack(pady=5)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show instructions: {str(e)}")

    def exit_app(self):
        try:
            if self.anti_recoil_running:
                self.anti_recoil_running = False
                if self.anti_recoil_thread:
                    self.anti_recoil_thread.join(timeout=1.0)
            if self.gamepad:
                self.gamepad.reset()
            self.root.destroy()
            sys.exit(0)
        except Exception as e:
            pass
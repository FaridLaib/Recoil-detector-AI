# record/gui_utils.py
import os  # Add this import
import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
from PIL import Image, ImageTk
import cv2
import numpy as np
from record.utils import BASE_DIR

def browse_image(app):
    try:
        file = filedialog.askopenfilename(filetypes=[("Images", "*.jpeg *.jpg *.png")])
        if file:
            app.image_entry.delete(0, tk.END)
            app.image_entry.insert(0, file)
            app.image_path = file
            app.load_image(file)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to browse image: {str(e)}")

def browse_json(app):
    try:
        file = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json")],
            initialdir=os.path.join(BASE_DIR, "common", "patterns"),
            title="Select JSON Pattern File"
        )
        if file:
            app.json_path_var.set(file)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to browse JSON: {str(e)}")

def pick_color(app):
    try:
        color = colorchooser.askcolor(title="Choose Color")[0]
        if color:
            app.selected_color = (int(color[2]), int(color[1]), int(color[0]))
            messagebox.showinfo("Success", f"Color Selected: RGB{color}")
        else:
            app.selected_color = (255, 0, 0)
            messagebox.showinfo("Error", "Color selection cancelled, using default color RGB(255,0,0)")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to select color: {str(e)}")

def match_background_color(app):
    try:
        if app.current_image is None:
            messagebox.showerror("Error", "Please load an image first.")
            return
        img = app.current_image
        height, width = img.shape[:2]
        border_size = 10
        top = img[0:border_size, :, :]
        bottom = img[-border_size:, :, :]
        left = img[:, 0:border_size, :]
        right = img[:, -border_size:, :]
        border_pixels = np.vstack((top.reshape(-1, 3), bottom.reshape(-1, 3),
                                  left.reshape(-1, 3), right.reshape(-1, 3)))
        avg_color = np.mean(border_pixels, axis=0).astype(int)
        app.selected_color = tuple(int(c) for c in avg_color)
        avg_color_rgb = (avg_color[2], avg_color[1], avg_color[0])
        messagebox.showinfo("Success", f"Background color matched: RGB{avg_color_rgb}")
    except Exception as e:
        app.selected_color = (255, 0, 0)
        messagebox.showerror("Error", f"Failed to match background color: {str(e)}. Using default color (red).")

def toggle_select_region_mode(app):
    try:
        if not app.image_path:
            messagebox.showerror("Error", "Please load an image first.")
            return
        app.select_region_mode = not app.select_region_mode
        if app.select_region_mode:
            app.adjust_mode = False
            app.paint_mode = False
            app.canvas.unbind("<B1-Motion>")
            app.canvas.unbind("<ButtonRelease-1>")
            app.canvas.bind("<Button-1>", lambda event: start_region_select(app, event))
            app.canvas.bind("<B1-Motion>", lambda event: update_region_select(app, event))
            app.canvas.bind("<ButtonRelease-1>", lambda event: end_region_select(app, event))
            messagebox.showinfo("Info", "Click and drag to select a region to match the color. Click 'Select Region to Match' again to exit.")
        else:
            app.canvas.unbind("<Button-1>")
            app.canvas.unbind("<B1-Motion>")
            app.canvas.unbind("<ButtonRelease-1>")
            app.canvas.delete("region_rect")
            app.start_x = None
            app.start_y = None
            app.rect_id = None
            app.visualize_points()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to toggle select region mode: {str(e)}")

def start_region_select(app, event):
    try:
        if not app.select_region_mode:
            return
        app.start_x = event.x
        app.start_y = event.y
        app.canvas.delete("region_rect")
        app.rect_id = app.canvas.create_rectangle(app.start_x, app.start_y, app.start_x, app.start_y, outline="blue", tags="region_rect")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start region selection: {str(e)}")

def update_region_select(app, event):
    try:
        if not app.select_region_mode or app.start_x is None:
            return
        app.canvas.coords(app.rect_id, app.start_x, app.start_y, event.x, event.y)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to update region selection: {str(e)}")

def end_region_select(app, event):
    try:
        if not app.select_region_mode or app.start_x is None:
            return
        end_x = event.x
        end_y = event.y
        img_width, img_height = Image.open(app.image_path).size
        canvas_width = app.canvas.winfo_width()
        canvas_height = app.canvas.winfo_height()
        scale_x = img_width / canvas_width
        scale_y = img_height / canvas_height
        x1 = int(min(app.start_x, end_x) * scale_x)
        y1 = int(min(app.start_y, end_y) * scale_y)
        x2 = int(max(app.start_x, end_x) * scale_x)
        y2 = int(max(app.start_y, end_y) * scale_y)
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(img_width - 1, x2)
        y2 = min(img_height - 1, y2)
        region = app.current_image[y1:y2, x1:x2]
        if region.size == 0:
            messagebox.showerror("Error", "Selected region is too small. Please select a larger area.")
            return
        avg_color = np.mean(region.reshape(-1, 3), axis=0).astype(int)
        app.selected_color = tuple(int(c) for c in avg_color)
        avg_color_rgb = (avg_color[2], avg_color[1], avg_color[0])
        messagebox.showinfo("Success", f"Region color matched: RGB{avg_color_rgb}")
    except Exception as e:
        app.selected_color = (255, 0, 0)
        messagebox.showerror("Error", f"Failed to match region color: {str(e)}. Using default color (red).")
    finally:
        app.canvas.delete("region_rect")
        app.start_x = None
        app.start_y = None
        app.rect_id = None
        app.visualize_points()

def paint(app):
    try:
        if not app.image_path:
            messagebox.showerror("Error", "Please load an image first.")
            return
        app.paint_mode = not app.paint_mode
        if app.paint_mode:
            app.adjust_mode = False
            app.select_region_mode = False
            app.canvas.unbind("<Button-1>")
            app.canvas.unbind("<B1-Motion>")
            app.canvas.unbind("<ButtonRelease-1>")
            app.canvas.bind("<B1-Motion>", lambda event: paint_event(app, event))
            app.canvas.bind("<ButtonRelease-1>", lambda event: stop_paint(app))
            app.detection_controls.save_image_button.grid()
            app.detection_controls.overwrite_check.grid()
            messagebox.showinfo("Info", "Click and drag to paint with selected color. Click 'Paint' again to exit.")
        else:
            app.canvas.unbind("<B1-Motion>")
            app.canvas.unbind("<ButtonRelease-1>")
            app.visualize_points()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to toggle paint mode: {str(e)}")

def paint_event(app, event):
    try:
        if not app.paint_mode:
            return
        if not isinstance(app.selected_color, tuple) or len(app.selected_color) != 3 or not all(isinstance(c, (int, np.integer)) for c in app.selected_color):
            app.selected_color = (255, 0, 0)
            messagebox.showwarning("Warning", f"Invalid color: {app.selected_color}. Using default color (red).")
        else:
            app.selected_color = tuple(int(c) for c in app.selected_color)
        img_width, img_height = Image.open(app.image_path).size
        canvas_width = app.canvas.winfo_width()
        canvas_height = app.canvas.winfo_height()
        scale_x = img_width / canvas_width
        scale_y = img_height / canvas_height
        x = int(event.x * scale_x)
        y = int(event.y * scale_y)
        brush_size = app.brush_size_var.get()
        cv2.circle(app.current_image, (x, y), brush_size, app.selected_color, -1)
        img_pil = Image.fromarray(cv2.cvtColor(app.current_image, cv2.COLOR_BGR2RGB))
        img_pil = img_pil.resize((canvas_width, canvas_height), Image.LANCZOS)
        app.images.append(ImageTk.PhotoImage(img_pil))
        app.canvas.delete("all")
        app.canvas.create_image(0, 0, image=app.images[-1], anchor="nw")
        if app.thresh_image:
            app.canvas.create_image(0, 0, image=app.thresh_image, anchor="nw")
        app.visualize_points()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to paint: {str(e)}")

def stop_paint(app):
    try:
        app.visualize_points()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to stop paint: {str(e)}")

def save_image(app):
    try:
        if app.overwrite_var.get():
            cv2.imwrite(app.image_path, app.current_image)
            messagebox.showinfo("Success", f"Image overwritten at {app.image_path}.")
        else:
            new_file = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpeg *.jpg")])
            if new_file:
                cv2.imwrite(new_file, app.current_image)
                messagebox.showinfo("Success", f"Image saved as {new_file}.")
            else:
                messagebox.showinfo("Info", "Image saving canceled.")
        app.detection_controls.save_image_button.grid_remove()
        app.detection_controls.overwrite_check.grid_remove()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save image: {str(e)}")

def toggle_adjust_mode(app, enable):
    try:
        if enable:
            if not app.image_path:
                messagebox.showerror("Error", "Please load and analyze an image first.")
                return
            app.adjust_mode = True
            app.paint_mode = False
            app.select_region_mode = False
            app.canvas.unbind("<Button-1>")
            app.canvas.unbind("<B1-Motion>")
            app.canvas.unbind("<ButtonRelease-1>")
            app.canvas.bind("<Button-1>", lambda event: add_point(app, event))
            app.canvas.bind("<Button-3>", lambda event: remove_point(app, event))
            app.detection_controls.done_button.grid()
            messagebox.showinfo("Success", "Left-click to add a bullet impact, right-click to remove an existing detection. Click 'Done' when finished.")
        else:
            app.adjust_mode = False
            app.detection_controls.done_button.grid_remove()
            app.canvas.unbind("<Button-1>")
            app.canvas.unbind("<Button-3>")
            app.visualize_points()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to toggle adjust mode: {str(e)}")

def add_point(app, event):
    try:
        if not app.adjust_mode:
            return
        img_width, img_height = Image.open(app.image_path).size
        canvas_width = app.canvas.winfo_width()
        canvas_height = app.canvas.winfo_height()
        scale_x = img_width / canvas_width
        scale_y = img_height / canvas_height
        x = int(event.x * scale_x)
        y = int(event.y * scale_y)
        app.points.append((x, y))
        app.points.sort(key=lambda p: p[1], reverse=True)
        app.visualize_points()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add point: {str(e)}")

def remove_point(app, event):
    try:
        if not app.adjust_mode:
            return
        img_width, img_height = Image.open(app.image_path).size
        canvas_width = app.canvas.winfo_width()
        canvas_height = app.canvas.winfo_height()
        scale_x = img_width / canvas_width
        scale_y = img_height / canvas_height
        click_x = int(event.x * scale_x)
        click_y = int(event.y * scale_y)
        threshold = 10
        nearest_point = None
        min_dist = float('inf')
        for i, (x, y) in enumerate(app.points):
            dist = ((click_x - x) ** 2 + (click_y - y) ** 2) ** 0.5
            if dist < min_dist and dist < threshold:
                min_dist = dist
                nearest_point = i
        if nearest_point is not None:
            app.points.pop(nearest_point)
            app.points.sort(key=lambda p: p[1], reverse=True)
            app.visualize_points()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to remove point: {str(e)}")

def show_instructions(app):
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
        popup = tk.Toplevel(app.root)
        popup.title("Instructions")
        popup.geometry("600x500")
        popup.transient(app.root)
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

def show_save_warning(app):
    try:
        popup = tk.Toplevel(app.root)
        popup.title("Save Warning")
        popup.geometry("300x150")
        popup.transient(app.root)
        popup.grab_set()
        save_button_x = app.detection_controls.save_button.winfo_rootx()
        save_button_y = app.detection_controls.save_button.winfo_rooty()
        save_button_width = app.detection_controls.save_button.winfo_width()
        popup.geometry(f"300x150+{save_button_x + save_button_width + 2}+{save_button_y}")
        tk.Label(popup, text="It's always preferable to save a standard recoil without modifying vertical/horizontal/zoom first as a base, then create your own modified version.", wraplength=280).pack(padx=10, pady=10)
        tk.Button(popup, text="OK", command=popup.destroy).pack(pady=5)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to show save warning: {str(e)}")
import tkinter as tk
from PIL import Image, ImageTk
import pyautogui
import yaml
import os
import logging

# Setup logging
logging.basicConfig(
    filename='region_selector_log.txt',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configuration file path
CONFIG_FILE = "region_config.yaml"

class RegionSelector:
    def __init__(self, root):
        self.root = root
        self.root.title("Select Region for Gun Detection")
        self.screen_width, self.screen_height = 1920, 1080  # Your resolution
        self.start_x = None
        self.start_y = None
        self.rect = None

        # Create a canvas to display the screenshot
        self.canvas = tk.Canvas(root, width=self.screen_width, height=self.screen_height)
        self.canvas.pack()

        # Take a screenshot
        self.take_screenshot()

        # Bind mouse events
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

        # Add Save and Cancel buttons
        self.save_button = tk.Button(root, text="Save Region", command=self.save_region)
        self.save_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.cancel_button = tk.Button(root, text="Cancel", command=self.root.quit)
        self.cancel_button.pack(side=tk.RIGHT, padx=5, pady=5)

    def take_screenshot(self):
        # Take a screenshot using pyautogui
        screenshot = pyautogui.screenshot()
        # Convert to PIL Image
        self.screenshot = screenshot  # Already a PIL Image
        # Display on canvas
        self.photo = ImageTk.PhotoImage(self.screenshot)
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        logging.info("Screenshot captured")

    def on_mouse_down(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='red', width=2
        )
        logging.debug(f"Mouse down at: ({self.start_x}, {self.start_y})")

    def on_mouse_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)
        logging.debug(f"Dragging to: ({event.x}, {event.y})")

    def on_mouse_up(self, event):
        end_x, end_y = event.x, event.y
        # Ensure coordinates are within screen bounds
        x1 = max(0, min(self.start_x, end_x))
        y1 = max(0, min(self.start_y, end_y))
        x2 = min(self.screen_width, max(self.start_x, end_x))
        y2 = min(self.screen_height, max(self.start_y, end_y))
        width = x2 - x1
        height = y2 - y1
        print(f"Selected region: left={x1}, top={y1}, width={width}, height={height}")
        logging.info(f"Selected region: left={x1}, top={y1}, width={width}, height={height}")

    def save_region(self):
        if not self.rect:
            print("Error: No region selected")
            logging.error("No region selected")
            return

        # Get rectangle coordinates
        coords = self.canvas.coords(self.rect)
        x1, y1, x2, y2 = map(int, coords)
        # Calculate region
        left = min(x1, x2)
        top = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)

        # Ensure coordinates are valid
        if width <= 0 or height <= 0:
            print("Error: Invalid region size")
            logging.error("Invalid region size")
            return

        # Print coordinates
        print(f"Saved region: left={left}, top={top}, width={width}, height={height}")

        # Save to YAML file
        config_data = {
            'scan_coord_gun': {
                'left': left,
                'top': top,
                'width': width,
                'height': height
            }
        }
        with open(CONFIG_FILE, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False)
        logging.info(f"Saved region coordinates to {CONFIG_FILE}")

        # Close the application
        self.root.quit()

def main():
    # Create the main window
    root = tk.Tk()
    app = RegionSelector(root)
    root.mainloop()

if __name__ == "__main__":
    main()

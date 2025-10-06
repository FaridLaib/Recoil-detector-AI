import time
import numpy as np
import XInput
import vgamepad as vg
import tkinter as tk

# Load pattern from R99.txt
pattern_path = "R301_json.txt"
pattern = []

try:
    with open(pattern_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                parts = list(map(float, line.replace('\t', ',').split(',')))
                if len(parts) != 3:
                    continue
                x, y, duration = parts
                y = max(y, 0)  # Recoil only pulls upward
                pattern.append((x, y, duration / 1000))  # Convert ms to seconds
            except ValueError:
                continue
except FileNotFoundError:
    print(f"Error: {pattern_path} not found")
    exit(1)

if not pattern:
    print("Error: No valid data in R99.txt")
    exit(1)

# Normalize pattern
x_vals = [p[0] for p in pattern]
y_vals = [p[1] for p in pattern]

max_x = max(abs(v) for v in x_vals) or 1.0
max_y = max(abs(v) for v in y_vals) or 1.0

normalized_pattern = [
    (x / max_x, y / max_y, duration)
    for (x, y, duration) in pattern
]

print(f"Loaded {len(normalized_pattern)} pattern points.")
print(f"Max X: {max_x}, Max Y: {max_y}")

# Gamepad init
gamepad = vg.VX360Gamepad()

# Globals
sens = 1.0
zoom_sens = 1.0
modifier = sens * zoom_sens

# Input detection
def is_trigger_pressed():
    try:
        state = XInput.get_state(0)
        trigger_value = state.Gamepad.bRightTrigger / 255.0
        return trigger_value > 0.1
    except XInput.XInputNotConnectedError:
        return False

# Apply pattern
def apply_anti_recoil():
    global modifier
    if not is_trigger_pressed():
        return

    for i, (x, y, duration) in enumerate(normalized_pattern):
        if not is_trigger_pressed():
            break

        x_stick = x * modifier
        y_stick = -y * modifier  # Compensate up-recoil with downward stick

        x_stick = np.clip(x_stick, -1.0, 1.0)
        y_stick = np.clip(y_stick, -1.0, 1.0)

        print(f"[{i}] Stick: X={x_stick:.3f}, Y={y_stick:.3f}, Duration={duration:.4f}s")

        gamepad.right_joystick_float(x_stick, y_stick)
        gamepad.update()
        time.sleep(duration)

    gamepad.right_joystick_float(0.0, 0.0)
    gamepad.update()
    #time.sleep(0.05)

# GUI
root = tk.Tk()
root.title("Anti-Recoil Control")
root.geometry("400x400")

status_label = tk.Label(root, text="Hold RT to activate", font=("Arial", 12))
status_label.pack(pady=10)

def update_label(var, label):
    def inner(value):
        var.set(float(value))
        label.config(text=f"{var.get():.2f}")
        global modifier, sens, zoom_sens
        sens = sens_var.get()
        zoom_sens = zoom_sens_var.get()
        modifier = sens * zoom_sens
        print(f"Modifier: {modifier:.3f}")
    return inner

sens_var = tk.DoubleVar(value=1.0)
zoom_sens_var = tk.DoubleVar(value=1.0)

for label_text, var in [("Right Stick Sensitivity", sens_var), ("Zoom Sensitivity", zoom_sens_var)]:
    tk.Label(root, text=label_text).pack()
    val_label = tk.Label(root, text=f"{var.get():.2f}")
    val_label.pack()
    scale = tk.Scale(root, from_=0.1, to=2.0, resolution=0.05, orient=tk.HORIZONTAL,
                     command=update_label(var, val_label), length=300)
    scale.set(1.0)
    scale.pack(pady=10)

# Poll loop
def loop():
    if is_trigger_pressed():
        apply_anti_recoil()
    root.after(10, loop)

loop()
root.mainloop()

import vgamepad as vg
from inputs import get_gamepad
import time

# Initialize virtual Xbox controller
try:
    gamepad = vg.VX360Gamepad()
except Exception as e:
    print(f"Failed to initialize vgamepad: {e}")
    exit()

def send_controller_button_to_xim():
    """Simulate pressing and releasing D-Pad Up on the virtual controller."""
    try:
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)  # D-Pad Up
        gamepad.update()
        time.sleep(0.1)  # Hold for 100ms
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
        gamepad.update()
        print("Sent D-Pad Up to XIM")
    except Exception as e:
        print(f"Error sending controller button: {e}")

def main():
    print("Waiting for Y button press on controller. Press Ctrl+C to stop.")
    try:
        while True:
            events = get_gamepad()
            for event in events:
                if event.ev_type == "Key" and event.code == "BTN_NORTH" and event.state == 1:  # Y button pressed
                    send_controller_button_to_xim()
                    time.sleep(0.2)  # Debounce to avoid rapid triggers
    except KeyboardInterrupt:
        print("Script stopped.")
    finally:
        gamepad.reset()
        gamepad.update()

if __name__ == "__main__":
    main()
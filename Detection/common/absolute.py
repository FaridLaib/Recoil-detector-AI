import time
import XInput
import numpy as np
import logging
import os

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(os.path.join(os.path.dirname(__file__), '..', 'logs', 'absolute_log.txt')), logging.StreamHandler()]
)

class AntiRecoil:
    def __init__(self, pattern, fire_rate, zoom_correction_factor=1.0, y_scale=1.0, x_scale=1.0, gamepad=None):
        self.pattern = pattern
        self.fire_rate = fire_rate
        self.zoom_correction_factor = zoom_correction_factor
        self.gamepad = gamepad
        self.y_scale = y_scale
        self.x_scale = x_scale
        self.trigger_button = None
        logging.info(f"Initialized AntiRecoil with fire_rate={fire_rate}, zoom_correction_factor={zoom_correction_factor}, y_scale={y_scale}, x_scale={x_scale}")

    def set_trigger_button(self, button_flag):
        self.trigger_button = button_flag

    @staticmethod
    def is_trigger_pressed_static():
        try:
            state = XInput.get_state(0)
            return state.Gamepad.bRightTrigger / 255.0 > 0.01
        except XInput.XInputNotConnectedError:
            return False

    def is_trigger_pressed(self):
        try:
            state = XInput.get_state(0)
            if self.trigger_button is None:
                return state.Gamepad.bRightTrigger / 255.0 > 0.01
            else:
                return state.Gamepad.wButtons & self.trigger_button
        except XInput.XInputNotConnectedError:
            return False

    def reset_stick(self):
        if self.gamepad:
            self.gamepad.right_joystick_float(0.0, 0.0)
            self.gamepad.update()
            logging.debug("Stick reset")

    def apply_anti_recoil(self):
        if not self.gamepad:
            logging.error("No gamepad provided")
            return

        logging.info("Starting anti-recoil with absolute negation")

        for i, (x, y) in enumerate(self.pattern):
            if not self.is_trigger_pressed():
                logging.info("Trigger released — stopping anti-recoil")
                break

            # Negate x, use positive y to counter upward recoil (inverted y-axis)
            dx = -x
            dy = -y  # Changed from dy = -y to dy = +y

            # Apply scaling factors
            dx *= self.zoom_correction_factor * self.x_scale
            dy *= self.zoom_correction_factor * self.y_scale

            # Normalize to joystick range with stronger correction
            x_stick = np.clip(dx / 300.0, -1.0, 1.0)  # Changed from 100.0 to 50.0
            y_stick = np.clip(dy / 300.0, -1.0, 1.0)  # Changed from 100.0 to 50.0

            self.gamepad.right_joystick_float(x_stick, y_stick)
            self.gamepad.update()

            logging.debug(f"Step {i}: dx={dx:.1f}, dy={dy:.1f} -> x_stick={x_stick:.3f}, y_stick={y_stick:.3f}")
            time.sleep(60 / self.fire_rate)

        self.reset_stick()
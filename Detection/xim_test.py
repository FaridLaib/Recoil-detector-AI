import pydirectinput
import time
import logging
import os

# Configure logging
log_dir = r"C:\REKOILX - BEST\logs"
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'xim_test_log.txt')),
        logging.StreamHandler()
    ]
)

def simulate_key_press(key='f2'):
    """Simulate a single F2 key press with pydirectinput on Logitech keyboard."""
    try:
        start_time = time.time()
        logging.debug(f"Simulating {key} key press on Logitech keyboard at {start_time}")
        pydirectinput.press(key)  # Press and release F2
        end_time = time.time()
        logging.info(f"Pressed {key} (XIM R-301 anti-recoil via Dragon keyboard), duration: {(end_time - start_time) * 1000:.2f}ms")
    except Exception as e:
        logging.error(f"Failed to press {key}: {e}")

def main():
    logging.info("Starting XIM test script. Press Ctrl+C to stop.")
    try:
        while True:
            simulate_key_press('f2')  # Simulate F2 press (triggers R-301 anti-recoil in XIM)
            time.sleep(1)  # Wait 1 second between presses
    except KeyboardInterrupt:
        logging.info("XIM test script stopped by user.")

if __name__ == "__main__":
    # Initialize pydirectinput
    pydirectinput.FAILSAFE = True  # Move mouse to upper-left to stop
    main()
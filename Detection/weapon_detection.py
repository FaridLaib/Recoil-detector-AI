# detection/weapon_detection.py
import cv2 as cv
import numpy as np
from mss import mss
import pytesseract
import logging
from weapon_corrections import WEAPON_CORRECTIONS
import difflib
from helpers import read_config
import os

pytesseract.pytesseract.tesseract_cmd = r'C:\REKOILX\Detection\tesseract\tesseract.exe'

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(os.path.join(os.path.dirname(__file__), '..', 'logs', 'weapon_detection_log.txt')), logging.StreamHandler()]
)

sct = mss()

try:
    config = read_config()
    COORDINATES = {
        "slot_1_name": config.get("scan_coord_one", {"left": 1531, "top": 1033, "width": 137, "height": 24}),
        "slot_2_name": config.get("scan_coord_two", {"left": 1676, "top": 1034, "width": 141, "height": 21}),
        "slot_1_active": config.get("slot_1_active", {"left": 1518, "top": 1024, "width": 166, "height": 20}),
        "slot_2_active": config.get("slot_2_active", {"left": 1661, "top": 1024, "width": 170, "height": 20}),
        "attachment": config.get("scan_coord_attachment", {"left": 1600, "top": 980, "width": 200, "height": 50}),
        "ammo": config.get("scan_coord_ammo", {"left": 1650, "top": 1050, "width": 80, "height": 40}),
        "mag_icon": config.get("scan_coord_mag_icon", {"left": 1519, "top": 996, "width": 117, "height": 32})
    }
    logging.info("Loaded coordinates from config")
except Exception as e:
    logging.error(f"Failed to load config: {e}")
    COORDINATES = {
        "slot_1_name": {"left": 1531, "top": 1033, "width": 137, "height": 24},
        "slot_2_name": {"left": 1676, "top": 1034, "width": 141, "height": 21},
        "slot_1_active": {"left": 1518, "top": 1024, "width": 166, "height": 20},
        "slot_2_active": {"left": 1661, "top": 1024, "width": 170, "height": 20},
        "attachment": {"left": 1600, "top": 980, "width": 200, "height": 50},
        "ammo": {"left": 1650, "top": 1050, "width": 80, "height": 40},
        "mag_icon": {"left": 1519, "top": 996, "width": 117, "height": 32}
    }
    logging.warning("Using default coordinates")

KNOWN_WEAPONS = set(WEAPON_CORRECTIONS.values()) | {"R-99", "R-301", "FLATLINE", "ALTERNATOR", "VOLT"}

# Paths to magazine icon templates
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), '..', 'ammo_size')
MAG_TEMPLATES = {
    "Base": "R-99_Blank.png",
    "Purple/Gold": "R-99_PG.png"
}

def capture_screenshot(region):
    try:
        image = sct.grab(region)
        image_array = np.array(image)
        image_array = cv.cvtColor(image_array, cv.COLOR_BGRA2BGR)
        logging.debug("Screenshot captured")
        return image_array
    except Exception as e:
        logging.error(f"Screenshot capture failed: {e}")
        return None

def read_text(image):
    try:
        text = pytesseract.image_to_string(
            image,
            config='--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-.'
        )
        text = text.strip().upper().replace('0', 'O').replace('5', 'S')
        for char in [",", ":", ";", "!", "?", "\n"]:
            text = text.replace(char, '')
        text = WEAPON_CORRECTIONS.get(text, text)
        logging.debug(f"Read text: {text}")
        return text
    except Exception as e:
        logging.debug(f"Tesseract error: {e}")
        return ""

def get_brightness(image):
    try:
        gray = cv.cvtColor(image, cv.COLOR_BGRA2GRAY)
        brightness = np.mean(gray)
        logging.debug(f"Brightness: {brightness}")
        return brightness
    except Exception as e:
        logging.error(f"Brightness calculation failed: {e}")
        return 0

def match_weapon(text):
    text = text.strip().upper()
    if any(x in text for x in ["MM", "GMM"]) or not text:
        logging.debug(f"Non-weapon text filtered: {text}")
        return "None"
    if text in KNOWN_WEAPONS:
        logging.debug(f"Matched weapon: {text}")
        return text
    close_matches = difflib.get_close_matches(text, KNOWN_WEAPONS, n=1, cutoff=0.7)
    result = close_matches[0] if close_matches else "None"
    logging.debug(f"Weapon match: {text} -> {result}")
    return result

def detect_magazine_icon(image):
    try:
        image_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        best_match = None
        best_score = -1
        match_threshold = 0.8

        for mag_type, template_name in MAG_TEMPLATES.items():
            template_path = os.path.join(TEMPLATE_PATH, template_name)
            template = cv.imread(template_path, cv.IMREAD_GRAYSCALE)
            if template is None:
                logging.error(f"Failed to load template: {template_path}")
                continue

            result = cv.matchTemplate(image_gray, template, cv.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv.minMaxLoc(result)
            logging.debug(f"Template match for {mag_type}: score={max_val:.3f}")

            if max_val > best_score and max_val >= match_threshold:
                best_score = max_val
                best_match = mag_type

        if best_match:
            logging.info(f"Detected magazine: {best_match} (score={best_score:.3f})")
            return best_match
        else:
            logging.warning("No magazine icon matched (scores below threshold)")
            return None
    except Exception as e:
        logging.error(f"Magazine icon detection failed: {e}")
        return None

def detect_weapons(active_slot_hint="slot_1"):
    result = {
        "active_weapon": {"name": "None", "slot": "Unknown", "magazine_type": None},
        "slot_1": {"name": "None"},
        "slot_2": {"name": "None"}
    }

    try:
        brightness_1_img = sct.grab(COORDINATES["slot_1_active"])
        brightness_2_img = sct.grab(COORDINATES["slot_2_active"])
        brightness_1 = get_brightness(np.array(brightness_1_img))
        brightness_2 = get_brightness(np.array(brightness_2_img))
        active_slot = "slot_1" if brightness_1 > brightness_2 else "slot_2"
        logging.debug(f"Active slot: {active_slot}, Brightness: slot_1={brightness_1}, slot_2={brightness_2}")

        img_slot_1 = capture_screenshot(COORDINATES["slot_1_name"])
        img_slot_2 = capture_screenshot(COORDINATES["slot_2_name"])
        img_mag_icon = capture_screenshot(COORDINATES["mag_icon"])
        if img_slot_1 is None or img_slot_2 is None or img_mag_icon is None:
            logging.error("Failed to capture screenshots")
            return result, 0.0

        # Save captured images for debugging
        debug_dir = os.path.join(os.path.dirname(__file__), '..', 'logs', 'debug_images')
        os.makedirs(debug_dir, exist_ok=True)
        cv.imwrite(os.path.join(debug_dir, 'slot_1_img.png'), img_slot_1)
        cv.imwrite(os.path.join(debug_dir, 'slot_2_img.png'), img_slot_2)
        cv.imwrite(os.path.join(debug_dir, 'mag_icon_img.png'), img_mag_icon)
        logging.debug(f"Saved debug images to {debug_dir}")

        text_slot_1 = read_text(img_slot_1)
        text_slot_2 = read_text(img_slot_2)
        result["slot_1"]["name"] = match_weapon(text_slot_1)
        result["slot_2"]["name"] = match_weapon(text_slot_2)

        # Detect magazine icon only for R-99
        magazine_type = None
        if result["slot_1"]["name"] == "R-99" or result["slot_2"]["name"] == "R-99":
            magazine_type = detect_magazine_icon(img_mag_icon)

        if active_slot == "slot_1" and result["slot_1"]["name"] != "None":
            result["active_weapon"] = {
                "name": result["slot_1"]["name"],
                "slot": "Slot 1",
                "magazine_type": magazine_type
            }
        elif active_slot == "slot_2" and result["slot_2"]["name"] != "None":
            result["active_weapon"] = {
                "name": result["slot_2"]["name"],
                "slot": "Slot 2",
                "magazine_type": magazine_type
            }

        logging.info(f"Detected: {result['active_weapon']['name']} ({result['active_weapon']['slot']}), Magazine: {magazine_type}")
    except Exception as e:
        logging.error(f"Detection failed: {e}")

    return result, 0.0
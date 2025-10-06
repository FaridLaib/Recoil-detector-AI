import yaml
import os
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('log.txt'), logging.StreamHandler()]
)

yaml_config = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")

def config_generator():
    logging.info("Starting config generation")
    print("Please input the values for the first scan box [Ex. - left,top,width,height]:")
    weapon_scan_box_one = input().split(",")
    try:
        weapon_one_scan_coordinates = {
            "left": int(weapon_scan_box_one[0]),
            "top": int(weapon_scan_box_one[1]),
            "width": int(weapon_scan_box_one[2]),
            "height": int(weapon_scan_box_one[3])
        }
        logging.debug(f"Weapon one scan coordinates: {weapon_one_scan_coordinates}")
    except (ValueError, IndexError) as e:
        logging.error(f"Invalid input for weapon one scan: {e}")
        return

    print("Please input the values for the second scan box [Ex. - left,top,width,height]:")
    weapon_scan_box_two = input().split(",")
    try:
        weapon_two_scan_coordinates = {
            "left": int(weapon_scan_box_two[0]),
            "top": int(weapon_scan_box_two[1]),
            "width": int(weapon_scan_box_two[2]),
            "height": int(weapon_scan_box_two[3])
        }
        logging.debug(f"Weapon two scan coordinates: {weapon_two_scan_coordinates}")
    except (ValueError, IndexError) as e:
        logging.error(f"Invalid input for weapon two scan: {e}")
        return

    print("Please input the values for the attachment scan box [Ex. - left,top,width,height]:")
    attachment_scan_box = input().split(",")
    try:
        attachment_scan_coordinates = {
            "left": int(attachment_scan_box[0]),
            "top": int(attachment_scan_box[1]),
            "width": int(attachment_scan_box[2]),
            "height": int(attachment_scan_box[3])
        }
        logging.debug(f"Attachment scan coordinates: {attachment_scan_coordinates}")
    except (ValueError, IndexError) as e:
        logging.error(f"Invalid input for attachment scan: {e}")
        return

    print("Please input the values for the ammo scan box [Ex. - left,top,width,height]:")
    ammo_scan_box = input().split(",")
    try:
        ammo_scan_coordinates = {
            "left": int(ammo_scan_box[0]),
            "top": int(ammo_scan_box[1]),
            "width": int(ammo_scan_box[2]),
            "height": int(ammo_scan_box[3])
        }
        logging.debug(f"Ammo scan coordinates: {ammo_scan_coordinates}")
    except (ValueError, IndexError) as e:
        logging.error(f"Invalid input for ammo scan: {e}")
        return

    print("Enter the controller stick sensitivity modifier (e.g., 10.0 for less sensitive, 2.0 for more sensitive):")
    try:
        recoil_pattern_modifier = float(input())
        logging.debug(f"Recoil pattern modifier: {recoil_pattern_modifier}")
    except ValueError as e:
        logging.error(f"Invalid input for modifier: {e}")
        return

    data = {
        "scan_coord_one": weapon_one_scan_coordinates,
        "scan_coord_two": weapon_two_scan_coordinates,
        "scan_coord_attachment": attachment_scan_coordinates,
        "scan_coord_ammo": ammo_scan_coordinates,
        "modifier_value": recoil_pattern_modifier
    }

    try:
        with open(yaml_config, "w") as outfile:
            yaml.dump(data, outfile, default_flow_style=False)
        logging.info("Config file generated successfully")
    except Exception as e:
        logging.error(f"Failed to save config: {e}")

def read_config():
    try:
        with open(yaml_config, "r") as stream:
            data = yaml.safe_load(stream)
        logging.info("Config file read successfully")
        return data
    except Exception as e:
        logging.error(f"Failed to read config file: {e}")
        raise
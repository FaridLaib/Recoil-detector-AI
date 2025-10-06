# REKOILX-detector-AI
REKOILX is a Python-based launcher and toolkit for recording, adjusting, and applying recoil control patterns in FPS games.
It includes a GUI launcher, recoil pattern recorder, and weapon detection system powered by image recognition.
Tested on Apex Legends and resutls were fantastic.
🚀 How to Run

Install dependencies

pip install -r requirements.txt


(If no file exists, ensure you have tkinter, opencv-python, Pillow, pyserial, and easyocr installed.)

Launch the GUI

python launcher.py


From the launcher, choose:

Record/Adjust Patterns → Opens record/main.py

Detect Weapon and Apply Recoil → Opens Detection/gui.py

⚙️ Configuration

region_config.yaml — Defines pixel regions for image capture and detection.

R99diagn.json — Stores recoil data for a specific weapon (e.g., R99).

logs/ — Contains diagnostic files such as launcher_log.txt.

🧠 Notes

You can edit or add new weapon profiles by copying and modifying .json files.

The GUI and subsystems communicate via subprocess calls for modularity.

Logs are auto-generated on run and can be safely deleted.



<img width="405" height="332" alt="image" src="https://github.com/user-attachments/assets/4856e5b2-a320-4e2e-8888-25c412e097fa" />
<img width="975" height="1074" alt="image" src="https://github.com/user-attachments/assets/73d06010-3fc9-41d9-8b49-f66065aa510d" />
<img width="158" height="580" alt="R-99_Blank_Bruiser_v1" src="https://github.com/user-attachments/assets/76d77055-eca8-4250-b2ac-f62073188e6f" />



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

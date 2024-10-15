
# 🦾 Dobot Arm Automation with Kapla Building 🧱

This project is designed to automate the movement of a **Dobot** robotic arm to build structures with Kapla blocks using instructions from a JSON file. It integrates various libraries and hardware components to control the arm’s movements, servo motors, and GPIO pins for precise actions.

## 🚀 Features
- Controls the **Dobot** robotic arm via serial communication
- Reads building instructions from a `JSON` file
- Implements servo motor movements for vertical and horizontal actions
- Automated Kapla block pickup, rotation, and placement
- GPIO control for servo motors on the **Raspberry Pi**
- Modular design for easy expansion and additional control logic

## 📋 Usage Instructions

### 1. Requirements
- Dobot robotic arm
- Raspberry Pi (for GPIO control)
- Python environment with necessary libraries:
  - `serial.tools` for serial communication
  - `dobot_extensions` and `pydobot` for Dobot control
  - `RPi.GPIO` for controlling servos on Raspberry Pi
  - `numpy`, `time`, `sys`, `argparse`, `json`, `math` for general operations
- Ensure the Dobot arm is connected via the correct port (`/dev/ttyUSB0`).

### 2. Installation
1. Install the required Python libraries:
   ```bash
   pip install pyserial pydobot numpy RPi.GPIO
   ```
2. Clone the repository and navigate to the project directory.
3. Make sure the Dobot is properly connected and powered on.

### 3. Running the Script
1. To launch the main script with optional arguments for setting the home position and loading backups:
   ```bash
   python main.py -s [0|1|2|3] -l [0|1]
   ```
   - `-s` or `--sethome`: Set the initialization mode:
     - 0: No initialization
     - 1: Initialize arm and rail
     - 2: Initialize rail only
     - 3: Initialize arm only
   - `-l` or `--load`: Load or create a new backup:
     - 0: Create a new backup
     - 1: Load an existing backup

2. The arm will perform tasks based on the JSON instructions file (`construction.json`), controlling the Kapla block placement.

## 🔧 Requirements
- **Dobot** robotic arm with USB connection
- **Raspberry Pi** for GPIO control of servos
- **Kapla blocks** to build a physical structure
- **JSON instructions file** to define the building sequence

## 📄 License
This project is licensed under the GNU General Public License v3.0. You can read more about the license here: [GNU GPLv3 License](https://www.gnu.org/licenses/gpl-3.0.en.html).

## 🛡️ Disclaimer
⚠️ **Important**: This tool should be used responsibly. Ensure proper safety measures when working with robotic arms and connected hardware.

## 🙌 Contribution
Feel free to contribute to the project by submitting pull requests or opening issues. All contributions are welcome under the terms of the GNU GPLv3 license.

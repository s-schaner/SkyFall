# SkyFall

SkyFall is a tactical GUI interface for white-hat UAV reconnaissance. It visualizes
UAV locations and detected wireless targets on an interactive map.

## Requirements
* Python 3.8+
* PyQt5 and PyQtWebEngine

## Running
Install dependencies and run the GUI:

```bash
./install.sh       # or .\install.ps1 on Windows
python gui/main.py
```

On Windows the application relies on `netsh` for network scanning, while Linux
uses `iwlist` and the aircrack-ng suite. No extra WiFi libraries are required.

The application stores captured node and target data in a local SQLite
database (`skyfall.db`). Markers are loaded from this database when the GUI
starts.

Use the **Select Hardware** button in the sidebar to choose which WiFi
interface and GPS device will be used for surveys. Hardware discovery is
supported on both Windows and Linux.

The new **WiFi Control** dialog allows scanning for nearby access points
and placing your selected interface into monitor mode. You can choose the
desired channel, SSID and encryption method before starting packet
capture via aircrack-ng utilities.

You can also run `hardware.py` directly from the command line to list
available WiFi interfaces and GPS devices detected on your system.

To bundle as a single executable you can use PyInstaller:

```bash
pip install pyinstaller
pyinstaller gui/main.py --onefile --noconsole
```

## Files
- `gui/main.py` – main PyQt GUI application.
- `gui/map.html` – embedded Leaflet map used by the GUI.
- `database.py` – simple SQLite interface used by the GUI.
- `wifi.py` – helper functions for WiFi scanning and monitor mode.
- `hardware.py` – cross-platform discovery of WiFi interfaces and GPS devices.
- `install.sh` / `install.ps1` – scripts for installing dependencies and
  initializing the database.

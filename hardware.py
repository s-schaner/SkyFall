import os
import sys
import subprocess
from typing import Dict, List


def list_wifi_interfaces() -> List[str]:
    """Return available WiFi interfaces on the current system."""
    wifi = []
    if sys.platform.startswith("linux"):
        # Try using iw to list wireless interfaces
        try:
            output = subprocess.check_output(["iw", "dev"], text=True, stderr=subprocess.DEVNULL)
            for line in output.splitlines():
                line = line.strip()
                if line.startswith("Interface"):
                    wifi.append(line.split()[1])
        except Exception:
            pass
        # Fall back to checking /sys/class/net
        if not wifi:
            try:
                for iface in os.listdir("/sys/class/net"):
                    if iface.startswith(("wlan", "wifi", "wl", "ath", "wlp")):
                        wifi.append(iface)
            except Exception:
                pass
    elif sys.platform.startswith("win"):
        try:
            out = subprocess.check_output(
                ["netsh", "wlan", "show", "interfaces"],
                text=True,
                stderr=subprocess.DEVNULL,
            )
            for line in out.splitlines():
                if "Name" in line:
                    wifi.append(line.split(":", 1)[1].strip())
        except Exception:
            pass
    return wifi


def list_gps_devices() -> List[str]:
    """Return available GPS devices on the current system."""
    gps = []
    if sys.platform.startswith("linux"):
        try:
            for dev in os.listdir("/dev"):
                lower = dev.lower()
                if lower.startswith(("ttyusb", "ttyacm")) or "gps" in lower:
                    gps.append(os.path.join("/dev", dev))
        except Exception:
            pass
    elif sys.platform.startswith("win"):
        try:
            out = subprocess.check_output(
                ["wmic", "path", "Win32_SerialPort", "get", "DeviceID,Name"],
                text=True,
                stderr=subprocess.DEVNULL,
            )
            for line in out.splitlines():
                if not line.strip():
                    continue
                if "COM" in line:
                    if "GPS" in line.upper() or "GNSS" in line.upper():
                        device = line.split()[0]
                        gps.append(device)
        except Exception:
            pass
    return gps


def discover_hardware() -> Dict[str, List[str]]:
    """Return a dictionary with lists of WiFi interfaces and GPS devices."""
    return {"wifi": list_wifi_interfaces(), "gps": list_gps_devices()}


if __name__ == "__main__":
    hw = discover_hardware()
    print("WiFi interfaces:")
    for iface in hw["wifi"]:
        print(f"  {iface}")
    print("GPS devices:")
    for dev in hw["gps"]:
        print(f"  {dev}")

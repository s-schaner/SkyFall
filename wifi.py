import re
import subprocess
from typing import List, Dict


def scan_networks(interface: str) -> List[Dict[str, str]]:
    """Scan for WiFi networks using iwlist or airodump-ng output."""
    try:
        output = subprocess.check_output(
            ["iwlist", interface, "scan"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return []

    cells = output.split("Cell ")[1:]
    networks = []
    essid_re = re.compile(r"ESSID:\"(.*)\"")
    chan_re = re.compile(r"Channel:(\d+)")
    enc_re = re.compile(r"Encryption key:(on|off)")
    for cell in cells:
        essid = essid_re.search(cell)
        chan = chan_re.search(cell)
        enc = enc_re.search(cell)
        if essid:
            networks.append({
                "ssid": essid.group(1),
                "channel": chan.group(1) if chan else "",
                "encryption": "on" if enc and enc.group(1) == "on" else "off",
            })
    return networks


def start_monitor_mode(interface: str, channel: str = None):
    """Place interface into monitor mode using aircrack-ng utilities."""
    cmd = ["airmon-ng", "start", interface]
    if channel:
        cmd.append(channel)
    try:
        subprocess.check_call(cmd, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def stop_monitor_mode(interface: str):
    """Stop monitor mode on the given interface."""
    cmd = ["airmon-ng", "stop", interface]
    try:
        subprocess.check_call(cmd, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def capture_packets(interface: str, output_prefix: str = "capture"):
    """Capture WiFi packets using airodump-ng."""
    cmd = ["airodump-ng", "-w", output_prefix, interface]
    try:
        subprocess.check_call(cmd)
    except Exception:
        pass

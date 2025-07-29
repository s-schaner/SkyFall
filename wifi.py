"""Utility helpers for WiFi scanning and monitor mode."""

import os
import re
import subprocess
import sys
from typing import List, Dict


def scan_networks(interface: str) -> List[Dict[str, str]]:
    """Scan for WiFi networks on Linux or Windows."""

    if sys.platform.startswith("win"):
        try:
            output = subprocess.check_output(
                ["netsh", "wlan", "show", "networks", "mode=Bssid"],
                text=True,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            return []

        networks = []
        ssid_re = re.compile(r"SSID\s+\d+\s+:\s+(.*)")
        bssid_re = re.compile(r"BSSID\s+\d+\s+:\s+(.*)")
        chan_re = re.compile(r"Channel\s+:\s+(\d+)")
        enc_re = re.compile(r"Authentication\s+:\s+(.*)")
        lines = output.splitlines()
        current = {}
        for line in lines:
            ssid_match = ssid_re.search(line)
            if ssid_match:
                if current:
                    networks.append(current)
                current = {"ssid": ssid_match.group(1), "channel": "", "encryption": ""}
                continue
            if not current:
                continue
            chan_match = chan_re.search(line)
            if chan_match:
                current["channel"] = chan_match.group(1)
            enc_match = enc_re.search(line)
            if enc_match:
                current["encryption"] = enc_match.group(1)
        if current:
            networks.append(current)
        return networks

    # Default to Linux iwlist scanning
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
    """Place interface into monitor mode if supported."""
    if sys.platform.startswith("win"):
        # Monitor mode not generally available on Windows via netsh
        return

    cmd = ["airmon-ng", "start", interface]
    if channel:
        cmd.append(channel)
    try:
        subprocess.check_call(cmd, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def stop_monitor_mode(interface: str):
    """Stop monitor mode on the given interface."""
    if sys.platform.startswith("win"):
        return

    cmd = ["airmon-ng", "stop", interface]
    try:
        subprocess.check_call(cmd, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def capture_packets(interface: str, output_prefix: str = "capture"):
    """Capture WiFi packets using airodump-ng."""
    if sys.platform.startswith("win"):
        return

    cmd = ["airodump-ng", "-w", output_prefix, interface]
    try:
        subprocess.check_call(cmd)
    except Exception:
        pass

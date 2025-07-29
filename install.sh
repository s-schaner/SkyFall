#!/bin/bash
set -e

# Install system packages (Debian/Ubuntu style)
if command -v apt-get >/dev/null; then
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip aircrack-ng iw gpsd sqlite3
fi

# Install Python dependencies
pip3 install -r requirements.txt

# Initialize the database
python3 database.py --init

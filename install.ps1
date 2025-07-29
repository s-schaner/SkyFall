$ErrorActionPreference = "Stop"

# Install Python packages
pip install -r requirements.txt

# Attempt to install aircrack-ng if winget is available
if (Get-Command winget -ErrorAction SilentlyContinue) {
    winget install -e --id Aircrack-ng.Aircrack-ng | Out-Null
}

# Initialize the database
python database.py --init


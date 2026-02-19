#!/bin/bash
# G13 Linux GUI Launcher
# Uses pkexec for graphical sudo prompt

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python3"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: Virtual environment not found at $SCRIPT_DIR/.venv"
    echo "Please run: cd $SCRIPT_DIR && python3 -m venv .venv && pip install -e ."
    exit 1
fi

# Check if G13 is connected
if ! lsusb | grep -q "046d:c21c"; then
    zenity --warning --text="G13 device not detected.\n\nThe GUI will start but button input won't work until the device is connected." --width=300 2>/dev/null || \
    echo "Warning: G13 device not detected"
fi

# Launch with pkexec for libusb access (required for button input)
pkexec env DISPLAY="$DISPLAY" XAUTHORITY="$XAUTHORITY" "$VENV_PYTHON" -m g13_linux.gui.main --libusb

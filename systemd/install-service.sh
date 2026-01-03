#!/bin/bash
# Install G13 OPS as a user systemd service

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_FILE="$SCRIPT_DIR/g13-linux-user.service"
USER_SERVICE_DIR="$HOME/.config/systemd/user"

echo "G13 OPS Systemd Service Installer"
echo "=================================="

# Check if g13-linux-gui is installed
if ! command -v g13-linux-gui &> /dev/null; then
    # Check if it's in .local/bin
    if [ -f "$HOME/.local/bin/g13-linux-gui" ]; then
        echo "[OK] g13-linux-gui found in ~/.local/bin"
    else
        echo "[ERROR] g13-linux-gui not found!"
        echo "Install with: pip install --user -e ."
        exit 1
    fi
else
    echo "[OK] g13-linux-gui found"
fi

# Create user service directory if needed
mkdir -p "$USER_SERVICE_DIR"
echo "[OK] Service directory: $USER_SERVICE_DIR"

# Copy service file
cp "$SERVICE_FILE" "$USER_SERVICE_DIR/g13-linux.service"
echo "[OK] Service file installed"

# Reload systemd
systemctl --user daemon-reload
echo "[OK] Systemd reloaded"

# Enable and start service
echo ""
echo "To enable auto-start on login:"
echo "  systemctl --user enable g13-linux.service"
echo ""
echo "To start now:"
echo "  systemctl --user start g13-linux.service"
echo ""
echo "To check status:"
echo "  systemctl --user status g13-linux.service"
echo ""
echo "To view logs:"
echo "  journalctl --user -u g13-linux.service -f"

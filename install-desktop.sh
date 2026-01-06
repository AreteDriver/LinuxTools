#!/bin/bash
# Install G13 Linux desktop launcher

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing G13 Linux desktop launcher..."

# Create applications directory if needed
mkdir -p ~/.local/share/applications

# Copy desktop file with correct paths
sed "s|/home/arete/projects/G13_Linux|$SCRIPT_DIR|g" \
    "$SCRIPT_DIR/resources/g13-linux-gui.desktop" > ~/.local/share/applications/g13-linux-gui.desktop

# Update desktop database
update-desktop-database ~/.local/share/applications 2>/dev/null || true

echo "Done! G13 Linux should now appear in your applications menu."
echo ""
echo "You can also run directly: $SCRIPT_DIR/g13-linux-gui.sh"

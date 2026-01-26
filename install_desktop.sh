#!/bin/bash
#
# Install desktop entry for EVE Rebellion
#
# This script creates a desktop entry that appears in your application menu.
# Run this after extracting the portable package.
#

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Desktop entry locations
USER_DESKTOP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
DESKTOP_FILE="$USER_DESKTOP_DIR/MinmatarRebellion.desktop"

echo "Installing EVE Rebellion desktop entry..."
echo "Install directory: $SCRIPT_DIR"

# Create applications directory if it doesn't exist
mkdir -p "$USER_DESKTOP_DIR"

# Create desktop entry with correct paths
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Minmatar Rebellion
Comment=EVE-inspired arcade space shooter
Exec=$SCRIPT_DIR/run_game.sh
Icon=$SCRIPT_DIR/assets/icon.png
Terminal=false
Categories=Game;ArcadeGame;
Keywords=eve;space;shooter;arcade;minmatar;
StartupNotify=true
EOF

# Make the launcher executable
chmod +x "$SCRIPT_DIR/run_game.sh"

# Update desktop database if available
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$USER_DESKTOP_DIR" 2>/dev/null || true
fi

echo "Desktop entry installed successfully!"
echo "You should now see 'Minmatar Rebellion' in your application menu."
echo ""
echo "To uninstall, run: rm $DESKTOP_FILE"

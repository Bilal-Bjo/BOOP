#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

echo ""
echo "  ✨ JUST BOOP IT ✨"
echo ""
echo "  Installing Boop for Linux..."
echo ""

# Create virtual environment
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# Install dependencies
pip install watchdog pyyaml pystray Pillow --quiet

# Create desktop entry for autostart
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/boop.desktop << EOF
[Desktop Entry]
Type=Application
Name=Boop
Exec=$VENV_DIR/bin/python $SCRIPT_DIR/app.py
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Comment=Organize your Downloads folder
EOF

# Start Boop now
nohup "$VENV_DIR/bin/python" "$SCRIPT_DIR/app.py" > /dev/null 2>&1 &

echo "  ✨ Boop is ready!"
echo "  Look for ✨ in your system tray."
echo ""

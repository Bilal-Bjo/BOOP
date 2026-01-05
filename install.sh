#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
VENV_DIR="$PROJECT_DIR/.venv"
APP_NAME="Boop"
APP_PATH="/Applications/$APP_NAME.app"
PLIST_NAME="com.user.boop.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/$PLIST_NAME"

echo ""
echo "  ✨ JUST BOOP IT ✨"
echo ""
echo "  Installing Boop..."
echo ""

# Stop any running Boop instance
echo "  Stopping existing Boop instance..."
launchctl unload "$HOME/Library/LaunchAgents/com.user.downloadorganizer.plist" 2>/dev/null || true
launchctl unload "$PLIST_DEST" 2>/dev/null || true
pkill -f "app.py" 2>/dev/null || true
sleep 1

# Remove old versions
rm -f "$HOME/Library/LaunchAgents/com.user.downloadorganizer.plist"
rm -rf "/Applications/Download Organizer.app"
rm -rf "$APP_PATH"

# Remove old venv to ensure clean install
if [ -d "$VENV_DIR" ]; then
    echo "  Removing old virtual environment..."
    rm -rf "$VENV_DIR"
fi

# Create virtual environment
echo "  Creating virtual environment..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# Install dependencies
echo "  Installing dependencies..."
pip install --upgrade pip --quiet
pip install watchdog pyyaml rumps Pillow --quiet

# Generate icon
python "$PROJECT_DIR/icon.py"

# Create app bundle
echo "  Creating app bundle..."
mkdir -p "$APP_PATH/Contents/MacOS"
mkdir -p "$APP_PATH/Contents/Resources"

# App launcher script
cat > "$APP_PATH/Contents/MacOS/launcher" << EOF
#!/bin/bash
exec "$VENV_DIR/bin/python" "$PROJECT_DIR/app.py"
EOF
chmod +x "$APP_PATH/Contents/MacOS/launcher"

# App Info.plist
cat > "$APP_PATH/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>$APP_NAME</string>
    <key>CFBundleDisplayName</key>
    <string>$APP_NAME</string>
    <key>CFBundleIdentifier</key>
    <string>com.user.boop</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleExecutable</key>
    <string>launcher</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>LSUIElement</key>
    <true/>
</dict>
</plist>
EOF

# Copy icon
cp "$PROJECT_DIR/AppIcon.icns" "$APP_PATH/Contents/Resources/"

# Refresh icon cache
touch "$APP_PATH"

# Create LaunchAgent plist
cat > "$PLIST_DEST" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.boop</string>
    <key>ProgramArguments</key>
    <array>
        <string>$APP_PATH/Contents/MacOS/launcher</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/boop.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/boop.error.log</string>
</dict>
</plist>
EOF

# Load the service
launchctl load "$PLIST_DEST"

echo ""
echo "  ✨ Boop is ready!"
echo "  Look for ✨ in your menu bar."
echo ""

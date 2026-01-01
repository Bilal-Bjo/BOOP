#!/bin/bash
echo "Uninstalling Boop..."

# Remove autostart entry
rm -f ~/.config/autostart/boop.desktop

# Kill running Boop process
pkill -f "boop/app.py" 2>/dev/null || true

echo "Done! Boop has been removed. 👋"

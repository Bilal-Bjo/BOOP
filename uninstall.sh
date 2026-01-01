#!/bin/bash
set -e

echo "Uninstalling Boop..."

launchctl unload "$HOME/Library/LaunchAgents/com.user.boop.plist" 2>/dev/null || true
rm -f "$HOME/Library/LaunchAgents/com.user.boop.plist"
rm -rf "/Applications/Boop.app"

echo "Done! Boop has been removed. 👋"

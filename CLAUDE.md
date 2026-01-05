# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Boop is a cross-platform system tray application that automatically organizes files in the Downloads folder by moving them into category subfolders based on file extension.

## Development Commands

### Run directly (development)
```bash
# Requires: watchdog, pyyaml, pystray, Pillow (+ rumps on macOS)
python app.py
```

### Install as system service
```bash
# macOS
./install.sh

# Windows
.\install.bat

# Linux
./install-linux.sh
```

### Uninstall
```bash
# macOS: ./uninstall.sh
# Windows: .\uninstall.bat
# Linux: ./uninstall-linux.sh
```

### Generate app icon (macOS only)
```bash
python icon.py  # Creates AppIcon.icns
```

## Architecture

### Core Components

**app.py** - Single-file application (~550 lines) containing:
- `DownloadHandler` (FileSystemEventHandler): Watches for file creation/modification events, implements debounce logic to wait for downloads to complete before moving
- `Boop`: Core organizer class - starts/stops the watcher, handles file movement and duplicate naming
- `run_macos()`: macOS-specific UI using `rumps` library for menu bar integration
- `run_windows_linux()`: Windows/Linux UI using `pystray` for system tray

**config.yaml** - Extension-to-category mapping (100+ extensions across 11 categories: Images, Documents, Videos, Audio, Archives, Code, Applications, Fonts, Ebooks, 3D, Design)

### Key Behaviors
- Only watches root of Downloads folder (ignores subfolders)
- Hidden files (starting with `.`) are ignored
- 2-second debounce prevents moving incomplete downloads
- Duplicate files get `_1`, `_2` suffixes
- Unrecognized extensions go to "Other" folder

### Platform Detection
`get_platform()` returns `'macos'`, `'windows'`, or `'linux'` and determines which UI to launch.

## Logs (macOS)
- stdout: `/tmp/boop.log`
- stderr: `/tmp/boop.error.log`

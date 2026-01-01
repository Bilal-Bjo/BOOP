# ✨ Boop

A tiny cross-platform system tray app that magically organizes your Downloads folder.

```
     ╔═══════════════════════════════════════╗
     ║                                       ║
     ║         ✨ JUST BOOP IT ✨            ║
     ║                                       ║
     ║   Downloads messy? Don't stress.      ║
     ║   Boop handles the rest.              ║
     ║                                       ║
     ╚═══════════════════════════════════════╝
```

![Python](https://img.shields.io/badge/Python-3.10+-green)
![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows%20%7C%20Linux-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## What it does

- 👀 **Watches** your Downloads folder in real-time
- 🪄 **Automatically boops** files into the right folders
- ✨ **Lives in your system tray** - out of sight, out of mind
- 📄 **Click to reveal** your last booped file
- 🔄 **One-click reorganize** - boop everything at once

```
~/Downloads/
├── Images/       <- .jpg, .png, .gif, .svg, .webp
├── Documents/    <- .pdf, .doc, .docx, .xls, .txt
├── Videos/       <- .mp4, .mov, .avi, .mkv
├── Audio/        <- .mp3, .wav, .flac, .m4a
├── Archives/     <- .zip, .rar, .7z, .tar.gz
├── Code/         <- .py, .js, .html, .css, .json
├── Applications/ <- .dmg, .pkg, .exe, .msi
└── Other/        <- everything else
```

## Installation

### macOS

```bash
git clone https://github.com/yourusername/boop.git
cd boop
chmod +x install.sh
./install.sh
```

### Windows

```powershell
git clone https://github.com/yourusername/boop.git
cd boop
.\install.bat
```

### Linux

```bash
git clone https://github.com/yourusername/boop.git
cd boop
chmod +x install-linux.sh
./install-linux.sh
```

### Manual (Any Platform)

```bash
pip install watchdog pyyaml pystray Pillow
# On macOS only: pip install rumps
python app.py
```

## Usage

Click the ✨ in your system tray (menu bar on macOS):

| Menu Item | What it does |
|-----------|--------------|
| ✓ Monitoring Downloads | Status - it's watching |
| 📄 filename → Category | Click to reveal in Finder/Explorer |
| 🔄 Reorganize Now | Boop all existing files |
| Open Downloads Folder | Opens ~/Downloads |
| Quit | Stop the magic |

When a file gets booped, you'll see a notification!

## Configuration

Edit `config.yaml` to customize:

```yaml
watch_folder: ~/Downloads    # or C:\Users\You\Downloads on Windows
debounce_seconds: 2          # Wait for downloads to finish

categories:
  Images:
    - .jpg
    - .png
    # Add your own...
```

Then restart Boop.

## How it works

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   New file appears in Downloads                             │
│              │                                              │
│              ▼                                              │
│   Watchdog detects file creation                            │
│              │                                              │
│              ▼                                              │
│   Debounce: wait 2 seconds for download to complete         │
│              │                                              │
│              ▼                                              │
│   Check file extension → lookup category                    │
│              │                                              │
│              ▼                                              │
│   Move file to ~/Downloads/{Category}/                      │
│              │                                              │
│              ▼                                              │
│   ✨ Boop! Notification sent                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

~400 lines of well-documented Python. Simple magic. ✨

## Tech Stack

| Library | Purpose |
|---------|---------|
| [watchdog](https://github.com/gorakhargosh/watchdog) | Cross-platform file watching |
| [pystray](https://github.com/moses-palmer/pystray) | System tray (Windows/Linux) |
| [rumps](https://github.com/jaredks/rumps) | Menu bar (macOS) |
| [PyYAML](https://pyyaml.org/) | Config parsing |
| [Pillow](https://pillow.readthedocs.io/) | Icon generation |

## Uninstall

**macOS:** `./uninstall.sh`
**Windows:** `.\uninstall.bat`
**Linux:** `./uninstall-linux.sh`

## Project Structure

```
boop/
├── app.py          # The magic (cross-platform, ~400 lines)
├── config.yaml     # Categories configuration
├── icon.py         # Generates the app icon
├── install.sh      # macOS installer
├── install.bat     # Windows installer
├── install-linux.sh# Linux installer
└── README.md       # You are here
```

## Contributing

Fork it. Break it. Make it yours.

Ideas:
- ↩️ Undo last boop
- ⌨️ Keyboard shortcuts
- 📁 Custom destinations per category
- 🔔 Notification preferences
- 📊 Statistics dashboard

## License

MIT - do whatever you want.

---

Made with ✨ by someone who was tired of a messy Downloads folder.

## **JUST BOOP IT.**

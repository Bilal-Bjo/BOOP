#!/usr/bin/env python3
"""
Boop - A cross-platform system tray app that magically organizes your Downloads folder.

JUST BOOP IT! ✨

Supported Platforms:
    - macOS: Uses rumps for menu bar integration
    - Windows: Uses pystray for system tray integration
    - Linux: Uses pystray for system tray integration

How it works:
    1. Watches ~/Downloads (or configured folder) for new files
    2. Waits for downloads to complete (debounce prevents moving incomplete files)
    3. Moves files to category subfolders based on file extension
    4. Shows status in system tray with quick access to recent files

Usage:
    python app.py
"""

import platform
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Optional

import yaml
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# =============================================================================
# CONFIGURATION
# =============================================================================

CONFIG_PATH = Path(__file__).parent / "config.yaml"


def load_config() -> dict:
    """
    Load configuration from config.yaml.

    Returns:
        dict: Configuration with watch_folder, debounce_seconds, and categories
    """
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def build_extension_map(categories: dict) -> dict[str, str]:
    """
    Build a reverse lookup map from file extension to category name.

    Args:
        categories: Dict mapping category names to lists of extensions
                   e.g., {"Images": [".jpg", ".png"], "Documents": [".pdf"]}

    Returns:
        Dict mapping extensions to category names
        e.g., {".jpg": "Images", ".png": "Images", ".pdf": "Documents"}
    """
    ext_map = {}
    for category, extensions in categories.items():
        for ext in extensions:
            ext_map[ext.lower()] = category
    return ext_map


# =============================================================================
# FILE SYSTEM WATCHER
# =============================================================================

class DownloadHandler(FileSystemEventHandler):
    """
    Watches for new files and moves them to appropriate category folders.

    Uses debouncing to wait for downloads to complete before moving files.
    This prevents moving partially downloaded files.

    Attributes:
        watch_folder: The folder being monitored (e.g., ~/Downloads)
        ext_map: Maps file extensions to category names
        debounce: Seconds to wait after last file modification
        pending: Files waiting to be moved {path: last_modified_time}
        on_file_moved: Callback function when a file is moved
    """

    def __init__(
        self,
        watch_folder: Path,
        ext_map: dict[str, str],
        debounce: float,
        on_file_moved: Optional[callable] = None
    ):
        """
        Initialize the download handler.

        Args:
            watch_folder: Directory to monitor for new files
            ext_map: Mapping of file extensions to category names
            debounce: Seconds to wait for file to stabilize before moving
            on_file_moved: Optional callback(dest_path, category) when file is moved
        """
        self.watch_folder = watch_folder
        self.ext_map = ext_map
        self.debounce = debounce
        self.on_file_moved = on_file_moved
        self.pending: dict[Path, float] = {}

    def on_created(self, event):
        """
        Called when a new file is created in the watch folder.

        Adds the file to pending list but doesn't move it yet.
        We wait for the debounce period to ensure download is complete.
        """
        if event.is_directory:
            return

        path = Path(event.src_path)

        # Only watch root of Downloads, ignore files in subfolders
        if path.parent != self.watch_folder:
            return

        # Ignore hidden files (like .DS_Store, .crdownload, etc.)
        if path.name.startswith("."):
            return

        self.pending[path] = time.time()

    def on_modified(self, event):
        """
        Called when a file is modified.

        Resets the debounce timer for pending files.
        This ensures we wait for downloads to fully complete.
        """
        if event.is_directory:
            return

        path = Path(event.src_path)
        if path in self.pending:
            self.pending[path] = time.time()

    def process_pending(self):
        """
        Move files that have been stable for the debounce period.

        Called periodically to check if any pending files are ready to move.
        A file is ready when it hasn't been modified for `debounce` seconds.
        """
        now = time.time()
        to_remove = []

        for path, last_modified in list(self.pending.items()):
            # Skip if file was recently modified (still downloading)
            if now - last_modified < self.debounce:
                continue

            to_remove.append(path)

            if not path.exists():
                continue

            self.move_file(path)

        # Clean up processed files from pending list
        for path in to_remove:
            self.pending.pop(path, None)

    def move_file(self, path: Path):
        """
        Move a file to its appropriate category folder.

        Args:
            path: Path to the file to move

        The destination folder is determined by the file's extension.
        If no matching category is found, the file goes to "Other".
        Duplicate filenames are handled by appending _1, _2, etc.
        """
        ext = path.suffix.lower()
        category = self.ext_map.get(ext, "Other")
        dest_folder = self.watch_folder / category

        # Create category folder if it doesn't exist
        dest_folder.mkdir(exist_ok=True)
        dest_path = dest_folder / path.name

        # Handle duplicate filenames: file.pdf -> file_1.pdf -> file_2.pdf
        if dest_path.exists():
            stem = path.stem
            counter = 1
            while dest_path.exists():
                dest_path = dest_folder / f"{stem}_{counter}{ext}"
                counter += 1

        # Move the file
        shutil.move(str(path), str(dest_path))

        # Notify callback if provided
        if self.on_file_moved:
            self.on_file_moved(dest_path, category)


class Boop:
    """
    Core Boop functionality - cross-platform file organizer.

    This class handles the file watching and organization logic.
    Platform-specific UI (menu bar / system tray) is handled separately.

    Attributes:
        config: Loaded configuration from config.yaml
        watch_folder: Folder being monitored
        handler: FileSystemEventHandler for watching files
        observer: Watchdog observer running in background
        last_file: Most recently organized file
        on_file_moved: Callback when a file is organized
    """

    def __init__(self, on_file_moved: Optional[callable] = None):
        """
        Initialize Boop.

        Args:
            on_file_moved: Optional callback(path, category) when file is moved
        """
        self.config = load_config()
        self.watch_folder = Path(self.config["watch_folder"]).expanduser()
        self.on_file_moved = on_file_moved
        self.last_file: Optional[Path] = None
        self.observer: Optional[Observer] = None
        self.handler: Optional[DownloadHandler] = None
        self._running = False

    def start(self):
        """Start watching for new downloads."""
        ext_map = build_extension_map(self.config["categories"])
        debounce = self.config.get("debounce_seconds", 2)

        def file_moved_callback(path, category):
            self.last_file = path
            if self.on_file_moved:
                self.on_file_moved(path, category)

        self.handler = DownloadHandler(
            self.watch_folder,
            ext_map,
            debounce,
            file_moved_callback
        )

        self.observer = Observer()
        self.observer.schedule(self.handler, str(self.watch_folder), recursive=False)
        self.observer.start()
        self._running = True

        # Start background thread to process pending files
        def process_loop():
            while self._running:
                if self.handler:
                    self.handler.process_pending()
                time.sleep(1)

        thread = threading.Thread(target=process_loop, daemon=True)
        thread.start()

    def stop(self):
        """Stop watching for downloads."""
        self._running = False
        if self.observer:
            self.observer.stop()
            self.observer.join()

    def reorganize_all(self) -> int:
        """
        Organize all existing files in the Downloads folder.

        Returns:
            Number of files organized
        """
        ext_map = build_extension_map(self.config["categories"])
        count = 0

        for path in self.watch_folder.iterdir():
            # Skip folders and hidden files
            if path.is_dir() or path.name.startswith("."):
                continue

            ext = path.suffix.lower()
            category = ext_map.get(ext, "Other")
            dest_folder = self.watch_folder / category

            dest_folder.mkdir(exist_ok=True)
            dest_path = dest_folder / path.name

            # Handle duplicates
            if dest_path.exists():
                stem = path.stem
                counter = 1
                while dest_path.exists():
                    dest_path = dest_folder / f"{stem}_{counter}{ext}"
                    counter += 1

            shutil.move(str(path), str(dest_path))
            count += 1

            self.last_file = dest_path
            if self.on_file_moved:
                self.on_file_moved(dest_path, category)

        return count

    def open_last_file(self):
        """Open the last organized file in the system file manager."""
        if self.last_file and self.last_file.exists():
            open_in_file_manager(self.last_file)

    def open_downloads_folder(self):
        """Open the Downloads folder in the system file manager."""
        open_in_file_manager(self.watch_folder)


# =============================================================================
# CROSS-PLATFORM UTILITIES
# =============================================================================

def get_platform() -> str:
    """
    Get the current platform.

    Returns:
        'macos', 'windows', or 'linux'
    """
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    elif system == "windows":
        return "windows"
    else:
        return "linux"


def open_in_file_manager(path: Path):
    """
    Open a file or folder in the system's file manager.

    Args:
        path: Path to file or folder to reveal

    On macOS: Opens Finder and selects the file
    On Windows: Opens Explorer and selects the file
    On Linux: Opens the default file manager
    """
    system = get_platform()

    if system == "macos":
        subprocess.run(["open", "-R", str(path)])
    elif system == "windows":
        subprocess.run(["explorer", "/select,", str(path)])
    else:  # Linux
        subprocess.run(["xdg-open", str(path.parent)])


def send_notification(title: str, message: str):
    """
    Send a system notification.

    Args:
        title: Notification title
        message: Notification body text
    """
    system = get_platform()

    if system == "macos":
        # Use osascript for macOS notifications
        script = f'display notification "{message}" with title "{title}"'
        subprocess.run(["osascript", "-e", script])
    elif system == "windows":
        # Use PowerShell for Windows notifications
        try:
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast(title, message, duration=3)
        except ImportError:
            pass  # win10toast not installed
    else:  # Linux
        subprocess.run(["notify-send", title, message])


# =============================================================================
# PLATFORM-SPECIFIC UI
# =============================================================================

def run_macos():
    """Run Boop with macOS menu bar UI using rumps."""
    import rumps

    class BoopApp(rumps.App):
        def __init__(self):
            super().__init__("✨", quit_button=None)

            self.boop = Boop(on_file_moved=self.on_file_moved)

            # Build menu
            self.status_item = rumps.MenuItem("✓ Monitoring Downloads")
            self.status_item.set_callback(None)

            self.last_file_item = rumps.MenuItem("No recent files")
            self.last_file_item.set_callback(self.open_last_file)

            self.reorganize_item = rumps.MenuItem("🔄 Reorganize Now")
            self.reorganize_item.set_callback(self.reorganize_all)

            self.open_downloads = rumps.MenuItem("Open Downloads Folder")
            self.open_downloads.set_callback(self.open_downloads_folder)

            self.menu = [
                self.status_item,
                None,
                self.last_file_item,
                None,
                self.reorganize_item,
                self.open_downloads,
                None,
                rumps.MenuItem("Quit", callback=self.quit_app),
            ]

            self.boop.start()

        def on_file_moved(self, path: Path, category: str):
            """Called when a file is organized."""
            name = path.name if len(path.name) <= 30 else path.name[:27] + "..."
            self.last_file_item.title = f"📄 {name} → {category}"

            # Flash icon
            self.title = "🪄"
            rumps.Timer(lambda _: setattr(self, 'title', '✨'), 2).start()

        def open_last_file(self, _):
            self.boop.open_last_file()

        def open_downloads_folder(self, _):
            self.boop.open_downloads_folder()

        def reorganize_all(self, _):
            count = self.boop.reorganize_all()
            rumps.notification("Boop", "", f"Booped {count} file(s) ✨")

        def quit_app(self, _):
            self.boop.stop()
            rumps.quit_application()

    BoopApp().run()


def run_windows_linux():
    """Run Boop with Windows/Linux system tray UI using pystray."""
    from PIL import Image, ImageDraw
    import pystray

    # Create a simple icon (purple circle with star)
    def create_icon():
        size = 64
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        # Purple circle
        draw.ellipse([4, 4, size-4, size-4], fill=(138, 79, 255))
        # White star in center
        center = size // 2
        points = []
        for i in range(5):
            import math
            angle = math.radians(i * 72 - 90)
            points.append((center + 15 * math.cos(angle), center + 15 * math.sin(angle)))
            angle = math.radians(i * 72 - 90 + 36)
            points.append((center + 7 * math.cos(angle), center + 7 * math.sin(angle)))
        draw.polygon(points, fill=(255, 255, 255))
        return img

    boop = Boop()
    last_file_text = "No recent files"

    def on_file_moved(path: Path, category: str):
        nonlocal last_file_text
        name = path.name if len(path.name) <= 30 else path.name[:27] + "..."
        last_file_text = f"{name} → {category}"
        send_notification("Boop", f"Booped: {name} → {category}")

    boop.on_file_moved = on_file_moved
    boop.start()

    def open_last(icon, item):
        boop.open_last_file()

    def open_downloads(icon, item):
        boop.open_downloads_folder()

    def reorganize(icon, item):
        count = boop.reorganize_all()
        send_notification("Boop", f"Booped {count} file(s) ✨")

    def quit_app(icon, item):
        boop.stop()
        icon.stop()

    menu = pystray.Menu(
        pystray.MenuItem("✓ Monitoring Downloads", lambda: None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(lambda text: last_file_text, open_last),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Reorganize Now", reorganize),
        pystray.MenuItem("Open Downloads Folder", open_downloads),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", quit_app),
    )

    icon = pystray.Icon("Boop", create_icon(), "Boop ✨", menu)
    icon.run()


def main():
    """
    Main entry point - automatically selects the right UI for the platform.
    """
    system = get_platform()

    print("✨ Boop is starting...")
    print(f"   Platform: {system}")
    print(f"   Watching: {Path(load_config()['watch_folder']).expanduser()}")
    print()

    if system == "macos":
        run_macos()
    else:
        run_windows_linux()


if __name__ == "__main__":
    main()

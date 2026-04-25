import os
import sys
from pathlib import Path


PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = PACKAGE_DIR.parent


def _data_dir() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        return base / "healthy_pet"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "healthy_pet"
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "healthy_pet"


def _assets_dir() -> Path:
    packaged = PACKAGE_DIR / "res"
    if packaged.exists():
        return packaged
    return PROJECT_DIR / "res"


DATA_DIR = _data_dir()
LEGACY_DATA_DIR = PROJECT_DIR / "data"
ASSETS_DIR = _assets_dir()
ICON_PATH = ASSETS_DIR / "icons" / "icon.png"
NOTIFICATION_SOUND_PATH = ASSETS_DIR / "sounds" / "Notification.wav"
KITTY_ACTION_DIR = ASSETS_DIR / "role" / "Kitty" / "action"

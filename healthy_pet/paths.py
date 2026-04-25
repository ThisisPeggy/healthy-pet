from pathlib import Path


PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = PACKAGE_DIR.parent
DATA_DIR = PROJECT_DIR / "data"
ASSETS_DIR = PROJECT_DIR / "res"
ICON_PATH = ASSETS_DIR / "icons" / "icon.png"
NOTIFICATION_SOUND_PATH = ASSETS_DIR / "sounds" / "Notification.wav"
KITTY_ACTION_DIR = ASSETS_DIR / "role" / "Kitty" / "action"

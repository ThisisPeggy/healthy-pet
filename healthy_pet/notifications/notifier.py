from __future__ import annotations

from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtWidgets import QApplication, QSystemTrayIcon

from healthy_pet.paths import NOTIFICATION_SOUND_PATH
from healthy_pet.settings import HealthSettings


class Notifier:
    def __init__(self, tray: QSystemTrayIcon, settings: HealthSettings):
        self.tray = tray
        self.settings = settings
        self.sound = QSoundEffect()
        if NOTIFICATION_SOUND_PATH.exists():
            self.sound.setSource(QUrl.fromLocalFile(str(NOTIFICATION_SOUND_PATH)))
            self.sound.setVolume(0.8)

    def apply_settings(self, settings: HealthSettings) -> None:
        self.settings = settings

    def show(self, title: str, message: str, kind: str | None = None) -> None:
        if self._should_play_sound(kind):
            if self.sound.source().isValid():
                self.sound.play()
            else:
                QApplication.beep()

    def _should_play_sound(self, kind: str | None) -> bool:
        if not self.settings.sound_enabled:
            return False
        if kind == "eye":
            return self.settings.sound_eye_enabled
        if kind == "standing":
            return self.settings.sound_standing_enabled
        if kind == "sleep":
            return self.settings.sound_sleep_enabled
        return True

from __future__ import annotations

from PySide6.QtWidgets import QApplication, QSystemTrayIcon

from healthy_pet.settings import HealthSettings


class Notifier:
    def __init__(self, tray: QSystemTrayIcon, settings: HealthSettings):
        self.tray = tray
        self.settings = settings

    def apply_settings(self, settings: HealthSettings) -> None:
        self.settings = settings

    def show(self, title: str, message: str) -> None:
        if self.settings.sound_enabled:
            QApplication.beep()
        if self.tray.isVisible():
            icon = getattr(QSystemTrayIcon, "Information", QSystemTrayIcon.MessageIcon.Information)
            self.tray.showMessage(title, message, icon, 8000)

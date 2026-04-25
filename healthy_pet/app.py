from __future__ import annotations

import sys

from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from healthy_pet.i18n import get_i18n
from healthy_pet.notifications.notifier import Notifier
from healthy_pet.paths import ICON_PATH
from healthy_pet.pet.window import PetWindow
from healthy_pet.reminders.activity import ActivityTracker
from healthy_pet.reminders.engine import Reminder, ReminderController
from healthy_pet.startup import set_startup_enabled
from healthy_pet.settings import HealthSettings, SettingsStore
from healthy_pet.ui.settings_window import SettingsWindow


class HealthyPetApplication(QApplication):
    def __init__(self, argv: list[str]):
        super().__init__(argv)
        self.setQuitOnLastWindowClosed(False)

        self.i18n = get_i18n()
        self.settings_store = SettingsStore()
        self.settings = self.settings_store.load()
        self.settings_window: SettingsWindow | None = None

        self.tray = self._create_tray()
        self.notifier = Notifier(self.tray, self.settings)
        self.activity = ActivityTracker(self)
        self.activity.start()
        self.pet = PetWindow(self.settings)
        self.controller = ReminderController(self.settings, self.activity, self)
        self._sync_startup()

        self.pet.acknowledged.connect(self.controller.acknowledge)
        self.pet.test_reminder_requested.connect(self.controller.trigger_test)
        self.pet.reset_work_timer_requested.connect(self.controller.reset_work_session)
        self.pet.request_settings.connect(self.show_settings)
        self.pet.request_quit.connect(self.quit_app)
        self.pet.language_changed.connect(self.on_language_changed)
        self.controller.reminder_triggered.connect(self._show_reminder)
        self.controller.reminder_updated.connect(self._update_reminder)
        self.controller.reminder_hidden.connect(self._hide_reminder)
        self.controller.reminder_cleared.connect(self.pet.clear_reminder)

    def show_settings(self) -> None:
        if self.settings_window is None:
            self.settings_window = SettingsWindow(self.settings)
            self.settings_window.settings_saved.connect(self.apply_settings)
        else:
            self.settings_window.set_settings(self.settings)
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()

    def apply_settings(self, settings: HealthSettings) -> None:
        self.settings = settings
        self.settings_store.save(settings)
        self.notifier.apply_settings(settings)
        self.pet.apply_settings(settings)
        self.controller.apply_settings(settings)
        self._sync_startup()

    def on_language_changed(self) -> None:
        """语言改变时更新界面"""
        self._update_tray_menu()
        self.pet.update_language()

    def quit_app(self) -> None:
        self.activity.stop()
        self.tray.hide()
        self.pet.close()
        sys.exit(0)

    def _show_reminder(self, reminder: Reminder) -> None:
        self.pet.show_reminder(reminder.message, reminder.action)
        self.notifier.show(reminder.title, reminder.message, reminder.kind)

    def _update_reminder(self, reminder: Reminder) -> None:
        self.pet.update_reminder(reminder.message)

    def _hide_reminder(self, kind: str) -> None:
        if kind == "sleep":
            self.pet.hide_bubble_keep_action()
        else:
            self.pet.clear_reminder()

    def _create_tray(self) -> QSystemTrayIcon:
        tray = QSystemTrayIcon(QIcon(str(ICON_PATH)), self)
        tray.setToolTip(self.i18n.t("tray.title"))
        tray.show()
        self.tray = tray  # 先赋值
        self._update_tray_menu()  # 再更新菜单
        return tray

    def _update_tray_menu(self) -> None:
        """更新托盘菜单（用于语言切换）"""
        self.tray_menu = QMenu()
        self.tray_menu.setStyleSheet(
            """
            QMenu {
                text-align: left;
            }
            QMenu::item {
                padding: 5px 20px 5px 12px;
                text-align: left;
            }
            """
        )

        settings_action = QAction(self.i18n.t("menu.settings"), self)
        reset_work_action = QAction(self.i18n.t("menu.reset_timer"), self)
        quit_action = QAction(self.i18n.t("menu.quit"), self)

        settings_action.triggered.connect(self.show_settings)
        reset_work_action.triggered.connect(self._reset_work_from_menu)
        quit_action.triggered.connect(self.quit_app)

        self.tray_menu.addAction(settings_action)
        self.tray_menu.addAction(reset_work_action)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(quit_action)
        self.tray.setContextMenu(self.tray_menu)

    def _reset_work_from_menu(self) -> None:
        self.controller.reset_work_session()

    def _sync_startup(self) -> None:
        set_startup_enabled(self.settings.start_on_boot)

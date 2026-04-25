from __future__ import annotations

from PySide6.QtCore import QTime, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QSpinBox,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from healthy_pet.i18n import get_i18n
from healthy_pet.settings import HealthSettings


class SettingsWindow(QDialog):
    settings_saved = Signal(object)

    def __init__(self, settings: HealthSettings, parent=None):
        super().__init__(parent)
        self.i18n = get_i18n()
        self.setWindowTitle(self.i18n.t("settings.title"))
        self.setMinimumWidth(560)

        self.enabled_check = QCheckBox(self.i18n.t("settings.enabled"))
        self.start_on_boot_check = QCheckBox(self.i18n.t("settings.start_on_boot"))
        self.eye_spin = QSpinBox()
        self.eye_spin.setRange(1, 180)
        self.eye_spin.setSuffix(" " + ("分钟" if self.i18n.get_language() == "zh_CN" else "min"))
        self.eye_message_edit = QLineEdit()
        self.eye_message_edit.setMinimumWidth(260)
        self.eye_message_edit.setPlaceholderText(self.i18n.t("message.eye.default"))
        self.eye_rest_spin = QSpinBox()
        self.eye_rest_spin.setRange(5, 300)
        self.eye_rest_spin.setSuffix(" " + ("秒" if self.i18n.get_language() == "zh_CN" else "s"))
        self.standing_spin = QSpinBox()
        self.standing_spin.setRange(5, 360)
        self.standing_spin.setSuffix(" " + ("分钟" if self.i18n.get_language() == "zh_CN" else "min"))
        self.standing_message_edit = QLineEdit()
        self.standing_message_edit.setMinimumWidth(260)
        self.standing_message_edit.setPlaceholderText(self.i18n.t("message.standing.default"))
        self.standing_break_spin = QSpinBox()
        self.standing_break_spin.setRange(1, 60)
        self.standing_break_spin.setSuffix(" " + ("分钟" if self.i18n.get_language() == "zh_CN" else "min"))
        self.idle_spin = QSpinBox()
        self.idle_spin.setRange(1, 60)
        self.idle_spin.setSuffix(" " + ("分钟" if self.i18n.get_language() == "zh_CN" else "min"))
        self.sleep_time = QTimeEdit()
        self.sleep_time.setDisplayFormat("HH:mm")
        self.sleep_message_edit = QLineEdit()
        self.sleep_message_edit.setMinimumWidth(260)
        self.sleep_message_edit.setPlaceholderText(self.i18n.t("message.sleep.default"))
        self.sound_check = QCheckBox(self.i18n.t("settings.sound"))
        self.sound_eye_check = QCheckBox(self.i18n.t("settings.sound_eye"))
        self.sound_standing_check = QCheckBox(self.i18n.t("settings.sound_standing"))
        self.sound_sleep_check = QCheckBox(self.i18n.t("settings.sound_sleep"))
        self.sound_options = QWidget()
        sound_layout = QHBoxLayout(self.sound_options)
        sound_layout.setContentsMargins(0, 0, 0, 0)
        sound_layout.setSpacing(14)
        sound_layout.addWidget(self.sound_eye_check)
        sound_layout.addWidget(self.sound_standing_check)
        sound_layout.addWidget(self.sound_sleep_check)
        sound_layout.addStretch(1)
        self.sound_check.toggled.connect(self.sound_options.setEnabled)
        self.top_check = QCheckBox(self.i18n.t("settings.always_on_top"))
        self.scale_spin = QDoubleSpinBox()
        self.scale_spin.setRange(0.5, 3.0)
        self.scale_spin.setSingleStep(0.1)
        
        # 语言选择
        self.language_combo = QComboBox()
        self.language_combo.addItem("中文", "zh_CN")
        self.language_combo.addItem("English", "en_US")
        current_lang = self.i18n.get_language()
        index = self.language_combo.findData(current_lang)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
        self.language_combo.currentIndexChanged.connect(self._on_language_changed)

        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(10)
        form.addRow("", self.enabled_check)
        form.addRow("", self.start_on_boot_check)
        form.addRow(self.i18n.t("settings.eye_interval"), self.eye_spin)
        form.addRow(self.i18n.t("settings.eye_message"), self.eye_message_edit)
        form.addRow(self.i18n.t("settings.eye_rest"), self.eye_rest_spin)
        form.addRow(self.i18n.t("settings.standing_interval"), self.standing_spin)
        form.addRow(self.i18n.t("settings.standing_message"), self.standing_message_edit)
        form.addRow(self.i18n.t("settings.standing_break"), self.standing_break_spin)
        form.addRow(self.i18n.t("settings.idle_reset"), self.idle_spin)
        form.addRow(self.i18n.t("settings.sleep_time"), self.sleep_time)
        form.addRow(self.i18n.t("settings.sleep_message"), self.sleep_message_edit)
        form.addRow("", self.sound_check)
        form.addRow(self.i18n.t("settings.sound_options"), self.sound_options)
        form.addRow("", self.top_check)
        form.addRow(self.i18n.t("settings.pet_scale"), self.scale_spin)
        form.addRow(self.i18n.t("settings.language"), self.language_combo)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.buttons.button(QDialogButtonBox.Save).setText(self.i18n.t("settings.save"))
        self.buttons.button(QDialogButtonBox.Cancel).setText(self.i18n.t("settings.cancel"))
        self.buttons.accepted.connect(self._save)
        self.buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self.buttons)

        self.set_settings(settings)

    def set_settings(self, settings: HealthSettings) -> None:
        self.enabled_check.setChecked(settings.enabled)
        self.start_on_boot_check.setChecked(settings.start_on_boot)
        self.eye_spin.setValue(settings.eye_interval_minutes)
        self.eye_message_edit.setText(settings.eye_message)
        self.eye_rest_spin.setValue(settings.eye_rest_seconds)
        self.standing_spin.setValue(settings.standing_interval_minutes)
        self.standing_message_edit.setText(settings.standing_message)
        self.standing_break_spin.setValue(settings.standing_break_minutes)
        self.idle_spin.setValue(settings.idle_reset_minutes)
        self.sleep_time.setTime(QTime(settings.sleep_hour, settings.sleep_minute))
        self.sleep_message_edit.setText(settings.sleep_message)
        self.sound_check.setChecked(settings.sound_enabled)
        self.sound_eye_check.setChecked(settings.sound_eye_enabled)
        self.sound_standing_check.setChecked(settings.sound_standing_enabled)
        self.sound_sleep_check.setChecked(settings.sound_sleep_enabled)
        self.sound_options.setEnabled(settings.sound_enabled)
        self.top_check.setChecked(settings.always_on_top)
        self.scale_spin.setValue(settings.pet_scale)

    def _on_language_changed(self, index: int) -> None:
        """语言改变时保存语言设置"""
        language = self.language_combo.itemData(index)
        if language and language != self.i18n.get_language():
            self.i18n.save_language(language)
            # 通知用户需要重新打开设置窗口
            from PySide6.QtWidgets import QMessageBox
            if self.i18n.get_language() == "zh_CN":
                QMessageBox.information(self, "语言已更改", "语言设置已保存。请重新打开设置窗口查看效果。")
            else:
                QMessageBox.information(self, "Language Changed", "Language setting saved. Please reopen settings to see the changes.")
            self.reject()
    
    def _save(self) -> None:
        sleep_time = self.sleep_time.time()
        settings = HealthSettings(
            enabled=self.enabled_check.isChecked(),
            start_on_boot=self.start_on_boot_check.isChecked(),
            eye_interval_minutes=self.eye_spin.value(),
            eye_message=self.eye_message_edit.text(),
            eye_rest_seconds=self.eye_rest_spin.value(),
            standing_interval_minutes=self.standing_spin.value(),
            standing_message=self.standing_message_edit.text(),
            standing_break_minutes=self.standing_break_spin.value(),
            idle_reset_minutes=self.idle_spin.value(),
            sleep_hour=sleep_time.hour(),
            sleep_minute=sleep_time.minute(),
            sleep_message=self.sleep_message_edit.text(),
            sleep_idle_clear_minutes=60,
            sound_enabled=self.sound_check.isChecked(),
            sound_eye_enabled=self.sound_eye_check.isChecked(),
            sound_standing_enabled=self.sound_standing_check.isChecked(),
            sound_sleep_enabled=self.sound_sleep_check.isChecked(),
            always_on_top=self.top_check.isChecked(),
            pet_scale=self.scale_spin.value(),
        )
        self.settings_saved.emit(settings)
        self.accept()

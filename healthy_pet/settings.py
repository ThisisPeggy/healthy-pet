from __future__ import annotations

import json
from dataclasses import asdict, dataclass, fields
from typing import Any

from .paths import DATA_DIR, LEGACY_DATA_DIR


SETTINGS_FILE = DATA_DIR / "healthy_settings.json"
LEGACY_SETTINGS_FILE = LEGACY_DATA_DIR / "healthy_settings.json"


@dataclass
class HealthSettings:
    enabled: bool = True
    start_on_boot: bool = True
    eye_interval_minutes: int = 20
    eye_message: str = "看看远处吧"
    eye_rest_seconds: int = 20
    standing_interval_minutes: int = 60
    standing_message: str = "已经工作很久了，站起来活动一下吧。"
    standing_break_minutes: int = 5
    idle_reset_minutes: int = 5
    sleep_hour: int = 23
    sleep_minute: int = 30
    sleep_message: str = "主人不要熬夜哦，跟我一起睡觉吧。"
    sleep_idle_clear_minutes: int = 60
    sound_enabled: bool = True
    sound_eye_enabled: bool = True
    sound_standing_enabled: bool = True
    sound_sleep_enabled: bool = True
    always_on_top: bool = True
    pet_scale: float = 1.0


def _field_names() -> set[str]:
    return {field.name for field in fields(HealthSettings)}


def _coerce_settings(raw: dict[str, Any]) -> HealthSettings:
    allowed = {key: value for key, value in raw.items() if key in _field_names()}
    settings = HealthSettings(**allowed)
    settings.eye_interval_minutes = max(1, min(180, int(settings.eye_interval_minutes)))
    settings.eye_message = str(settings.eye_message).strip() or HealthSettings.eye_message
    settings.eye_rest_seconds = max(5, min(300, int(settings.eye_rest_seconds)))
    settings.standing_interval_minutes = max(5, min(360, int(settings.standing_interval_minutes)))
    settings.standing_message = str(settings.standing_message).strip() or HealthSettings.standing_message
    settings.standing_break_minutes = max(1, min(60, int(settings.standing_break_minutes)))
    settings.idle_reset_minutes = max(1, min(60, int(settings.idle_reset_minutes)))
    settings.sleep_hour = max(0, min(23, int(settings.sleep_hour)))
    settings.sleep_minute = max(0, min(59, int(settings.sleep_minute)))
    settings.sleep_message = str(settings.sleep_message).strip() or HealthSettings.sleep_message
    settings.sleep_idle_clear_minutes = max(5, min(720, int(settings.sleep_idle_clear_minutes)))
    settings.pet_scale = max(0.5, min(3.0, float(settings.pet_scale)))
    return settings


class SettingsStore:
    def __init__(self, path=SETTINGS_FILE):
        self.path = path

    def load(self) -> HealthSettings:
        if not self.path.exists():
            if self.path == SETTINGS_FILE and LEGACY_SETTINGS_FILE.exists():
                try:
                    raw = json.loads(LEGACY_SETTINGS_FILE.read_text(encoding="utf-8"))
                    settings = _coerce_settings(raw)
                    self.save(settings)
                    return settings
                except (OSError, json.JSONDecodeError, TypeError, ValueError):
                    pass
            settings = HealthSettings()
            self.save(settings)
            return settings

        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            settings = HealthSettings()
            self.save(settings)
            return settings

        return _coerce_settings(raw)

    def save(self, settings: HealthSettings) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(asdict(settings), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

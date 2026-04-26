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


def _to_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off"}:
            return False
    if isinstance(value, (int, float)):
        return bool(value)
    return default


def _bounded_int(value: Any, default: int, minimum: int, maximum: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = default
    return max(minimum, min(maximum, number))


def _bounded_float(value: Any, default: float, minimum: float, maximum: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default
    return max(minimum, min(maximum, number))


def _message(value: Any, default: str) -> str:
    text = str(value).strip() if value is not None else ""
    return text or default


def _coerce_settings(raw: dict[str, Any]) -> HealthSettings:
    allowed = {key: value for key, value in raw.items() if key in _field_names()}
    settings = HealthSettings()
    settings.enabled = _to_bool(allowed.get("enabled", settings.enabled), settings.enabled)
    settings.start_on_boot = _to_bool(
        allowed.get("start_on_boot", settings.start_on_boot),
        settings.start_on_boot,
    )
    settings.eye_interval_minutes = _bounded_int(
        allowed.get("eye_interval_minutes", settings.eye_interval_minutes),
        settings.eye_interval_minutes,
        1,
        180,
    )
    settings.eye_message = _message(
        allowed.get("eye_message", settings.eye_message),
        HealthSettings.eye_message,
    )
    settings.eye_rest_seconds = _bounded_int(
        allowed.get("eye_rest_seconds", settings.eye_rest_seconds),
        settings.eye_rest_seconds,
        5,
        300,
    )
    settings.standing_interval_minutes = _bounded_int(
        allowed.get("standing_interval_minutes", settings.standing_interval_minutes),
        settings.standing_interval_minutes,
        5,
        360,
    )
    settings.standing_message = _message(
        allowed.get("standing_message", settings.standing_message),
        HealthSettings.standing_message,
    )
    settings.standing_break_minutes = _bounded_int(
        allowed.get("standing_break_minutes", settings.standing_break_minutes),
        settings.standing_break_minutes,
        1,
        60,
    )
    settings.idle_reset_minutes = _bounded_int(
        allowed.get("idle_reset_minutes", settings.idle_reset_minutes),
        settings.idle_reset_minutes,
        1,
        60,
    )
    settings.sleep_hour = _bounded_int(
        allowed.get("sleep_hour", settings.sleep_hour),
        settings.sleep_hour,
        0,
        23,
    )
    settings.sleep_minute = _bounded_int(
        allowed.get("sleep_minute", settings.sleep_minute),
        settings.sleep_minute,
        0,
        59,
    )
    settings.sleep_message = _message(
        allowed.get("sleep_message", settings.sleep_message),
        HealthSettings.sleep_message,
    )
    settings.sleep_idle_clear_minutes = _bounded_int(
        allowed.get("sleep_idle_clear_minutes", settings.sleep_idle_clear_minutes),
        settings.sleep_idle_clear_minutes,
        5,
        720,
    )
    settings.sound_enabled = _to_bool(
        allowed.get("sound_enabled", settings.sound_enabled),
        settings.sound_enabled,
    )
    settings.sound_eye_enabled = _to_bool(
        allowed.get("sound_eye_enabled", settings.sound_eye_enabled),
        settings.sound_eye_enabled,
    )
    settings.sound_standing_enabled = _to_bool(
        allowed.get("sound_standing_enabled", settings.sound_standing_enabled),
        settings.sound_standing_enabled,
    )
    settings.sound_sleep_enabled = _to_bool(
        allowed.get("sound_sleep_enabled", settings.sound_sleep_enabled),
        settings.sound_sleep_enabled,
    )
    settings.always_on_top = _to_bool(
        allowed.get("always_on_top", settings.always_on_top),
        settings.always_on_top,
    )
    settings.pet_scale = _bounded_float(
        allowed.get("pet_scale", settings.pet_scale),
        settings.pet_scale,
        0.5,
        3.0,
    )
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

        try:
            return _coerce_settings(raw)
        except (TypeError, ValueError):
            settings = HealthSettings()
            self.save(settings)
            return settings

    def save(self, settings: HealthSettings) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(asdict(settings), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

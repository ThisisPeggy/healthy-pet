import json
import tempfile
import unittest
from pathlib import Path

from healthy_pet.settings import HealthSettings, SettingsStore, _coerce_settings


class SettingsCoercionTests(unittest.TestCase):
    def test_coerce_settings_clamps_and_falls_back_for_invalid_values(self) -> None:
        settings = _coerce_settings(
            {
                "enabled": "false",
                "start_on_boot": "yes",
                "eye_interval_minutes": "999",
                "eye_message": "   ",
                "eye_rest_seconds": "bad",
                "standing_interval_minutes": -1,
                "sleep_hour": 99,
                "sleep_minute": None,
                "sound_enabled": "off",
                "always_on_top": 0,
                "pet_scale": "9.5",
                "unknown": "ignored",
            }
        )

        self.assertFalse(settings.enabled)
        self.assertTrue(settings.start_on_boot)
        self.assertEqual(settings.eye_interval_minutes, 180)
        self.assertEqual(settings.eye_message, HealthSettings.eye_message)
        self.assertEqual(settings.eye_rest_seconds, HealthSettings.eye_rest_seconds)
        self.assertEqual(settings.standing_interval_minutes, 5)
        self.assertEqual(settings.sleep_hour, 23)
        self.assertEqual(settings.sleep_minute, HealthSettings.sleep_minute)
        self.assertFalse(settings.sound_enabled)
        self.assertFalse(settings.always_on_top)
        self.assertEqual(settings.pet_scale, 3.0)

    def test_store_recovers_from_invalid_json_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "settings.json"
            path.write_text(
                json.dumps({"eye_interval_minutes": {"not": "a number"}}),
                encoding="utf-8",
            )

            settings = SettingsStore(path).load()

        self.assertEqual(settings.eye_interval_minutes, HealthSettings.eye_interval_minutes)

    def test_store_save_creates_custom_parent_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "nested" / "settings.json"

            SettingsStore(path).save(HealthSettings(enabled=False))

            data = json.loads(path.read_text(encoding="utf-8"))

        self.assertFalse(data["enabled"])


if __name__ == "__main__":
    unittest.main()

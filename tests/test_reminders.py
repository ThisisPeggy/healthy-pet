import unittest
from datetime import date
from unittest.mock import patch

from PySide6.QtCore import QCoreApplication

from healthy_pet.reminders.engine import ReminderController
from healthy_pet.settings import HealthSettings


class FakeActivity:
    def __init__(self, idle_seconds: float = 0.0):
        self.idle_seconds = idle_seconds

    def is_recently_active(self, window_seconds: int = 5) -> bool:
        return self.idle_seconds <= window_seconds

    def seconds_since_input(self) -> float:
        return self.idle_seconds


class ReminderControllerTests(unittest.TestCase):
    app: QCoreApplication | None = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QCoreApplication.instance() or QCoreApplication([])

    def make_controller(
        self,
        settings: HealthSettings | None = None,
        activity: FakeActivity | None = None,
    ) -> ReminderController:
        settings = settings or HealthSettings(sleep_hour=0, sleep_minute=0)
        controller = ReminderController(settings, activity or FakeActivity())
        controller.timer.stop()
        return controller

    def test_sleep_reminder_only_triggers_once_per_date(self) -> None:
        controller = self.make_controller()

        first = controller._next_reminder(0.0)
        second = controller._next_reminder(0.0)

        self.assertIsNotNone(first)
        self.assertEqual(first.kind, "sleep")
        self.assertIsNone(second)

    def test_sleep_reminder_can_trigger_again_on_new_date(self) -> None:
        controller = self.make_controller()
        controller.last_sleep_reminder_date = date(2000, 1, 1)

        reminder = controller._next_reminder(0.0)

        self.assertIsNotNone(reminder)
        self.assertEqual(reminder.kind, "sleep")

    def test_format_seconds(self) -> None:
        self.assertEqual(ReminderController._format_seconds(65), "01:05")
        self.assertEqual(ReminderController._format_seconds(-1), "00:00")

    def test_eye_reminder_takes_priority_over_standing(self) -> None:
        settings = HealthSettings(
            sleep_hour=23,
            sleep_minute=59,
            eye_interval_minutes=20,
            standing_interval_minutes=60,
        )
        controller = self.make_controller(settings=settings)
        controller.active_session_seconds = 60 * 60

        reminder = controller._next_reminder(100.0)

        self.assertIsNotNone(reminder)
        self.assertEqual(reminder.kind, "eye")

    def test_tick_resets_work_session_after_idle_threshold(self) -> None:
        activity = FakeActivity(idle_seconds=10 * 60)
        controller = self.make_controller(
            settings=HealthSettings(sleep_hour=23, sleep_minute=59, idle_reset_minutes=5),
            activity=activity,
        )
        controller.active_session_seconds = 1200.0
        controller.last_eye_reminder_seconds = 600.0
        controller.last_standing_reminder_seconds = 600.0

        controller.tick()

        self.assertEqual(controller.active_session_seconds, 0.0)
        self.assertEqual(controller.last_eye_reminder_seconds, 0.0)
        self.assertEqual(controller.last_standing_reminder_seconds, 0.0)

    def test_acknowledging_standing_starts_break_countdown(self) -> None:
        controller = self.make_controller(
            settings=HealthSettings(sleep_hour=23, sleep_minute=59, standing_break_minutes=5)
        )
        controller.current_reminder = controller._standing_waiting_reminder()
        controller.reminder_phase = "waiting"

        controller.acknowledge()

        self.assertEqual(controller.reminder_phase, "running")
        self.assertIsNotNone(controller.current_reminder)
        self.assertEqual(controller.current_reminder.phase, "running")

    def test_standing_break_completion_clears_current_reminder(self) -> None:
        controller = self.make_controller(
            settings=HealthSettings(sleep_hour=23, sleep_minute=59, standing_break_minutes=1)
        )
        controller._start_standing_break()

        controller._tick_standing_break(controller.break_started_ts + 61)

        self.assertIsNone(controller.current_reminder)
        self.assertEqual(controller.reminder_phase, "idle")

    def test_eye_rest_activity_restarts_countdown(self) -> None:
        activity = FakeActivity(idle_seconds=0)
        controller = self.make_controller(
            settings=HealthSettings(sleep_hour=23, sleep_minute=59, eye_rest_seconds=20),
            activity=activity,
        )
        controller.eye_rest_started_ts = 100.0
        controller.current_reminder = controller._eye_running_reminder(100.0)
        controller.reminder_phase = "running"

        controller._tick_eye_rest(110.0)

        self.assertEqual(controller.eye_rest_started_ts, 110.0)
        self.assertIsNotNone(controller.current_reminder)

    def test_sleep_reminder_hides_after_idle_threshold(self) -> None:
        activity = FakeActivity(idle_seconds=61 * 60)
        controller = self.make_controller(
            settings=HealthSettings(sleep_idle_clear_minutes=60),
            activity=activity,
        )
        controller.current_reminder = controller._sleep_reminder()
        hidden: list[str] = []
        controller.reminder_hidden.connect(hidden.append)

        controller._tick_sleep()

        self.assertIsNone(controller.current_reminder)
        self.assertEqual(controller.reminder_phase, "sleeping")
        self.assertTrue(controller.sleeping_after_idle)
        self.assertEqual(hidden, ["sleep"])

    def test_sleeping_after_idle_clears_when_user_returns(self) -> None:
        activity = FakeActivity(idle_seconds=0)
        controller = self.make_controller(activity=activity)
        controller.sleeping_after_idle = True
        cleared = []
        controller.reminder_cleared.connect(lambda: cleared.append(True))

        controller.tick()

        self.assertFalse(controller.sleeping_after_idle)
        self.assertEqual(cleared, [True])

    def test_tick_accumulates_active_session_time(self) -> None:
        controller = self.make_controller(settings=HealthSettings(sleep_hour=23, sleep_minute=59))
        controller.last_loop_ts = 10.0
        with patch("healthy_pet.reminders.engine.time.monotonic", return_value=15.5):
            controller.tick()

        self.assertEqual(controller.active_session_seconds, 5.5)


if __name__ == "__main__":
    unittest.main()

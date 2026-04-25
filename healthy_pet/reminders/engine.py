from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime

from PySide6.QtCore import QObject, QTimer, Signal

from healthy_pet.settings import HealthSettings

from .activity import ActivityTracker


@dataclass(frozen=True)
class Reminder:
    kind: str
    title: str
    message: str
    action: str
    phase: str = "waiting"


class ReminderController(QObject):
    reminder_triggered = Signal(object)
    reminder_updated = Signal(object)
    reminder_cleared = Signal()
    reminder_hidden = Signal(str)

    def __init__(self, settings: HealthSettings, activity: ActivityTracker, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.activity = activity
        self.current_reminder: Reminder | None = None
        self.reminder_phase = "idle"
        self.active_session_seconds = 0.0
        now = time.monotonic()
        self.last_eye_reminder_ts = now  # 初始化为当前时间，避免启动时立即触发
        self.last_standing_reminder_ts = now  # 初始化为当前时间，避免启动时立即触发
        self.last_loop_ts = now
        self.sleep_reminder_count = 0
        self.break_started_ts = 0.0
        self.eye_rest_started_ts = 0.0
        self.sleeping_after_idle = False

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(1000)

    def apply_settings(self, settings: HealthSettings) -> None:
        self.settings = settings

    def trigger_test(self, kind: str) -> None:
        self._clear_current(emit=False)
        self.sleeping_after_idle = False

        if kind == "standing":
            reminder = self._standing_waiting_reminder()
        elif kind == "eye":
            self.eye_rest_started_ts = time.monotonic()
            reminder = self._eye_running_reminder(self.eye_rest_started_ts)
        elif kind == "sleep":
            reminder = self._sleep_reminder()
        else:
            return

        self.current_reminder = reminder
        self.reminder_phase = reminder.phase
        self.reminder_triggered.emit(reminder)

    def reset_work_session(self) -> None:
        self.active_session_seconds = 0.0
        self.last_eye_reminder_ts = 0.0
        self.last_standing_reminder_ts = 0.0
        self._clear_current()

    def acknowledge(self) -> None:
        if self.sleeping_after_idle:
            self.sleeping_after_idle = False
            self.reminder_cleared.emit()
            return

        if self.current_reminder is None:
            return

        kind = self.current_reminder.kind
        if kind == "standing":
            if self.reminder_phase == "waiting":
                self._start_standing_break()
        elif kind == "sleep":
            # 睡眠提醒不响应确认，保持显示
            pass

    def tick(self) -> None:
        now = time.monotonic()
        elapsed = max(0.0, now - self.last_loop_ts)
        self.last_loop_ts = now

        if self.sleeping_after_idle:
            if self.activity.is_recently_active(window_seconds=5):
                self.sleeping_after_idle = False
                self.reminder_cleared.emit()
            return

        if self.current_reminder is not None:
            if self.current_reminder.kind == "standing" and self.reminder_phase == "running":
                self._tick_standing_break(now)
            elif self.current_reminder.kind == "eye" and self.reminder_phase == "running":
                self._tick_eye_rest(now)
            elif self.current_reminder.kind == "sleep":
                self._tick_sleep()
            return

        if self.activity.is_recently_active(window_seconds=300):
            self.active_session_seconds += elapsed
        elif self.activity.seconds_since_input() >= self.settings.idle_reset_minutes * 60:
            self.active_session_seconds = 0.0
            self.last_eye_reminder_ts = 0.0
            self.last_standing_reminder_ts = 0.0

        if not self.settings.enabled or self.current_reminder is not None:
            return

        reminder = self._next_reminder(now)
        if reminder is None:
            return

        self.current_reminder = reminder
        self.reminder_phase = reminder.phase
        if reminder.kind == "sleep":
            self.sleep_reminder_count += 1
        self.reminder_triggered.emit(reminder)

    def _next_reminder(self, now: float) -> Reminder | None:
        # 睡眠提醒：一旦触发就持续显示，不重复弹出
        if self._sleep_due(now):
            return self._sleep_reminder()

        # 护眼提醒优先（每20分钟）
        eye_elapsed = now - self.last_eye_reminder_ts
        if eye_elapsed >= self.settings.eye_interval_minutes * 60:
            self.eye_rest_started_ts = now
            self.last_eye_reminder_ts = now
            return self._eye_running_reminder(now)

        # 久坐提醒（每60分钟）
        standing_elapsed = now - self.last_standing_reminder_ts
        if standing_elapsed >= self.settings.standing_interval_minutes * 60:
            self.last_standing_reminder_ts = now
            return self._standing_waiting_reminder()

        return None

    def _sleep_due(self, now: float) -> bool:
        # 如果已经在显示睡眠提醒，不重复触发
        if self.current_reminder is not None and self.current_reminder.kind == "sleep":
            return False
            
        if not self.activity.is_recently_active(window_seconds=300):
            return False

        current = datetime.now()
        cutoff = current.replace(
            hour=self.settings.sleep_hour,
            minute=self.settings.sleep_minute,
            second=0,
            microsecond=0,
        )
        if current < cutoff:
            self.sleep_reminder_count = 0
            return False

        # 只在第一次触发，之后持续显示
        return self.sleep_reminder_count == 0

    def _sleep_reminder(self) -> Reminder:
        return Reminder(
            kind="sleep",
            title="睡觉提醒",
            message=self.settings.sleep_message,
            action="sleep",
        )

    def _standing_waiting_reminder(self) -> Reminder:
        return Reminder(
            kind="standing",
            title="久坐提醒",
            message=self.settings.standing_message,
            action="walk",
        )

    def _start_standing_break(self) -> None:
        self.reminder_phase = "running"
        self.break_started_ts = time.monotonic()
        self.current_reminder = self._standing_running_reminder(self.settings.standing_break_minutes * 60)
        self.reminder_updated.emit(self.current_reminder)

    def _tick_standing_break(self, now: float) -> None:
        break_seconds = self.settings.standing_break_minutes * 60
        elapsed_break = max(0.0, now - self.break_started_ts)
        remaining = max(0, int(round(break_seconds - elapsed_break)))

        if remaining <= 0:
            # 站立休息完成，不重置护眼计时
            self._clear_current()
            return

        self.current_reminder = self._standing_running_reminder(remaining)
        self.reminder_updated.emit(self.current_reminder)

    def _standing_running_reminder(self, remaining_seconds: int) -> Reminder:
        return Reminder(
            kind="standing",
            title="站立倒计时",
            message=f"站立倒计时 {self._format_seconds(remaining_seconds)}",
            action="idle",
            phase="running",
        )

    def _eye_running_reminder(self, now: float) -> Reminder:
        elapsed = max(0.0, now - self.eye_rest_started_ts)
        remaining = max(0, int(round(self.settings.eye_rest_seconds - elapsed)))
        return Reminder(
            kind="eye",
            title="护眼提醒",
            message=f"{self.settings.eye_message} {remaining}",
            action="idle",
            phase="running",
        )

    def _tick_eye_rest(self, now: float) -> None:
        # 如果用户在休息期间有活动，重置倒计时（说明没有真正休息眼睛）
        if self.activity.is_recently_active(window_seconds=5):
            self.eye_rest_started_ts = now  # 重新开始倒计时
        
        elapsed = now - self.eye_rest_started_ts
        remaining = int(round(self.settings.eye_rest_seconds - elapsed))
        if remaining <= 0:
            # 护眼休息完成
            self.eye_rest_started_ts = 0.0
            self._clear_current()
            return

        self.current_reminder = self._eye_running_reminder(now)
        self.reminder_updated.emit(self.current_reminder)

    def _tick_sleep(self) -> None:
        if self.activity.seconds_since_input() < self.settings.sleep_idle_clear_minutes * 60:
            return

        self.current_reminder = None
        self.reminder_phase = "sleeping"
        self.sleeping_after_idle = True
        self.reminder_hidden.emit("sleep")

    def _clear_current(self, emit: bool = True) -> None:
        self.current_reminder = None
        self.reminder_phase = "idle"
        self.break_started_ts = 0.0
        self.eye_rest_started_ts = 0.0
        if emit:
            self.reminder_cleared.emit()

    @staticmethod
    def _format_seconds(total_seconds: int) -> str:
        minutes, seconds = divmod(max(0, total_seconds), 60)
        return f"{minutes:02d}:{seconds:02d}"

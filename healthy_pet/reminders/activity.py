from __future__ import annotations

import time
import re
import subprocess
import sys
from typing import Any

from PySide6.QtCore import QObject


class ActivityTracker(QObject):
    """Tracks global computer input activity.

    macOS uses IOHIDSystem idle time, which avoids the Accessibility permission
    and listener thread issues that can happen with global input hooks.
    
    Windows and Linux use pynput to monitor keyboard and mouse events.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.last_input_ts = time.monotonic()
        self.available = False
        self.mode = "fallback"
        self._mouse_listener: Any = None
        self._keyboard_listener: Any = None
        # macOS 缓存空闲时间，避免频繁调用 ioreg
        self._mac_idle_cache = 0.0
        self._mac_idle_cache_ts = 0.0
        self._mac_idle_cache_ttl = 3.0

    def start(self) -> None:
        if sys.platform == "darwin":
            self.mode = "mac_idle"
            self.available = True
            return

        # Windows and Linux: use pynput
        try:
            from pynput import keyboard, mouse
        except Exception as e:
            print(f"Warning: pynput not available: {e}")
            return

        if mouse is None or keyboard is None:
            return

        try:
            self._mouse_listener = mouse.Listener(
                on_move=self._touch,
                on_click=self._touch,
                on_scroll=self._touch,
            )
            self._keyboard_listener = keyboard.Listener(on_press=self._touch)
            self._mouse_listener.start()
            self._keyboard_listener.start()
            self.mode = "pynput"
            self.available = True
        except Exception as e:
            print(f"Warning: Failed to start activity tracker: {e}")
            self.available = False

    def stop(self) -> None:
        for listener in (self._mouse_listener, self._keyboard_listener):
            if listener is not None:
                try:
                    listener.stop()
                except Exception:
                    pass

    def seconds_since_input(self) -> float:
        if self.mode == "mac_idle":
            idle_seconds = self._mac_idle_seconds()
            if idle_seconds is not None:
                return idle_seconds
            return 0.0
        return time.monotonic() - self.last_input_ts

    def is_recently_active(self, window_seconds: int = 5) -> bool:
        if not self.available:
            return True
        return self.seconds_since_input() <= window_seconds

    def _touch(self, *_args, **_kwargs) -> None:
        self.last_input_ts = time.monotonic()

    def _mac_idle_seconds(self) -> float | None:
        now = time.monotonic()
        if now - self._mac_idle_cache_ts < self._mac_idle_cache_ttl:
            return self._mac_idle_cache + (now - self._mac_idle_cache_ts)
        
        try:
            result = subprocess.run(
                ["ioreg", "-c", "IOHIDSystem"],
                capture_output=True,
                text=True,
                timeout=1,
                check=False,
            )
        except (OSError, subprocess.SubprocessError):
            return None

        match = re.search(r'"HIDIdleTime"\s*=\s*(\d+)', result.stdout)
        if match is None:
            return None
        
        idle_seconds = int(match.group(1)) / 1_000_000_000
        self._mac_idle_cache = idle_seconds
        self._mac_idle_cache_ts = now
        return idle_seconds

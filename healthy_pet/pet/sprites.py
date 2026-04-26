from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QBitmap, QColor, QPainter, QPixmap


@dataclass(frozen=True)
class SpriteFrames:
    pixmaps: list[QPixmap]
    masks: list[QBitmap | None]


def natural_frame_key(path: Path) -> tuple[str, int]:
    match = re.search(r"_(\d+)\.png$", path.name)
    return path.stem, int(match.group(1)) if match else 0


class SpriteLibrary:
    def __init__(self, action_dir: Path):
        self.action_dir = action_dir
        self.actions = self._load_actions()
        self._scaled_cache: dict[tuple[str, float], SpriteFrames] = {}

    def has_action(self, action: str) -> bool:
        return action in self.actions

    def scaled_frames(self, action: str, scale: float) -> SpriteFrames:
        key = (action, scale)
        cached = self._scaled_cache.get(key)
        if cached is None:
            cached = self._scale_frames(self.actions[action], scale)
            self._scaled_cache[key] = cached
        return cached

    def clear_cache(self) -> None:
        self._scaled_cache.clear()

    def _load_actions(self) -> dict[str, list[QPixmap]]:
        idle = self._load_frames("stand")
        left = self._load_frames("leftwalk")
        right = self._load_frames("rightwalk")
        sleep = self._load_frames("sleep")
        angry = self._load_frames("angry")
        drag = self._load_frames("drag") or idle
        fall = self._load_frames("fall") or idle

        return {
            "idle": idle,
            "walk": right,
            "left_walk": left,
            "right_walk": right,
            "sleep": sleep,
            "angry": angry,
            "drag": drag,
            "fall": fall,
        }

    def _load_frames(self, prefix: str) -> list[QPixmap]:
        files = sorted(self.action_dir.glob(f"{prefix}_*.png"), key=natural_frame_key)
        frames = [QPixmap(str(path)) for path in files]
        frames = [frame for frame in frames if not frame.isNull()]
        return frames or [fallback_frame()]

    def _scale_frames(self, frames: list[QPixmap], scale: float) -> SpriteFrames:
        pixmaps: list[QPixmap] = []
        masks: list[QBitmap | None] = []
        for frame in frames:
            width = max(1, int(frame.width() * scale))
            height = max(1, int(frame.height() * scale))
            pixmap = frame.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            pixmaps.append(pixmap)
            masks.append(frame_mask(pixmap))
        return SpriteFrames(pixmaps=pixmaps, masks=masks)


def frame_mask(pixmap: QPixmap) -> QBitmap | None:
    mask = pixmap.mask()
    if mask.isNull():
        alpha_mask = pixmap.toImage().createAlphaMask()
        if not alpha_mask.isNull():
            mask = QBitmap.fromImage(alpha_mask)
    return None if mask.isNull() else mask


def fallback_frame() -> QPixmap:
    pixmap = QPixmap(120, 120)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QColor("#009faa"))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(16, 20, 88, 88)
    painter.end()
    return pixmap

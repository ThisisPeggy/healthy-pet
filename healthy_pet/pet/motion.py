from __future__ import annotations

from dataclasses import dataclass, field

from PySide6.QtCore import QPoint


@dataclass
class PetMotionState:
    drag_offset: QPoint = field(default_factory=QPoint)
    dragging: bool = False
    mouse_moving: bool = False
    on_floor: bool = True
    falling: bool = False
    drag_visual_active: bool = False
    speed_x: float = 0.0
    speed_y: float = 0.0
    gravity: float = 0.15
    speed_decay: float = 0.5
    drag_activation_threshold: int = 3
    press_position: QPoint | None = None
    mouse_positions_x: list[int] = field(default_factory=lambda: [0, 0, 0, 0])
    mouse_positions_y: list[int] = field(default_factory=lambda: [0, 0, 0, 0])

    def start_drag(self, drag_offset: QPoint, press_position: QPoint) -> None:
        self.drag_offset = drag_offset
        self.dragging = True
        self.drag_visual_active = False
        self.mouse_moving = False
        self.press_position = press_position
        if self.falling:
            self.falling = False

    def should_show_drag(self, cursor_pos: QPoint) -> bool:
        if self.drag_visual_active or self.press_position is None:
            return self.drag_visual_active
        dx = abs(cursor_pos.x() - self.press_position.x())
        dy = abs(cursor_pos.y() - self.press_position.y())
        if max(dx, dy) >= self.drag_activation_threshold:
            self.drag_visual_active = True
        return self.drag_visual_active

    def record_mouse_position(self, cursor_pos: QPoint) -> None:
        self.mouse_moving = True
        self.mouse_positions_x = self.mouse_positions_x[1:] + [cursor_pos.x()]
        self.mouse_positions_y = self.mouse_positions_y[1:] + [cursor_pos.y()]

    def release_drag(self) -> None:
        self.dragging = False
        self.drag_visual_active = False
        self.press_position = None
        if self.mouse_moving and self.mouse_positions_x[0] != 0:
            self.speed_x = (self.mouse_positions_x[-1] - self.mouse_positions_x[-3]) / 2.0 * 0.5
            self.speed_y = (self.mouse_positions_y[-1] - self.mouse_positions_y[-3]) / 2.0 * 0.5
        else:
            self.speed_x = 0.0
            self.speed_y = 0.0

        self.falling = True
        self.on_floor = False
        self.mouse_moving = False
        self.reset_mouse_history()

    def reset_mouse_history(self) -> None:
        self.mouse_positions_x = [0, 0, 0, 0]
        self.mouse_positions_y = [0, 0, 0, 0]

    def stop_on_floor(self) -> None:
        self.speed_x = 0.0
        self.speed_y = 0.0
        self.falling = False
        self.on_floor = True

    def cancel_drag(self) -> None:
        self.dragging = False
        self.drag_visual_active = False
        self.mouse_moving = False
        self.press_position = None
        self.reset_mouse_history()

    def apply_gravity(self) -> None:
        self.speed_y += self.gravity

    def bounce_x(self) -> None:
        self.speed_x = -self.speed_x * self.speed_decay

    def bounce_y(self) -> None:
        self.speed_y = -self.speed_y * self.speed_decay

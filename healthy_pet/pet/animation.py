from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PetAnimationState:
    action_name: str = "idle"
    frame_index: int = 0
    persistent_action: bool = False
    base_action_name: str = "idle"
    base_action_persistent: bool = False
    walk_origin_x: int = 0
    walk_direction: int = 1
    walk_range: int = 90
    walk_step: int = 6

    def start_action(self, action: str, persistent: bool) -> None:
        self.action_name = action
        if action not in {"drag", "fall"}:
            self.base_action_name = action
            self.base_action_persistent = persistent
        self.frame_index = 0
        self.persistent_action = persistent

    def restore_base_action(self, available_actions: set[str]) -> tuple[str, bool]:
        action = self.base_action_name if self.base_action_name in available_actions else "idle"
        return action, self.base_action_persistent

    def reset_walk_motion(self, current_x: int, width: int, geometry) -> None:
        self.walk_origin_x = current_x
        self.walk_direction = 1
        if self.walk_origin_x + width + self.walk_range > geometry.right():
            self.walk_direction = -1
        elif self.walk_origin_x - self.walk_range < geometry.left():
            self.walk_direction = 1

    def walk_frame_key(self) -> str:
        return "left_walk" if self.walk_direction < 0 else "right_walk"

    def next_walk_x(self, current_x: int) -> tuple[int, str | None]:
        next_x = current_x + self.walk_direction * self.walk_step
        if next_x > self.walk_origin_x + self.walk_range:
            self.walk_direction = -1
            return self.walk_origin_x + self.walk_range, "left"
        if next_x < self.walk_origin_x - self.walk_range:
            self.walk_direction = 1
            return self.walk_origin_x - self.walk_range, "right"
        return next_x, None

    def should_advance_walk(self, dragging: bool) -> bool:
        return self.action_name == "walk" and self.persistent_action and not dragging

    def advance_frame(self, frame_count: int) -> bool:
        self.frame_index += 1
        if self.frame_index < frame_count:
            return True
        if self.persistent_action:
            self.frame_index = 0
            return True
        return False

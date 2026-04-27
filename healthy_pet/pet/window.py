from __future__ import annotations

import sys

from PySide6.QtCore import QPoint, Qt, QTimer, Signal
from PySide6.QtGui import QAction, QBitmap, QMouseEvent, QPixmap
from PySide6.QtWidgets import QApplication, QLabel, QMenu, QVBoxLayout, QWidget

from healthy_pet.i18n import get_i18n
from healthy_pet.notifications.bubble import BubbleWindow
from healthy_pet.paths import KITTY_ACTION_DIR
from healthy_pet.pet.animation import PetAnimationState
from healthy_pet.pet.motion import PetMotionState
from healthy_pet.pet.native_window import apply_native_window_tweaks, maintain_topmost
from healthy_pet.pet.sprites import SpriteLibrary
from healthy_pet.settings import HealthSettings


def _event_global_pos(event: QMouseEvent) -> QPoint:
    if hasattr(event, "globalPosition"):
        return event.globalPosition().toPoint()
    return event.globalPos()


class PetWindow(QWidget):
    acknowledged = Signal()
    reset_work_timer_requested = Signal()
    request_settings = Signal()
    request_quit = Signal()

    def __init__(self, settings: HealthSettings):
        super().__init__(None)
        self.settings = settings
        self.i18n = get_i18n()
        self.motion = PetMotionState()
        self.animation = PetAnimationState()
        self.action_frames: list[QPixmap] = []
        self.action_masks: list[QBitmap | None] = []

        self.bubble = BubbleWindow()
        self.bubble.acknowledged.connect(self.acknowledge)

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setAttribute(Qt.WA_TranslucentBackground, True)
        self.image_label.setStyleSheet("background: transparent; border: none;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.image_label)

        self.sprites = SpriteLibrary(KITTY_ACTION_DIR)
        self._apply_window_flags()
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)  # 不自动填充背景
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

        # 动画定时器
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self._advance_frame)
        self.animation_timer.start(160)
        
        # 物理效果定时器
        self.physics_timer = QTimer(self)
        self.physics_timer.timeout.connect(self._update_physics)
        self.physics_timer.start(30)  # 约33fps

        # 置顶维护定时器（每5秒重新应用置顶设置）
        self._topmost_timer = QTimer(self)
        self._topmost_timer.timeout.connect(self._maintain_topmost)
        self._topmost_timer.start(5000)

        self.play_action("idle")
        self._move_to_default_position()
        self.winId()
        self._apply_native_window_tweaks()
        self.show()

    def apply_settings(self, settings: HealthSettings) -> None:
        self.settings = settings
        self.sprites.clear_cache()
        self._apply_window_flags()
        self.play_action(self.animation.action_name)
        self.show()
        self._apply_native_window_tweaks()

    def show_reminder(
        self,
        message: str,
        action: str,
    ) -> None:
        self.play_action(action, persistent=True)
        self.bubble.show_message(message, self._bubble_anchor())

    def update_reminder(self, message: str) -> None:
        # 只更新文字，不重新计算位置和大小（除非文字长度变化很大）
        if self.bubble.isVisible():
            old_text = self.bubble.message_label.text()
            # 如果文字内容相似（只是数字变化），只更新文字不重新布局
            if len(message) - len(old_text) < 5:
                self.bubble.message_label.setText(message)
                return
        self.bubble.show_message(message, self._bubble_anchor())

    def hide_bubble_keep_action(self) -> None:
        self.bubble.clear()

    def clear_reminder(self) -> None:
        self.bubble.clear()
        self.play_action("idle")

    def acknowledge(self) -> None:
        self.acknowledged.emit()

    def play_action(self, action: str, persistent: bool = False) -> None:
        action_name = action if self.sprites.has_action(action) else "idle"
        self.animation.start_action(action_name, persistent)
        frames_key = action_name
        if action_name == "walk":
            self._reset_walk_motion()
            frames_key = self.animation.walk_frame_key()
        self._set_sprite_frames(frames_key)
        max_width = max(frame.width() for frame in self.action_frames)
        max_height = max(frame.height() for frame in self.action_frames)
        self.image_label.setFixedSize(max_width, max_height)
        self._set_frame()

    def moveEvent(self, event) -> None:
        # 气泡跟随宠物移动（下落时由 _update_physics 处理）
        if self.bubble.isVisible() and not self.motion.falling:
            self.bubble.move_to_anchor(self._bubble_anchor())
        super().moveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            drag_offset = _event_global_pos(event) - self.frameGeometry().topLeft()
            self.motion.start_drag(drag_offset, _event_global_pos(event))
            event.accept()
            return
        if event.button() == Qt.RightButton:
            self._show_context_menu(event.pos())
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.motion.dragging:
            cursor_pos = _event_global_pos(event)
            geometry = self._screen_geometry(cursor_pos)
            new_pos = cursor_pos - self.motion.drag_offset
            clamped_x, clamped_y = self._clamp_to_geometry(new_pos.x(), new_pos.y(), geometry)
            self.move(clamped_x, clamped_y)
            self.motion.record_mouse_position(cursor_pos)
            
            # 显示拖拽动画
            if self.motion.should_show_drag(cursor_pos) and self.animation.action_name != "drag":
                self.play_action("drag", persistent=True)
            
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            if self.motion.drag_visual_active or self.motion.mouse_moving:
                self.motion.release_drag()
                self.play_action("fall", persistent=True)
            else:
                self.motion.cancel_drag()
            event.accept()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.acknowledge()
            event.accept()
    
    def _update_physics(self) -> None:
        """更新物理效果（重力、下落、地面检测）"""
        if not self.motion.falling or self.motion.dragging:
            return
        
        # 获取屏幕信息
        screen = self.screen() or QApplication.primaryScreen()
        screen_geo = screen.availableGeometry()
        
        # 应用重力
        self.motion.apply_gravity()
        
        # 更新位置
        new_x = self.x() + int(self.motion.speed_x)
        new_y = self.y() + int(self.motion.speed_y)
        
        # 地面检测 - 紧贴屏幕底部
        ground_y = self._ground_y(screen_geo)
        if new_y >= ground_y:
            new_y = ground_y
            self.motion.stop_on_floor()
            self._restore_base_action()
            new_y = self._ground_y(screen_geo)
        
        # 左右边界检测和反弹
        if new_x <= screen_geo.left():
            new_x = screen_geo.left()
            self.motion.bounce_x()
        elif new_x >= self._max_x(screen_geo):
            new_x = self._max_x(screen_geo)
            self.motion.bounce_x()
        
        # 顶部边界检测和反弹
        if new_y <= screen_geo.top():
            new_y = screen_geo.top()
            self.motion.bounce_y()
        
        # 移动到新位置
        self.move(new_x, new_y)
        
        # 同步更新气泡位置
        if self.bubble.isVisible():
            self.bubble.move_to_anchor(self._bubble_anchor())

    def closeEvent(self, event) -> None:
        self.bubble.close()
        super().closeEvent(event)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._apply_native_window_tweaks()
        QTimer.singleShot(0, self._apply_native_window_tweaks)
        QTimer.singleShot(100, self._apply_native_window_tweaks)
        QTimer.singleShot(500, self._maintain_topmost)
        QTimer.singleShot(1500, self._maintain_topmost)

    def _apply_window_flags(self) -> None:
        """初始化窗体, 无边框半透明窗口（参考DyberPet实现）"""
        if self.settings.always_on_top:
            if sys.platform == 'win32':
                self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow | Qt.NoDropShadowWindowHint)
            elif sys.platform == "darwin":
                self.setWindowFlags(
                    Qt.FramelessWindowHint
                    | Qt.WindowStaysOnTopHint
                    | Qt.NoDropShadowWindowHint
                    | Qt.Tool
                    | Qt.WindowDoesNotAcceptFocus
                )
            else:
                self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.NoDropShadowWindowHint)
        else:
            if sys.platform == 'win32':
                self.setWindowFlags(Qt.FramelessWindowHint | Qt.SubWindow | Qt.NoDropShadowWindowHint)
            else:
                # SubWindow not work in MacOS
                self.setWindowFlags(Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        if sys.platform == "darwin":
            self.setAttribute(Qt.WA_MacAlwaysShowToolWindow, True)
        self.repaint()

    def _apply_native_window_tweaks(self) -> None:
        """Apply platform-specific window tweaks for proper topmost behavior."""
        apply_native_window_tweaks(self, self.settings.always_on_top)

    def _maintain_topmost(self) -> None:
        """Periodically re-apply topmost settings to ensure window stays on top."""
        maintain_topmost(self, self.settings.always_on_top)

    def _set_sprite_frames(self, action_key: str) -> None:
        frames = self.sprites.scaled_frames(action_key, self.settings.pet_scale)
        self.action_frames = frames.pixmaps
        self.action_masks = frames.masks

    def _advance_frame(self) -> None:
        if not self.action_frames:
            return

        if self.animation.should_advance_walk(self.motion.dragging):
            self._advance_walk_position()

        if not self.animation.advance_frame(len(self.action_frames)):
            self.play_action("idle")
            return
        self._set_frame()

    def _set_frame(self) -> None:
        if not self.action_frames:
            return

        pixmap = self.action_frames[self.animation.frame_index]
        
        # 记录旧的窗口大小
        old_height = self.height()
        
        # 设置label大小和图片
        self.image_label.setFixedSize(pixmap.width(), pixmap.height())
        self.image_label.setPixmap(pixmap)
        
        # 设置窗口大小等于label大小（因为布局边距为0）
        self.setFixedSize(pixmap.size())

        # Match the native window shape to the sprite alpha to avoid a
        # rectangular host window showing around the pet on Windows.
        mask = (
            self.action_masks[self.animation.frame_index]
            if self.animation.frame_index < len(self.action_masks)
            else None
        )
        if mask is not None:
            self.setMask(mask)
        else:
            self.clearMask()

        # 如果在地面上且窗口高度改变了，调整位置保持贴地
        if self.motion.on_floor and old_height != self.height():
            screen = self.screen() or QApplication.primaryScreen()
            screen_geo = screen.availableGeometry()
            ground_y = self._ground_y(screen_geo)
            self.move(self.x(), ground_y)
        
        self.bubble.move_to_anchor(self._bubble_anchor())

    def _advance_walk_position(self) -> None:
        next_x, direction = self.animation.next_walk_x(self.x())
        if direction is not None:
            self._set_walk_frames(direction)

        self.move(next_x, self.y())

    def _reset_walk_motion(self) -> None:
        screen = self.screen() or QApplication.primaryScreen()
        geometry = screen.availableGeometry()
        self.animation.reset_walk_motion(self.x(), self.width(), geometry)

    def _set_walk_frames(self, direction: str) -> None:
        action_key = "left_walk" if direction == "left" else "right_walk"
        if not self.sprites.has_action(action_key):
            return
        self._set_sprite_frames(action_key)
        max_width = max(frame.width() for frame in self.action_frames)
        max_height = max(frame.height() for frame in self.action_frames)
        self.image_label.setFixedSize(max_width, max_height)
        self.animation.frame_index = 0

    def _restore_base_action(self) -> None:
        action, persistent = self.animation.restore_base_action(set(self.sprites.actions))
        self.play_action(action, persistent=persistent)

    def _move_to_default_position(self) -> None:
        geometry = self._screen_geometry()
        
        # 移动到屏幕右下角，紧贴底部
        self.move(
            max(geometry.left(), self._max_x(geometry) - 96),
            self._ground_y(geometry)
        )

    def _ground_y(self, geometry) -> int:
        return geometry.bottom() - self.height() + 1

    def _max_x(self, geometry) -> int:
        return max(geometry.left(), geometry.right() - self.width() + 1)

    def _screen_geometry(self, global_pos: QPoint | None = None):
        screen = None
        if global_pos is not None:
            screen = QApplication.screenAt(global_pos)
        if screen is None and self.windowHandle() is not None and self.windowHandle().screen() is not None:
            screen = self.windowHandle().screen()
        if screen is None and self.screen() is not None:
            screen = self.screen()
        if screen is None:
            screen = QApplication.primaryScreen()
        return screen.availableGeometry()

    def _clamp_to_geometry(self, x: int, y: int, geometry) -> tuple[int, int]:
        clamped_x = min(max(x, geometry.left()), self._max_x(geometry))
        clamped_y = min(max(y, geometry.top()), self._ground_y(geometry))
        return clamped_x, clamped_y

    def _bubble_anchor(self) -> QPoint:
        return QPoint(self.x() + self.width() // 2, self.y())

    def update_language(self) -> None:
        """更新语言"""
        self.i18n = get_i18n()

    def _show_context_menu(self, pos: QPoint) -> None:
        menu = QMenu(self)
        menu.setStyleSheet(
            """
            QMenu {
                text-align: left;
            }
            QMenu::item {
                padding: 5px 20px 5px 12px;
                text-align: left;
            }
            """
        )
        reset_work_action = QAction(self.i18n.t("menu.reset_timer"), self)
        settings_action = QAction(self.i18n.t("menu.settings"), self)
        quit_action = QAction(self.i18n.t("menu.quit"), self)

        reset_work_action.triggered.connect(self.reset_work_timer_requested.emit)
        settings_action.triggered.connect(self.request_settings.emit)
        quit_action.triggered.connect(self.request_quit.emit)

        menu.addAction(reset_work_action)
        menu.addSeparator()
        menu.addAction(settings_action)
        menu.addSeparator()
        menu.addAction(quit_action)
        menu.exec(self.mapToGlobal(pos))

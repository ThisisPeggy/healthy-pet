from __future__ import annotations

import ctypes
import re
import sys
from ctypes import wintypes
from pathlib import Path

from PySide6.QtCore import QPoint, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QAction, QColor, QMouseEvent, QPainter, QPixmap, QBitmap
from PySide6.QtWidgets import QApplication, QLabel, QMenu, QVBoxLayout, QWidget

from healthy_pet.i18n import get_i18n
from healthy_pet.notifications.bubble import BubbleWindow
from healthy_pet.paths import KITTY_ACTION_DIR
from healthy_pet.settings import HealthSettings


DWMWA_NCRENDERING_POLICY = 2
DWMWA_WINDOW_CORNER_PREFERENCE = 33
DWMWA_BORDER_COLOR = 34
DWMWA_REDIRECTIONBITMAP_ALPHA = 39

DWMNCRP_DISABLED = 1
DWMWCP_DONOTROUND = 1
DWMWA_COLOR_NONE = 0xFFFFFFFE

SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOZORDER = 0x0004
SWP_NOACTIVATE = 0x0010
SWP_FRAMECHANGED = 0x0020


def _event_global_pos(event: QMouseEvent) -> QPoint:
    if hasattr(event, "globalPosition"):
        return event.globalPosition().toPoint()
    return event.globalPos()


def _natural_key(path: Path) -> tuple[str, int]:
    match = re.search(r"_(\d+)\.png$", path.name)
    return path.stem, int(match.group(1)) if match else 0


def _set_dwm_attribute(hwnd: int, attribute: int, value) -> bool:
    try:
        result = ctypes.windll.dwmapi.DwmSetWindowAttribute(
            wintypes.HWND(hwnd),
            wintypes.DWORD(attribute),
            ctypes.byref(value),
            ctypes.sizeof(value),
        )
        return result == 0
    except Exception:
        return False


class PetWindow(QWidget):
    acknowledged = Signal()
    test_reminder_requested = Signal(str)
    reset_work_timer_requested = Signal()
    request_settings = Signal()
    request_quit = Signal()
    language_changed = Signal()

    def __init__(self, settings: HealthSettings):
        super().__init__(None)
        self.settings = settings
        self.i18n = get_i18n()
        
        # 拖拽相关
        self.drag_offset = QPoint()
        self.dragging = False
        self.mouse_moving = False
        
        # 物理效果相关
        self.on_floor = True
        self.falling = False
        self.drag_speed_x = 0.0
        self.drag_speed_y = 0.0
        self.gravity = 0.15
        self.speed_decay = 0.5
        
        # 鼠标位置记录（用于计算抛物线）
        self.mouse_positions_x = [0, 0, 0, 0]
        self.mouse_positions_y = [0, 0, 0, 0]
        
        # 动画相关
        self.action_name = "idle"
        self.action_frames: list[QPixmap] = []
        self.action_size = QSize(1, 1)
        self.frame_index = 0
        self.persistent_action = False
        self.walk_origin_x = 0
        self.walk_direction = 1
        self.walk_range = 90
        self.walk_step = 6

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

        self.actions = self._load_actions()
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

        self.play_action("idle")
        self._move_to_default_position()
        self.show()

    def apply_settings(self, settings: HealthSettings) -> None:
        self.settings = settings
        self._apply_window_flags()
        self.play_action(self.action_name)
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
        self.bubble.show_message(message, self._bubble_anchor())

    def hide_bubble_keep_action(self) -> None:
        self.bubble.clear()

    def clear_reminder(self) -> None:
        self.bubble.clear()
        self.play_action("idle")

    def acknowledge(self) -> None:
        self.acknowledged.emit()

    def play_action(self, action: str, persistent: bool = False) -> None:
        self.action_name = action if action in self.actions else "idle"
        frames_key = self.action_name
        if self.action_name == "walk":
            self._reset_walk_motion()
            frames_key = "left_walk" if self.walk_direction < 0 else "right_walk"
        self.action_frames = self._scaled_frames(self.actions[frames_key])
        max_width = max(frame.width() for frame in self.action_frames)
        max_height = max(frame.height() for frame in self.action_frames)
        self.action_size = QSize(max_width, max_height)
        self.image_label.setFixedSize(self.action_size)
        self.frame_index = 0
        self.persistent_action = persistent
        self._set_frame()

    def moveEvent(self, event) -> None:
        self.bubble.move_to_anchor(self._bubble_anchor())
        super().moveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.mouse_moving = False
            self.drag_offset = _event_global_pos(event) - self.frameGeometry().topLeft()
            
            # 如果在地面上，停止物理效果
            if self.on_floor:
                self.falling = False
                self.on_floor = False
            
            event.accept()
            return
        if event.button() == Qt.RightButton:
            self._show_context_menu(event.pos())
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.dragging:
            self.mouse_moving = True
            cursor_pos = _event_global_pos(event)
            geometry = self._screen_geometry(cursor_pos)
            new_pos = cursor_pos - self.drag_offset
            clamped_x, clamped_y = self._clamp_to_geometry(new_pos.x(), new_pos.y(), geometry)
            self.move(clamped_x, clamped_y)
            
            # 记录鼠标位置用于计算抛物线
            self.mouse_positions_x = self.mouse_positions_x[1:] + [cursor_pos.x()]
            self.mouse_positions_y = self.mouse_positions_y[1:] + [cursor_pos.y()]
            
            # 显示拖拽动画
            if self.action_name != "drag":
                self.play_action("drag", persistent=True)
            
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.dragging = False
            
            # 如果只是点击没有移动，触发拍拍
            if not self.mouse_moving and self.on_floor:
                self._on_pat()
            
            # 如果移动了，计算抛物线速度
            elif self.mouse_moving:
                # 计算速度（基于最后几个位置）
                if self.mouse_positions_x[0] != 0:
                    self.drag_speed_x = (self.mouse_positions_x[-1] - self.mouse_positions_x[-3]) / 2.0 * 0.5
                    self.drag_speed_y = (self.mouse_positions_y[-1] - self.mouse_positions_y[-3]) / 2.0 * 0.5
                else:
                    self.drag_speed_x = 0
                    self.drag_speed_y = 0
                
                # 开始下落
                self.falling = True
                self.on_floor = False
                self.play_action("fall", persistent=True)
                
                # 重置鼠标位置记录
                self.mouse_positions_x = [0, 0, 0, 0]
                self.mouse_positions_y = [0, 0, 0, 0]
            
            self.mouse_moving = False
            event.accept()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.acknowledge()
            event.accept()
    
    def _on_pat(self) -> None:
        """拍拍宠物"""
        # 播放拍拍动画
        if "patpat" in self.actions:
            self.play_action("patpat")
    
    def _update_physics(self) -> None:
        """更新物理效果（重力、下落、地面检测）"""
        if not self.falling or self.dragging:
            return
        
        # 获取屏幕信息
        screen = self.screen() or QApplication.primaryScreen()
        screen_geo = screen.availableGeometry()
        
        # 应用重力
        self.drag_speed_y += self.gravity
        
        # 更新位置
        new_x = self.x() + int(self.drag_speed_x)
        new_y = self.y() + int(self.drag_speed_y)
        
        # 地面检测 - 紧贴屏幕底部
        ground_y = self._ground_y(screen_geo)
        if new_y >= ground_y:
            new_y = ground_y
            self.drag_speed_y = 0
            self.drag_speed_x = 0
            self.falling = False
            self.on_floor = True
            self.play_action("idle")
            new_y = self._ground_y(screen_geo)
        
        # 左右边界检测和反弹
        if new_x <= screen_geo.left():
            new_x = screen_geo.left()
            self.drag_speed_x = -self.drag_speed_x * self.speed_decay
        elif new_x >= self._max_x(screen_geo):
            new_x = self._max_x(screen_geo)
            self.drag_speed_x = -self.drag_speed_x * self.speed_decay
        
        # 顶部边界检测和反弹
        if new_y <= screen_geo.top():
            new_y = screen_geo.top()
            self.drag_speed_y = -self.drag_speed_y * self.speed_decay
        
        # 移动到新位置
        self.move(new_x, new_y)

    def closeEvent(self, event) -> None:
        self.bubble.close()
        super().closeEvent(event)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._apply_native_window_tweaks()
        QTimer.singleShot(0, self._apply_native_window_tweaks)
        QTimer.singleShot(100, self._apply_native_window_tweaks)

    def _apply_window_flags(self) -> None:
        """初始化窗体, 无边框半透明窗口（参考DyberPet实现）"""
        if self.settings.always_on_top:
            if sys.platform == 'win32':
                self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow | Qt.NoDropShadowWindowHint)
            else:
                # SubWindow not work in MacOS
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
        self.repaint()

    def _apply_native_window_tweaks(self) -> None:
        if sys.platform != "win32":
            return

        hwnd = int(self.winId())
        if not hwnd:
            return

        nc_policy = ctypes.c_int(DWMNCRP_DISABLED)
        _set_dwm_attribute(hwnd, DWMWA_NCRENDERING_POLICY, nc_policy)

        corner_preference = ctypes.c_int(DWMWCP_DONOTROUND)
        _set_dwm_attribute(hwnd, DWMWA_WINDOW_CORNER_PREFERENCE, corner_preference)

        border_color = ctypes.c_uint(DWMWA_COLOR_NONE)
        _set_dwm_attribute(hwnd, DWMWA_BORDER_COLOR, border_color)

        build = getattr(sys.getwindowsversion(), "build", 0)
        if build >= 26100:
            use_alpha = wintypes.BOOL(1)
            _set_dwm_attribute(hwnd, DWMWA_REDIRECTIONBITMAP_ALPHA, use_alpha)

        ctypes.windll.user32.SetWindowPos(
            wintypes.HWND(hwnd),
            wintypes.HWND(0),
            0,
            0,
            0,
            0,
            SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE | SWP_FRAMECHANGED,
        )

    def _load_actions(self) -> dict[str, list[QPixmap]]:
        idle = self._load_frames("stand")
        left = self._load_frames("leftwalk")
        right = self._load_frames("rightwalk")
        sleep = self._load_frames("sleep")
        angry = self._load_frames("angry")
        drag = self._load_frames("drag")
        fall = self._load_frames("fall")
        patpat = self._load_frames("patpat")
        
        # 如果没有专门的动画，使用默认的
        if not drag:
            drag = idle
        if not fall:
            fall = idle
        if not patpat:
            patpat = idle
        
        return {
            "idle": idle,
            "walk": right,
            "left_walk": left,
            "right_walk": right,
            "sleep": sleep,
            "angry": angry,
            "drag": drag,
            "fall": fall,
            "patpat": patpat,
        }

    def _load_frames(self, prefix: str) -> list[QPixmap]:
        files = sorted(KITTY_ACTION_DIR.glob(f"{prefix}_*.png"), key=_natural_key)
        frames = [QPixmap(str(path)) for path in files]
        frames = [frame for frame in frames if not frame.isNull()]
        return frames or [self._fallback_frame()]

    def _scaled_frames(self, frames: list[QPixmap]) -> list[QPixmap]:
        scaled: list[QPixmap] = []
        for frame in frames:
            width = max(1, int(frame.width() * self.settings.pet_scale))
            height = max(1, int(frame.height() * self.settings.pet_scale))
            scaled.append(frame.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        return scaled

    def _fallback_frame(self) -> QPixmap:
        pixmap = QPixmap(120, 120)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor("#009faa"))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(16, 20, 88, 88)
        painter.end()
        return pixmap

    def _advance_frame(self) -> None:
        if not self.action_frames:
            return

        if self.action_name == "walk" and self.persistent_action and not self.dragging:
            self._advance_walk_position()

        self.frame_index += 1
        if self.frame_index >= len(self.action_frames):
            if self.persistent_action:
                self.frame_index = 0
            else:
                self.play_action("idle")
                return
        self._set_frame()

    def _set_frame(self) -> None:
        if not self.action_frames:
            return

        pixmap = self.action_frames[self.frame_index]
        
        # 记录旧的窗口大小
        old_height = self.height()
        
        # 设置label大小和图片
        self.image_label.setFixedSize(pixmap.width(), pixmap.height())
        self.image_label.setPixmap(pixmap)
        
        # 设置窗口大小等于label大小（因为布局边距为0）
        self.setFixedSize(pixmap.size())

        # Match the native window shape to the sprite alpha to avoid a
        # rectangular host window showing around the pet on Windows.
        mask = pixmap.mask()
        if mask.isNull():
            alpha_mask = pixmap.toImage().createAlphaMask()
            if not alpha_mask.isNull():
                mask = QBitmap.fromImage(alpha_mask)
        if not mask.isNull():
            self.setMask(mask)
        else:
            self.clearMask()

        # 如果在地面上且窗口高度改变了，调整位置保持贴地
        if self.on_floor and old_height != self.height():
            screen = self.screen() or QApplication.primaryScreen()
            screen_geo = screen.availableGeometry()
            ground_y = self._ground_y(screen_geo)
            self.move(self.x(), ground_y)
        
        self.bubble.move_to_anchor(self._bubble_anchor())

    def _advance_walk_position(self) -> None:
        next_x = self.x() + self.walk_direction * self.walk_step
        if next_x > self.walk_origin_x + self.walk_range:
            self.walk_direction = -1
            next_x = self.walk_origin_x + self.walk_range
            self._set_walk_frames("left")
        elif next_x < self.walk_origin_x - self.walk_range:
            self.walk_direction = 1
            next_x = self.walk_origin_x - self.walk_range
            self._set_walk_frames("right")

        self.move(next_x, self.y())

    def _reset_walk_motion(self) -> None:
        self.walk_origin_x = self.x()
        self.walk_direction = 1

        screen = self.screen() or QApplication.primaryScreen()
        geometry = screen.availableGeometry()
        if self.walk_origin_x + self.width() + self.walk_range > geometry.right():
            self.walk_direction = -1
        elif self.walk_origin_x - self.walk_range < geometry.left():
            self.walk_direction = 1

    def _set_walk_frames(self, direction: str) -> None:
        frames = self.actions.get("left_walk" if direction == "left" else "right_walk")
        if not frames:
            return
        self.action_frames = self._scaled_frames(frames)
        max_width = max(frame.width() for frame in self.action_frames)
        max_height = max(frame.height() for frame in self.action_frames)
        self.action_size = QSize(max_width, max_height)
        self.image_label.setFixedSize(self.action_size)
        self.frame_index = 0

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

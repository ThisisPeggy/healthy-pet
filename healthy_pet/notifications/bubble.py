from __future__ import annotations

from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout


class BubbleWindow(QFrame):
    acknowledged = Signal()
    MIN_WIDTH = 80
    MAX_WIDTH = 320
    PADDING = 20

    def __init__(self):
        super().__init__(None)
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.NoDropShadowWindowHint
            | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.container = QFrame(self)
        self.container.setObjectName("BubbleContainer")

        self.message_label = QLabel(self.container)
        self.message_label.setObjectName("BubbleLabel")
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        content_layout = QHBoxLayout(self.container)
        content_layout.setContentsMargins(10, 6, 10, 6)
        content_layout.setSpacing(0)
        content_layout.addWidget(self.message_label)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.container)

        self.setStyleSheet(
            """
            BubbleWindow {
                background: transparent;
            }
            #BubbleContainer {
                background-color: rgb(255, 255, 255);
                border: 1px solid rgb(200, 200, 200);
                border-radius: 10px;
            }
            #BubbleLabel {
                color: rgb(30, 30, 30);
                font-size: 14px;
                font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
                border: none;
                background: transparent;
            }
            """
        )

    def show_message(self, message: str, anchor: QPoint) -> None:
        self.message_label.setText(message)
        self._resize_to_message()
        self.move_to_anchor(anchor)
        self.show()
        self.raise_()

    def move_to_anchor(self, anchor: QPoint) -> None:
        self.move(anchor.x() - self.width() // 2, anchor.y() - self.height() - 12)

    def clear(self) -> None:
        self.hide()

    def _resize_to_message(self) -> None:
        """根据文字内容智能调整气泡大小"""
        # 获取文字的理想尺寸
        font_metrics = self.message_label.fontMetrics()
        text = self.message_label.text()
        
        # 计算单行文字的宽度
        text_width = font_metrics.horizontalAdvance(text)
        
        # 根据文字长度决定气泡宽度
        if text_width <= self.MIN_WIDTH:
            # 短文字：使用最小宽度
            label_width = self.MIN_WIDTH
        elif text_width <= self.MAX_WIDTH:
            # 中等长度：使用实际宽度加上一些边距
            label_width = text_width + self.PADDING
        else:
            # 长文字：使用最大宽度，自动换行
            label_width = self.MAX_WIDTH
        
        # 计算对应宽度下的文字高度
        label_height = font_metrics.boundingRect(
            0, 0, label_width, 0,
            Qt.TextWordWrap | Qt.AlignCenter,
            text
        ).height()
        
        # 确保高度至少能容纳一行文字
        min_height = font_metrics.height()
        label_height = max(label_height, min_height)
        
        # 添加一些垂直边距
        label_height += 8
        
        # 计算容器尺寸
        margins = self.container.layout().contentsMargins()
        container_width = label_width + margins.left() + margins.right()
        container_height = label_height + margins.top() + margins.bottom()
        
        # 设置尺寸
        self.message_label.setFixedSize(label_width, label_height)
        self.container.setFixedSize(container_width, container_height)
        self.setFixedSize(container_width, container_height)

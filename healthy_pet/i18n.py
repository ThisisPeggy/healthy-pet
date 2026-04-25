"""
国际化支持模块
Internationalization support module
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from healthy_pet.paths import DATA_DIR


LANGUAGE_FILE = DATA_DIR / "language.json"


class I18n:
    """简单的国际化类"""
    
    def __init__(self):
        self.current_language = "zh_CN"
        self.translations = {
            "zh_CN": self._chinese_translations(),
            "en_US": self._english_translations(),
        }
        self.load_language()
    
    def load_language(self) -> None:
        """从文件加载语言设置"""
        if LANGUAGE_FILE.exists():
            try:
                data = json.loads(LANGUAGE_FILE.read_text(encoding="utf-8"))
                lang = data.get("language", "zh_CN")
                if lang in self.translations:
                    self.current_language = lang
            except (OSError, json.JSONDecodeError):
                pass
    
    def save_language(self, language: str) -> None:
        """保存语言设置"""
        if language in self.translations:
            self.current_language = language
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            LANGUAGE_FILE.write_text(
                json.dumps({"language": language}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
    
    def t(self, key: str) -> str:
        """翻译文本"""
        return self.translations[self.current_language].get(key, key)
    
    def get_language(self) -> str:
        """获取当前语言"""
        return self.current_language
    
    def get_language_name(self) -> str:
        """获取当前语言名称"""
        return "中文" if self.current_language == "zh_CN" else "English"
    
    @staticmethod
    def _chinese_translations() -> dict[str, str]:
        return {
            # 菜单
            "menu.reset_timer": "重置工作计时",
            "menu.settings": "提醒设置",
            "menu.quit": "退出",
            
            # 托盘
            "tray.title": "健康桌宠",
            
            # 提醒类型
            "reminder.eye.title": "护眼提醒",
            "reminder.standing.title": "久坐提醒",
            "reminder.sleep.title": "睡觉提醒",
            "reminder.standing.countdown": "站立倒计时",
            
            # 设置窗口
            "settings.title": "健康提醒设置",
            "settings.enabled": "启用提醒",
            "settings.start_on_boot": "开机自启",
            "settings.eye_interval": "护眼提醒间隔（分钟）",
            "settings.eye_message": "护眼提醒消息",
            "settings.eye_rest": "护眼休息时长（秒）",
            "settings.standing_interval": "久坐提醒间隔（分钟）",
            "settings.standing_message": "久坐提醒消息",
            "settings.standing_break": "站立休息时长（分钟）",
            "settings.idle_reset": "空闲重置时间（分钟）",
            "settings.sleep_time": "睡觉提醒时间",
            "settings.sleep_message": "睡觉提醒消息",
            "settings.sound": "启用提醒声音",
            "settings.sound_options": "有声音的提醒",
            "settings.sound_eye": "护眼",
            "settings.sound_standing": "久坐",
            "settings.sound_sleep": "睡觉",
            "settings.always_on_top": "窗口置顶",
            "settings.pet_scale": "宠物大小",
            "settings.language": "语言 / Language",
            "settings.save": "保存",
            "settings.cancel": "取消",
            
            # 默认消息
            "message.eye.default": "看看远处吧",
            "message.standing.default": "已经工作很久了，站起来活动一下吧。",
            "message.sleep.default": "主人不要熬夜哦，跟我一起睡觉吧。",
        }
    
    @staticmethod
    def _english_translations() -> dict[str, str]:
        return {
            # Menu
            "menu.reset_timer": "Reset Work Timer",
            "menu.settings": "Settings",
            "menu.quit": "Quit",
            
            # Tray
            "tray.title": "healthy_pet",
            
            # Reminder types
            "reminder.eye.title": "Eye Rest Reminder",
            "reminder.standing.title": "Standing Reminder",
            "reminder.sleep.title": "Sleep Reminder",
            "reminder.standing.countdown": "Standing Countdown",
            
            # Settings window
            "settings.title": "Health Reminder Settings",
            "settings.enabled": "Enable Reminders",
            "settings.start_on_boot": "Start on Boot",
            "settings.eye_interval": "Eye Rest Interval (minutes)",
            "settings.eye_message": "Eye Rest Message",
            "settings.eye_rest": "Eye Rest Duration (seconds)",
            "settings.standing_interval": "Standing Interval (minutes)",
            "settings.standing_message": "Standing Message",
            "settings.standing_break": "Standing Break Duration (minutes)",
            "settings.idle_reset": "Idle Reset Time (minutes)",
            "settings.sleep_time": "Sleep Reminder Time",
            "settings.sleep_message": "Sleep Message",
            "settings.sound": "Enable Sound",
            "settings.sound_options": "Reminders with Sound",
            "settings.sound_eye": "Eyes",
            "settings.sound_standing": "Standing",
            "settings.sound_sleep": "Sleep",
            "settings.always_on_top": "Always on Top",
            "settings.pet_scale": "Pet Scale",
            "settings.language": "Language / 语言",
            "settings.save": "Save",
            "settings.cancel": "Cancel",
            
            # Default messages
            "message.eye.default": "Look away and rest your eyes",
            "message.standing.default": "You've been working for a while. Time to stand up and move!",
            "message.sleep.default": "It's late. Time to sleep!",
        }


# 全局实例
_i18n = I18n()


def t(key: str) -> str:
    """翻译文本的快捷函数"""
    return _i18n.t(key)


def get_i18n() -> I18n:
    """获取 i18n 实例"""
    return _i18n

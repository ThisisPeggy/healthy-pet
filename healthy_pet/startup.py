from __future__ import annotations

import sys
from pathlib import Path


REGISTRY_VALUE_NAME = "healthy_pet"


def _is_windows() -> bool:
    return sys.platform == "win32"


def _is_macos() -> bool:
    return sys.platform == "darwin"


def _is_linux() -> bool:
    return sys.platform.startswith("linux")


def _python_executable() -> Path:
    current = Path(sys.executable)
    if current.name.lower() == "python.exe":
        pythonw = current.with_name("pythonw.exe")
        if pythonw.exists():
            return pythonw
    return current


def get_startup_command() -> str:
    executable = _python_executable()
    return f'"{executable}" -m healthy_pet'


def _get_macos_plist_path() -> Path:
    """获取 macOS LaunchAgent plist 文件路径"""
    return Path.home() / "Library" / "LaunchAgents" / "com.healthypet.app.plist"


def _get_linux_autostart_path() -> Path:
    """获取 Linux autostart desktop 文件路径"""
    return Path.home() / ".config" / "autostart" / "healthy-pet.desktop"


def _create_macos_plist() -> str:
    """创建 macOS plist 文件内容"""
    executable = _python_executable()
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.healthypet.app</string>
    <key>ProgramArguments</key>
    <array>
        <string>{executable}</string>
        <string>-m</string>
        <string>healthy_pet</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
"""


def _create_linux_desktop() -> str:
    """创建 Linux desktop 文件内容"""
    executable = _python_executable()
    return f"""[Desktop Entry]
Type=Application
Name=Healthy Pet
Comment=Desktop health reminder pet
Exec={executable} -m healthy_pet
Icon=healthy-pet
Terminal=false
Categories=Utility;
X-GNOME-Autostart-enabled=true
"""


def is_startup_enabled() -> bool:
    if _is_windows():
        return _is_startup_enabled_windows()
    elif _is_macos():
        return _is_startup_enabled_macos()
    elif _is_linux():
        return _is_startup_enabled_linux()
    return False


def _is_startup_enabled_windows() -> bool:
    """检查 Windows 开机自启是否启用"""
    import winreg

    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_READ,
        ) as key:
            value, _ = winreg.QueryValueEx(key, REGISTRY_VALUE_NAME)
            return value == get_startup_command()
    except FileNotFoundError:
        return False
    except OSError:
        return False


def _is_startup_enabled_macos() -> bool:
    """检查 macOS 开机自启是否启用"""
    plist_path = _get_macos_plist_path()
    return plist_path.exists()


def _is_startup_enabled_linux() -> bool:
    """检查 Linux 开机自启是否启用"""
    desktop_path = _get_linux_autostart_path()
    return desktop_path.exists()


def set_startup_enabled(enabled: bool) -> bool:
    if _is_windows():
        return _set_startup_enabled_windows(enabled)
    elif _is_macos():
        return _set_startup_enabled_macos(enabled)
    elif _is_linux():
        return _set_startup_enabled_linux(enabled)
    return False


def _set_startup_enabled_windows(enabled: bool) -> bool:
    """设置 Windows 开机自启"""
    import winreg

    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE,
        ) as key:
            if enabled:
                winreg.SetValueEx(
                    key,
                    REGISTRY_VALUE_NAME,
                    0,
                    winreg.REG_SZ,
                    get_startup_command(),
                )
            else:
                try:
                    winreg.DeleteValue(key, REGISTRY_VALUE_NAME)
                except FileNotFoundError:
                    pass
        return True
    except OSError:
        return False


def _set_startup_enabled_macos(enabled: bool) -> bool:
    """设置 macOS 开机自启"""
    plist_path = _get_macos_plist_path()
    
    try:
        if enabled:
            # 创建 LaunchAgents 目录（如果不存在）
            plist_path.parent.mkdir(parents=True, exist_ok=True)
            # 写入 plist 文件
            plist_path.write_text(_create_macos_plist(), encoding="utf-8")
        else:
            # 删除 plist 文件
            if plist_path.exists():
                plist_path.unlink()
        return True
    except (OSError, PermissionError):
        return False


def _set_startup_enabled_linux(enabled: bool) -> bool:
    """设置 Linux 开机自启"""
    desktop_path = _get_linux_autostart_path()
    
    try:
        if enabled:
            # 创建 autostart 目录（如果不存在）
            desktop_path.parent.mkdir(parents=True, exist_ok=True)
            # 写入 desktop 文件
            desktop_path.write_text(_create_linux_desktop(), encoding="utf-8")
        else:
            # 删除 desktop 文件
            if desktop_path.exists():
                desktop_path.unlink()
        return True
    except (OSError, PermissionError):
        return False

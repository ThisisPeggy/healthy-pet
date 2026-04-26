from __future__ import annotations

import ctypes
import subprocess
import sys
from ctypes import c_void_p, wintypes

from PySide6.QtWidgets import QWidget


# Windows DWM attributes
DWMWA_NCRENDERING_POLICY = 2
DWMWA_WINDOW_CORNER_PREFERENCE = 33
DWMWA_BORDER_COLOR = 34
DWMWA_REDIRECTIONBITMAP_ALPHA = 39

DWMNCRP_DISABLED = 1
DWMWCP_DONOTROUND = 1
DWMWA_COLOR_NONE = 0xFFFFFFFE

# Windows SetWindowPos flags
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOACTIVATE = 0x0010
SWP_FRAMECHANGED = 0x0020
HWND_TOPMOST = -1

# macOS window levels and collection behavior flags
KCG_SCREEN_SAVER_WINDOW_LEVEL = 1000
NS_WINDOW_COLLECTION_BEHAVIOR_CAN_JOIN_ALL_SPACES = 1 << 0
NS_WINDOW_COLLECTION_BEHAVIOR_STATIONARY = 1 << 4
NS_WINDOW_COLLECTION_BEHAVIOR_IGNORES_CYCLE = 1 << 6
NS_WINDOW_COLLECTION_BEHAVIOR_FULL_SCREEN_AUXILIARY = 1 << 18


def apply_native_window_tweaks(window: QWidget, always_on_top: bool) -> None:
    """Apply platform-specific window settings after Qt creates the native window."""
    if sys.platform == "win32":
        _apply_windows_window_tweaks(window, always_on_top)
    elif sys.platform == "darwin":
        _apply_macos_window_level(window)
    elif sys.platform in ("linux", "linux2") and always_on_top:
        _apply_linux_window_above(window)


def maintain_topmost(window: QWidget, always_on_top: bool) -> None:
    """Reapply topmost behavior for platforms that can lose it during window changes."""
    if not always_on_top:
        return

    if sys.platform == "win32":
        _set_windows_topmost(window)
    elif sys.platform == "darwin":
        _apply_macos_window_level(window)
    elif sys.platform in ("linux", "linux2"):
        _apply_linux_window_above(window)


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


def _apply_windows_window_tweaks(window: QWidget, always_on_top: bool) -> None:
    hwnd = int(window.winId())
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

    if always_on_top:
        _set_windows_topmost(window)


def _set_windows_topmost(window: QWidget) -> None:
    hwnd = int(window.winId())
    if not hwnd:
        return

    ctypes.windll.user32.SetWindowPos(
        wintypes.HWND(hwnd),
        wintypes.HWND(HWND_TOPMOST),
        0,
        0,
        0,
        0,
        SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_FRAMECHANGED,
    )


def _apply_macos_window_level(window: QWidget) -> None:
    if sys.platform != "darwin":
        return

    try:
        import objc

        ns_view = objc.objc_object(c_void_p=int(window.winId()))
        ns_window = ns_view.window()
        if ns_window is None:
            return
        _configure_macos_window(ns_window)
    except Exception:
        _apply_macos_window_level_ctypes(window)


def _configure_macos_window(ns_window) -> None:
    ns_window.setLevel_(KCG_SCREEN_SAVER_WINDOW_LEVEL)
    ns_window.setCollectionBehavior_(
        NS_WINDOW_COLLECTION_BEHAVIOR_CAN_JOIN_ALL_SPACES
        | NS_WINDOW_COLLECTION_BEHAVIOR_STATIONARY
        | NS_WINDOW_COLLECTION_BEHAVIOR_FULL_SCREEN_AUXILIARY
        | NS_WINDOW_COLLECTION_BEHAVIOR_IGNORES_CYCLE
    )
    ns_window.setHidesOnDeactivate_(False)


def _apply_macos_window_level_ctypes(window: QWidget) -> None:
    try:
        objc = ctypes.cdll.LoadLibrary("/usr/lib/libobjc.A.dylib")

        objc.objc_getClass.restype = ctypes.c_void_p
        objc.objc_getClass.argtypes = [ctypes.c_char_p]
        objc.sel_registerName.restype = ctypes.c_void_p
        objc.sel_registerName.argtypes = [ctypes.c_char_p]
        objc.objc_msgSend.restype = ctypes.c_void_p
        objc.objc_msgSend.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

        ns_view = ctypes.c_void_p(int(window.winId()))
        window_sel = objc.sel_registerName(b"window")
        set_level_sel = objc.sel_registerName(b"setLevel:")
        set_collection_sel = objc.sel_registerName(b"setCollectionBehavior:")
        set_hides_on_deactivate_sel = objc.sel_registerName(b"setHidesOnDeactivate:")

        ns_window = objc.objc_msgSend(ns_view, window_sel)
        if not ns_window:
            return

        objc.objc_msgSend.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_long]
        objc.objc_msgSend(ns_window, set_level_sel, KCG_SCREEN_SAVER_WINDOW_LEVEL)
        objc.objc_msgSend(
            ns_window,
            set_collection_sel,
            NS_WINDOW_COLLECTION_BEHAVIOR_CAN_JOIN_ALL_SPACES
            | NS_WINDOW_COLLECTION_BEHAVIOR_STATIONARY
            | NS_WINDOW_COLLECTION_BEHAVIOR_FULL_SCREEN_AUXILIARY
            | NS_WINDOW_COLLECTION_BEHAVIOR_IGNORES_CYCLE,
        )

        objc.objc_msgSend.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_bool]
        objc.objc_msgSend(ns_window, set_hides_on_deactivate_sel, False)
    except Exception:
        pass


def _apply_linux_window_above(window: QWidget) -> None:
    try:
        from Xlib import X, Xatom, display
        from Xlib.protocol import event
    except ImportError:
        _apply_linux_window_above_xdotool(window)
        return

    try:
        dpy = display.Display()
        win = dpy.create_resource_object("window", int(window.winId()))
        net_wm_state = dpy.intern_atom("_NET_WM_STATE")
        net_wm_state_above = dpy.intern_atom("_NET_WM_STATE_ABOVE")

        root = dpy.screen().root
        root.send_event(
            event.ClientMessage(
                window=win,
                client_type=net_wm_state,
                data=(32, [1, net_wm_state_above, 0, 1, 0]),
            ),
            event_mask=X.SubstructureRedirectMask | X.SubstructureNotifyMask,
        )
        win.change_property(net_wm_state, Xatom.ATOM, 32, [net_wm_state_above])
        win.configure(stack_mode=X.Above)
        dpy.flush()
    except Exception:
        pass


def _apply_linux_window_above_xdotool(window: QWidget) -> None:
    win_id = str(int(window.winId()))
    try:
        subprocess.run(
            ["xdotool", "windowstate", "--add", "ABOVE", win_id],
            check=False,
            capture_output=True,
        )
        subprocess.run(
            ["xdotool", "windowraise", win_id],
            check=False,
            capture_output=True,
        )
    except Exception:
        pass

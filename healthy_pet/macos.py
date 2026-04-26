from __future__ import annotations

import ctypes
import sys
from ctypes import c_char_p, c_long, c_void_p


NS_APPLICATION_ACTIVATION_POLICY_ACCESSORY = 1


def hide_dock_icon() -> None:
    """Hide the Python Dock icon on macOS while keeping app windows usable."""
    if sys.platform != "darwin":
        return

    try:
        objc = ctypes.cdll.LoadLibrary("/usr/lib/libobjc.A.dylib")
        objc.objc_getClass.argtypes = [c_char_p]
        objc.objc_getClass.restype = c_void_p
        objc.sel_registerName.argtypes = [c_char_p]
        objc.sel_registerName.restype = c_void_p
        objc.objc_msgSend.argtypes = [c_void_p, c_void_p]
        objc.objc_msgSend.restype = c_void_p

        ns_application = objc.objc_getClass(b"NSApplication")
        shared_application = objc.sel_registerName(b"sharedApplication")
        app = objc.objc_msgSend(ns_application, shared_application)
        if not app:
            return

        set_activation_policy = objc.sel_registerName(b"setActivationPolicy:")
        objc.objc_msgSend.argtypes = [c_void_p, c_void_p, c_long]
        objc.objc_msgSend.restype = c_void_p
        objc.objc_msgSend(
            app,
            set_activation_policy,
            NS_APPLICATION_ACTIVATION_POLICY_ACCESSORY,
        )
    except Exception:
        return

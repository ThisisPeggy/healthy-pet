"""Entry point for running healthy_pet as a module."""

import subprocess
import sys

from healthy_pet.app import HealthyPetApplication
from healthy_pet.startup import _python_executable
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

try:
    from tendo import singleton
except Exception:
    singleton = None


def main() -> int:
    """Main entry point for the application."""
    if singleton is not None:
        try:
            singleton.SingleInstance()
        except Exception:
            return 0

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = HealthyPetApplication(sys.argv)
    app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)
    return app.exec()


def launch_detached() -> int:
    """Launch the app as a detached background process."""
    kwargs = {
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
        "close_fds": True,
    }
    if sys.platform == "win32":
        kwargs["creationflags"] = (
            subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        )
    else:
        kwargs["start_new_session"] = True

    subprocess.Popen(
        [str(_python_executable()), "-m", "healthy_pet"],
        **kwargs,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Entry point for running healthy_pet as a module."""

import sys
from healthy_pet.app import HealthyPetApplication
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


if __name__ == "__main__":
    sys.exit(main())

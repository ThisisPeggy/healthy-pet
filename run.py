import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from healthy_pet.app import HealthyPetApplication

try:
    from tendo import singleton
except Exception:  # pragma: no cover - optional runtime guard
    singleton = None


def main() -> int:
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

"""PySide6 entry point for PromptGen Tool."""

from __future__ import annotations
import sys
import os

# Ensure repo root is on the Python path when launched directly
_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from PySide6.QtWidgets import QApplication

from ui.styles import apply as apply_style
from ui.main_window import MainWindow


def main() -> int:
    # High-DPI support is on by default in PySide6 6.x — no attribute needed

    app = QApplication(sys.argv)
    app.setApplicationName("PromptGen Tool")
    app.setOrganizationName("PromptGen")

    apply_style(app)

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

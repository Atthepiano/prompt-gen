"""Base class for all PromptGen tabs.

Every tab is a QScrollArea wrapping a QWidget so content is always
scrollable — no clipping on small windows.

Subclasses implement `_build_ui(body: QWidget)` and, optionally:
  - `build_prompt() -> str`        called by main window for generation
  - `save_dir() -> str`            per-tab save directory
  - `image_prefix -> str`          filename prefix for saved images
  - `get_reference_images() -> list[bytes]`
  - `on_tab_activated()`           called when this tab is switched to
  - `on_image_saved(path: str)`    called after the image is saved
"""

from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QSizePolicy


class BaseTab(QScrollArea):
    image_prefix: str = "image"
    text_last:    bool = False

    def __init__(self, window, parent=None):
        super().__init__(parent)
        self.window = window   # reference to MainWindow

        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        body = QWidget()
        body.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        self._layout = QVBoxLayout(body)
        self._layout.setContentsMargins(12, 12, 12, 12)
        self._layout.setSpacing(8)
        self.setWidget(body)

        self._build_ui(body)
        # Push content to the top, not stretching to fill space
        self._layout.addStretch(1)

    def _build_ui(self, body: QWidget):
        """Override in each tab to add widgets to *body* via self._layout."""
        raise NotImplementedError

    # ── Optional overrides ─────────────────────────────────────────────

    def build_prompt(self) -> str:
        return ""

    def save_dir(self) -> str:
        return ""

    def get_reference_images(self) -> list[bytes]:
        return []

    def on_tab_activated(self):
        pass

    def on_image_saved(self, path: str):
        pass

    # ── Helper: set output text in the right panel ─────────────────────

    def set_output(self, text: str):
        self.window.set_output(text)

    def set_status(self, msg: str):
        self.window.set_status(msg)

    def t(self, text: str) -> str:
        return self.window.t(text)

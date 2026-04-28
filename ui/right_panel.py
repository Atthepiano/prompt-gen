"""Right-side panel: output log, image preview, action buttons, status bar."""

from __future__ import annotations
import os
from io import BytesIO

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QImage, QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QComboBox, QSizePolicy,
    QScrollArea, QGridLayout, QFrame,
)

from ui.styles import PALETTE as P


class ImageThumbnail(QLabel):
    """A clickable thumbnail used inside the batch-preview grid."""
    clicked = Signal(int)

    def __init__(self, index: int, parent=None):
        super().__init__(parent)
        self._index = index
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(QSize(128, 128))
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(
            f"border: 2px solid {P['border']}; border-radius: 4px;"
            f"background-color: {P['surface2']};"
        )

    def mousePressEvent(self, _event):
        self.clicked.emit(self._index)

    def set_selected(self, selected: bool):
        colour = P["accent"] if selected else P["border"]
        self.setStyleSheet(
            f"border: 2px solid {colour}; border-radius: 4px;"
            f"background-color: {P['surface2']};"
        )


class RightPanel(QWidget):
    """The right half of the main window.

    Signals
    -------
    save_requested()
    discard_requested()
    edit_requested()
    undo_edit_requested()
    generate_image_requested(concurrent: int)
    copy_requested()
    """

    save_requested         = Signal()
    discard_requested      = Signal()
    edit_requested         = Signal()
    undo_edit_requested    = Signal()
    generate_image_requested = Signal(int)   # concurrent count
    copy_requested         = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pending_images: list[bytes | None] = []
        self._active_index = 0
        self._undo_stack: list[bytes] = []
        self._current_bytes: bytes | None = None
        self._current_mime: str = "image/png"
        self._build_ui()

    # ── Build ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        # ── Output log ──
        lbl_out = QLabel("Generated Output / Logs:")
        lbl_out.setObjectName("header")
        root.addWidget(lbl_out)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFixedHeight(140)
        self.output_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        root.addWidget(self.output_text)

        # ── Image preview header ──
        lbl_prev = QLabel("Image Preview:")
        lbl_prev.setObjectName("header")
        root.addWidget(lbl_prev)

        # Single-image preview label
        self.preview_label = QLabel("No preview image")
        self.preview_label.setObjectName("preview_placeholder")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(200)
        self.preview_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        root.addWidget(self.preview_label)

        # Batch grid (hidden by default)
        grid_container = QScrollArea()
        grid_container.setWidgetResizable(True)
        grid_container.setMaximumHeight(160)
        grid_container.setVisible(False)
        self._grid_container = grid_container

        self._grid_widget = QWidget()
        self._grid_layout = QGridLayout(self._grid_widget)
        self._grid_layout.setSpacing(4)
        grid_container.setWidget(self._grid_widget)
        root.addWidget(grid_container)

        # Prev / Next navigation (visible during batch)
        nav_frame = QWidget()
        nav_frame.setVisible(False)
        self._nav_frame = nav_frame
        nav_layout = QHBoxLayout(nav_frame)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        self.btn_prev = QPushButton("◀  Previous")
        self.btn_next = QPushButton("Next  ▶")
        self.btn_prev.clicked.connect(self._on_prev)
        self.btn_next.clicked.connect(self._on_next)
        nav_layout.addWidget(self.btn_prev)
        nav_layout.addWidget(self.btn_next)
        root.addWidget(nav_frame)

        # ── Action buttons ──
        btn_row = QHBoxLayout()
        self.btn_save    = QPushButton("Save Image")
        self.btn_discard = QPushButton("Discard Image")
        self.btn_edit    = QPushButton("Edit Image")
        self.btn_undo    = QPushButton("Undo Edit")
        for btn in (self.btn_save, self.btn_discard, self.btn_edit, self.btn_undo):
            btn.setEnabled(False)
            btn_row.addWidget(btn)
        self.btn_save.clicked.connect(self.save_requested)
        self.btn_discard.clicked.connect(self.discard_requested)
        self.btn_edit.clicked.connect(self.edit_requested)
        self.btn_undo.clicked.connect(self.undo_edit_requested)
        root.addLayout(btn_row)

        # ── Concurrency + copy row ──
        ctrl_row = QHBoxLayout()
        ctrl_row.addWidget(QLabel("Concurrent images:"))
        self.concurrent_combo = QComboBox()
        self.concurrent_combo.addItems(["1", "2", "4", "6", "8"])
        self.concurrent_combo.setFixedWidth(60)
        ctrl_row.addWidget(self.concurrent_combo)
        ctrl_row.addStretch()

        self.btn_copy = QPushButton("Copy to Clipboard")
        ctrl_row.addWidget(self.btn_copy)
        self.btn_copy.clicked.connect(self.copy_requested)
        root.addLayout(ctrl_row)

        # ── Generate image button ──
        self.btn_gen = QPushButton("Generate Image")
        self.btn_gen.setObjectName("primary")
        self.btn_gen.clicked.connect(self._on_generate)
        root.addWidget(self.btn_gen)

    # ── Slots / helpers ───────────────────────────────────────────────────

    def _on_generate(self):
        count = int(self.concurrent_combo.currentText())
        self.generate_image_requested.emit(count)

    def _on_prev(self):
        if self._active_index > 0:
            self._show_image_at(self._active_index - 1)

    def _on_next(self):
        if self._active_index < len(self._pending_images) - 1:
            self._show_image_at(self._active_index + 1)

    def _show_image_at(self, index: int):
        if index < 0 or index >= len(self._pending_images):
            return
        data = self._pending_images[index]
        if data is None:
            return
        self._active_index = index
        self._set_preview_bytes(data)
        # highlight thumbnail
        for i, thumb in enumerate(self._thumbs):
            thumb.set_selected(i == index)

    # ── Public API ────────────────────────────────────────────────────────

    def set_output(self, text: str):
        self.output_text.setPlainText(text)

    def append_output(self, text: str):
        self.output_text.append(text)

    def set_busy(self, busy: bool):
        self.btn_gen.setEnabled(not busy)
        if busy:
            self.btn_edit.setEnabled(False)

    def set_generate_button_label(self, label: str):
        self.btn_gen.setText(label)

    # ── Image display ─────────────────────────────────────────────────────

    def _bytes_to_pixmap(self, data: bytes) -> QPixmap:
        img = QImage()
        img.loadFromData(data)
        return QPixmap.fromImage(img)

    def _set_preview_bytes(self, data: bytes):
        """Show *data* in the main preview label, scaled to fit."""
        pix = self._bytes_to_pixmap(data)
        scaled = pix.scaled(
            self.preview_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.preview_label.setPixmap(scaled)
        self._current_bytes = data

    def show_single_image(self, data: bytes, mime: str = "image/png"):
        """Display one image; switch to single-view mode."""
        self._pending_images = [data]
        self._active_index = 0
        self._current_bytes = data
        self._current_mime = mime
        self._undo_stack.clear()

        self._grid_container.setVisible(False)
        self._nav_frame.setVisible(False)
        self._set_preview_bytes(data)
        self.preview_label.setVisible(True)

        self.btn_save.setEnabled(True)
        self.btn_discard.setEnabled(True)
        self.btn_edit.setEnabled(True)
        self.btn_undo.setEnabled(False)

    def show_batch_images(self, images: list[bytes], mime: str = "image/png"):
        """Display multiple images; first one shown large, rest as thumbnails."""
        self._pending_images = list(images)
        self._active_index = 0
        self._current_bytes = images[0] if images else None
        self._current_mime = mime
        self._undo_stack.clear()

        # Clear old grid
        for i in reversed(range(self._grid_layout.count())):
            self._grid_layout.itemAt(i).widget().deleteLater()

        self._thumbs: list[ImageThumbnail] = []
        for idx, data in enumerate(images):
            thumb = ImageThumbnail(idx)
            thumb.clicked.connect(self._show_image_at)
            pix = self._bytes_to_pixmap(data).scaled(
                QSize(120, 120), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            thumb.setPixmap(pix)
            col = idx % 6
            row = idx // 6
            self._grid_layout.addWidget(thumb, row, col)
            self._thumbs.append(thumb)

        self._thumbs[0].set_selected(True)
        self._set_preview_bytes(images[0])
        self.preview_label.setVisible(True)
        self._grid_container.setVisible(len(images) > 1)
        self._nav_frame.setVisible(len(images) > 1)

        self.btn_save.setEnabled(True)
        self.btn_discard.setEnabled(True)
        self.btn_edit.setEnabled(True)
        self.btn_undo.setEnabled(False)

    def clear_preview(self):
        self._pending_images = []
        self._active_index = 0
        self._current_bytes = None
        self._undo_stack.clear()
        self.preview_label.setText("No preview image")
        self.preview_label.setPixmap(QPixmap())
        self._grid_container.setVisible(False)
        self._nav_frame.setVisible(False)
        self.btn_save.setEnabled(False)
        self.btn_discard.setEnabled(False)
        self.btn_edit.setEnabled(False)
        self.btn_undo.setEnabled(False)

    def push_edit(self, data: bytes, mime: str = "image/png"):
        """Called after a successful image edit; keeps undo history."""
        if self._current_bytes:
            self._undo_stack.append(self._current_bytes)
        self._current_bytes = data
        self._current_mime = mime
        self._pending_images[self._active_index] = data
        self._set_preview_bytes(data)
        self.btn_undo.setEnabled(True)

    def pop_undo(self) -> bytes | None:
        """Revert to previous version; returns the reverted bytes or None."""
        if not self._undo_stack:
            return None
        prev = self._undo_stack.pop()
        self._current_bytes = prev
        self._pending_images[self._active_index] = prev
        self._set_preview_bytes(prev)
        self.btn_undo.setEnabled(bool(self._undo_stack))
        return prev

    # ── Accessors ─────────────────────────────────────────────────────────

    @property
    def current_image_bytes(self) -> bytes | None:
        return self._current_bytes

    @property
    def current_image_mime(self) -> str:
        return self._current_mime

    @property
    def active_index(self) -> int:
        return self._active_index

    @property
    def all_images(self) -> list[bytes]:
        return [b for b in self._pending_images if b is not None]

    def resizeEvent(self, event):
        """Re-scale the main preview when the panel is resized."""
        super().resizeEvent(event)
        if self._current_bytes:
            self._set_preview_bytes(self._current_bytes)

"""Asset Curation tab — image comparison / selection tool."""

from __future__ import annotations
import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QKeyEvent
from PySide6.QtWidgets import (
    QLabel, QPushButton, QListWidget, QAbstractItemView,
    QSplitter, QFrame, QFileDialog, QMessageBox,
    QHBoxLayout, QVBoxLayout, QScrollArea, QGridLayout, QWidget,
)

import curation_tool as ct
from ui.tabs.base_tab import BaseTab


class CurationTab(BaseTab):
    """Conflict-resolution curation tool: compare variant images and pick one."""

    def __init__(self, window, parent=None):
        self._curator = ct.AssetCurator()
        self._curation_queue: list[str] = []
        self._current_index: int = 0
        self._variant_paths: list[str] = []   # current item's variant paths
        super().__init__(window, parent)

    def _build_ui(self, body):
        lay = self._layout

        # ── Full-height splitter ───────────────────────────────────────────
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        lay.addWidget(splitter, 1)

        # ── SIDEBAR ───────────────────────────────────────────────────────
        sidebar = QWidget()
        sb_lay  = QVBoxLayout(sidebar)
        sb_lay.setContentsMargins(0, 0, 8, 0)
        sb_lay.setSpacing(8)

        sb_lay.addWidget(_bold("Configuration"))

        sb_lay.addWidget(QLabel("Target Folder (Output):"))
        self.edit_target = _line_row(sb_lay, "Browse Target…", self._browse_target)

        sb_lay.addWidget(_sep())

        sb_lay.addWidget(QLabel("Source Folders (Inputs):"))
        self.lst_sources = QListWidget()
        self.lst_sources.setSelectionMode(QAbstractItemView.SingleSelection)
        sb_lay.addWidget(self.lst_sources, 1)

        btn_batch = QPushButton("+ Add via File Selection…")
        btn_batch.clicked.connect(self._add_sources_batch)
        sb_lay.addWidget(btn_batch)

        row2 = QHBoxLayout()
        btn_folder = QPushButton("+ Add Folder")
        btn_folder.clicked.connect(self._add_source_folder)
        btn_remove  = QPushButton("− Remove")
        btn_remove.clicked.connect(self._remove_source)
        row2.addWidget(btn_folder)
        row2.addWidget(btn_remove)
        sb_lay.addLayout(row2)

        sb_lay.addWidget(_sep())

        self.lbl_status = QLabel("Ready")
        self.lbl_status.setObjectName("subheader")
        self.lbl_status.setWordWrap(True)
        sb_lay.addWidget(self.lbl_status)

        self.btn_start = QPushButton("START SESSION")
        self.btn_start.setObjectName("primary")
        self.btn_start.clicked.connect(self._start_session)
        sb_lay.addWidget(self.btn_start)

        sidebar.setMinimumWidth(240)
        sidebar.setMaximumWidth(360)

        # ── MAIN VIEW ─────────────────────────────────────────────────────
        main_w  = QWidget()
        main_lay = QVBoxLayout(main_w)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(8)

        self.lbl_info = QLabel("Waiting to start…")
        self.lbl_info.setObjectName("header")
        self.lbl_info.setAlignment(Qt.AlignCenter)
        main_lay.addWidget(self.lbl_info)

        # Scrollable comparison grid
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._grid_widget = QWidget()
        self._grid_layout = QGridLayout(self._grid_widget)
        self._grid_layout.setSpacing(12)
        self._scroll_area.setWidget(self._grid_widget)
        main_lay.addWidget(self._scroll_area, 1)

        self.btn_skip = QPushButton("Skip / Discard All")
        self.btn_skip.setEnabled(False)
        self.btn_skip.clicked.connect(self._skip_item)
        main_lay.addWidget(self.btn_skip, 0, Qt.AlignCenter)

        # Assemble
        splitter.addWidget(sidebar)
        splitter.addWidget(main_w)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

    # ── Sidebar helpers ────────────────────────────────────────────────────

    def _browse_target(self):
        path = QFileDialog.getExistingDirectory(self, "Select Target Folder")
        if path:
            self.edit_target.setText(path)

    def _add_sources_batch(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Select any file inside source folder(s)", "",
            "All Files (*)")
        seen = set(self.lst_sources.item(i).text()
                   for i in range(self.lst_sources.count()))
        for fp in paths:
            folder = os.path.dirname(fp)
            if folder not in seen:
                self.lst_sources.addItem(folder)
                seen.add(folder)

    def _add_source_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Source Folder")
        if path:
            seen = {self.lst_sources.item(i).text()
                    for i in range(self.lst_sources.count())}
            if path not in seen:
                self.lst_sources.addItem(path)

    def _remove_source(self):
        row = self.lst_sources.currentRow()
        if row >= 0:
            self.lst_sources.takeItem(row)

    # ── Session logic ──────────────────────────────────────────────────────

    def _start_session(self):
        sources = [self.lst_sources.item(i).text()
                   for i in range(self.lst_sources.count())]
        target = self.edit_target.text().strip()

        if not sources:
            QMessageBox.warning(self, "Error", "Please add at least one source folder.")
            return
        if not target:
            QMessageBox.warning(self, "Error", "Please select a target folder.")
            return

        self._curator.set_config(sources, target)
        total, conflicts = self._curator.scan_files()
        auto = self._curator.auto_resolve_uniques()

        msg = (f"Scan complete.\n"
               f"Total files: {total}\n"
               f"Auto-resolved (unique): {auto}\n"
               f"Conflicts to review: {conflicts}")
        QMessageBox.information(self, "Session Started", msg)

        self._curation_queue   = self._curator.get_pending_conflicts()
        self._current_index    = 0
        self._load_next_item()

    def _load_next_item(self):
        if self._current_index >= len(self._curation_queue):
            self.lbl_info.setText("Session complete! All items resolved.")
            self._clear_grid()
            self.btn_skip.setEnabled(False)
            return

        filename = self._curation_queue[self._current_index]
        variants = self._curator.get_variants(filename)
        self._variant_paths = list(variants)

        prog = f"({self._current_index + 1}/{len(self._curation_queue)})"
        self.lbl_info.setText(f"{prog}  Comparing: {filename}")
        self.btn_skip.setEnabled(True)

        self._clear_grid()
        COL_LIMIT = 3
        for i, path in enumerate(self._variant_paths):
            row_i = i // COL_LIMIT
            col_i = i % COL_LIMIT

            cell = QFrame()
            cell.setFrameShape(QFrame.Box)
            cell_lay = QVBoxLayout(cell)
            cell_lay.setSpacing(4)

            pix = QPixmap(path)
            if pix.isNull():
                cell_lay.addWidget(QLabel("⚠ Error loading image"))
            else:
                pix = pix.scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                img_btn = _PixmapButton(pix)
                img_btn.clicked.connect(
                    lambda checked=False, p=path: self._select_item(p))
                cell_lay.addWidget(img_btn, 0, Qt.AlignCenter)

            hotkey = str(i + 1)
            lbl = QLabel(f"[{hotkey}] Source {i + 1}")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-weight: bold;")
            cell_lay.addWidget(lbl)

            src_folder = os.path.basename(os.path.dirname(path))
            sub = QLabel(src_folder)
            sub.setObjectName("subheader")
            sub.setAlignment(Qt.AlignCenter)
            cell_lay.addWidget(sub)

            self._grid_layout.addWidget(cell, row_i, col_i)

    def _clear_grid(self):
        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _select_item(self, path: str):
        filename = self._curation_queue[self._current_index]
        if self._curator.commit_selection(filename, path):
            self._current_index += 1
            self._load_next_item()
        else:
            QMessageBox.critical(self, "Error", "Failed to copy file.")

    def _skip_item(self):
        filename = self._curation_queue[self._current_index]
        self._curator.skip_file(filename)
        self._current_index += 1
        self._load_next_item()

    # ── Keyboard shortcuts ────────────────────────────────────────────────

    def keyPressEvent(self, event: QKeyEvent):
        key = event.text()
        if key in "123456789" and self._variant_paths:
            idx = int(key) - 1
            if 0 <= idx < len(self._variant_paths):
                self._select_item(self._variant_paths[idx])
                return
        super().keyPressEvent(event)

    def on_tab_activated(self):
        """Called when this tab becomes active (hook from MainWindow)."""
        self.setFocus()

    # ── BaseTab interface ─────────────────────────────────────────────────

    def build_prompt(self) -> str:
        return ""

    def save_dir(self) -> str:
        return self.edit_target.text().strip() or self.window.image_save_dir


# ── Helper widgets ─────────────────────────────────────────────────────────

class _PixmapButton(QPushButton):
    """A push-button that shows an image."""

    def __init__(self, pixmap: QPixmap, parent=None):
        super().__init__(parent)
        self.setIcon(pixmap)    # type: ignore[arg-type]
        from PySide6.QtCore import QSize
        self.setIconSize(QSize(pixmap.width(), pixmap.height()))
        self.setFixedSize(pixmap.width() + 8, pixmap.height() + 8)
        self.setCursor(Qt.PointingHandCursor)


def _bold(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("header")
    return lbl


def _line_row(parent_layout: QVBoxLayout, btn_text: str, callback) -> "QLineEdit":
    from PySide6.QtWidgets import QLineEdit
    row = QHBoxLayout()
    edit = QLineEdit()
    edit.setPlaceholderText("(none)")
    btn  = QPushButton(btn_text)
    btn.setFixedWidth(140)
    btn.clicked.connect(callback)
    row.addWidget(edit, 1)
    row.addWidget(btn)
    parent_layout.addLayout(row)
    return edit


def _sep() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.HLine)
    return f

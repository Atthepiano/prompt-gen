"""Asset Library tab — browse, filter, rate, and manage saved generations."""

from __future__ import annotations
import json
import mimetypes
import os
import subprocess

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QLabel, QPushButton, QComboBox, QSpinBox, QLineEdit, QTextEdit,
    QTreeWidget, QTreeWidgetItem, QGroupBox,
    QSplitter, QFrame, QMessageBox,
    QHBoxLayout, QVBoxLayout, QWidget,
)

from ui.tabs.base_tab import BaseTab


class LibraryTab(BaseTab):
    """Browse all saved library entries, rate them, and act on them."""

    def __init__(self, window, parent=None):
        self._selected_id: int | None = None
        super().__init__(window, parent)

    def _build_ui(self, body):
        from core import library as _lib
        self._lib = _lib

        lay = self._layout

        # ── Toolbar ───────────────────────────────────────────────────────
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        toolbar.addWidget(QLabel("Type:"))
        self.combo_type = QComboBox()
        type_options = ["(all)", "spaceship", "mecha", "mecha_part", "ship",
                        "items", "character", "clothing", "slicer",
                        "curation", "gemini", "clothing_swap"]
        self.combo_type.addItems(type_options)
        self.combo_type.setFixedWidth(130)
        toolbar.addWidget(self.combo_type)

        toolbar.addWidget(QLabel("Min ★:"))
        self.spin_rating = QSpinBox()
        self.spin_rating.setRange(0, 5)
        self.spin_rating.setFixedWidth(50)
        toolbar.addWidget(self.spin_rating)

        toolbar.addWidget(QLabel("Search:"))
        self.edit_search = QLineEdit()
        self.edit_search.setPlaceholderText("keyword…")
        self.edit_search.setFixedWidth(200)
        self.edit_search.returnPressed.connect(self._refresh)
        toolbar.addWidget(self.edit_search)

        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self._refresh)
        toolbar.addWidget(btn_refresh)

        self.lbl_count = QLabel("")
        self.lbl_count.setObjectName("subheader")
        toolbar.addWidget(self.lbl_count)
        toolbar.addStretch(1)
        lay.addLayout(toolbar)

        # ── Splitter: tree left | detail right ────────────────────────────
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        lay.addWidget(splitter, 1)

        # ── LEFT: Tree ────────────────────────────────────────────────────
        self.tree = QTreeWidget()
        self.tree.setColumnCount(5)
        self.tree.setHeaderLabels(["ID", "Time", "Type", "★", "Prompt / Notes"])
        self.tree.setColumnWidth(0, 50)
        self.tree.setColumnWidth(1, 145)
        self.tree.setColumnWidth(2, 90)
        self.tree.setColumnWidth(3, 40)
        self.tree.setColumnWidth(4, 340)
        self.tree.setRootIsDecorated(False)
        self.tree.setSortingEnabled(True)
        self.tree.itemSelectionChanged.connect(self._on_select)
        splitter.addWidget(self.tree)

        # ── RIGHT: Detail ─────────────────────────────────────────────────
        detail = QWidget()
        detail.setMinimumWidth(380)
        detail.setMaximumWidth(500)
        d_lay = QVBoxLayout(detail)
        d_lay.setContentsMargins(8, 0, 0, 0)
        d_lay.setSpacing(8)

        self.lbl_preview = QLabel("No preview image")
        self.lbl_preview.setAlignment(Qt.AlignCenter)
        self.lbl_preview.setFrameShape(QFrame.Box)
        self.lbl_preview.setMinimumHeight(200)
        self.lbl_preview.setMaximumHeight(380)
        d_lay.addWidget(self.lbl_preview)

        grp = QGroupBox("Details")
        g_lay = QVBoxLayout(grp)

        # Rating + Tags row
        meta_row = QHBoxLayout()
        meta_row.addWidget(QLabel("★"))
        self.spin_entry_rating = QSpinBox()
        self.spin_entry_rating.setRange(0, 5)
        self.spin_entry_rating.setFixedWidth(50)
        self.spin_entry_rating.valueChanged.connect(self._save_rating)
        meta_row.addWidget(self.spin_entry_rating)
        meta_row.addWidget(QLabel("Tags:"))
        self.edit_tags = QLineEdit()
        self.edit_tags.setPlaceholderText("comma-separated tags")
        self.edit_tags.editingFinished.connect(self._save_tags)
        meta_row.addWidget(self.edit_tags, 1)
        g_lay.addLayout(meta_row)

        self.txt_detail = QTextEdit()
        self.txt_detail.setReadOnly(True)
        self.txt_detail.setMinimumHeight(120)
        g_lay.addWidget(self.txt_detail, 1)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_copy   = QPushButton("Copy Prompt")
        btn_folder = QPushButton("Open Folder")
        btn_gemini = QPushButton("Edit with Gemini")
        btn_delete = QPushButton("Delete Entry")
        btn_copy.clicked.connect(self._copy_prompt)
        btn_folder.clicked.connect(self._open_folder)
        btn_gemini.clicked.connect(self._edit_with_gemini)
        btn_delete.clicked.connect(self._delete_entry)
        btn_row.addWidget(btn_copy)
        btn_row.addWidget(btn_folder)
        btn_row.addWidget(btn_gemini)
        btn_row.addStretch(1)
        btn_row.addWidget(btn_delete)
        g_lay.addLayout(btn_row)

        grp.setLayout(g_lay)
        d_lay.addWidget(grp, 1)

        splitter.addWidget(detail)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)

        self._refresh()

    # ── Data ──────────────────────────────────────────────────────────────

    def _refresh(self):
        gtype = self.combo_type.currentText()
        if gtype == "(all)":
            gtype = None
        kw = self.edit_search.text().strip() or None
        min_r = self.spin_rating.value()

        entries = self._lib.list_entries(
            generator_type=gtype,
            min_rating=min_r,
            keyword=kw,
            limit=500,
        )

        self.tree.setSortingEnabled(False)
        self.tree.clear()
        for e in entries:
            time_str = e.created_at.replace("T", " ").rsplit("+", 1)[0]
            stars    = "★" * e.rating + "·" * (5 - e.rating)
            preview  = (e.prompt or e.notes or "").replace("\n", " ")
            if len(preview) > 80:
                preview = preview[:80] + "…"
            item = QTreeWidgetItem([
                str(e.id), time_str, e.generator_type, stars, preview])
            item.setData(0, Qt.UserRole, e.id)
            item.setTextAlignment(0, Qt.AlignRight | Qt.AlignVCenter)
            item.setTextAlignment(3, Qt.AlignCenter)
            self.tree.addTopLevelItem(item)

        self.tree.setSortingEnabled(True)
        self.lbl_count.setText(f"{len(entries)} entries")

    def _on_select(self):
        items = self.tree.selectedItems()
        if not items:
            return
        entry_id = items[0].data(0, Qt.UserRole)
        if entry_id is None:
            return

        entry = self._lib.get_entry(int(entry_id))
        if not entry:
            return
        self._selected_id = entry.id

        # Rating & tags (block signals to avoid triggering save)
        self.spin_entry_rating.blockSignals(True)
        self.spin_entry_rating.setValue(entry.rating)
        self.spin_entry_rating.blockSignals(False)
        self.edit_tags.blockSignals(True)
        self.edit_tags.setText(", ".join(entry.tags))
        self.edit_tags.blockSignals(False)

        # Detail text
        params_str = (json.dumps(entry.params, ensure_ascii=False, indent=2)
                      if entry.params else "(none)")
        body = (
            f"# Image\n{entry.image_path}\n\n"
            f"# Created\n{entry.created_at}\n\n"
            f"# Generator\n{entry.generator_type}\n\n"
            f"# Batch\n{entry.source_batch_id or '-'}\n\n"
            f"# Notes\n{entry.notes or '-'}\n\n"
            f"# Params\n{params_str}\n\n"
            f"# Prompt\n{entry.prompt or '-'}\n"
        )
        self.txt_detail.setPlainText(body)

        # Preview image
        self.lbl_preview.setPixmap(QPixmap())
        self.lbl_preview.setText("No preview image")
        if entry.image_path and os.path.exists(entry.image_path):
            pix = QPixmap(entry.image_path)
            if not pix.isNull():
                pix = pix.scaled(380, 380, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.lbl_preview.setPixmap(pix)
                self.lbl_preview.setText("")

    # ── Actions ───────────────────────────────────────────────────────────

    def _save_rating(self, value: int):
        if self._selected_id is None:
            return
        self._lib.update_rating(self._selected_id, value)
        # Update star column in-place
        items = self.tree.findItems(str(self._selected_id), Qt.MatchExactly, 0)
        if items:
            items[0].setText(3, "★" * value + "·" * (5 - value))

    def _save_tags(self):
        if self._selected_id is None:
            return
        raw  = self.edit_tags.text()
        tags = [t.strip() for t in raw.replace("，", ",").split(",") if t.strip()]
        self._lib.update_tags(self._selected_id, tags)

    def _copy_prompt(self):
        if self._selected_id is None:
            return
        entry = self._lib.get_entry(self._selected_id)
        if not entry or not entry.prompt:
            return
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(entry.prompt)
        self.window.set_status("Prompt copied to clipboard!")

    def _open_folder(self):
        if self._selected_id is None:
            return
        entry = self._lib.get_entry(self._selected_id)
        if not entry or not entry.image_path:
            return
        if not os.path.exists(entry.image_path):
            QMessageBox.information(self, "Info", "File no longer exists.")
            return
        try:
            if os.name == "nt":
                subprocess.Popen(["explorer", "/select,", os.path.normpath(entry.image_path)])
            else:
                subprocess.Popen(["xdg-open", os.path.dirname(entry.image_path)])
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _edit_with_gemini(self):
        if self._selected_id is None:
            return
        entry = self._lib.get_entry(self._selected_id)
        if not entry:
            return
        if not entry.image_path or not os.path.exists(entry.image_path):
            QMessageBox.critical(self, "Error", "File no longer exists.")
            return
        _, api_key, _, _ = self.window.get_credentials()
        if not api_key:
            QMessageBox.warning(self, "No API Key", "Add your API key in Settings first.")
            return
        try:
            with open(entry.image_path, "rb") as fh:
                image_bytes = fh.read()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return
        mime = mimetypes.guess_type(entry.image_path)[0] or "image/png"
        self.window.load_image_for_edit(
            image_bytes, mime,
            prefix=f"{entry.generator_type}_edit",
            batch_id=f"edit:{entry.id}",
            initial_prompt=entry.prompt or "",
        )

    def _delete_entry(self):
        if self._selected_id is None:
            return
        reply = QMessageBox.question(
            self, "Confirm",
            "Delete this library entry?\n(The image file is kept on disk.)",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        self._lib.delete_entry(self._selected_id)
        self._selected_id = None
        self.txt_detail.clear()
        self.lbl_preview.setText("No preview image")
        self.lbl_preview.setPixmap(QPixmap())
        self._refresh()

    # ── Tab hooks ─────────────────────────────────────────────────────────

    def on_tab_activated(self):
        """Auto-refresh when switching to this tab."""
        self._refresh()

    def build_prompt(self) -> str:
        return ""

    def save_dir(self) -> str:
        return self.window.image_save_dir

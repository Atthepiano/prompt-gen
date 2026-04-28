"""Item Icons tab."""

from __future__ import annotations
import os

from PySide6.QtWidgets import (
    QLabel, QCheckBox, QPushButton, QHBoxLayout,
    QFileDialog, QMessageBox,
)

import item_generator as ig
from ui.tabs.base_tab import BaseTab
from ui.workers import ItemPromptWorker


class ItemsTab(BaseTab):
    image_prefix = "items"

    def __init__(self, window, parent=None):
        self._csv_path = ig.DEFAULT_CSV_PATH
        super().__init__(window, parent)

    def _build_ui(self, body):
        lay = self._layout

        title = QLabel("Item Icon Generation")
        title.setObjectName("header")
        lay.addWidget(title)

        desc = QLabel(
            "Generates a prompt for a 8×8 sprite sheet (64 items) "
            "from the selected CSV file.")
        desc.setObjectName("subheader")
        desc.setWordWrap(True)
        lay.addWidget(desc)

        # ── CSV selection ──
        csv_row = QHBoxLayout()
        btn_csv = QPushButton("Select CSV…")
        btn_csv.clicked.connect(self._select_csv)
        self.lbl_csv = QLabel(os.path.basename(self._csv_path))
        csv_row.addWidget(btn_csv)
        csv_row.addWidget(self.lbl_csv, 1)
        lay.addLayout(csv_row)

        # status
        exists = os.path.exists(self._csv_path)
        self.lbl_status = QLabel(
            f"✓ CSV found: {self._csv_path}" if exists
            else f"✗ CSV not found: {self._csv_path}")
        self.lbl_status.setObjectName("subheader")
        self.lbl_status.setWordWrap(True)
        lay.addWidget(self.lbl_status)

        # ── Options ──
        self.chk_translate = QCheckBox(
            "Auto-Translate Content to English (Recommended)")
        self.chk_translate.setChecked(True)
        lay.addWidget(self.chk_translate)

        self.chk_cache = QCheckBox("Write Translation Result into CSV (Cache)")
        self.chk_cache.setChecked(True)
        lay.addWidget(self.chk_cache)

        # ── Generate ──
        self.btn_gen = QPushButton("GENERATE ICON GRID (8×8)")
        self.btn_gen.setObjectName("primary")
        self.btn_gen.setEnabled(exists)
        self.btn_gen.clicked.connect(self._generate)
        lay.addWidget(self.btn_gen)

    def _select_csv(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select CSV", os.path.dirname(self._csv_path),
            "CSV Files (*.csv);;All Files (*)")
        if path:
            self._csv_path = path
            self.lbl_csv.setText(os.path.basename(path))
            exists = os.path.exists(path)
            self.lbl_status.setText(
                f"✓ CSV selected: {path}" if exists
                else f"✗ File not found: {path}")
            self.btn_gen.setEnabled(exists)

    def _generate(self):
        self.window.set_busy(True, "Generating prompt…")
        w = ItemPromptWorker(
            self._csv_path,
            self.chk_translate.isChecked(),
            self.chk_cache.isChecked(),
        )
        w.finished.connect(self._on_done)
        w.error.connect(self._on_error)
        self.window._active_workers.append(w)
        w.finished.connect(lambda _: self.window._active_workers.remove(w))
        w.start()

    def _on_done(self, prompt: str):
        self.window.set_busy(False, "Prompt generated.")
        self.set_output(prompt)

    def _on_error(self, msg: str):
        self.window.set_busy(False, "Error.")
        QMessageBox.critical(self, "Error", msg)

    def save_dir(self) -> str:
        return self.window.items_save_dir or self.window.image_save_dir

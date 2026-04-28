"""Image Slicer tab."""

from __future__ import annotations
import os
import sys

from PySide6.QtWidgets import (
    QLabel, QLineEdit, QPushButton, QCheckBox, QGroupBox,
    QHBoxLayout, QGridLayout, QFrame, QFileDialog, QMessageBox,
)

import item_generator as ig
from ui.tabs.base_tab import BaseTab
from ui.workers import SlicerWorker


class SlicerTab(BaseTab):

    def __init__(self, window, parent=None):
        self._slicer_files: list[str] = []
        self._csv_path = ig.DEFAULT_CSV_PATH
        super().__init__(window, parent)

    def _build_ui(self, body):
        lay = self._layout

        title = QLabel("Image Slicer")
        title.setObjectName("header")
        lay.addWidget(title)

        # ── 1. Input ──
        sec1 = QLabel("1. Select Grid Image(s):")
        sec1.setObjectName("header")
        lay.addWidget(sec1)

        btn_row = QHBoxLayout()
        btn_files  = QPushButton("Select Image File(s)…")
        btn_folder = QPushButton("Select Folder (Batch)…")
        btn_files.clicked.connect(self._select_files)
        btn_folder.clicked.connect(self._select_folder)
        btn_row.addWidget(btn_files)
        btn_row.addWidget(btn_folder)
        lay.addLayout(btn_row)

        self.lbl_files = QLabel("No file selected")
        self.lbl_files.setObjectName("subheader")
        self.lbl_files.setWordWrap(True)
        lay.addWidget(self.lbl_files)

        # ── 2. Output dir ──
        sec2 = QLabel("2. Output Directory:")
        sec2.setObjectName("header")
        lay.addWidget(sec2)
        lay.addWidget(QLabel("(Leave empty → each image gets its own subfolder)"))

        outdir_row = QHBoxLayout()
        self.edit_outdir = QLineEdit()
        self.edit_outdir.setPlaceholderText("(auto)")
        btn_browse_out = QPushButton("Browse…")
        btn_browse_out.setFixedWidth(70)
        btn_browse_out.clicked.connect(self._browse_outdir)
        outdir_row.addWidget(self.edit_outdir)
        outdir_row.addWidget(btn_browse_out)
        lay.addLayout(outdir_row)

        # ── 3. Grid config ──
        grp_cfg = QGroupBox("Advanced Configuration")
        cfg_lay = QGridLayout(grp_cfg)

        cfg_lay.addWidget(QLabel("Grid Size (Row×Col):"), 0, 0)
        self.edit_grid = QLineEdit("8")
        self.edit_grid.setFixedWidth(50)
        cfg_lay.addWidget(self.edit_grid, 0, 1)

        cfg_lay.addWidget(QLabel("Norm Scale (0.1–1.0):"), 0, 2)
        self.edit_scale = QLineEdit("0.85")
        self.edit_scale.setFixedWidth(50)
        cfg_lay.addWidget(self.edit_scale, 0, 3)

        self.chk_smart = QCheckBox("Smart Crop (auto-detect grid — overrides row/col)")
        self.chk_smart.toggled.connect(self._toggle_smart)
        cfg_lay.addWidget(self.chk_smart, 1, 0, 1, 4)
        lay.addWidget(grp_cfg)

        # ── 4. Naming ──
        lay.addWidget(_sep())
        sec3 = QLabel("3. Naming Options:")
        sec3.setObjectName("header")
        lay.addWidget(sec3)

        rename_row = QHBoxLayout()
        rename_row.addWidget(QLabel("Rename:"))
        self.edit_rename = QLineEdit()
        self.edit_rename.setPlaceholderText("(optional — overrides CSV naming)")
        rename_row.addWidget(self.edit_rename)
        lay.addLayout(rename_row)

        self.chk_auto_suffix = QCheckBox(
            "Batch auto suffix (e.g. weapon_01_01, weapon_02_01)")
        self.chk_auto_suffix.setChecked(True)
        lay.addWidget(self.chk_auto_suffix)

        self.chk_csv_naming = QCheckBox("Use CSV for Filenames (Smart Naming)")
        self.chk_csv_naming.setChecked(True)
        self.chk_csv_naming.toggled.connect(self._toggle_csv_naming)
        lay.addWidget(self.chk_csv_naming)

        self.chk_translate = QCheckBox("Auto-Translate Filenames (ZH → EN)")
        self.chk_translate.setChecked(True)
        lay.addWidget(self.chk_translate)

        self.chk_cache = QCheckBox("Write Translation Result into CSV (Cache)")
        self.chk_cache.setChecked(True)
        lay.addWidget(self.chk_cache)

        csv_row = QHBoxLayout()
        self.btn_csv = QPushButton("Select CSV…")
        self.btn_csv.clicked.connect(self._select_csv)
        self.lbl_csv = QLabel(os.path.basename(self._csv_path))
        self.lbl_csv.setObjectName("subheader")
        csv_row.addWidget(self.btn_csv)
        csv_row.addWidget(self.lbl_csv, 1)
        lay.addLayout(csv_row)

        # ── 5. Processing ──
        lay.addWidget(_sep())
        sec4 = QLabel("4. Processing Options:")
        sec4.setObjectName("header")
        lay.addWidget(sec4)

        self.chk_remove_bg = QCheckBox("Remove Background" + (
            "" if self._rembg_available() else "  [Setup Required]"))
        lay.addWidget(self.chk_remove_bg)

        self.chk_normalize = QCheckBox("Normalize Size & Position (Trim & Center 90%)")
        lay.addWidget(self.chk_normalize)

        # ── Slice button ──
        lay.addWidget(_sep())
        self.btn_slice = QPushButton("SLICE INTO ICONS")
        self.btn_slice.setObjectName("primary")
        self.btn_slice.setEnabled(False)
        self.btn_slice.clicked.connect(self._slice)
        lay.addWidget(self.btn_slice)

    # ── Logic ─────────────────────────────────────────────────────────────

    def _rembg_available(self) -> bool:
        if getattr(sys, "frozen", False):
            return os.path.exists(os.path.join(
                os.path.dirname(sys.executable), "worker_rembg.exe"))
        venv_py = os.path.join(os.getcwd(), ".venv_rembg", "Scripts", "python.exe")
        return os.path.exists(venv_py)

    def _select_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Grid Image(s)", "",
            "Images (*.png *.jpg *.jpeg *.webp *.bmp);;All Files (*)")
        if paths:
            self._slicer_files = paths
            self.lbl_files.setText(
                f"{len(paths)} file(s) selected — "
                + ", ".join(os.path.basename(p) for p in paths[:3])
                + ("…" if len(paths) > 3 else ""))
            self.btn_slice.setEnabled(True)

    def _select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            exts = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
            files = [
                os.path.join(folder, f) for f in os.listdir(folder)
                if os.path.splitext(f)[1].lower() in exts]
            if files:
                self._slicer_files = files
                self.lbl_files.setText(
                    f"{len(files)} image(s) in {os.path.basename(folder)}/")
                self.btn_slice.setEnabled(True)
            else:
                QMessageBox.warning(self, "No images", "No image files found in that folder.")

    def _browse_outdir(self):
        path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if path:
            self.edit_outdir.setText(path)

    def _select_csv(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select CSV", os.path.dirname(self._csv_path),
            "CSV Files (*.csv);;All Files (*)")
        if path:
            self._csv_path = path
            self.lbl_csv.setText(os.path.basename(path))

    def _toggle_smart(self, checked: bool):
        self.edit_grid.setEnabled(not checked)

    def _toggle_csv_naming(self, checked: bool):
        self.chk_translate.setEnabled(checked)
        self.chk_cache.setEnabled(checked)
        self.btn_csv.setEnabled(checked)

    def _parse_grid(self):
        txt = self.edit_grid.text().strip()
        if "x" in txt.lower():
            parts = txt.lower().split("x")
            return int(parts[0]), int(parts[1])
        n = int(txt)
        return n, n

    def _slice(self):
        if not self._slicer_files:
            return
        try:
            rows, cols = self._parse_grid()
        except ValueError:
            QMessageBox.warning(self, "Invalid grid", "Enter grid size like '8' or '8x8'.")
            return
        try:
            scale = float(self.edit_scale.text())
        except ValueError:
            scale = 0.85

        out_dir = self.edit_outdir.text().strip() or None
        csv_path = self._csv_path if self.chk_csv_naming.isChecked() else None

        self.window.set_busy(True, "Slicing images…")
        w = SlicerWorker(
            files=self._slicer_files,
            rows=rows, cols=cols,
            out_dir=out_dir,
            csv_path=csv_path,
            translate=self.chk_translate.isChecked(),
            remove_bg=self.chk_remove_bg.isChecked(),
            cache=self.chk_cache.isChecked(),
            normalize=self.chk_normalize.isChecked(),
            scale=scale,
            rename=self.edit_rename.text().strip(),
            auto_suffix=self.chk_auto_suffix.isChecked(),
            smart_crop=self.chk_smart.isChecked(),
        )
        w.progress.connect(self.window.set_status)
        w.finished.connect(self._on_done)
        w.error.connect(self._on_error)
        self.window._active_workers.append(w)
        w.finished.connect(lambda _: self.window._active_workers.remove(w))
        w.start()

    def _on_done(self, result: dict):
        self.window.set_busy(False)
        success = result["success"]
        errors  = result["errors"]
        msg = f"Done. {success} image(s) sliced successfully."
        if errors:
            msg += f"\n{len(errors)} error(s):\n" + "\n".join(errors[:5])
            QMessageBox.warning(self, "Slicer", msg)
        else:
            self.window.set_status(msg)

    def _on_error(self, msg: str):
        self.window.set_busy(False)
        QMessageBox.critical(self, "Slicer Error", msg)


def _sep():
    f = QFrame()
    f.setFrameShape(QFrame.HLine)
    return f

"""Settings tab."""

from __future__ import annotations
import os

from PySide6.QtWidgets import (
    QLabel, QLineEdit, QComboBox, QPushButton, QGroupBox,
    QRadioButton, QButtonGroup, QHBoxLayout, QGridLayout,
    QWidget, QMessageBox, QFileDialog,
)

import gemini_service as gs
import core.openai_service as oi
from ui.tabs.base_tab import BaseTab


class SettingsTab(BaseTab):

    def __init__(self, window, parent=None):
        super().__init__(window, parent)

    def _build_ui(self, body):
        lay = self._layout
        cfg = self.window.config

        # ── Title ──
        title = QLabel("Settings")
        title.setObjectName("header")
        lay.addWidget(title)

        # ── API Provider ──
        grp_prov = QGroupBox("API Provider")
        prov_lay = QHBoxLayout(grp_prov)
        self.rb_gemini = QRadioButton("Gemini")
        self.rb_openai = QRadioButton("OpenAI")
        self._prov_group = QButtonGroup()
        self._prov_group.addButton(self.rb_gemini, 0)
        self._prov_group.addButton(self.rb_openai, 1)
        prov_lay.addWidget(self.rb_gemini)
        prov_lay.addWidget(self.rb_openai)
        prov_lay.addStretch()
        if self.window.api_provider == "OpenAI":
            self.rb_openai.setChecked(True)
        else:
            self.rb_gemini.setChecked(True)
        self._prov_group.buttonClicked.connect(self._on_provider_changed)
        lay.addWidget(grp_prov)

        # ── Gemini section ──
        self.grp_gemini = QGroupBox("Gemini")
        g_lay = QGridLayout(self.grp_gemini)
        g_lay.setColumnStretch(1, 1)

        g_lay.addWidget(QLabel("API Key:"), 0, 0)
        self.edit_gemini_key = QLineEdit(self.window.gemini_api_key)
        self.edit_gemini_key.setPlaceholderText("AIza…")
        g_lay.addWidget(self.edit_gemini_key, 0, 1)

        g_lay.addWidget(QLabel("Model:"), 1, 0)
        self.combo_gemini_model = QComboBox()
        opts = list(gs.IMAGE_MODELS)
        cur = self.window.gemini_model.replace("models/", "")
        if cur and cur not in opts:
            opts.insert(0, cur)
        self.combo_gemini_model.addItems(opts)
        if cur in opts:
            self.combo_gemini_model.setCurrentText(cur)
        g_lay.addWidget(self.combo_gemini_model, 1, 1)
        lay.addWidget(self.grp_gemini)

        # ── OpenAI section ──
        self.grp_openai = QGroupBox("OpenAI")
        o_lay = QGridLayout(self.grp_openai)
        o_lay.setColumnStretch(1, 1)

        o_lay.addWidget(QLabel("API Key:"), 0, 0)
        self.edit_openai_key = QLineEdit(self.window.openai_api_key)
        self.edit_openai_key.setPlaceholderText("sk-…")
        o_lay.addWidget(self.edit_openai_key, 0, 1)

        o_lay.addWidget(QLabel("Base URL:"), 1, 0)
        self.edit_openai_url = QLineEdit(self.window.openai_base_url)
        o_lay.addWidget(self.edit_openai_url, 1, 1)

        o_lay.addWidget(QLabel("Model:"), 2, 0)
        self.combo_openai_model = QComboBox()
        om_opts = list(oi.ALL_MODELS)
        cur_om = self.window.openai_model
        if cur_om and cur_om not in om_opts:
            om_opts.insert(0, cur_om)
        self.combo_openai_model.addItems(om_opts)
        self.combo_openai_model.setCurrentText(cur_om)
        o_lay.addWidget(self.combo_openai_model, 2, 1)

        o_lay.addWidget(QLabel("Image Size:"), 3, 0)
        self.combo_openai_size = QComboBox()
        self.combo_openai_size.addItems(oi.SIZES_GPT_IMAGE)
        self.combo_openai_size.setCurrentText(self.window.openai_image_size)
        o_lay.addWidget(self.combo_openai_size, 3, 1)

        o_lay.addWidget(QLabel("Image Quality:"), 4, 0)
        self.combo_openai_quality = QComboBox()
        self.combo_openai_quality.addItems(oi.QUALITY_OPTIONS)
        self.combo_openai_quality.setCurrentText(self.window.openai_image_quality)
        o_lay.addWidget(self.combo_openai_quality, 4, 1)
        lay.addWidget(self.grp_openai)

        self._on_provider_changed()   # set initial visibility

        # ── Save dirs ──
        grp_dirs = QGroupBox("Image Save Directories")
        d_lay = QGridLayout(grp_dirs)
        d_lay.setColumnStretch(1, 1)

        dir_defs = [
            ("Global Default:",  "edit_global_dir",    self.window.image_save_dir),
            ("Spaceship:",       "edit_spaceship_dir", self.window.spaceship_save_dir),
            ("Item Icons:",      "edit_items_dir",     self.window.items_save_dir),
            ("Character:",       "edit_character_dir", self.window.character_save_dir),
            ("Clothing:",        "edit_clothing_dir",  self.window.clothing_save_dir),
        ]
        for r, (lbl, attr, val) in enumerate(dir_defs):
            d_lay.addWidget(QLabel(lbl), r, 0)
            edit = QLineEdit(val)
            setattr(self, attr, edit)
            d_lay.addWidget(edit, r, 1)
            btn = QPushButton("Browse…")
            btn.setFixedWidth(70)
            btn.clicked.connect(lambda _, e=edit: self._browse_dir(e))
            d_lay.addWidget(btn, r, 2)
        lay.addWidget(grp_dirs)

        # ── Language ──
        grp_lang = QGroupBox("UI Language")
        l_lay = QHBoxLayout(grp_lang)
        self.combo_lang = QComboBox()
        self.combo_lang.addItems(["English", "Chinese (重启后生效)"])
        self.combo_lang.setCurrentIndex(1 if self.window.ui_lang == "zh" else 0)
        l_lay.addWidget(self.combo_lang)
        l_lay.addStretch()
        lay.addWidget(grp_lang)

        # ── Save button ──
        btn_save = QPushButton("Save Settings")
        btn_save.setObjectName("primary")
        btn_save.clicked.connect(self._save)
        lay.addWidget(btn_save)

    # ── Logic ─────────────────────────────────────────────────────────────

    def _on_provider_changed(self):
        is_openai = self.rb_openai.isChecked()
        self.grp_openai.setVisible(is_openai)
        self.grp_gemini.setVisible(not is_openai)

    def _browse_dir(self, edit: QLineEdit):
        path = QFileDialog.getExistingDirectory(
            self, "Select Directory", edit.text() or os.path.expanduser("~"))
        if path:
            edit.setText(path)

    def _save(self):
        cfg = {
            "api_provider":        "OpenAI" if self.rb_openai.isChecked() else "Gemini",
            "gemini_api_key":      self.edit_gemini_key.text().strip(),
            "gemini_model":        self.combo_gemini_model.currentText(),
            "openai_api_key":      self.edit_openai_key.text().strip(),
            "openai_base_url":     self.edit_openai_url.text().strip(),
            "openai_model":        self.combo_openai_model.currentText(),
            "openai_image_size":   self.combo_openai_size.currentText(),
            "openai_image_quality": self.combo_openai_quality.currentText(),
            "image_save_dir":      self.edit_global_dir.text().strip() or "outputs",
            "spaceship_save_dir":  self.edit_spaceship_dir.text().strip(),
            "items_save_dir":      self.edit_items_dir.text().strip(),
            "character_save_dir":  self.edit_character_dir.text().strip(),
            "clothing_save_dir":   self.edit_clothing_dir.text().strip(),
            "language":            "zh" if self.combo_lang.currentIndex() == 1 else "en",
        }
        self.window.on_settings_saved(cfg)
        QMessageBox.information(self, "Settings", "Settings saved.")

    # ── Public API for main_window ─────────────────────────────────────────

    def provider(self) -> str:
        return "OpenAI" if self.rb_openai.isChecked() else "Gemini"

    def get_credentials(self):
        """Return (provider, key, model, extra_kwargs)."""
        if self.rb_openai.isChecked():
            key     = self.edit_openai_key.text().strip()
            model   = self.combo_openai_model.currentText()
            base_url = self.edit_openai_url.text().strip() or oi.DEFAULT_BASE_URL
            size    = self.combo_openai_size.currentText()
            quality = self.combo_openai_quality.currentText()
            return "OpenAI", key, model, {
                "base_url": base_url, "size": size, "quality": quality}
        else:
            key   = self.edit_gemini_key.text().strip()
            model = self.combo_gemini_model.currentText()
            return "Gemini", key, model, {}

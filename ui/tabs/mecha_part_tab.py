"""Mecha Components tab (hand weapons, shields, shoulder pods)."""

from __future__ import annotations
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QLabel, QComboBox, QCheckBox, QPushButton,
    QFrame, QMessageBox, QColorDialog,
)

import mecha_part_generator as mpg
import prompt_generator as pg
from ui.tabs.base_tab import BaseTab


class MechaPartTab(BaseTab):
    image_prefix = "mecha_part"

    def __init__(self, window, parent=None):
        self._lang = window.ui_lang
        self._primary_color   = "#444444"
        self._secondary_color = "#00FFFF"
        super().__init__(window, parent)

    def _build_ui(self, body):
        lay = self._layout
        lang = self._lang

        title = QLabel("Mecha Component Prompt Generation")
        title.setObjectName("header")
        lay.addWidget(title)
        sub = QLabel(
            "Generate a 4-view reference sheet for an individual piece of mecha equipment "
            "(hand weapon, shield, shoulder pod).")
        sub.setObjectName("subheader")
        sub.setWordWrap(True)
        lay.addWidget(sub)
        lay.addWidget(_sep())

        # ── Component Category ──
        self._subcat_map = mpg.get_subcategory_label_map(lang)
        lay.addWidget(QLabel(self.t("Component Category:")))
        self.combo_subcat = QComboBox()
        self.combo_subcat.addItems(list(self._subcat_map.keys()))
        self.combo_subcat.currentIndexChanged.connect(self._update_variants)
        lay.addWidget(self.combo_subcat)

        # ── Structural Variant ──
        lay.addWidget(QLabel(self.t("Structural Variant (Form Factor):")))
        self.combo_variant = QComboBox()
        lay.addWidget(self.combo_variant)

        # ── Tech Tier ──
        self._tier_map = mpg.get_tier_label_map(lang)
        lay.addWidget(QLabel(self.t("Tech Tier:")))
        self.combo_tier = QComboBox()
        self.combo_tier.addItems(list(self._tier_map.keys()))
        self.combo_tier.setCurrentIndex(2)
        lay.addWidget(self.combo_tier)

        lay.addWidget(_sep())

        # ── Manufacturer ──
        lay.addWidget(QLabel(self.t("Manufacturer Preset")))
        self.combo_manu = QComboBox()
        self._manu_list = ["None / Generic"] + pg.get_manufacturer_names()
        self.combo_manu.addItems(self._manu_list)
        self.combo_manu.currentIndexChanged.connect(self._on_manu_change)
        lay.addWidget(self.combo_manu)

        self.lbl_manu_desc = QLabel("")
        self.lbl_manu_desc.setObjectName("subheader")
        self.lbl_manu_desc.setWordWrap(True)
        lay.addWidget(self.lbl_manu_desc)

        lay.addWidget(_sep())

        # ── Color override ──
        lay.addWidget(QLabel(self.t("Color Override")))
        self.chk_colors = QCheckBox(self.t("Enable Custom Colors"))
        self.chk_colors.toggled.connect(self._toggle_color_buttons)
        lay.addWidget(self.chk_colors)

        self.btn_primary = QPushButton(self.t("Pick Main Color"))
        self.btn_primary.setEnabled(False)
        self.btn_primary.clicked.connect(lambda: self._pick_color("primary"))
        lay.addWidget(self.btn_primary)

        self.btn_secondary = QPushButton(self.t("Pick Energy/Glow Color"))
        self.btn_secondary.setEnabled(False)
        self.btn_secondary.clicked.connect(lambda: self._pick_color("secondary"))
        lay.addWidget(self.btn_secondary)

        lay.addWidget(_sep())

        self.btn_gen = QPushButton(self.t("GENERATE MECHA COMPONENT PROMPT"))
        self.btn_gen.setObjectName("primary")
        self.btn_gen.clicked.connect(self._generate)
        lay.addWidget(self.btn_gen)

        self._update_variants()

    # ── Logic ─────────────────────────────────────────────────────────────

    def _update_variants(self):
        lang = self._lang
        sub_label = self.combo_subcat.currentText()
        sub_key = self._subcat_map.get(sub_label, sub_label)
        self._variant_map = mpg.get_variant_label_map(sub_key, lang)
        opts = list(self._variant_map.keys())
        self.combo_variant.clear()
        self.combo_variant.addItems(opts)

    def _on_manu_change(self):
        name = self.combo_manu.currentText()
        if name and name != "None / Generic":
            m = pg.get_manufacturer_by_name(name)
            if m:
                desc = f"{m.get('design_language', '')}  |  {m.get('color_palette', '')}"
                self.lbl_manu_desc.setText(desc)
            else:
                self.lbl_manu_desc.setText("")
        else:
            self.lbl_manu_desc.setText("")

    def _toggle_color_buttons(self):
        en = self.chk_colors.isChecked()
        self.btn_primary.setEnabled(en)
        self.btn_secondary.setEnabled(en)

    def _pick_color(self, slot: str):
        color = QColorDialog.getColor(parent=self)
        if not color.isValid():
            return
        hex_col = color.name()
        if slot == "primary":
            self._primary_color = hex_col
            self.btn_primary.setText(f"Main: {hex_col}")
            self.btn_primary.setStyleSheet(
                f"background-color:{hex_col}; color:{'#000' if _light(color) else '#fff'};")
        else:
            self._secondary_color = hex_col
            self.btn_secondary.setText(f"Glow: {hex_col}")
            self.btn_secondary.setStyleSheet(
                f"background-color:{hex_col}; color:{'#000' if _light(color) else '#fff'};")

    def _generate(self):
        sub_label  = self.combo_subcat.currentText()
        var_label  = self.combo_variant.currentText()
        tier_label = self.combo_tier.currentText()
        manu = self.combo_manu.currentText()

        sub_key  = self._subcat_map.get(sub_label, sub_label)
        var_key  = self._variant_map.get(var_label, var_label)
        tier_key = self._tier_map.get(tier_label, tier_label)

        if not sub_key or not tier_key:
            QMessageBox.warning(self, "Error", "Please select all options.")
            return

        manu_val = None if manu == "None / Generic" else manu
        p_col = self._primary_color   if self.chk_colors.isChecked() else None
        s_col = self._secondary_color if self.chk_colors.isChecked() else None

        prompt = mpg.generate_mecha_part_prompt_by_strings(
            tier_name=tier_key,
            subcategory_key=sub_key,
            primary_color=p_col,
            secondary_color=s_col,
            manufacturer_name=manu_val,
            variation_key=var_key,
        )
        self.set_output(prompt)

    def build_prompt(self) -> str:
        self._generate()
        return self.window.right.output_text.toPlainText()

    def save_dir(self) -> str:
        return self.window.image_save_dir


def _sep():
    f = QFrame()
    f.setFrameShape(QFrame.HLine)
    return f

def _light(c: QColor) -> bool:
    return (c.red() * 299 + c.green() * 587 + c.blue() * 114) / 1000 > 128

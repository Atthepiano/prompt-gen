"""Spaceship Components tab."""

from __future__ import annotations
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QLabel, QComboBox, QCheckBox, QPushButton,
    QHBoxLayout, QFrame, QMessageBox, QColorDialog, QWidget,
)

import prompt_generator as pg
from ui.tabs.base_tab import BaseTab


class SpaceshipTab(BaseTab):
    image_prefix = "spaceship_comp"

    def __init__(self, window, parent=None):
        self._primary_color   = None
        self._secondary_color = None
        super().__init__(window, parent)

    def _build_ui(self, body):
        lay = self._layout

        # ── Title ──
        title = QLabel("Spaceship Components")
        title.setObjectName("header")
        lay.addWidget(title)

        sub = QLabel("Generate a prompt for a single spaceship component reference sheet.")
        sub.setObjectName("subheader")
        sub.setWordWrap(True)
        lay.addWidget(sub)

        lay.addWidget(_sep())

        # ── Category ──
        lay.addWidget(QLabel(self.t("Component Category:")))
        self.combo_cat = QComboBox()
        self._component_map = pg.get_component_map()
        self.combo_cat.addItems(list(self._component_map.keys()))
        self.combo_cat.currentIndexChanged.connect(self._update_subcategories)
        lay.addWidget(self.combo_cat)

        # ── Subcategory ──
        lay.addWidget(QLabel(self.t("Subcategory:")))
        self.combo_sub = QComboBox()
        self.combo_sub.currentIndexChanged.connect(self._update_variants)
        lay.addWidget(self.combo_sub)

        # ── Structural Variant ──
        lay.addWidget(QLabel(self.t("Structural Variant (Form Factor):")))
        self.combo_var = QComboBox()
        lay.addWidget(self.combo_var)

        # ── Tech Tier ──
        lay.addWidget(QLabel(self.t("Tech Tier:")))
        self.combo_tier = QComboBox()
        self.combo_tier.addItems(pg.get_tier_list())
        self.combo_tier.setCurrentIndex(2)  # default Tier 3
        lay.addWidget(self.combo_tier)

        lay.addWidget(_sep())

        # ── Manufacturer ──
        manu_lbl = QLabel(self.t("Manufacturer Preset"))
        manu_lbl.setObjectName("header")
        lay.addWidget(manu_lbl)

        self.combo_manu = QComboBox()
        self._manu_list = ["None / Generic"] + pg.get_manufacturer_names()
        self.combo_manu.addItems(self._manu_list)
        self.combo_manu.currentIndexChanged.connect(self._on_manufacturer_change)
        lay.addWidget(self.combo_manu)

        self.lbl_manu_desc = QLabel("")
        self.lbl_manu_desc.setObjectName("subheader")
        self.lbl_manu_desc.setWordWrap(True)
        lay.addWidget(self.lbl_manu_desc)

        lay.addWidget(_sep())

        # ── Color override ──
        color_lbl = QLabel(self.t("Color Override"))
        color_lbl.setObjectName("header")
        lay.addWidget(color_lbl)

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

        # ── Generate ──
        self.btn_gen = QPushButton(self.t("GENERATE COMPONENT PROMPT"))
        self.btn_gen.setObjectName("primary")
        self.btn_gen.clicked.connect(self._generate)
        lay.addWidget(self.btn_gen)

        # Initialise cascades
        self._update_subcategories()

    # ── Cascades ──────────────────────────────────────────────────────────

    def _update_subcategories(self):
        cat = self.combo_cat.currentText()
        subs = self._component_map.get(cat, [])
        self.combo_sub.blockSignals(True)
        self.combo_sub.clear()
        self.combo_sub.addItems(subs)
        self.combo_sub.blockSignals(False)
        self._update_variants()

    def _update_variants(self):
        cat = self.combo_cat.currentText()
        sub = self.combo_sub.currentText()
        variants = pg.get_variants_for_subcategory(cat, sub)
        self.combo_var.clear()
        if variants:
            self.combo_var.addItems(variants)
        else:
            self.combo_var.addItem("Standard")

    def _on_manufacturer_change(self):
        name = self.combo_manu.currentText()
        if name and name != "None / Generic":
            data = pg.get_manufacturer_by_name(name)
            self.lbl_manu_desc.setText(data.get("description", "") if data else "")
            self.chk_colors.setChecked(False)
            self.chk_colors.setEnabled(False)
        else:
            self.lbl_manu_desc.setText("")
            self.chk_colors.setEnabled(True)
        self._toggle_color_buttons()

    def _toggle_color_buttons(self):
        enabled = self.chk_colors.isChecked() and self.chk_colors.isEnabled()
        self.btn_primary.setEnabled(enabled)
        self.btn_secondary.setEnabled(enabled)

    def _pick_color(self, slot: str):
        color = QColorDialog.getColor(parent=self)
        if not color.isValid():
            return
        hex_col = color.name()
        if slot == "primary":
            self._primary_color = hex_col
            self.btn_primary.setText(f"Main: {hex_col}")
            self.btn_primary.setStyleSheet(
                f"background-color: {hex_col}; color: {'#000' if _is_light(color) else '#fff'};")
        else:
            self._secondary_color = hex_col
            self.btn_secondary.setText(f"Glow: {hex_col}")
            self.btn_secondary.setStyleSheet(
                f"background-color: {hex_col}; color: {'#000' if _is_light(color) else '#fff'};")

    # ── Generation ────────────────────────────────────────────────────────

    def _generate(self):
        tier = self.combo_tier.currentText()
        cat  = self.combo_cat.currentText()
        sub  = self.combo_sub.currentText()
        var  = self.combo_var.currentText()
        manu = self.combo_manu.currentText()

        if not (tier and cat and sub):
            QMessageBox.warning(self, "Error", "Please select all options.")
            return

        p_col = self._primary_color   if self.chk_colors.isChecked() else None
        s_col = self._secondary_color if self.chk_colors.isChecked() else None
        manu_val = None if manu == "None / Generic" else manu

        prompt = pg.generate_prompt_by_strings(
            tier, cat, sub,
            primary_color=p_col,
            secondary_color=s_col,
            manufacturer_name=manu_val,
            variation_name=var,
        )
        self.set_output(prompt)

    def build_prompt(self) -> str:
        self._generate()
        return self.window.right.output_text.toPlainText()

    def save_dir(self) -> str:
        return self.window.spaceship_save_dir or self.window.image_save_dir


# ── Utilities ──────────────────────────────────────────────────────────────

def _sep() -> QFrame:
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    return line


def _is_light(color: QColor) -> bool:
    """Return True if the colour is light (use dark text on it)."""
    return (color.red() * 299 + color.green() * 587 + color.blue() * 114) / 1000 > 128

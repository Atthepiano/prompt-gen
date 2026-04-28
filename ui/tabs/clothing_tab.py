"""Clothing Presets tab."""

from __future__ import annotations
import os

from PySide6.QtWidgets import (
    QLabel, QComboBox, QCheckBox, QPushButton, QListWidget, QAbstractItemView,
    QGroupBox, QGridLayout, QHBoxLayout, QVBoxLayout, QLineEdit,
    QFrame, QFileDialog, QMessageBox, QWidget,
)

import clothing_generator as clg
from ui.tabs.base_tab import BaseTab


class ClothingTab(BaseTab):
    image_prefix = "clothing"

    def __init__(self, window, parent=None):
        self._lang = window.ui_lang
        self._swap_character_path: str = ""
        self._swap_clothing_path:  str = ""
        super().__init__(window, parent)

    def _build_ui(self, body):
        lay = self._layout
        lang = self._lang

        title = QLabel("Clothing Preset Generation")
        title.setObjectName("header")
        lay.addWidget(title)
        sub = QLabel("Build a modular clothing preset prompt for retro sci-fi outfit sheets.")
        sub.setObjectName("subheader")
        sub.setWordWrap(True)
        lay.addWidget(sub)
        lay.addWidget(_sep())

        # ── Two-column layout ──────────────────────────────────────────────
        cols = QHBoxLayout()
        cols.setSpacing(12)
        left  = QVBoxLayout()
        right = QVBoxLayout()
        left.setSpacing(10)
        right.setSpacing(10)

        # ── LEFT: Faction & Role ──
        grp_faction = QGroupBox("Faction & Role")
        fl = QGridLayout(grp_faction)
        fl.setColumnStretch(1, 1)

        fl.addWidget(QLabel("Faction:"), 0, 0)
        self.combo_faction = QComboBox()
        self._faction_desc_map = clg.get_faction_description_map(lang)
        self.combo_faction.addItems(clg.get_faction_options(lang))
        self.combo_faction.currentTextChanged.connect(self._update_faction_desc)
        fl.addWidget(self.combo_faction, 0, 1)

        fl.addWidget(QLabel("Outfit Gender:"), 1, 0)
        self.combo_gender = QComboBox()
        self.combo_gender.addItems(clg.get_gender_options(lang))
        self.combo_gender.currentTextChanged.connect(self._refresh_outfit_categories)
        fl.addWidget(self.combo_gender, 1, 1)

        fl.addWidget(QLabel("Role Archetype:"), 2, 0)
        self.combo_role = QComboBox()
        self.combo_role.addItems(clg.get_role_options(lang))
        self.combo_role.currentTextChanged.connect(self._refresh_outfit_categories)
        fl.addWidget(self.combo_role, 2, 1)

        self.lbl_faction_desc = QLabel("")
        self.lbl_faction_desc.setObjectName("subheader")
        self.lbl_faction_desc.setWordWrap(True)
        fl.addWidget(self.lbl_faction_desc, 3, 0, 1, 2)
        left.addWidget(grp_faction)

        # ── LEFT: Presentation & Layout ──
        grp_layout = QGroupBox("Presentation & Layout")
        ll = QGridLayout(grp_layout)
        ll.setColumnStretch(1, 1)

        ll.addWidget(QLabel("View Mode:"), 0, 0)
        self.combo_view_mode = QComboBox()
        self.combo_view_mode.addItems(clg.get_view_mode_options(lang))
        ll.addWidget(self.combo_view_mode, 0, 1)

        ll.addWidget(QLabel("Aspect Ratio:"), 1, 0)
        self.combo_aspect = QComboBox()
        self.combo_aspect.addItems(clg.get_aspect_ratio_options(lang))
        ll.addWidget(self.combo_aspect, 1, 1)

        ll.addWidget(QLabel("Pose:"), 2, 0)
        self.combo_pose = QComboBox()
        self.combo_pose.addItems(clg.get_pose_options(lang))
        ll.addWidget(self.combo_pose, 2, 1)

        ll.addWidget(QLabel("Presentation:"), 3, 0)
        self.combo_presentation = QComboBox()
        self.combo_presentation.addItems(clg.get_presentation_options(lang))
        ll.addWidget(self.combo_presentation, 3, 1)
        left.addWidget(grp_layout)

        # ── LEFT: Outfit Swap (Gemini) ──
        grp_swap = QGroupBox("Outfit Swap (Gemini Preview)")
        sl = QGridLayout(grp_swap)
        sl.setColumnStretch(1, 1)

        sl.addWidget(QLabel("Character Image:"), 0, 0)
        self.lbl_char_img = QLabel("No image selected")
        self.lbl_char_img.setObjectName("subheader")
        self.lbl_char_img.setWordWrap(True)
        sl.addWidget(self.lbl_char_img, 0, 1)

        btn_char = QPushButton("Select Character Image…")
        btn_char.clicked.connect(self._select_character_image)
        sl.addWidget(btn_char, 1, 1)

        sl.addWidget(QLabel("Clothing Preset Image:"), 2, 0)
        self.lbl_clothing_img = QLabel("No image selected")
        self.lbl_clothing_img.setObjectName("subheader")
        self.lbl_clothing_img.setWordWrap(True)
        sl.addWidget(self.lbl_clothing_img, 2, 1)

        btn_cloth = QPushButton("Select Clothing Image…")
        btn_cloth.clicked.connect(self._select_clothing_image)
        sl.addWidget(btn_cloth, 3, 1)

        sl.addWidget(QLabel("Output Name:"), 4, 0)
        self.edit_swap_name = QLineEdit("swap_preview")
        sl.addWidget(self.edit_swap_name, 4, 1)

        btn_swap = QPushButton("Run Outfit Swap (Gemini)")
        btn_swap.clicked.connect(self._run_outfit_swap)
        sl.addWidget(btn_swap, 5, 0, 1, 2)
        left.addWidget(grp_swap)

        left.addStretch(1)

        # ── RIGHT: Outfit Build ──
        grp_outfit = QGroupBox("Outfit Build")
        ol = QGridLayout(grp_outfit)
        ol.setColumnStretch(1, 1)

        ol.addWidget(QLabel("Outfit Category:"), 0, 0)
        self.combo_outfit_cat = QComboBox()
        ol.addWidget(self.combo_outfit_cat, 0, 1)

        self.chk_show_all = QCheckBox("Show all outfit categories")
        self.chk_show_all.toggled.connect(self._refresh_outfit_categories)
        ol.addWidget(self.chk_show_all, 1, 0, 1, 2)

        ol.addWidget(QLabel("Silhouette:"), 2, 0)
        self.combo_silhouette = QComboBox()
        self.combo_silhouette.addItems(clg.get_silhouette_options(lang))
        ol.addWidget(self.combo_silhouette, 2, 1)

        ol.addWidget(QLabel("Layering:"), 3, 0)
        self.combo_layering = QComboBox()
        self.combo_layering.addItems(clg.get_layering_options(lang))
        ol.addWidget(self.combo_layering, 3, 1)

        ol.addWidget(QLabel("Material:"), 4, 0)
        self.combo_material = QComboBox()
        self.combo_material.addItems(clg.get_material_options(lang))
        ol.addWidget(self.combo_material, 4, 1)

        ol.addWidget(QLabel("Palette:"), 5, 0)
        self.combo_palette = QComboBox()
        self.combo_palette.addItems(clg.get_palette_options(lang))
        ol.addWidget(self.combo_palette, 5, 1)

        ol.addWidget(QLabel("Wear State:"), 6, 0)
        self.combo_wear_state = QComboBox()
        self.combo_wear_state.addItems(clg.get_wear_state_options(lang))
        ol.addWidget(self.combo_wear_state, 6, 1)
        right.addWidget(grp_outfit)

        # ── RIGHT: Detail Accents ──
        grp_detail = QGroupBox("Detail Accents (multi-select)")
        dl = QGridLayout(grp_detail)
        self.list_detail = QListWidget()
        self.list_detail.setSelectionMode(QAbstractItemView.MultiSelection)
        self.list_detail.addItems(clg.get_detail_accent_options(lang))
        self.list_detail.setMaximumHeight(100)
        dl.addWidget(self.list_detail)
        right.addWidget(grp_detail)

        # ── RIGHT: Accessories ──
        grp_acc = QGroupBox("Accessories (multi-select)")
        al = QGridLayout(grp_acc)
        self.list_accessories = QListWidget()
        self.list_accessories.setSelectionMode(QAbstractItemView.MultiSelection)
        self.list_accessories.addItems(clg.get_accessory_options(lang))
        self.list_accessories.setMaximumHeight(100)
        al.addWidget(self.list_accessories)
        right.addWidget(grp_acc)

        # ── RIGHT: Insignia ──
        grp_insignia = QGroupBox("Insignia & Markings (multi-select)")
        il = QGridLayout(grp_insignia)
        self.list_insignia = QListWidget()
        self.list_insignia.setSelectionMode(QAbstractItemView.MultiSelection)
        self.list_insignia.addItems(clg.get_insignia_options(lang))
        self.list_insignia.setMaximumHeight(80)
        il.addWidget(self.list_insignia)
        right.addWidget(grp_insignia)

        # ── RIGHT: Misc ──
        grp_misc = QGroupBox("Misc")
        ml = QVBoxLayout(grp_misc)
        ml.addWidget(QLabel("Custom notes (comma separated):"))
        self.edit_custom_notes = QLineEdit()
        self.edit_custom_notes.setPlaceholderText("(optional)")
        ml.addWidget(self.edit_custom_notes)
        right.addWidget(grp_misc)

        right.addStretch(1)

        # Assemble columns
        left_w  = QWidget(); left_w.setLayout(left)
        right_w = QWidget(); right_w.setLayout(right)
        cols.addWidget(left_w,  1)
        cols.addWidget(right_w, 1)
        lay.addLayout(cols)

        # ── Extra modifiers + Generate ──
        lay.addWidget(_sep())
        extra_row = QHBoxLayout()
        extra_row.addWidget(QLabel("Extra modifiers (optional):"))
        self.edit_extra = QLineEdit()
        self.edit_extra.setPlaceholderText("(optional)")
        extra_row.addWidget(self.edit_extra, 1)
        lay.addLayout(extra_row)

        self.btn_gen = QPushButton("GENERATE CLOTHING PROMPT")
        self.btn_gen.setObjectName("primary")
        self.btn_gen.clicked.connect(self._generate)
        lay.addWidget(self.btn_gen)

        # Init dynamic state
        self._refresh_outfit_categories()
        self._update_faction_desc(self.combo_faction.currentText())

    # ── Dynamic updates ───────────────────────────────────────────────────

    def _update_faction_desc(self, faction_label: str):
        desc = self._faction_desc_map.get(faction_label, "")
        self.lbl_faction_desc.setText(desc or "No faction description")

    def _refresh_outfit_categories(self):
        lang     = self._lang
        role     = self.combo_role.currentText()
        allow_all = self.chk_show_all.isChecked()
        options  = clg.get_outfit_category_options_for_role(lang, role, allow_all)
        if not options:
            options = clg.get_outfit_category_options(lang)
        current = self.combo_outfit_cat.currentText()
        self.combo_outfit_cat.blockSignals(True)
        self.combo_outfit_cat.clear()
        self.combo_outfit_cat.addItems(options)
        idx = self.combo_outfit_cat.findText(current)
        self.combo_outfit_cat.setCurrentIndex(max(idx, 0))
        self.combo_outfit_cat.blockSignals(False)

    # ── Image selection ───────────────────────────────────────────────────

    def _select_character_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Character Image", "",
            "Images (*.png *.jpg *.jpeg *.webp *.gif);;All Files (*)")
        if path:
            self._swap_character_path = path
            self.lbl_char_img.setText(os.path.basename(path))

    def _select_clothing_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Clothing Preset Image", "",
            "Images (*.png *.jpg *.jpeg *.webp *.gif);;All Files (*)")
        if path:
            self._swap_clothing_path = path
            self.lbl_clothing_img.setText(os.path.basename(path))

    # ── Outfit swap ───────────────────────────────────────────────────────

    def _build_outfit_swap_prompt(self) -> str:
        lines = [
            "You are given two images.",
            "First image: the character to keep (face, body proportions, pose, lighting).",
            "Second image: the clothing preset to apply.",
            "Replace only the outfit on the character with the clothing from the second image.",
            "Keep identity, face, hair, skin, and pose unchanged.",
            "Do NOT change the framing, camera angle, crop, or composition of Image 1.",
            "The output must keep Image 1's exact framing and silhouette scale.",
            "Adapt the clothing to the character, not the character to the clothing.",
            "This is an outfit swap, NOT a head swap. Do not move or replace the head.",
            "Match the retro 90s Japanese realistic sci-fi anime cel-shaded look.",
            "Keep the background clean and simple.",
        ]
        extra = self.edit_extra.text().strip()
        if extra:
            lines.append(f"Extra notes: {extra}.")
        return "\n".join(lines)

    def _run_outfit_swap(self):
        if not self._swap_character_path or not os.path.exists(self._swap_character_path):
            QMessageBox.warning(self, "Missing Image", "Please select a character image first.")
            return
        if not self._swap_clothing_path or not os.path.exists(self._swap_clothing_path):
            QMessageBox.warning(self, "Missing Image", "Please select a clothing preset image first.")
            return

        provider, api_key, model, extra_kwargs = self.window.get_credentials()
        if not api_key:
            QMessageBox.warning(self, "No API Key", "API key is missing. Please add it in Settings.")
            return

        prompt = self._build_outfit_swap_prompt()
        self.window.run_gemini_edit_with_images(
            prompt=prompt,
            image_paths=[self._swap_character_path, self._swap_clothing_path],
            output_name=self.edit_swap_name.text().strip() or "swap_preview",
        )

    # ── Generation ────────────────────────────────────────────────────────

    def _generate(self):
        lang = self._lang

        def _multi(lst: QListWidget) -> list[str]:
            return [lst.item(i).text()
                    for i in range(lst.count())
                    if lst.item(i).isSelected()]

        extra_notes = " ".join(filter(None, [
            self.edit_custom_notes.text().strip(),
            self.edit_extra.text().strip(),
        ]))

        try:
            prompt = clg.generate_clothing_preset_prompt(
                faction=self.combo_faction.currentText(),
                gender=self.combo_gender.currentText(),
                role=self.combo_role.currentText(),
                outfit_category=self.combo_outfit_cat.currentText(),
                silhouette=self.combo_silhouette.currentText(),
                layering=self.combo_layering.currentText(),
                material=self.combo_material.currentText(),
                palette=self.combo_palette.currentText(),
                wear_state=self.combo_wear_state.currentText(),
                presentation=self.combo_presentation.currentText(),
                pose=self.combo_pose.currentText(),
                view_mode=self.combo_view_mode.currentText(),
                aspect_ratio=self.combo_aspect.currentText(),
                detail_accents=_multi(self.list_detail),
                accessories=_multi(self.list_accessories),
                insignia=_multi(self.list_insignia),
                extra_notes=extra_notes,
                include_style=True,
                include_background=True,
                include_mood=True,
                swap_ready=True,
                lang=lang,
            )
            self.set_output(prompt)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def build_prompt(self) -> str:
        self._generate()
        return self.window.right.output_text.toPlainText()

    def save_dir(self) -> str:
        return self.window.clothing_save_dir or self.window.image_save_dir

    def get_reference_images(self) -> list[tuple[bytes, str]]:
        """Return selected reference images for outfit swap generation."""
        refs = []
        for path in (self._swap_character_path, self._swap_clothing_path):
            if path and os.path.exists(path):
                import mimetypes
                with open(path, "rb") as fh:
                    data = fh.read()
                mime = mimetypes.guess_type(path)[0] or "image/png"
                refs.append((data, mime))
        return refs


def _sep():
    f = QFrame()
    f.setFrameShape(QFrame.HLine)
    return f

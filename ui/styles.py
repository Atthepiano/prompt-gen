"""Dark theme stylesheet for the PromptGen Tool (PySide6 QSS)."""

# ── Colour palette ──────────────────────────────────────────────────────────
PALETTE = {
    "bg":        "#1e1e2e",   # main window background
    "surface":   "#2a2a3e",   # panels, group boxes
    "surface2":  "#313244",   # inputs, list items
    "border":    "#45475a",   # borders / separators
    "accent":    "#89b4fa",   # primary accent (blue)
    "accent2":   "#cba6f7",   # secondary accent (mauve) – used for active tabs
    "text":      "#cdd6f4",   # primary text
    "text_dim":  "#6c7086",   # placeholder / disabled text
    "success":   "#a6e3a1",   # green
    "warning":   "#f9e2af",   # yellow
    "error":     "#f38ba8",   # red
    "btn_hover": "#3d3d5c",   # button hover
    "btn_press": "#4d4d6c",   # button pressed
}

P = PALETTE   # shorthand


STYLESHEET = f"""
/* ── Global ──────────────────────────────────────────────────────────────── */
QWidget {{
    background-color: {P['bg']};
    color: {P['text']};
    font-family: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
    font-size: 13px;
}}

QMainWindow {{
    background-color: {P['bg']};
}}

/* ── QSplitter ───────────────────────────────────────────────────────────── */
QSplitter::handle {{
    background-color: {P['border']};
    width: 2px;
}}
QSplitter::handle:hover {{
    background-color: {P['accent']};
}}

/* ── QTabWidget ──────────────────────────────────────────────────────────── */
QTabWidget::pane {{
    border: 1px solid {P['border']};
    border-radius: 4px;
    background-color: {P['surface']};
    top: -1px;
}}
QTabBar::tab {{
    background-color: {P['surface2']};
    color: {P['text_dim']};
    padding: 6px 14px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    border: 1px solid {P['border']};
    border-bottom: none;
}}
QTabBar::tab:selected {{
    background-color: {P['surface']};
    color: {P['accent2']};
    border-bottom-color: {P['surface']};
}}
QTabBar::tab:hover:!selected {{
    background-color: {P['btn_hover']};
    color: {P['text']};
}}

/* ── QScrollArea ─────────────────────────────────────────────────────────── */
QScrollArea {{
    border: none;
    background-color: transparent;
}}
QScrollArea > QWidget > QWidget {{
    background-color: transparent;
}}

/* ── Scrollbars ──────────────────────────────────────────────────────────── */
QScrollBar:vertical {{
    background-color: {P['surface2']};
    width: 8px;
    border-radius: 4px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background-color: {P['border']};
    border-radius: 4px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background-color: {P['accent']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    background-color: {P['surface2']};
    height: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:horizontal {{
    background-color: {P['border']};
    border-radius: 4px;
    min-width: 24px;
}}
QScrollBar::handle:horizontal:hover {{
    background-color: {P['accent']};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* ── QPushButton ─────────────────────────────────────────────────────────── */
QPushButton {{
    background-color: {P['surface2']};
    color: {P['text']};
    border: 1px solid {P['border']};
    border-radius: 4px;
    padding: 5px 14px;
    min-height: 26px;
}}
QPushButton:hover {{
    background-color: {P['btn_hover']};
    border-color: {P['accent']};
}}
QPushButton:pressed {{
    background-color: {P['btn_press']};
}}
QPushButton:disabled {{
    color: {P['text_dim']};
    border-color: {P['border']};
}}
QPushButton#primary {{
    background-color: {P['accent']};
    color: #1e1e2e;
    font-weight: bold;
    border: none;
    padding: 8px 16px;
    min-height: 34px;
}}
QPushButton#primary:hover {{
    background-color: #b0d0ff;
}}
QPushButton#primary:pressed {{
    background-color: #6090d0;
}}
QPushButton#primary:disabled {{
    background-color: {P['border']};
    color: {P['text_dim']};
}}

/* ── QLineEdit ───────────────────────────────────────────────────────────── */
QLineEdit {{
    background-color: {P['surface2']};
    border: 1px solid {P['border']};
    border-radius: 4px;
    padding: 4px 8px;
    color: {P['text']};
    min-height: 24px;
}}
QLineEdit:focus {{
    border-color: {P['accent']};
}}
QLineEdit:disabled {{
    color: {P['text_dim']};
}}

/* ── QComboBox ───────────────────────────────────────────────────────────── */
QComboBox {{
    background-color: {P['surface2']};
    border: 1px solid {P['border']};
    border-radius: 4px;
    padding: 4px 8px;
    color: {P['text']};
    min-height: 24px;
}}
QComboBox:focus {{
    border-color: {P['accent']};
}}
QComboBox::drop-down {{
    border: none;
    width: 20px;
}}
QComboBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid {P['text_dim']};
    margin-right: 6px;
}}
QComboBox QAbstractItemView {{
    background-color: {P['surface2']};
    border: 1px solid {P['border']};
    selection-background-color: {P['btn_hover']};
    selection-color: {P['accent']};
    outline: none;
}}

/* ── QTextEdit / QPlainTextEdit ──────────────────────────────────────────── */
QTextEdit, QPlainTextEdit {{
    background-color: {P['surface2']};
    border: 1px solid {P['border']};
    border-radius: 4px;
    color: {P['text']};
    font-family: "Consolas", "Fira Code", monospace;
    font-size: 12px;
    padding: 4px;
}}
QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {P['accent']};
}}

/* ── QCheckBox ───────────────────────────────────────────────────────────── */
QCheckBox {{
    spacing: 6px;
    color: {P['text']};
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {P['border']};
    border-radius: 3px;
    background-color: {P['surface2']};
}}
QCheckBox::indicator:checked {{
    background-color: {P['accent']};
    border-color: {P['accent']};
}}
QCheckBox::indicator:hover {{
    border-color: {P['accent']};
}}

/* ── QGroupBox ───────────────────────────────────────────────────────────── */
QGroupBox {{
    border: 1px solid {P['border']};
    border-radius: 4px;
    margin-top: 8px;
    padding: 8px 8px 6px 8px;
    font-weight: bold;
    color: {P['text']};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 4px;
    color: {P['accent']};
}}

/* ── QListWidget ─────────────────────────────────────────────────────────── */
QListWidget {{
    background-color: {P['surface2']};
    border: 1px solid {P['border']};
    border-radius: 4px;
    outline: none;
}}
QListWidget::item {{
    padding: 3px 6px;
}}
QListWidget::item:selected {{
    background-color: {P['btn_hover']};
    color: {P['accent']};
}}
QListWidget::item:hover {{
    background-color: {P['btn_press']};
}}

/* ── QTreeWidget ─────────────────────────────────────────────────────────── */
QTreeWidget {{
    background-color: {P['surface2']};
    border: 1px solid {P['border']};
    border-radius: 4px;
    outline: none;
    alternate-background-color: {P['surface']};
}}
QTreeWidget::item {{
    padding: 3px 0;
}}
QTreeWidget::item:selected {{
    background-color: {P['btn_hover']};
    color: {P['accent']};
}}
QHeaderView::section {{
    background-color: {P['surface']};
    color: {P['text_dim']};
    border: none;
    border-right: 1px solid {P['border']};
    border-bottom: 1px solid {P['border']};
    padding: 4px 8px;
    font-weight: bold;
}}

/* ── QSlider ─────────────────────────────────────────────────────────────── */
QSlider::groove:horizontal {{
    height: 4px;
    background-color: {P['surface2']};
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background-color: {P['accent']};
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}}
QSlider::sub-page:horizontal {{
    background-color: {P['accent']};
    border-radius: 2px;
}}

/* ── QLabel ──────────────────────────────────────────────────────────────── */
QLabel {{
    background-color: transparent;
}}
QLabel#header {{
    font-size: 15px;
    font-weight: bold;
    color: {P['text']};
}}
QLabel#subheader {{
    font-size: 12px;
    color: {P['text_dim']};
}}
QLabel#preview_placeholder {{
    background-color: {P['surface2']};
    border: 1px solid {P['border']};
    border-radius: 4px;
    color: {P['text_dim']};
    font-size: 13px;
}}

/* ── QStatusBar ──────────────────────────────────────────────────────────── */
QStatusBar {{
    background-color: {P['surface']};
    color: {P['text_dim']};
    border-top: 1px solid {P['border']};
    font-size: 12px;
}}

/* ── QRadioButton ────────────────────────────────────────────────────────── */
QRadioButton {{
    spacing: 6px;
    color: {P['text']};
}}
QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {P['border']};
    border-radius: 8px;
    background-color: {P['surface2']};
}}
QRadioButton::indicator:checked {{
    background-color: {P['accent']};
    border-color: {P['accent']};
}}

/* ── QFrame (horizontal separator) ──────────────────────────────────────── */
QFrame[frameShape="4"],
QFrame[frameShape="HLine"] {{
    color: {P['border']};
    max-height: 1px;
    background-color: {P['border']};
}}

/* ── QSizeGrip ───────────────────────────────────────────────────────────── */
QSizeGrip {{
    image: none;
    background-color: transparent;
}}

/* ── QDialog ─────────────────────────────────────────────────────────────── */
QDialog {{
    background-color: {P['bg']};
}}

/* ── QMessageBox ─────────────────────────────────────────────────────────── */
QMessageBox {{
    background-color: {P['bg']};
}}
QMessageBox QLabel {{
    color: {P['text']};
}}
"""


def apply(app) -> None:
    """Apply the dark stylesheet to a QApplication instance."""
    app.setStyleSheet(STYLESHEET)

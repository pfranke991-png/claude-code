"""Matte-Black / Neon-Green Dark Theme for PyQt6."""

# Colors
BG_DARK = "#1a1a1a"
BG_MEDIUM = "#242424"
BG_LIGHT = "#2e2e2e"
BG_INPUT = "#1e1e1e"
NEON_GREEN = "#00ff88"
NEON_GREEN_DIM = "#00cc6a"
NEON_GREEN_GLOW = "#00ff8844"
TEXT_PRIMARY = "#e0e0e0"
TEXT_SECONDARY = "#888888"
TEXT_MUTED = "#555555"
BORDER = "#333333"
RED = "#ff4444"
YELLOW = "#ffaa00"
BLUE = "#4488ff"

STYLESHEET = f"""
QMainWindow, QWidget {{
    background-color: {BG_DARK};
    color: {TEXT_PRIMARY};
    font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    font-size: 13px;
}}

QTabWidget::pane {{
    border: 1px solid {BORDER};
    background-color: {BG_DARK};
    border-radius: 4px;
}}

QTabBar::tab {{
    background-color: {BG_MEDIUM};
    color: {TEXT_SECONDARY};
    padding: 10px 24px;
    margin-right: 2px;
    border: 1px solid {BORDER};
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: bold;
}}

QTabBar::tab:selected {{
    background-color: {BG_DARK};
    color: {NEON_GREEN};
    border-bottom: 2px solid {NEON_GREEN};
}}

QTabBar::tab:hover {{
    color: {NEON_GREEN_DIM};
}}

QPushButton {{
    background-color: {BG_LIGHT};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    padding: 8px 16px;
    border-radius: 6px;
    font-weight: bold;
}}

QPushButton:hover {{
    border-color: {NEON_GREEN_DIM};
    color: {NEON_GREEN};
}}

QPushButton:pressed {{
    background-color: {NEON_GREEN};
    color: {BG_DARK};
}}

QPushButton#startBtn {{
    background-color: {NEON_GREEN};
    color: {BG_DARK};
    font-size: 14px;
    padding: 10px 28px;
}}

QPushButton#startBtn:hover {{
    background-color: {NEON_GREEN_DIM};
}}

QPushButton#stopBtn {{
    background-color: {RED};
    color: white;
    font-size: 14px;
    padding: 10px 28px;
}}

QPushButton#pauseBtn {{
    background-color: {YELLOW};
    color: {BG_DARK};
    font-size: 14px;
    padding: 10px 28px;
}}

QPushButton#addProviderBtn {{
    background-color: {BG_MEDIUM};
    color: {NEON_GREEN};
    font-size: 28px;
    border: 2px dashed {NEON_GREEN_DIM};
    border-radius: 12px;
    min-width: 80px;
    min-height: 80px;
}}

QPushButton#addProviderBtn:hover {{
    border-color: {NEON_GREEN};
    background-color: {BG_LIGHT};
}}

QTextEdit, QPlainTextEdit {{
    background-color: {BG_INPUT};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 8px;
    font-size: 14px;
    selection-background-color: {NEON_GREEN_DIM};
    selection-color: {BG_DARK};
}}

QLineEdit {{
    background-color: {BG_INPUT};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 6px 10px;
}}

QLineEdit:focus, QTextEdit:focus {{
    border-color: {NEON_GREEN_DIM};
}}

QComboBox {{
    background-color: {BG_INPUT};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 6px 10px;
    min-width: 120px;
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

QComboBox QAbstractItemView {{
    background-color: {BG_MEDIUM};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    selection-background-color: {NEON_GREEN_DIM};
    selection-color: {BG_DARK};
}}

QSlider::groove:horizontal {{
    background: {BG_LIGHT};
    height: 6px;
    border-radius: 3px;
}}

QSlider::handle:horizontal {{
    background: {NEON_GREEN};
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}}

QSlider::sub-page:horizontal {{
    background: {NEON_GREEN_DIM};
    border-radius: 3px;
}}

QProgressBar {{
    background-color: {BG_LIGHT};
    border: 1px solid {BORDER};
    border-radius: 4px;
    text-align: center;
    color: {TEXT_PRIMARY};
    height: 8px;
}}

QProgressBar::chunk {{
    background-color: {NEON_GREEN};
    border-radius: 3px;
}}

QCheckBox {{
    color: {TEXT_PRIMARY};
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 1px solid {BORDER};
    border-radius: 4px;
    background-color: {BG_INPUT};
}}

QCheckBox::indicator:checked {{
    background-color: {NEON_GREEN};
    border-color: {NEON_GREEN};
}}

QLabel {{
    color: {TEXT_PRIMARY};
}}

QLabel#badge {{
    background-color: {BG_LIGHT};
    color: {NEON_GREEN};
    border: 1px solid {NEON_GREEN_DIM};
    border-radius: 10px;
    padding: 2px 10px;
    font-size: 11px;
}}

QLabel#badgeInactive {{
    background-color: {BG_LIGHT};
    color: {TEXT_MUTED};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 2px 10px;
    font-size: 11px;
}}

QLabel#sectionTitle {{
    color: {NEON_GREEN};
    font-size: 15px;
    font-weight: bold;
    padding: 4px 0;
}}

QLabel#subtitle {{
    color: {TEXT_SECONDARY};
    font-size: 12px;
}}

QTableWidget {{
    background-color: {BG_INPUT};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 6px;
    gridline-color: {BORDER};
}}

QTableWidget::item {{
    padding: 6px;
}}

QTableWidget::item:selected {{
    background-color: {NEON_GREEN_DIM};
    color: {BG_DARK};
}}

QHeaderView::section {{
    background-color: {BG_MEDIUM};
    color: {NEON_GREEN};
    border: 1px solid {BORDER};
    padding: 6px;
    font-weight: bold;
}}

QScrollBar:vertical {{
    background: {BG_DARK};
    width: 10px;
    border-radius: 5px;
}}

QScrollBar::handle:vertical {{
    background: {BG_LIGHT};
    min-height: 30px;
    border-radius: 5px;
}}

QScrollBar::handle:vertical:hover {{
    background: {NEON_GREEN_DIM};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QGroupBox {{
    border: 1px solid {BORDER};
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: bold;
    color: {NEON_GREEN};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}}

QListWidget {{
    background-color: {BG_INPUT};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 4px;
}}

QListWidget::item {{
    padding: 8px;
    border-bottom: 1px solid {BORDER};
}}

QListWidget::item:selected {{
    background-color: {NEON_GREEN_DIM};
    color: {BG_DARK};
}}

QListWidget::item:hover {{
    background-color: {BG_LIGHT};
}}

QSpinBox {{
    background-color: {BG_INPUT};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 4px 8px;
}}
"""

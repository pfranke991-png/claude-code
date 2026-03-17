"""Tab 1 - Transkription: Live-Text, Start/Pause/Stop, VU-Meter, Auto-Clipboard, Archiv."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QLabel, QCheckBox, QListWidget, QListWidgetItem, QProgressBar,
    QSplitter, QFrame,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

from ui.theme import NEON_GREEN, NEON_GREEN_DIM, BG_LIGHT, TEXT_SECONDARY


class TranscriptionTab(QWidget):
    """Main transcription interface."""

    request_start = pyqtSignal()
    request_pause = pyqtSignal()
    request_stop = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        # -- Status bar with badges --
        status_row = QHBoxLayout()

        self.whisper_badge = QLabel("Whisper: --")
        self.whisper_badge.setObjectName("badgeInactive")
        status_row.addWidget(self.whisper_badge)

        self.postproc_badge = QLabel("Post-Processing: Aus")
        self.postproc_badge.setObjectName("badgeInactive")
        status_row.addWidget(self.postproc_badge)

        self.time_label = QLabel("00:00")
        self.time_label.setStyleSheet(f"color: {NEON_GREEN}; font-size: 16px; font-weight: bold;")
        status_row.addStretch()
        status_row.addWidget(self.time_label)

        layout.addLayout(status_row)

        # -- VU Meter --
        self.vu_meter = QProgressBar()
        self.vu_meter.setRange(0, 100)
        self.vu_meter.setValue(0)
        self.vu_meter.setTextVisible(False)
        self.vu_meter.setFixedHeight(8)
        layout.addWidget(self.vu_meter)

        # -- Splitter: Text area + Archive --
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Text area
        text_frame = QFrame()
        text_layout = QVBoxLayout(text_frame)
        text_layout.setContentsMargins(0, 0, 0, 0)

        text_header = QHBoxLayout()
        text_title = QLabel("Transkription")
        text_title.setObjectName("sectionTitle")
        text_header.addWidget(text_title)
        text_header.addStretch()

        self.auto_clipboard = QCheckBox("Auto-Clipboard")
        self.auto_clipboard.setChecked(True)
        text_header.addWidget(self.auto_clipboard)

        self.copy_btn = QPushButton("Kopieren")
        self.copy_btn.setFixedWidth(90)
        self.copy_btn.clicked.connect(self._copy_text)
        text_header.addWidget(self.copy_btn)

        self.clear_btn = QPushButton("Leeren")
        self.clear_btn.setFixedWidth(80)
        self.clear_btn.clicked.connect(self._clear_text)
        text_header.addWidget(self.clear_btn)

        text_layout.addLayout(text_header)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Starte die Aufnahme um Text zu transkribieren...")
        self.text_edit.setFont(QFont("Segoe UI", 13))
        self.text_edit.setMinimumHeight(180)
        text_layout.addWidget(self.text_edit)

        splitter.addWidget(text_frame)

        # Archive
        archive_frame = QFrame()
        archive_layout = QVBoxLayout(archive_frame)
        archive_layout.setContentsMargins(0, 0, 0, 0)

        archive_header = QHBoxLayout()
        archive_title = QLabel("Archiv (letzte 25)")
        archive_title.setObjectName("sectionTitle")
        archive_header.addWidget(archive_title)
        archive_header.addStretch()
        archive_layout.addLayout(archive_header)

        self.archive_list = QListWidget()
        self.archive_list.setMaximumHeight(200)
        self.archive_list.itemClicked.connect(self._on_archive_click)
        archive_layout.addWidget(self.archive_list)

        splitter.addWidget(archive_frame)
        splitter.setSizes([400, 200])
        layout.addWidget(splitter)

        # -- Control buttons --
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.start_btn = QPushButton("Aufnahme starten")
        self.start_btn.setObjectName("startBtn")
        self.start_btn.setFixedWidth(180)
        self.start_btn.clicked.connect(self._on_start)
        btn_row.addWidget(self.start_btn)

        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setObjectName("pauseBtn")
        self.pause_btn.setFixedWidth(120)
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self._on_pause)
        btn_row.addWidget(self.pause_btn)

        self.stop_btn = QPushButton("Stopp")
        self.stop_btn.setObjectName("stopBtn")
        self.stop_btn.setFixedWidth(120)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._on_stop)
        btn_row.addWidget(self.stop_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

    def _on_start(self):
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.request_start.emit()

    def _on_pause(self):
        if self.pause_btn.text() == "Pause":
            self.pause_btn.setText("Fortsetzen")
            self.request_pause.emit()
        else:
            self.pause_btn.setText("Pause")
            self.request_start.emit()

    def _on_stop(self):
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setText("Pause")
        self.stop_btn.setEnabled(False)
        self.request_stop.emit()

    def _copy_text(self):
        try:
            import pyperclip
            pyperclip.copy(self.text_edit.toPlainText())
        except Exception:
            pass

    def _clear_text(self):
        self.text_edit.clear()

    def append_text(self, text):
        if text.strip():
            self.text_edit.append(text)

    def set_text(self, text):
        self.text_edit.setPlainText(text)

    def get_text(self):
        return self.text_edit.toPlainText()

    def update_vu(self, level):
        val = min(100, int(level * 500))
        self.vu_meter.setValue(val)

    def update_time(self, seconds):
        m, s = divmod(int(seconds), 60)
        self.time_label.setText(f"{m:02d}:{s:02d}")

    def set_whisper_badge(self, model_name):
        if model_name:
            self.whisper_badge.setText(f"Whisper: {model_name}")
            self.whisper_badge.setObjectName("badge")
        else:
            self.whisper_badge.setText("Whisper: Kein Modell")
            self.whisper_badge.setObjectName("badgeInactive")
        self.whisper_badge.style().unpolish(self.whisper_badge)
        self.whisper_badge.style().polish(self.whisper_badge)

    def set_postproc_badge(self, provider_name):
        if provider_name:
            self.postproc_badge.setText(f"Post-Processing: {provider_name}")
            self.postproc_badge.setObjectName("badge")
        else:
            self.postproc_badge.setText("Post-Processing: Aus")
            self.postproc_badge.setObjectName("badgeInactive")
        self.postproc_badge.style().unpolish(self.postproc_badge)
        self.postproc_badge.style().polish(self.postproc_badge)

    def load_archive(self, entries):
        self.archive_list.clear()
        for entry in entries:
            ts = entry.get("timestamp", "")[:16].replace("T", " ")
            preview = entry.get("text", "")[:80].replace("\n", " ")
            item = QListWidgetItem(f"[{ts}] {preview}")
            item.setData(Qt.ItemDataRole.UserRole, entry.get("text", ""))
            self.archive_list.addItem(item)

    def _on_archive_click(self, item):
        text = item.data(Qt.ItemDataRole.UserRole)
        if text:
            self.text_edit.setPlainText(text)

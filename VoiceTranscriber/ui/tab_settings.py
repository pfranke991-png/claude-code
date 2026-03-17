"""Tab 3 - Audio & Modelle: Device, Noise Reduction, Whisper Models."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QCheckBox, QGroupBox, QFormLayout, QSpinBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from core.audio import AudioRecorder
from core.transcriber import WhisperTranscriber
from ui.theme import NEON_GREEN, NEON_GREEN_DIM, TEXT_SECONDARY, RED


class ModelDownloadThread(QThread):
    """Background thread for downloading whisper models."""
    progress = pyqtSignal(str, str)  # status, message
    finished_signal = pyqtSignal(str)  # model_name

    def __init__(self, transcriber, model_name):
        super().__init__()
        self.transcriber = transcriber
        self.model_name = model_name

    def run(self):
        try:
            self.transcriber.load_model(
                self.model_name,
                callback=lambda s, m: self.progress.emit(s, m),
            )
            self.finished_signal.emit(self.model_name)
        except Exception as e:
            self.progress.emit("error", str(e))


class SettingsTab(QWidget):
    """Audio and model settings interface."""

    model_loaded = pyqtSignal(str)  # model_name
    settings_changed = pyqtSignal()

    def __init__(self, db, transcriber, parent=None):
        super().__init__(parent)
        self.db = db
        self.transcriber = transcriber
        self._download_thread = None
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(16)

        # -- Audio Settings --
        audio_group = QGroupBox("Audio-Einstellungen")
        audio_layout = QFormLayout()
        audio_layout.setSpacing(10)

        self.device_combo = QComboBox()
        self._populate_devices()
        audio_layout.addRow("Eingabegeraet:", self.device_combo)

        self.sample_rate_combo = QComboBox()
        self.sample_rate_combo.addItems(["16000", "22050", "44100", "48000"])
        self.sample_rate_combo.setCurrentText("16000")
        audio_layout.addRow("Sample Rate:", self.sample_rate_combo)

        self.chunk_spin = QSpinBox()
        self.chunk_spin.setRange(1, 10)
        self.chunk_spin.setValue(3)
        self.chunk_spin.setSuffix(" Sek.")
        audio_layout.addRow("Chunk-Groesse:", self.chunk_spin)

        self.noise_check = QCheckBox("Rauschreduzierung aktivieren")
        self.noise_check.setChecked(False)
        audio_layout.addRow("", self.noise_check)

        refresh_btn = QPushButton("Geraete aktualisieren")
        refresh_btn.setFixedWidth(180)
        refresh_btn.clicked.connect(self._populate_devices)
        audio_layout.addRow("", refresh_btn)

        audio_group.setLayout(audio_layout)
        layout.addWidget(audio_group)

        # -- Whisper Models --
        model_group = QGroupBox("Whisper Modelle (lokal)")
        model_layout = QVBoxLayout()

        model_info = QLabel("Modelle werden beim ersten Start heruntergeladen und in ~/.cache gespeichert.")
        model_info.setObjectName("subtitle")
        model_info.setWordWrap(True)
        model_layout.addWidget(model_info)

        self.model_table = QTableWidget()
        self.model_table.setColumnCount(5)
        self.model_table.setHorizontalHeaderLabels(["Modell", "Groesse", "Geschw.", "Qualitaet", "Aktion"])
        self.model_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.model_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.model_table.verticalHeader().setVisible(False)
        self._populate_model_table()
        model_layout.addWidget(self.model_table)

        self.download_bar = QProgressBar()
        self.download_bar.setTextVisible(True)
        self.download_bar.setFormat("Bereit")
        self.download_bar.setValue(0)
        self.download_bar.setFixedHeight(24)
        model_layout.addWidget(self.download_bar)

        model_group.setLayout(model_layout)
        layout.addWidget(model_group)

        layout.addStretch()

        # -- Save button --
        save_row = QHBoxLayout()
        save_row.addStretch()
        save_btn = QPushButton("Einstellungen speichern")
        save_btn.setStyleSheet(f"background-color: {NEON_GREEN}; color: #1a1a1a; font-weight: bold;")
        save_btn.clicked.connect(self._save_settings)
        save_row.addWidget(save_btn)
        layout.addLayout(save_row)

    def _populate_devices(self):
        self.device_combo.clear()
        self.device_combo.addItem("Standard-Geraet", None)
        devices = AudioRecorder.get_input_devices()
        for d in devices:
            self.device_combo.addItem(d["name"], d["index"])

    def _populate_model_table(self):
        models = WhisperTranscriber.MODELS
        downloaded = self.transcriber.get_downloaded_models()
        self.model_table.setRowCount(len(models))

        for i, m in enumerate(models):
            self.model_table.setItem(i, 0, QTableWidgetItem(m["name"]))
            self.model_table.setItem(i, 1, QTableWidgetItem(m["size"]))
            self.model_table.setItem(i, 2, QTableWidgetItem(m["speed"]))
            self.model_table.setItem(i, 3, QTableWidgetItem(m["quality"]))

            btn = QPushButton()
            if m["name"] in downloaded:
                if m["name"] == self.transcriber.model_name:
                    btn.setText("Aktiv")
                    btn.setStyleSheet(f"background-color: {NEON_GREEN}; color: #1a1a1a; font-weight: bold;")
                    btn.setEnabled(False)
                else:
                    btn.setText("Laden")
                    btn.setStyleSheet(f"color: {NEON_GREEN};")
                    btn.clicked.connect(lambda _, name=m["name"]: self._load_model(name))
            else:
                btn.setText("Herunterladen")
                btn.clicked.connect(lambda _, name=m["name"]: self._download_model(name))
            self.model_table.setCellWidget(i, 4, btn)

    def _download_model(self, model_name):
        if self._download_thread and self._download_thread.isRunning():
            return
        self.download_bar.setFormat(f"Lade {model_name}...")
        self.download_bar.setRange(0, 0)  # Indeterminate
        self._download_thread = ModelDownloadThread(self.transcriber, model_name)
        self._download_thread.progress.connect(self._on_download_progress)
        self._download_thread.finished_signal.connect(self._on_download_done)
        self._download_thread.start()

    def _load_model(self, model_name):
        self._download_model(model_name)

    def _on_download_progress(self, status, message):
        self.download_bar.setFormat(message)

    def _on_download_done(self, model_name):
        self.download_bar.setRange(0, 100)
        self.download_bar.setValue(100)
        self.download_bar.setFormat(f"Modell '{model_name}' geladen!")
        self._populate_model_table()
        self.model_loaded.emit(model_name)
        self.db.set_setting("whisper_model", model_name)

    def _save_settings(self):
        device_idx = self.device_combo.currentData()
        self.db.set_setting("audio_device", device_idx)
        self.db.set_setting("sample_rate", int(self.sample_rate_combo.currentText()))
        self.db.set_setting("chunk_duration", self.chunk_spin.value())
        self.db.set_setting("noise_reduce", self.noise_check.isChecked())
        self.settings_changed.emit()
        self.download_bar.setFormat("Einstellungen gespeichert!")

    def _load_settings(self):
        sr = self.db.get_setting("sample_rate", 16000)
        idx = self.sample_rate_combo.findText(str(sr))
        if idx >= 0:
            self.sample_rate_combo.setCurrentIndex(idx)

        chunk = self.db.get_setting("chunk_duration", 3)
        self.chunk_spin.setValue(chunk)

        nr = self.db.get_setting("noise_reduce", False)
        self.noise_check.setChecked(nr)

        device = self.db.get_setting("audio_device")
        if device is not None:
            for i in range(self.device_combo.count()):
                if self.device_combo.itemData(i) == device:
                    self.device_combo.setCurrentIndex(i)
                    break

    def get_device_index(self):
        return self.device_combo.currentData()

    def get_sample_rate(self):
        return int(self.sample_rate_combo.currentText())

    def get_chunk_duration(self):
        return self.chunk_spin.value()

    def is_noise_reduce(self):
        return self.noise_check.isChecked()

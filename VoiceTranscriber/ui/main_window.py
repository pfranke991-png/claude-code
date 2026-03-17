"""Main window with 3 tabs."""

import threading
import time
import numpy as np

from PyQt6.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout
from PyQt6.QtCore import QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QIcon

from core.database import Database
from core.audio import AudioRecorder
from core.transcriber import WhisperTranscriber
from core.postprocessor import PostProcessor
from ui.tab_transcription import TranscriptionTab
from ui.tab_providers import ProviderTab
from ui.tab_settings import SettingsTab
from ui.theme import STYLESHEET, NEON_GREEN


class TranscriptionSignals(QObject):
    """Signals for thread-safe UI updates from transcription thread."""
    text_ready = pyqtSignal(str)
    final_text = pyqtSignal(str)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Voice Transcriber")
        self.setMinimumSize(900, 700)
        self.resize(1000, 750)
        self.setStyleSheet(STYLESHEET)

        # Core components
        self.db = Database()
        self.recorder = AudioRecorder()
        self.transcriber = WhisperTranscriber()
        self.postprocessor = PostProcessor()
        self.signals = TranscriptionSignals()

        # State
        self._recording = False
        self._transcribe_thread = None
        self._stop_event = threading.Event()
        self._accumulated_audio = []
        self._start_time = 0

        self._setup_ui()
        self._connect_signals()
        self._load_initial_state()

        # Timers
        self._vu_timer = QTimer()
        self._vu_timer.timeout.connect(self._update_vu)
        self._time_timer = QTimer()
        self._time_timer.timeout.connect(self._update_time)

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tabs = QTabWidget()

        self.tab_transcription = TranscriptionTab()
        self.tab_providers = ProviderTab(self.db)
        self.tab_settings = SettingsTab(self.db, self.transcriber)

        self.tabs.addTab(self.tab_transcription, "Transkription")
        self.tabs.addTab(self.tab_providers, "API & Provider")
        self.tabs.addTab(self.tab_settings, "Audio & Modelle")

        layout.addWidget(self.tabs)

    def _connect_signals(self):
        # Transcription tab
        self.tab_transcription.request_start.connect(self._start_recording)
        self.tab_transcription.request_pause.connect(self._pause_recording)
        self.tab_transcription.request_stop.connect(self._stop_recording)

        # Settings tab
        self.tab_settings.model_loaded.connect(self._on_model_loaded)
        self.tab_settings.settings_changed.connect(self._apply_settings)

        # Provider tab
        self.tab_providers.provider_changed.connect(self._on_provider_changed)

        # Transcription signals (thread-safe)
        self.signals.text_ready.connect(self._on_live_text)
        self.signals.final_text.connect(self._on_final_text)

    def _load_initial_state(self):
        # Load archive
        archive = self.db.get_archive()
        self.tab_transcription.load_archive(archive)

        # Load last whisper model
        last_model = self.db.get_setting("whisper_model", "base")
        self._load_whisper_model(last_model)

        # Load active provider
        self._on_provider_changed()

    def _load_whisper_model(self, model_name):
        """Load whisper model in background."""
        def _load():
            try:
                self.transcriber.load_model(model_name)
                self.tab_transcription.set_whisper_badge(model_name)
            except Exception as e:
                print(f"Fehler beim Laden von Whisper Modell: {e}")
        threading.Thread(target=_load, daemon=True).start()

    def _on_model_loaded(self, model_name):
        self.tab_transcription.set_whisper_badge(model_name)

    def _on_provider_changed(self):
        provider = self.db.get_active_provider()
        if provider:
            try:
                self.postprocessor.configure(
                    provider["provider_type"],
                    provider.get("api_key", ""),
                    provider.get("base_url", ""),
                    provider.get("model", ""),
                    provider.get("prompt", ""),
                )
                self.tab_transcription.set_postproc_badge(provider["name"])
            except Exception:
                self.tab_transcription.set_postproc_badge(None)
        else:
            self.postprocessor.client = None
            self.tab_transcription.set_postproc_badge(None)

    def _apply_settings(self):
        nr = self.tab_settings.is_noise_reduce()
        self.transcriber.noise_reduce = nr
        sr = self.tab_settings.get_sample_rate()
        self.transcriber.sample_rate = sr

    def _start_recording(self):
        if self._recording:
            # Resume from pause
            self.recorder.resume()
            return

        self._apply_settings()
        self._recording = True
        self._stop_event.clear()
        self._accumulated_audio = []
        self._start_time = time.time()

        sr = self.tab_settings.get_sample_rate()
        chunk_dur = self.tab_settings.get_chunk_duration()
        device = self.tab_settings.get_device_index()

        self.recorder = AudioRecorder(
            sample_rate=sr,
            channels=1,
            chunk_duration=0.5,
        )
        self.recorder.start(device_index=device)

        # Start live transcription thread
        self._transcribe_thread = threading.Thread(
            target=self._live_transcribe_loop,
            args=(sr, chunk_dur),
            daemon=True,
        )
        self._transcribe_thread.start()

        self._vu_timer.start(50)
        self._time_timer.start(500)

    def _pause_recording(self):
        self.recorder.pause()

    def _stop_recording(self):
        self._recording = False
        self._stop_event.set()
        self.recorder.stop()
        self._vu_timer.stop()
        self._time_timer.stop()
        self.tab_transcription.update_vu(0)

        # Final transcription of complete audio
        def _final():
            audio = self.recorder.get_all_audio()
            duration = self.recorder.get_duration()
            if len(audio) > 0:
                text = self.transcriber.transcribe_audio(audio)
                # Post-process if configured
                raw_text = text
                if self.postprocessor.client and text.strip():
                    text = self.postprocessor.process(text)
                self.signals.final_text.emit(text)
                # Save to archive
                provider = self.db.get_active_provider()
                self.db.save_transcription(
                    text, raw_text,
                    provider=provider["name"] if provider else None,
                    model=self.transcriber.model_name,
                    duration_sec=duration,
                )
        threading.Thread(target=_final, daemon=True).start()

    def _live_transcribe_loop(self, sample_rate, chunk_duration_sec):
        """Background thread for live transcription."""
        buffer = []
        chunk_samples = int(sample_rate * chunk_duration_sec)

        while not self._stop_event.is_set():
            try:
                audio_chunk = self.recorder.audio_queue.get(timeout=0.5)
                buffer.append(audio_chunk)
                total = np.concatenate(buffer)

                if len(total) >= chunk_samples:
                    text = self.transcriber.transcribe_chunk(total, language="de")
                    if text.strip():
                        self.signals.text_ready.emit(text)
                    buffer = []
            except Exception:
                continue

    def _on_live_text(self, text):
        self.tab_transcription.append_text(text)

    def _on_final_text(self, text):
        self.tab_transcription.set_text(text)
        # Auto-clipboard
        if self.tab_transcription.auto_clipboard.isChecked():
            try:
                import pyperclip
                pyperclip.copy(text)
            except Exception:
                pass
        # Refresh archive
        archive = self.db.get_archive()
        self.tab_transcription.load_archive(archive)

    def _update_vu(self):
        try:
            level = self.recorder.level_queue.get_nowait()
            self.tab_transcription.update_vu(level)
        except Exception:
            pass

    def _update_time(self):
        if self._recording:
            elapsed = time.time() - self._start_time
            self.tab_transcription.update_time(elapsed)

    def closeEvent(self, event):
        if self._recording:
            self._stop_recording()
        event.accept()

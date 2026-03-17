import os
import threading
import queue
import numpy as np
from pathlib import Path


# Noise reduction is optional
try:
    import noisereduce as nr
    HAS_NOISEREDUCE = True
except ImportError:
    HAS_NOISEREDUCE = False


class WhisperTranscriber:
    """Local Whisper transcription using faster-whisper."""

    MODELS = [
        {"name": "tiny", "size": "~75 MB", "speed": "Sehr schnell", "quality": "Niedrig"},
        {"name": "base", "size": "~142 MB", "speed": "Schnell", "quality": "Mittel"},
        {"name": "small", "size": "~466 MB", "speed": "Mittel", "quality": "Gut"},
        {"name": "medium", "size": "~1.5 GB", "speed": "Langsam", "quality": "Sehr gut"},
        {"name": "large-v3", "size": "~3 GB", "speed": "Sehr langsam", "quality": "Exzellent"},
    ]

    def __init__(self):
        self.model = None
        self.model_name = None
        self.cache_dir = Path.home() / ".cache" / "voice_transcriber" / "whisper"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._loading = False
        self.noise_reduce = False
        self.sample_rate = 16000

    def is_model_downloaded(self, model_name):
        model_dir = self.cache_dir / f"models--Systran--faster-whisper-{model_name}"
        return model_dir.exists()

    def get_downloaded_models(self):
        downloaded = []
        for m in self.MODELS:
            if self.is_model_downloaded(m["name"]):
                downloaded.append(m["name"])
        return downloaded

    def load_model(self, model_name="base", callback=None):
        """Load whisper model. Downloads on first use. callback(status, progress) for UI updates."""
        self._loading = True
        try:
            if callback:
                callback("download", f"Lade Modell '{model_name}'...")
            from faster_whisper import WhisperModel
            self.model = WhisperModel(
                model_name,
                device="cpu",
                compute_type="int8",
                download_root=str(self.cache_dir),
            )
            self.model_name = model_name
            if callback:
                callback("ready", f"Modell '{model_name}' geladen")
        except Exception as e:
            if callback:
                callback("error", str(e))
            raise
        finally:
            self._loading = False

    def transcribe_audio(self, audio_data, language="de"):
        """Transcribe numpy audio array. Returns text string."""
        if self.model is None:
            return ""
        if len(audio_data) == 0:
            return ""

        # Apply noise reduction if enabled
        if self.noise_reduce and HAS_NOISEREDUCE:
            try:
                audio_data = nr.reduce_noise(y=audio_data, sr=self.sample_rate)
            except Exception:
                pass

        segments, info = self.model.transcribe(
            audio_data,
            language=language,
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
        )
        text_parts = []
        for segment in segments:
            text_parts.append(segment.text.strip())
        return " ".join(text_parts)

    def transcribe_chunk(self, audio_chunk, language="de"):
        """Transcribe a single audio chunk for live display."""
        if self.model is None:
            return ""
        if len(audio_chunk) < self.sample_rate * 0.3:
            return ""

        if self.noise_reduce and HAS_NOISEREDUCE:
            try:
                audio_chunk = nr.reduce_noise(y=audio_chunk, sr=self.sample_rate)
            except Exception:
                pass

        segments, _ = self.model.transcribe(
            audio_chunk,
            language=language,
            beam_size=1,
            vad_filter=True,
        )
        parts = []
        for seg in segments:
            parts.append(seg.text.strip())
        return " ".join(parts)

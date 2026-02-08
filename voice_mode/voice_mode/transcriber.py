"""Transkription mit Faster-Whisper."""

from __future__ import annotations

from typing import Iterable, List

import numpy as np
from faster_whisper import WhisperModel

from .config import Settings


class Transcriber:
    """Wrappt Faster-Whisper und nutzt den lokalen Modell-Cache."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        device = self.settings.ensure_device()
        if self.settings.compute_type == "auto":
            compute_type = "float16" if device == "cuda" else "int8"
        else:
            compute_type = self.settings.compute_type
        self.model = WhisperModel(
            self.settings.whisper_model,
            device=device,
            compute_type=compute_type,
            download_root=self.settings.whisper_download_root,
        )
        print(f"[info] Whisper geladen: {self.settings.whisper_model} auf {device} (compute_type={compute_type})")

    def transcribe(self, audio: np.ndarray) -> str:
        segments, _ = self.model.transcribe(
            audio,
            language=self.settings.language,
            vad_filter=self.settings.vad_filter,
            chunk_length=self.settings.chunk_length_seconds,
            without_timestamps=True,
            word_timestamps=False,
        )
        lines: List[str] = []
        for segment in segments if isinstance(segments, Iterable) else []:
            lines.append(segment.text.strip())
        transcript = " ".join(lines).strip()
        print(f"[transcript] {transcript}")
        return transcript

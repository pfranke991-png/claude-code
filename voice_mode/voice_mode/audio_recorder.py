"""Audioaufnahme mit Sounddevice.

Der Recorder sammelt rohe Float32-Frames und gibt einen einzelnen zusammengesetzten
NumPy-Array zurück. Fehler werden abgefangen, damit der Hotkey-Loop stabil bleibt.
"""

from __future__ import annotations

import queue
import sys
import threading
from typing import Optional

import numpy as np
import sounddevice as sd


class AudioRecorder:
    """Einfache Hotkey-gesteuerte Audioaufnahme."""

    def __init__(self, samplerate: int, channels: int, block_duration_ms: int = 30) -> None:
        self.samplerate = samplerate
        self.channels = channels
        self.block_duration_ms = block_duration_ms
        self._queue: "queue.Queue[np.ndarray]" = queue.Queue()
        self._stream: Optional[sd.InputStream] = None
        self._lock = threading.Lock()

    def _callback(self, indata: np.ndarray, frames: int, time, status) -> None:  # type: ignore[override]
        if status:
            print(f"[warn] Audio-Status: {status}", file=sys.stderr)
        self._queue.put(indata.copy())

    def start(self) -> None:
        """Startet die Aufnahme."""

        with self._lock:
            self._queue = queue.Queue()
            self._stream = sd.InputStream(
                samplerate=self.samplerate,
                channels=self.channels,
                blocksize=int(self.samplerate * self.block_duration_ms / 1000),
                callback=self._callback,
            )
            self._stream.start()
            print("[info] Aufnahme gestartet")

    def stop(self) -> np.ndarray:
        """Stoppt die Aufnahme und gibt die gesammelten Frames zurück."""

        with self._lock:
            if self._stream is not None:
                self._stream.stop()
                self._stream.close()
                self._stream = None
                print("[info] Aufnahme gestoppt")

        frames: list[np.ndarray] = []
        while not self._queue.empty():
            frames.append(self._queue.get())
        if not frames:
            raise RuntimeError("Keine Audiodaten empfangen. Mikrofon verfügbar?")
        audio = np.concatenate(frames, axis=0)
        if self.channels > 1:
            audio = np.mean(audio, axis=1, keepdims=False)
        return audio.squeeze()


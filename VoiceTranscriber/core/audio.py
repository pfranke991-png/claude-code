import numpy as np
import sounddevice as sd
import threading
import queue
import time


class AudioRecorder:
    """Handles audio recording with sounddevice."""

    def __init__(self, sample_rate=16000, channels=1, chunk_duration=0.5):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_duration = chunk_duration
        self.audio_queue = queue.Queue()
        self.level_queue = queue.Queue(maxsize=50)
        self.recording = False
        self.paused = False
        self.stream = None
        self._all_audio = []

    @staticmethod
    def get_input_devices():
        devices = sd.query_devices()
        inputs = []
        for i, d in enumerate(devices):
            if d["max_input_channels"] > 0:
                inputs.append({"index": i, "name": d["name"], "channels": d["max_input_channels"],
                               "sample_rate": d["default_samplerate"]})
        return inputs

    @staticmethod
    def get_default_input():
        try:
            info = sd.query_devices(kind="input")
            return info
        except Exception:
            return None

    def _audio_callback(self, indata, frames, time_info, status):
        if self.paused:
            return
        audio = indata[:, 0].copy()
        self.audio_queue.put(audio)
        self._all_audio.append(audio)
        # Compute RMS level for VU meter
        rms = float(np.sqrt(np.mean(audio ** 2)))
        try:
            self.level_queue.put_nowait(rms)
        except queue.Full:
            pass

    def start(self, device_index=None):
        self._all_audio = []
        self.recording = True
        self.paused = False
        # Drain queues
        while not self.audio_queue.empty():
            self.audio_queue.get_nowait()
        while not self.level_queue.empty():
            self.level_queue.get_nowait()

        kwargs = {
            "samplerate": self.sample_rate,
            "channels": self.channels,
            "dtype": "float32",
            "blocksize": int(self.sample_rate * self.chunk_duration),
            "callback": self._audio_callback,
        }
        if device_index is not None:
            kwargs["device"] = device_index

        self.stream = sd.InputStream(**kwargs)
        self.stream.start()

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def stop(self):
        self.recording = False
        self.paused = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

    def get_all_audio(self):
        if self._all_audio:
            return np.concatenate(self._all_audio)
        return np.array([], dtype=np.float32)

    def get_duration(self):
        total_samples = sum(len(a) for a in self._all_audio)
        return total_samples / self.sample_rate if self.sample_rate > 0 else 0

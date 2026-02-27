"""Hands-free Voice Mode for ChatGPT.

Features:
- Record audio via microphone with hotkeys (start/stop + pause/resume + quit)
- Local transcription with faster-whisper (GPU-ready, long recordings supported)
- Automatic send to chat model via OpenAI-compatible APIs (OpenAI/DeepSeek/etc.)
- Automatic text-to-speech playback (edge-tts preferred, pyttsx3 fallback)
- Copy transcript (and optionally reply) to clipboard

Run:
    python main.py --config config.json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import queue
import sys
import tempfile
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pyperclip
import sounddevice as sd
import soundfile as sf
from dotenv import load_dotenv
from faster_whisper import WhisperModel
from openai import OpenAI
from pynput import keyboard


try:
    import edge_tts
except Exception:  # noqa: BLE001
    edge_tts = None

try:
    import pyttsx3
except Exception:  # noqa: BLE001
    pyttsx3 = None


ASSISTANT_MODES: dict[str, str] = {
    "normal": "Antworte hilfreich, konkret und auf Deutsch.",
    "correct": "Korrigiere den folgenden Text sprachlich, ohne den Inhalt zu verändern.",
    "summarize": "Fasse den folgenden Text präzise in Stichpunkten zusammen.",
}


@dataclass
class AppConfig:
    provider: str
    api_key_env: str
    base_url: str
    chat_model: str
    system_prompt: str
    assistant_mode: str

    microphone_device: int | None
    samplerate: int
    channels: int

    whisper_model: str
    compute_type: str
    device: str
    language: str
    vad_filter: bool
    beam_size: int
    temperature: float

    tts_engine: str
    edge_voice: str
    edge_rate: str
    edge_volume: str
    pyttsx3_rate: int
    pyttsx3_volume: float

    copy_chat_reply_to_clipboard: bool
    hotkeys: dict[str, str]


class Recorder:
    """Streaming audio recorder with pause/resume support."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.audio_queue: queue.Queue[np.ndarray] = queue.Queue()
        self.frames: list[np.ndarray] = []
        self.stream: sd.InputStream | None = None

        self.is_recording = False
        self.is_paused = False

    def _audio_callback(self, indata: np.ndarray, frames: int, t: Any, status: sd.CallbackFlags) -> None:
        if status:
            print(f"[WARN] Audio callback status: {status}")
        if self.is_recording and not self.is_paused:
            self.audio_queue.put(indata.copy())

    def start(self) -> None:
        if self.is_recording:
            print("[INFO] Recording already active.")
            return

        self.frames.clear()
        self.audio_queue = queue.Queue()
        self.is_recording = True
        self.is_paused = False

        self.stream = sd.InputStream(
            samplerate=self.config.samplerate,
            channels=self.config.channels,
            dtype="float32",
            callback=self._audio_callback,
            device=self.config.microphone_device,
            blocksize=1024,
        )
        self.stream.start()
        print("[OK] Recording started.")

    def toggle_pause(self) -> None:
        if not self.is_recording:
            print("[INFO] Cannot pause: recording not active.")
            return
        self.is_paused = not self.is_paused
        print("[OK] Recording paused." if self.is_paused else "[OK] Recording resumed.")

    def stop(self) -> np.ndarray | None:
        if not self.is_recording:
            print("[INFO] No active recording.")
            return None

        self.is_recording = False

        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        while not self.audio_queue.empty():
            self.frames.append(self.audio_queue.get())

        if not self.frames:
            print("[WARN] No audio captured.")
            return None

        audio = np.concatenate(self.frames, axis=0).squeeze()
        duration = len(audio) / self.config.samplerate
        print(f"[OK] Recording stopped. Duration: {duration:.1f}s")
        return audio


class VoiceApp:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.recorder = Recorder(config)
        self.running = True

        api_key = os.getenv(config.api_key_env)
        if not api_key:
            raise RuntimeError(f"Missing API key. Set env var: {config.api_key_env}")

        self.client = OpenAI(api_key=api_key, base_url=config.base_url)

        print("[INIT] Loading Whisper model... (this can take a while)")
        self.whisper_model = WhisperModel(
            config.whisper_model,
            device=config.device,
            compute_type=config.compute_type,
        )
        print("[INIT] Whisper model ready.")

    def transcribe(self, audio: np.ndarray) -> str:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            temp_path = tmp.name

        try:
            sf.write(temp_path, audio, self.config.samplerate)
            segments, info = self.whisper_model.transcribe(
                temp_path,
                language=self.config.language,
                vad_filter=self.config.vad_filter,
                beam_size=self.config.beam_size,
                temperature=self.config.temperature,
                condition_on_previous_text=True,
            )
            text = " ".join(segment.text.strip() for segment in segments).strip()
            print(f"[OK] Transcribed ({info.language}/{info.language_probability:.2f}).")
            return text
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def build_user_prompt(self, transcript: str) -> str:
        mode_prompt = ASSISTANT_MODES.get(self.config.assistant_mode, ASSISTANT_MODES["normal"])
        return f"{mode_prompt}\n\n---\n{transcript}"

    def ask_llm(self, transcript: str) -> str:
        response = self.client.chat.completions.create(
            model=self.config.chat_model,
            messages=[
                {"role": "system", "content": self.config.system_prompt},
                {"role": "user", "content": self.build_user_prompt(transcript)},
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content or ""

    async def speak_edge(self, text: str) -> None:
        if edge_tts is None:
            raise RuntimeError("edge-tts not installed/importable.")

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            out_path = tmp.name

        try:
            communicate = edge_tts.Communicate(
                text,
                self.config.edge_voice,
                rate=self.config.edge_rate,
                volume=self.config.edge_volume,
            )
            await communicate.save(out_path)
            # Use sounddevice playback for minimal dependencies.
            data, samplerate = sf.read(out_path, dtype="float32")
            sd.play(data, samplerate)
            sd.wait()
        finally:
            Path(out_path).unlink(missing_ok=True)

    def speak_pyttsx3(self, text: str) -> None:
        if pyttsx3 is None:
            raise RuntimeError("pyttsx3 not installed/importable.")
        engine = pyttsx3.init()
        engine.setProperty("rate", self.config.pyttsx3_rate)
        engine.setProperty("volume", self.config.pyttsx3_volume)
        engine.say(text)
        engine.runAndWait()

    def speak(self, text: str) -> None:
        if not text.strip():
            return
        try:
            if self.config.tts_engine.lower() == "edge":
                asyncio.run(self.speak_edge(text))
            else:
                self.speak_pyttsx3(text)
        except Exception as exc:  # noqa: BLE001
            print(f"[WARN] TTS failed ({exc}). Falling back to pyttsx3 if available.")
            try:
                self.speak_pyttsx3(text)
            except Exception as fallback_exc:  # noqa: BLE001
                print(f"[ERR] Fallback TTS also failed: {fallback_exc}")

    def on_start_stop(self) -> None:
        if not self.recorder.is_recording:
            self.recorder.start()
            return

        audio = self.recorder.stop()
        if audio is None:
            return

        try:
            transcript = self.transcribe(audio)
            if not transcript:
                print("[WARN] Empty transcript.")
                return

            pyperclip.copy(transcript)
            print("\n[TRANSCRIPT]")
            print(transcript)
            print("[OK] Transcript copied to clipboard.")

            reply = self.ask_llm(transcript)
            print("\n[ASSISTANT]")
            print(reply)

            if self.config.copy_chat_reply_to_clipboard:
                pyperclip.copy(reply)
                print("[OK] Assistant reply copied to clipboard.")

            self.speak(reply)
        except Exception as exc:  # noqa: BLE001
            print(f"[ERR] Processing failed: {exc}")

    def on_pause_resume(self) -> None:
        self.recorder.toggle_pause()

    def on_quit(self) -> None:
        print("[OK] Quit requested.")
        if self.recorder.is_recording:
            self.recorder.stop()
        self.running = False

    def run(self) -> None:
        # Key strings are passed directly to pynput's HotKey parser.
        keymap = {
            self.config.hotkeys["start_stop"]: self.on_start_stop,
            self.config.hotkeys["pause_resume"]: self.on_pause_resume,
            self.config.hotkeys["quit"]: self.on_quit,
        }

        hotkeys = keyboard.GlobalHotKeys(keymap)

        print("\n=== Voice Mode Ready ===")
        print(f"Start/Stop: {self.config.hotkeys['start_stop']}")
        print(f"Pause/Resume: {self.config.hotkeys['pause_resume']}")
        print(f"Quit: {self.config.hotkeys['quit']}")
        print("Press hotkeys globally (works even outside terminal, OS permitting).\n")

        hotkeys.start()
        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.on_quit()
        finally:
            hotkeys.stop()


def load_config(path: str) -> AppConfig:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    return AppConfig(
        provider=raw.get("provider", "openai"),
        api_key_env=raw.get("api_key_env", "OPENAI_API_KEY"),
        base_url=raw.get("base_url", "https://api.openai.com/v1"),
        chat_model=raw.get("chat_model", "gpt-4o"),
        system_prompt=raw.get("system_prompt", "You are a helpful voice assistant."),
        assistant_mode=raw.get("assistant_mode", "normal"),
        microphone_device=raw.get("microphone_device"),
        samplerate=raw.get("samplerate", 16000),
        channels=raw.get("channels", 1),
        whisper_model=raw.get("whisper_model", "large-v3"),
        compute_type=raw.get("compute_type", "float16"),
        device=raw.get("device", "cuda"),
        language=raw.get("language", "de"),
        vad_filter=raw.get("vad_filter", True),
        beam_size=raw.get("beam_size", 5),
        temperature=raw.get("temperature", 0.0),
        tts_engine=raw.get("tts_engine", "edge"),
        edge_voice=raw.get("edge_voice", "de-DE-KatjaNeural"),
        edge_rate=raw.get("edge_rate", "+0%"),
        edge_volume=raw.get("edge_volume", "+0%"),
        pyttsx3_rate=raw.get("pyttsx3_rate", 190),
        pyttsx3_volume=raw.get("pyttsx3_volume", 1.0),
        copy_chat_reply_to_clipboard=raw.get("copy_chat_reply_to_clipboard", False),
        hotkeys=raw.get(
            "hotkeys",
            {
                "start_stop": "<f8>",
                "pause_resume": "<f9>",
                "quit": "<f10>",
            },
        ),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Hands-free Voice Mode for ChatGPT")
    parser.add_argument("--config", default="config.json", help="Path to config JSON file")
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="List available input devices and exit",
    )
    return parser.parse_args()


def main() -> int:
    load_dotenv()
    args = parse_args()

    if args.list_devices:
        print(sd.query_devices())
        return 0

    if not Path(args.config).exists():
        print(f"[ERR] Config not found: {args.config}")
        print("Copy config.example.json to config.json and edit values.")
        return 1

    try:
        config = load_config(args.config)
        app = VoiceApp(config)
        app.run()
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"[FATAL] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

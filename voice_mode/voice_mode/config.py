"""Konfiguration und Defaults für den Voice-Mode."""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


DEFAULT_CONFIG_PATH = Path(os.getenv("VOICE_CONFIG_PATH", "~/.config/voice_mode/settings.env")).expanduser()


@dataclass
class Settings:
    """Sammelobjekt für alle konfigurierbaren Parameter."""

    provider: str = "openai"
    api_key: Optional[str] = None
    api_base_url: Optional[str] = None
    model: str = "gpt-4o"

    whisper_model: str = "large-v3"
    whisper_download_root: str = str(Path("~/.cache/huggingface").expanduser())
    device: str = "auto"
    compute_type: str = "auto"
    language: Optional[str] = "de"
    vad_filter: bool = True
    chunk_length_seconds: float = 30.0

    samplerate: int = 16_000
    channels: int = 1
    block_duration_ms: int = 30

    hotkey: str = "<ctrl>+<alt>+s"

    tts_provider: str = "edge"
    tts_voice: str = "de-DE-KatjaNeural"
    tts_rate: str = "+0%"
    tts_volume: str = "0"

    list_models: bool = False
    prefetch_whisper: bool = False

    def ensure_device(self) -> str:
        if self.device != "auto":
            return self.device
        try:
            import torch  # type: ignore

            return "cuda" if torch.cuda.is_available() else "cpu"
        except Exception:
            return "cpu"

    def resolved_base_url(self) -> Optional[str]:
        if self.api_base_url:
            return self.api_base_url
        if self.provider == "lmstudio":
            return "http://127.0.0.1:1234/v1"
        if self.provider == "xai":
            return "https://api.x.ai/v1"
        return None


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def parse_args() -> Settings:
    parser = argparse.ArgumentParser(description="Hotkey-basierter Voice-Mode für ChatGPT")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="Pfad zu .env-ähnlicher Config")

    parser.add_argument("--provider", default=os.getenv("VOICE_PROVIDER", "openai"), help="openai, xai, lmstudio, custom")
    parser.add_argument("--api-key", default=os.getenv("VOICE_API_KEY") or os.getenv("OPENAI_API_KEY"), help="API-Key für Provider")
    parser.add_argument("--api-base-url", default=os.getenv("VOICE_API_BASE_URL"), help="OpenAI-kompatible Base URL")
    parser.add_argument("--model", default=os.getenv("VOICE_MODEL", os.getenv("OPENAI_MODEL", "gpt-4o")), help="Chat-Modell")
    parser.add_argument("--list-models", action="store_true", help="Modelle des gewählten Providers anzeigen und beenden")

    parser.add_argument("--whisper-model", default=os.getenv("WHISPER_MODEL", "large-v3"), help="Faster-Whisper Modell")
    parser.add_argument("--whisper-download-root", default=os.getenv("WHISPER_DOWNLOAD_ROOT", str(Path("~/.cache/huggingface").expanduser())), help="Lokaler Whisper Cache")
    parser.add_argument("--prefetch-whisper", action="store_true", help="Whisper Modell herunterladen und beenden")
    parser.add_argument("--device", default=os.getenv("WHISPER_DEVICE", "auto"), help="cuda, cpu oder auto")
    parser.add_argument("--compute-type", default=os.getenv("WHISPER_COMPUTE_TYPE", "auto"), help="float16, int8_float16, int8")
    parser.add_argument("--language", default=os.getenv("WHISPER_LANGUAGE", "de"), help="Sprach-Hint")
    parser.add_argument("--no-vad", action="store_true", help="VAD deaktivieren")
    parser.add_argument("--chunk-length", type=float, default=float(os.getenv("WHISPER_CHUNK", 30.0)), help="Chunk-Länge")

    parser.add_argument("--hotkey", default=os.getenv("VOICE_HOTKEY", "<ctrl>+<alt>+s"), help="Start/Stop-Hotkey")

    parser.add_argument("--tts-provider", default=os.getenv("TTS_PROVIDER", "edge"), help="edge oder pyttsx3")
    parser.add_argument("--tts-voice", default=os.getenv("TTS_VOICE", "de-DE-KatjaNeural"), help="edge-tts Stimme")
    parser.add_argument("--tts-rate", default=os.getenv("TTS_RATE", "+0%"), help="edge-tts Rate")
    parser.add_argument("--tts-volume", default=os.getenv("TTS_VOLUME", "0"), help="edge-tts Lautstärke")

    args = parser.parse_args()

    _load_env_file(Path(args.config).expanduser())
    provider = args.provider.lower()
    api_key = args.api_key or os.getenv("VOICE_API_KEY") or os.getenv("OPENAI_API_KEY")
    api_base_url = args.api_base_url or os.getenv("VOICE_API_BASE_URL")
    model = args.model or os.getenv("VOICE_MODEL")

    if provider != "lmstudio" and not api_key:
        parser.error("API-Key fehlt. Für lokalen LM Studio Provider ist kein Key notwendig.")

    return Settings(
        provider=provider,
        api_key=api_key,
        api_base_url=api_base_url,
        model=model,
        list_models=args.list_models,
        whisper_model=args.whisper_model,
        whisper_download_root=args.whisper_download_root,
        prefetch_whisper=args.prefetch_whisper,
        device=args.device,
        compute_type=args.compute_type,
        language=args.language,
        vad_filter=not args.no_vad,
        chunk_length_seconds=args.chunk_length,
        hotkey=args.hotkey,
        tts_provider=args.tts_provider,
        tts_voice=args.tts_voice,
        tts_rate=args.tts_rate,
        tts_volume=args.tts_volume,
    )

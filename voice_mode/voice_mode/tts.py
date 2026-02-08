"""Text-to-Speech mit edge-tts oder pyttsx3."""

from __future__ import annotations

import asyncio
import importlib.util
import tempfile
from pathlib import Path

import pyttsx3

from .config import Settings

edge_tts_spec = importlib.util.find_spec("edge_tts")
playsound_spec = importlib.util.find_spec("playsound")
if edge_tts_spec:
    import edge_tts  # type: ignore
else:  # pragma: no cover - optional dependency
    edge_tts = None  # type: ignore

if playsound_spec:
    from playsound import playsound
else:  # pragma: no cover - optional dependency
    playsound = None  # type: ignore


def _speak_edge(text: str, settings: Settings) -> None:
    if edge_tts is None or playsound is None:
        raise RuntimeError("edge-tts oder playsound nicht verfügbar")

    async def _run() -> None:
        communicator = edge_tts.Communicate(
            text,
            voice=settings.tts_voice,
            rate=settings.tts_rate,
            volume=settings.tts_volume,
        )
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            path = Path(tmp.name)
        try:
            async for chunk in communicator.stream():
                if chunk["type"] == "audio":
                    with path.open("ab") as f:
                        f.write(chunk["data"])
            playsound(str(path))
        finally:
            if path.exists():
                path.unlink(missing_ok=True)

    asyncio.run(_run())


def _speak_pyttsx3(text: str) -> None:
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def speak(text: str, settings: Settings) -> None:
    """Sprich den Text mit dem gewünschten Provider."""

    if not text.strip():
        return
    try:
        if settings.tts_provider.lower() == "edge":
            _speak_edge(text, settings)
        else:
            _speak_pyttsx3(text)
    except Exception as exc:
        print(f"[warn] TTS fehlgeschlagen ({exc}), fallback auf pyttsx3")
        _speak_pyttsx3(text)


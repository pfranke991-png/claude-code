"""CLI-Einstiegspunkt für den Hotkey-basierten Voice-Mode."""

from __future__ import annotations

import numpy as np

from .audio_recorder import AudioRecorder
from .chat_client import ChatClient
from .config import Settings, parse_args
from .hotkeys import HotkeyController
from .transcriber import Transcriber
from .tts import speak


class VoiceLoop:
    """Koordiniert Aufnahme, Transkription, Chat und TTS."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.recorder = AudioRecorder(settings.samplerate, settings.channels, settings.block_duration_ms)
        self.transcriber = Transcriber(settings)
        self.chat = ChatClient(settings)
        self.hotkeys = HotkeyController(settings.hotkey)

    def run(self) -> None:
        print("[info] Voice-Loop bereit. Hotkey drücken zum Starten. STRG+C beendet.")
        self.hotkeys.start()
        try:
            while True:
                print("[status] Warte auf Start-Hotkey …")
                self.hotkeys.wait_for_trigger()
                self.recorder.start()
                print("[status] Aufnahme läuft. Hotkey erneut drücken zum Stoppen …")
                self.hotkeys.wait_for_trigger()
                try:
                    audio = self.recorder.stop()
                except Exception as exc:
                    print(f"[error] Aufnahme fehlgeschlagen: {exc}")
                    continue
                self._process(audio)
        except KeyboardInterrupt:
            print("\n[info] Beendet per Tastatur.")
        finally:
            self.hotkeys.stop()

    def _process(self, audio: np.ndarray) -> None:
        try:
            transcript = self.transcriber.transcribe(audio)
            if not transcript:
                print("[warn] Kein Transkript erzeugt.")
                return
            answer = self.chat.ask(transcript)
            speak(answer, self.settings)
        except Exception as exc:
            print(f"[error] Verarbeitung fehlgeschlagen: {exc}")


def main() -> None:
    settings = parse_args()
    if settings.list_models:
        client = ChatClient(settings)
        for model in client.list_models():
            print(model)
        return
    if settings.prefetch_whisper:
        Transcriber(settings)
        print("[info] Whisper-Modell ist lokal verfügbar.")
        return
    loop = VoiceLoop(settings)
    loop.run()


if __name__ == "__main__":
    main()

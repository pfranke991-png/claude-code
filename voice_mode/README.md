# Voice Mode für ChatGPT (Python)

Überarbeiteter Voice-Workflow mit Hotkey-Aufnahme, lokaler Faster-Whisper-Transkription und direkter Antwort-Wiedergabe per TTS.

## Was jetzt verbessert wurde
- **Mehrere API-Quellen**: `openai`, `xai`, `lmstudio` (localhost) oder `custom` via OpenAI-kompatibler Base URL.
- **Model-Liste abrufen**: verfügbare Modelle pro Provider direkt per CLI (`--list-models`) oder Settings-GUI laden.
- **Lokale Whisper-Nutzung**: Standard jetzt `large-v3`, Download-Cache konfigurierbar, Vorab-Download per `--prefetch-whisper`.
- **Settings-GUI**: `python -m voice_mode.settings_gui` zum Speichern von Provider/API-Key/Model in `~/.config/voice_mode/settings.env`.
- **CPU/GPU Compute-Type Fix**: korrekte Auswahl von `float16` (CUDA) vs. `int8` (CPU).

## Schnellstart
```bash
cd voice_mode
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Optional: GUI öffnen und Settings speichern
python -m voice_mode.settings_gui

# Whisper Modell einmalig lokal cachen
python -m voice_mode.main --prefetch-whisper --whisper-model large-v3

# Modelle des Providers anzeigen
python -m voice_mode.main --provider openai --list-models

# Voice Loop starten
python -m voice_mode.main --provider openai --model gpt-4o --hotkey "<ctrl>+<alt>+s"
```

Für **LM Studio lokal**:
```bash
python -m voice_mode.main --provider lmstudio --model <dein-lokales-modell>
```
(LM Studio sollte auf `http://127.0.0.1:1234/v1` laufen.)

## Konfiguration
Die App lädt zuerst CLI-Parameter, danach optional `--config` (Default: `~/.config/voice_mode/settings.env`) für fehlende Werte.

| Option | Env | Default | Beschreibung |
| --- | --- | --- | --- |
| `--provider` | `VOICE_PROVIDER` | `openai` | `openai`, `xai`, `lmstudio`, `custom` |
| `--api-key` | `VOICE_API_KEY` / `OPENAI_API_KEY` | - | API-Key (bei `lmstudio` optional) |
| `--api-base-url` | `VOICE_API_BASE_URL` | providerabhängig | OpenAI-kompatible URL |
| `--model` | `VOICE_MODEL` / `OPENAI_MODEL` | `gpt-4o` | Chatmodell |
| `--list-models` | - | `false` | verfügbare Modelle ausgeben |
| `--whisper-model` | `WHISPER_MODEL` | `large-v3` | Whisper-Modell |
| `--whisper-download-root` | `WHISPER_DOWNLOAD_ROOT` | `~/.cache/huggingface` | lokaler Cache |
| `--prefetch-whisper` | - | `false` | Modell vorab herunterladen |
| `--device` | `WHISPER_DEVICE` | `auto` | `cuda`, `cpu`, `auto` |
| `--compute-type` | `WHISPER_COMPUTE_TYPE` | `auto` | z.B. `float16`, `int8` |
| `--hotkey` | `VOICE_HOTKEY` | `<ctrl>+<alt>+s` | Aufnahme Start/Stop |
| `--tts-provider` | `TTS_PROVIDER` | `edge` | `edge` oder `pyttsx3` |
| `--tts-voice` | `TTS_VOICE` | `de-DE-KatjaNeural` | Stimme |

## Zur Stimme „Eve"
Ein 1:1 Voice-Cloning der spezifischen Grok-"Eve"-Stimme ist ohne dediziertes Cloning-Modell/Voice-Lizenz nicht enthalten. Du kannst aber mit `edge-tts` nahe Stimmen testen (z.B. andere Neural Voices) oder später ElevenLabs/XTTS integrieren.

## Nächste sinnvolle Upgrades
- Verlauf in SQLite speichern (Transkript + Antwort + Audio-Metadaten)
- Streaming-Antworten sofort sprechen (geringere gefühlte Latenz)
- VAD vor Aufnahme (Push-to-talk + Auto-stop bei Stille)
- Alternative TTS-Backends (OpenAI TTS, Kokoro, Coqui XTTS)

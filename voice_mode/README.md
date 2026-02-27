# Voice Mode (Python, Faster-Whisper + ChatGPT + TTS)

Dieses Projekt ist ein **hands-free Voice-Mode**, der lokal transkribiert und automatisch mit einem LLM + Sprachausgabe arbeitet:

1. Aufnahme per Hotkey starten/stoppen (inkl. Pause/Resume)
2. Transkription lokal mit `faster-whisper` (z. B. `medium` / `large-v3`)
3. Transkript automatisch in die Zwischenablage kopieren
4. Transkript an ein OpenAI-kompatibles Chat-Modell senden (z. B. OpenAI, DeepSeek via Base-URL)
5. Antwort automatisch vorlesen (`edge-tts`, Fallback `pyttsx3`)

---

## Setup

```bash
cd voice_mode
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp config.example.json config.json
```

Setze deinen API-Key als Umgebungsvariable (abhängig von `api_key_env`):

```bash
export OPENAI_API_KEY="..."
# oder z.B.
export DEEPSEEK_API_KEY="..."
```

Dann starten:

```bash
python main.py --config config.json
```

Optional: Mikrofon-Geräte anzeigen:

```bash
python main.py --list-devices
```

---

## Konfiguration (`config.json`)

### API / LLM

- `provider`: Freitext-Label (z. B. `openai`, `deepseek`), aktuell nur für Dokumentation/Logik-Readability
- `api_key_env`: Name der Env-Variable mit API-Key
- `base_url`: API-Endpunkt (OpenAI-kompatibel)
  - OpenAI: `https://api.openai.com/v1`
  - DeepSeek (kompatibel): z. B. `https://api.deepseek.com/v1`
- `chat_model`: Chatmodell, z. B. `gpt-4o`
- `system_prompt`: globaler Assistant-Kontext
- `assistant_mode`:
  - `normal` = normal antworten
  - `correct` = nur Korrektur
  - `summarize` = Zusammenfassung

### Aufnahme / Whisper

- `microphone_device`: Geräte-Index (`null` = Standard-Mikro)
- `samplerate`: Empfehlung `16000`
- `channels`: typischerweise `1`
- `whisper_model`: `medium` / `large-v3`
- `device`: `cuda` (GPU) oder `cpu`
- `compute_type`:
  - GPU meist `float16`
  - CPU ggf. `int8` für weniger RAM/VRAM
- `language`: z. B. `de`, `en`
- `vad_filter`: aktiviert Voice Activity Detection
- `beam_size`: Genauigkeit vs. Latenz
- `temperature`: deterministic vs. kreativ

### TTS

- `tts_engine`: `edge` (empfohlen) oder `pyttsx3`
- `edge_voice`, `edge_rate`, `edge_volume`
- `pyttsx3_rate`, `pyttsx3_volume`

### Clipboard / Hotkeys

- `copy_chat_reply_to_clipboard`: Antwort ebenfalls kopieren
- `hotkeys.start_stop`: Aufnahme Start/Stop
- `hotkeys.pause_resume`: Pause/Fortsetzen
- `hotkeys.quit`: Programm beenden

---

## Bedienung

Nach Start zeigt die App Hotkeys an (Standard):

- `F8`: Start/Stop Aufnahme
- `F9`: Pause/Resume
- `F10`: Beenden

Flow:

1. F8 drücken und sprechen (auch längere Sessions möglich)
2. Optional F9 für Pausen
3. F8 stoppt und startet Verarbeitung
4. Transkript wird in Clipboard kopiert
5. LLM-Antwort wird erzeugt und vorgelesen

---

## Robustheit / Fehlerbehandlung

- Import-Fallback für TTS (`edge-tts` → `pyttsx3`)
- Fängt API-, Audio- und Laufzeitfehler ab
- Meldet leere Aufnahmen oder leere Transkripte klar

---

## Performance-Tipps (niedrige Latenz)

1. **GPU nutzen (`device=cuda`)** + `compute_type=float16`
2. Für schnellere Antwort statt `large-v3` testweise `medium` nehmen
3. `beam_size` reduzieren (z. B. 1–3) für Speed
4. Schlanke `system_prompt` / kurze Antworten forcieren
5. Gute Mikrofonqualität + konstante Eingangslautstärke

---

## Bonus-Ideen / nächste Schritte

- **Batch-Processing**: mehrfache Aufnahmen im Job-Queue-Modus
- **Streaming-Whisper**: echte laufende Teiltranskripte statt End-of-recording
- **Alternative TTS**: Coqui XTTS, ElevenLabs, Azure TTS
- **Chat-Logging**: JSONL/SQLite Speicherung aller Dialoge
- **Mini-GUI**: Tray-App mit Status, Pegel, Modus-Umschalter
- **Auto-Punctuation/Post-Processing**: Formatierung je nach Ziel (Mail, Notizen, Prompt)
- **Push-to-talk statt Toggle** für bestimmte Workflows

---

## Hinweis

`pynput`-Hotkeys können je nach Betriebssystem zusätzliche Berechtigungen benötigen.
Wenn globale Hotkeys nicht funktionieren, teste das Skript zunächst im aktiven Terminalfenster.

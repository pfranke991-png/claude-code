#!/usr/bin/env python3
"""
Voice Transcriber — NanoGPT Edition
Sprachaufnahme -> Whisper -> Transkription -> NanoGPT Chat
"""

import customtkinter as ctk
import tkinter as tk
import threading
import json
import os
import tempfile
import time
import sys
from pathlib import Path
from datetime import datetime

# ── Konstanten ────────────────────────────────────────────────────────────────

SETTINGS_PATH = Path.home() / ".voice_transcriber_settings.json"
SAMPLE_RATE = 16000
CHANNELS = 1

# Alle verfuegbaren Modelle (NanoGPT OpenAI-kompatibel)
MODELS: dict[str, str] = {
    "DeepSeek V4 Pro  [Thinking]": "deepseek/deepseek-v4-pro:thinking",
    "DeepSeek V4 Pro": "deepseek/deepseek-v4-pro",
    "MIMO 2.5 Pro  [Thinking]": "xiaomi/mimo-v2.5-pro:thinking",
    "MIMO 2.5 Pro": "xiaomi/mimo-v2.5-pro",
    "MIMO 2.5  [Thinking]": "xiaomi/mimo-v2.5:thinking",
    "MIMO 2.5": "xiaomi/mimo-v2.5",
    "GLM 5.1  [Thinking]": "zai-org/glm-5.1:thinking",
    "GLM 5.1": "zai-org/glm-5.1",
    "GLM 5.1 TEE": "TEE/glm-5.1",
}

WHISPER_MODELS = [
    "tiny", "base", "small", "medium",
    "large", "large-v2", "large-v3", "large-v3-turbo",
]

DEFAULT_SETTINGS: dict = {
    "nanogpt_api_key": "",
    "whisper_model": "large-v3",
    "ai_model": "deepseek/deepseek-v4-pro:thinking",
    "auto_copy": True,
    "language": "auto",
    "system_prompt": "Du bist ein hilfreicher Assistent.",
    "auto_send_to_ai": True,
}

# ── Farbpalette ───────────────────────────────────────────────────────────────

C = {
    "bg_deep":    "#0d0d1a",
    "bg_mid":     "#131320",
    "bg_header":  "#1a1a2e",
    "bubble_usr": "#163a6e",
    "bubble_ai":  "#1a1a2e",
    "accent":     "#4da6ff",
    "red":        "#c0392b",
    "green":      "#27ae60",
    "muted":      "#55556a",
    "border":     "#2a2a3e",
    "text":       "#e0e0f0",
}

# ── Einstellungen I/O ─────────────────────────────────────────────────────────

def load_settings() -> dict:
    if SETTINGS_PATH.exists():
        try:
            with open(SETTINGS_PATH, encoding="utf-8") as f:
                saved = json.load(f)
            return {**DEFAULT_SETTINGS, **saved}
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()


def save_settings(s: dict):
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(s, f, indent=2, ensure_ascii=False)


# ── Audio-Aufnahme ────────────────────────────────────────────────────────────

class AudioRecorder:
    def __init__(self):
        self._frames: list = []
        self._stream = None
        self.recording = False

    def start(self):
        import sounddevice as sd
        self._frames = []
        self.recording = True
        self._stream = sd.InputStream(
            samplerate=SAMPLE_RATE, channels=CHANNELS,
            dtype="float32", callback=self._cb,
        )
        self._stream.start()

    def _cb(self, indata, frames, time_info, status):
        if self.recording:
            self._frames.append(indata.copy())

    def stop(self):
        self.recording = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        if not self._frames:
            return None
        import numpy as np
        return np.concatenate(self._frames, axis=0)

    def save_wav(self, audio, path: str):
        import soundfile as sf
        sf.write(path, audio, SAMPLE_RATE)


# ── Whisper-Transkription ─────────────────────────────────────────────────────

class WhisperTranscriber:
    def __init__(self):
        self._model = None
        self._loaded_name: str | None = None
        self._lock = threading.Lock()

    def load(self, model_name: str, on_status=None):
        with self._lock:
            if self._loaded_name == model_name and self._model is not None:
                return
            if on_status:
                on_status(f"Lade Whisper '{model_name}' (erster Start: Download) ...")
            import whisper
            self._model = whisper.load_model(model_name)
            self._loaded_name = model_name

    def transcribe(self, path: str, model_name: str,
                   language: str | None = None,
                   on_status=None) -> str:
        self.load(model_name, on_status=on_status)
        if on_status:
            on_status("Transkribiere ...")
        opts: dict = {}
        if language and language != "auto":
            opts["language"] = language
        result = self._model.transcribe(str(path), **opts)
        return result["text"].strip()


# ── NanoGPT API-Client ────────────────────────────────────────────────────────

class NanoGPTClient:
    BASE_URL = "https://nano-gpt.com/api/v1"

    def __init__(self, api_key: str):
        from openai import OpenAI
        self._c = OpenAI(api_key=api_key, base_url=self.BASE_URL)

    def stream(self, messages: list, model: str):
        resp = self._c.chat.completions.create(
            model=model, messages=messages, stream=True,
        )
        for chunk in resp:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content


# ── Einstellungs-Fenster ──────────────────────────────────────────────────────

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent, settings: dict, on_save):
        super().__init__(parent)
        self.title("Einstellungen")
        self.geometry("580x720")
        self.resizable(False, True)
        self.grab_set()
        self._s = settings.copy()
        self._on_save = on_save
        self._build()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self):
        ctk.CTkLabel(self, text="  Einstellungen",
                     font=("Segoe UI", 20, "bold"),
                     text_color=C["accent"]).pack(anchor="w", padx=24, pady=(20, 4))

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=16, pady=4)

        # API-Key
        self._sec(scroll, "API-Key — NanoGPT")
        ctk.CTkLabel(scroll, text="API-Key:", anchor="w",
                     font=("Segoe UI", 12)).pack(fill="x", pady=(4, 2))
        self._key_var = ctk.StringVar(value=self._s.get("nanogpt_api_key", ""))
        row = ctk.CTkFrame(scroll, fg_color="transparent")
        row.pack(fill="x")
        self._key_entry = ctk.CTkEntry(
            row, textvariable=self._key_var, show="*", height=38,
            placeholder_text="nano-xxxxxxxxxxxxxxxx",
            font=("Courier New", 12),
        )
        self._key_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkButton(row, text="Zeigen", width=70, height=38,
                      command=self._toggle_key).pack(side="left")

        # KI-Modell
        self._sec(scroll, "KI-Modell")
        ctk.CTkLabel(scroll, text="Standard-Modell:", anchor="w",
                     font=("Segoe UI", 12)).pack(fill="x", pady=(4, 2))
        self._model_var = ctk.StringVar(value=self._to_display(self._s.get("ai_model", "")))
        ctk.CTkOptionMenu(
            scroll, variable=self._model_var,
            values=list(MODELS.keys()), height=38, dynamic_resizing=False,
        ).pack(fill="x")
        self._auto_send_var = ctk.BooleanVar(value=self._s.get("auto_send_to_ai", True))
        ctk.CTkCheckBox(
            scroll, text="Transkription automatisch an KI senden",
            variable=self._auto_send_var, font=("Segoe UI", 12),
        ).pack(anchor="w", pady=(10, 0))

        # Whisper
        self._sec(scroll, "Whisper Spracherkennung (lokales Modell)")
        self._whisper_var = ctk.StringVar(value=self._s.get("whisper_model", "large-v3"))
        ctk.CTkOptionMenu(
            scroll, variable=self._whisper_var,
            values=WHISPER_MODELS, height=38, width=200,
        ).pack(anchor="w", pady=(4, 2))
        ctk.CTkLabel(
            scroll,
            text=(
                "  tiny ~75 MB  |  base ~145 MB  |  small ~460 MB\n"
                "  medium ~1.5 GB  |  large-v3 ~3.1 GB  (empfohlen)\n"
                "  Wird automatisch beim ersten Start heruntergeladen."
            ),
            font=("Segoe UI", 10), text_color=C["muted"], justify="left",
        ).pack(anchor="w")

        # Sprache
        self._sec(scroll, "Erkennungssprache")
        self._lang_var = ctk.StringVar(value=self._s.get("language", "auto"))
        ctk.CTkOptionMenu(
            scroll, variable=self._lang_var,
            values=["auto", "de", "en", "fr", "es", "it", "ja", "zh", "ar"],
            height=38, width=180,
        ).pack(anchor="w", pady=(4, 0))
        ctk.CTkLabel(scroll, text="  'auto' = automatische Erkennung",
                     font=("Segoe UI", 10), text_color=C["muted"]).pack(anchor="w")

        # System-Prompt
        self._sec(scroll, "System-Prompt (Anweisung an KI)")
        self._prompt_box = ctk.CTkTextbox(scroll, height=80, font=("Segoe UI", 12))
        self._prompt_box.pack(fill="x", pady=(4, 0))
        self._prompt_box.insert("1.0", self._s.get("system_prompt", "Du bist ein hilfreicher Assistent."))

        # Verhalten
        self._sec(scroll, "Verhalten")
        self._copy_var = ctk.BooleanVar(value=self._s.get("auto_copy", True))
        ctk.CTkCheckBox(
            scroll, text="Transkription automatisch in Zwischenablage kopieren",
            variable=self._copy_var, font=("Segoe UI", 12),
        ).pack(anchor="w", pady=(4, 0))

        # Buttons
        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.pack(fill="x", padx=24, pady=(8, 20))
        ctk.CTkButton(btns, text="Abbrechen", fg_color=C["bg_mid"],
                      hover_color=C["border"], width=120,
                      command=self.destroy).pack(side="right", padx=(8, 0))
        ctk.CTkButton(btns, text="Speichern", width=130,
                      command=self._save).pack(side="right")

    def _sec(self, parent, title: str):
        ctk.CTkLabel(parent, text=title, font=("Segoe UI", 13, "bold"),
                     text_color=C["accent"], anchor="w").pack(fill="x", pady=(16, 2))
        ctk.CTkFrame(parent, height=1, fg_color=C["border"]).pack(fill="x", pady=(0, 6))

    def _toggle_key(self):
        cur = self._key_entry.cget("show")
        self._key_entry.configure(show="" if cur == "*" else "*")

    def _to_display(self, model_id: str) -> str:
        return next((k for k, v in MODELS.items() if v == model_id), list(MODELS.keys())[0])

    def _save(self):
        self._s["nanogpt_api_key"]  = self._key_var.get().strip()
        self._s["ai_model"]         = MODELS[self._model_var.get()]
        self._s["whisper_model"]    = self._whisper_var.get()
        self._s["language"]         = self._lang_var.get()
        self._s["system_prompt"]    = self._prompt_box.get("1.0", "end-1c").strip()
        self._s["auto_copy"]        = self._copy_var.get()
        self._s["auto_send_to_ai"]  = self._auto_send_var.get()
        save_settings(self._s)
        self._on_save(self._s)
        self.destroy()


# ── Haupt-Fenster ─────────────────────────────────────────────────────────────

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Voice Transcriber — NanoGPT")
        self.geometry("960x740")
        self.minsize(720, 520)
        self.configure(fg_color=C["bg_deep"])

        self._settings  = load_settings()
        self._recorder  = AudioRecorder()
        self._whisper   = WhisperTranscriber()
        self._recording = False
        self._busy      = False
        self._history:  list[dict] = []

        self._build_header()
        self._build_chat()
        self._build_status()
        self._build_toolbar()

        self._sys_msg("Bereit! Klicke auf   REC   oder druecke [Leertaste] zum Aufnehmen.")
        self._init_whisper()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_header(self):
        h = ctk.CTkFrame(self, height=56, fg_color=C["bg_header"], corner_radius=0)
        h.pack(fill="x")
        h.pack_propagate(False)

        ctk.CTkLabel(h, text="  Voice Transcriber",
                     font=("Segoe UI", 17, "bold"),
                     text_color=C["accent"]).pack(side="left", padx=16)

        # Settings + Clear buttons
        ctk.CTkButton(h, text="Einstellungen", width=120, height=32,
                      font=("Segoe UI", 12),
                      fg_color=C["bg_mid"], hover_color=C["border"],
                      command=self._open_settings).pack(side="right", padx=(0, 14))
        ctk.CTkButton(h, text="Chat leeren", width=100, height=32,
                      font=("Segoe UI", 12),
                      fg_color="#2a1010", hover_color="#3a1818",
                      command=self._clear_chat).pack(side="right", padx=(0, 6))

        # Model selector
        ctk.CTkLabel(h, text="Modell:", font=("Segoe UI", 11),
                     text_color=C["muted"]).pack(side="right", padx=(8, 4))
        self._model_var = ctk.StringVar(value=self._to_display(self._settings["ai_model"]))
        ctk.CTkOptionMenu(
            h, variable=self._model_var, values=list(MODELS.keys()),
            height=32, width=280, dynamic_resizing=False,
            command=self._on_model_change,
        ).pack(side="right", padx=(0, 6))

    def _build_chat(self):
        self._chat = ctk.CTkScrollableFrame(
            self, fg_color=C["bg_deep"],
            scrollbar_button_color=C["bg_mid"],
            scrollbar_button_hover_color=C["border"],
        )
        self._chat.pack(fill="both", expand=True)
        self._chat.columnconfigure(0, weight=1)

    def _build_status(self):
        sb = ctk.CTkFrame(self, height=26, fg_color=C["bg_mid"], corner_radius=0)
        sb.pack(fill="x")
        sb.pack_propagate(False)
        self._status_var = ctk.StringVar(value="Starte ...")
        ctk.CTkLabel(sb, textvariable=self._status_var,
                     font=("Segoe UI", 11), text_color=C["muted"]).pack(side="left", padx=14)
        self._clip_lbl = ctk.CTkLabel(sb, text="",
                                       font=("Segoe UI", 11), text_color=C["accent"])
        self._clip_lbl.pack(side="right", padx=14)

    def _build_toolbar(self):
        tb = ctk.CTkFrame(self, height=76, fg_color=C["bg_header"], corner_radius=0)
        tb.pack(fill="x")
        tb.pack_propagate(False)

        # Record button (right side, prominent)
        self._rec_btn = ctk.CTkButton(
            tb, text="  REC", width=110, height=46,
            font=("Segoe UI", 14, "bold"),
            fg_color=C["red"], hover_color="#e74c3c",
            command=self._toggle_rec,
        )
        self._rec_btn.pack(side="right", padx=(0, 16), pady=15)

        # Send button
        self._send_btn = ctk.CTkButton(
            tb, text="Senden", width=80, height=46,
            font=("Segoe UI", 13),
            command=self._send_text,
        )
        self._send_btn.pack(side="right", padx=(0, 6), pady=15)

        # Text input
        self._input = ctk.CTkEntry(
            tb, height=46, font=("Segoe UI", 13),
            fg_color=C["bg_mid"], border_color=C["border"],
            placeholder_text="Nachricht tippen oder REC druecken ...",
        )
        self._input.pack(side="left", fill="x", expand=True, padx=16, pady=15)
        self._input.bind("<Return>", lambda _e: self._send_text())

        # Spacebar toggles recording (only when input not focused)
        self.bind("<space>", self._on_space)

    # ── Hilfsmethoden ─────────────────────────────────────────────────────────

    def _to_display(self, model_id: str) -> str:
        return next((k for k, v in MODELS.items() if v == model_id), list(MODELS.keys())[0])

    def _set_status(self, text: str):
        self.after(0, lambda: self._status_var.set(text))

    def _scroll_bottom(self):
        self.after(80, lambda: self._chat._parent_canvas.yview_moveto(1.0))

    def _sys_msg(self, text: str):
        row = ctk.CTkFrame(self._chat, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=3)
        ctk.CTkLabel(row, text=text, font=("Segoe UI", 11),
                     text_color=C["muted"], wraplength=750, justify="center").pack()
        self._scroll_bottom()

    def _user_bubble(self, text: str):
        ts = datetime.now().strftime("%H:%M")
        row = ctk.CTkFrame(self._chat, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=4)
        bubble = ctk.CTkFrame(row, fg_color=C["bubble_usr"], corner_radius=18)
        bubble.pack(anchor="e", padx=(100, 6))
        ctk.CTkLabel(bubble, text=text, font=("Segoe UI", 13),
                     wraplength=580, justify="left",
                     padx=16, pady=10).pack()
        ctk.CTkLabel(bubble, text=ts, font=("Segoe UI", 9),
                     text_color="#4488bb", padx=14, pady=(0, 6)).pack(anchor="e")
        self._scroll_bottom()

    def _ai_bubble(self) -> ctk.CTkLabel:
        ts = datetime.now().strftime("%H:%M")
        row = ctk.CTkFrame(self._chat, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=4)
        bubble = ctk.CTkFrame(row, fg_color=C["bubble_ai"], corner_radius=18,
                               border_width=1, border_color=C["border"])
        bubble.pack(anchor="w", padx=(6, 100))
        name = self._model_var.get().split("[")[0].strip()
        ctk.CTkLabel(bubble, text=f"  {name}", font=("Segoe UI", 10, "bold"),
                     text_color=C["accent"], padx=16, pady=(10, 2)).pack(anchor="w")
        lbl = ctk.CTkLabel(bubble, text="...", font=("Segoe UI", 13),
                            wraplength=580, justify="left",
                            padx=16, pady=(2, 10))
        lbl.pack(anchor="w")
        ctk.CTkLabel(bubble, text=ts, font=("Segoe UI", 9),
                     text_color=C["muted"], padx=14, pady=(0, 6)).pack(anchor="w")
        self._scroll_bottom()
        return lbl

    # ── Whisper init ──────────────────────────────────────────────────────────

    def _init_whisper(self):
        def _run():
            try:
                mdl = self._settings["whisper_model"]
                self._set_status(f"Lade Whisper '{mdl}' ...")
                self._whisper.load(mdl, on_status=self._set_status)
                self._set_status(f"Bereit  —  Whisper '{mdl}' geladen")
            except Exception as exc:
                self._set_status(f"Whisper-Fehler: {exc}")
        threading.Thread(target=_run, daemon=True).start()

    # ── Aufnahme ──────────────────────────────────────────────────────────────

    def _on_space(self, _event):
        if self.focus_get() is self._input:
            return
        self._toggle_rec()

    def _toggle_rec(self):
        if self._recording:
            self._stop_rec()
        else:
            self._start_rec()

    def _start_rec(self):
        if self._recording:
            return
        self._recording = True
        self._rec_btn.configure(text="  STOP", fg_color=C["green"],
                                 hover_color="#2ecc71")
        self._set_status("  Aufnahme laeuft ... (erneut klicken zum Stoppen)")
        try:
            self._recorder.start()
        except Exception as exc:
            self._recording = False
            self._rec_btn.configure(text="  REC", fg_color=C["red"],
                                     hover_color="#e74c3c")
            self._set_status(f"Mikrofon-Fehler: {exc}")

    def _stop_rec(self):
        if not self._recording:
            return
        self._recording = False
        self._rec_btn.configure(text="  REC", fg_color=C["red"],
                                 hover_color="#e74c3c", state="disabled")
        self._set_status("Verarbeite Aufnahme ...")

        def _run():
            try:
                audio = self._recorder.stop()
                if audio is None or len(audio) / SAMPLE_RATE < 0.3:
                    self._set_status("  Aufnahme zu kurz (min. 0.3 s)")
                    return
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                    tmp = f.name
                self._recorder.save_wav(audio, tmp)
                text = self._whisper.transcribe(
                    tmp, self._settings["whisper_model"],
                    language=self._settings.get("language"),
                    on_status=self._set_status,
                )
                os.unlink(tmp)
                if not text:
                    self._set_status("  Nichts erkannt")
                    return
                self.after(0, lambda t=text: self._on_transcript(t))
            except Exception as exc:
                self._set_status(f"Fehler: {exc}")
            finally:
                self.after(0, lambda: self._rec_btn.configure(state="normal"))

        threading.Thread(target=_run, daemon=True).start()

    def _on_transcript(self, text: str):
        # Clipboard
        if self._settings.get("auto_copy", True):
            try:
                import pyperclip
                pyperclip.copy(text)
                self._clip_lbl.configure(text="  Kopiert!")
                self.after(3500, lambda: self._clip_lbl.configure(text=""))
            except Exception:
                pass

        self._user_bubble(text)
        self._history.append({"role": "user", "content": text})
        self._set_status("  Transkription abgeschlossen")

        if self._settings.get("auto_send_to_ai") and self._settings.get("nanogpt_api_key"):
            self._ask_ai()

    # ── Text senden ───────────────────────────────────────────────────────────

    def _send_text(self):
        text = self._input.get().strip()
        if not text:
            return
        self._input.delete(0, "end")
        self._user_bubble(text)
        self._history.append({"role": "user", "content": text})
        if not self._settings.get("nanogpt_api_key"):
            self._sys_msg("Kein API-Key gesetzt — bitte in Einstellungen eintragen.")
        else:
            self._ask_ai()

    # ── KI-Anfrage ────────────────────────────────────────────────────────────

    def _ask_ai(self):
        if self._busy:
            return
        self._busy = True
        self._set_status("Anfrage an KI ...")

        lbl = self._ai_bubble()
        msgs: list[dict] = []
        sp = self._settings.get("system_prompt", "").strip()
        if sp:
            msgs.append({"role": "system", "content": sp})
        msgs.extend(self._history)
        model = self._settings["ai_model"]
        key   = self._settings["nanogpt_api_key"]

        def _run():
            try:
                client = NanoGPTClient(key)
                full = ""
                for chunk in client.stream(msgs, model):
                    full += chunk
                    self.after(0, lambda t=full: lbl.configure(text=t))
                    self._scroll_bottom()
                self._history.append({"role": "assistant", "content": full})
                self._set_status("  Bereit")
            except Exception as exc:
                self.after(0, lambda e=str(exc): lbl.configure(text=f"[Fehler: {e}]"))
                self._set_status(f"KI-Fehler: {exc}")
            finally:
                self._busy = False

        threading.Thread(target=_run, daemon=True).start()

    # ── Steuerung ─────────────────────────────────────────────────────────────

    def _on_model_change(self, name: str):
        self._settings["ai_model"] = MODELS[name]
        save_settings(self._settings)

    def _clear_chat(self):
        for w in self._chat.winfo_children():
            w.destroy()
        self._history.clear()
        self._sys_msg("Chat geleert.")

    def _open_settings(self):
        SettingsWindow(self, self._settings, on_save=self._apply_settings)

    def _apply_settings(self, new: dict):
        old_whisper = self._settings.get("whisper_model")
        self._settings = new
        self._model_var.set(self._to_display(new["ai_model"]))
        if old_whisper != new.get("whisper_model"):
            self._init_whisper()


# ── Einstiegspunkt ────────────────────────────────────────────────────────────

def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    App().mainloop()


if __name__ == "__main__":
    main()

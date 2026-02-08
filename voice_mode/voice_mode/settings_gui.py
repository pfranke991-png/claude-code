"""Kleine Settings-GUI für Provider/Modelle und lokale Speicherung."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from .chat_client import ChatClient
from .config import DEFAULT_CONFIG_PATH, Settings


class SettingsWindow(ttk.Frame):
    def __init__(self, root: tk.Tk) -> None:
        super().__init__(root, padding=14)
        self.root = root
        self.root.title("Voice Mode Settings")
        self.grid(sticky="nsew")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        self.provider = tk.StringVar(value="openai")
        self.api_key = tk.StringVar(value="")
        self.base_url = tk.StringVar(value="")
        self.model = tk.StringVar(value="gpt-4o")
        self.whisper_model = tk.StringVar(value="large-v3")

        self._build()

    def _build(self) -> None:
        ttk.Label(self, text="Provider").grid(row=0, column=0, sticky="w")
        ttk.Combobox(self, textvariable=self.provider, values=["openai", "xai", "lmstudio", "custom"], state="readonly").grid(row=0, column=1, sticky="ew")
        ttk.Label(self, text="API Key").grid(row=1, column=0, sticky="w")
        ttk.Entry(self, textvariable=self.api_key, show="*").grid(row=1, column=1, sticky="ew")
        ttk.Label(self, text="Base URL").grid(row=2, column=0, sticky="w")
        ttk.Entry(self, textvariable=self.base_url).grid(row=2, column=1, sticky="ew")
        ttk.Label(self, text="Model").grid(row=3, column=0, sticky="w")
        ttk.Entry(self, textvariable=self.model).grid(row=3, column=1, sticky="ew")
        ttk.Label(self, text="Whisper").grid(row=4, column=0, sticky="w")
        ttk.Combobox(self, textvariable=self.whisper_model, values=["medium", "large-v3"], state="readonly").grid(row=4, column=1, sticky="ew")

        ttk.Button(self, text="Modelle laden", command=self._load_models).grid(row=5, column=0, pady=10, sticky="ew")
        ttk.Button(self, text="Speichern", command=self._save).grid(row=5, column=1, pady=10, sticky="ew")
        self.columnconfigure(1, weight=1)

    def _load_models(self) -> None:
        try:
            settings = Settings(
                provider=self.provider.get(),
                api_key=self.api_key.get() or None,
                api_base_url=self.base_url.get() or None,
                model=self.model.get(),
                whisper_model=self.whisper_model.get(),
            )
            models = ChatClient(settings).list_models()
        except Exception as exc:
            messagebox.showerror("Fehler", f"Modelle konnten nicht geladen werden: {exc}")
            return
        if not models:
            messagebox.showinfo("Modelle", "Keine Modelle gefunden")
            return
        self.model.set(models[0])
        messagebox.showinfo("Modelle", "Gefundene Modelle:\n" + "\n".join(models[:30]))

    def _save(self) -> None:
        path = Path(DEFAULT_CONFIG_PATH)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "\n".join(
                [
                    f"VOICE_PROVIDER={self.provider.get()}",
                    f"VOICE_API_KEY={self.api_key.get()}",
                    f"VOICE_API_BASE_URL={self.base_url.get()}",
                    f"VOICE_MODEL={self.model.get()}",
                    f"WHISPER_MODEL={self.whisper_model.get()}",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        messagebox.showinfo("Gespeichert", f"Konfiguration gespeichert: {path}")


def main() -> None:
    root = tk.Tk()
    SettingsWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()

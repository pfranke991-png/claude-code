"""Hotkey-Steuerung mit pynput."""

from __future__ import annotations

import threading
from pynput import keyboard


class HotkeyController:
    """Reagiert auf eine Toggle-Kombination und setzt ein Event."""

    def __init__(self, combination: str):
        self.combination = combination
        self._event = threading.Event()
        self._listener = keyboard.GlobalHotKeys({combination: self._on_trigger})

    def _on_trigger(self) -> None:
        self._event.set()

    def start(self) -> None:
        self._listener.start()
        print(f"[info] Hotkey aktiv: {self.combination}")

    def wait_for_trigger(self) -> None:
        self._event.wait()
        self._event.clear()

    def stop(self) -> None:
        self._listener.stop()


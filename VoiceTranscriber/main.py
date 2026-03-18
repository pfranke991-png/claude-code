#!/usr/bin/env python3
"""Voice Transcriber - Live Whisper Transkription mit Post-Processing."""

import sys
import os
import traceback

# Suppress HuggingFace symlink warning on Windows
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"


def main():
    # Step-by-step startup with error reporting at each stage
    print("[1/5] Starte Voice Transcriber...", flush=True)

    try:
        from PyQt6.QtWidgets import QApplication, QMessageBox
        print("[2/5] PyQt6 geladen.", flush=True)
    except Exception as e:
        print(f"FEHLER: PyQt6 konnte nicht geladen werden: {e}", file=sys.stderr)
        traceback.print_exc()
        input("Druecke Enter zum Beenden...")
        return 1

    try:
        from ui.main_window import MainWindow
        print("[3/5] Module geladen.", flush=True)
    except Exception as e:
        print(f"FEHLER beim Import: {e}", file=sys.stderr)
        traceback.print_exc()
        input("Druecke Enter zum Beenden...")
        return 1

    app = QApplication(sys.argv)
    app.setApplicationName("Voice Transcriber")

    # Set exception hook BEFORE creating window
    def handle_exception(exc_type, exc_value, exc_tb):
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        print(f"\nUnbehandelte Ausnahme:\n{error_msg}", file=sys.stderr, flush=True)
        try:
            QMessageBox.critical(None, "Fehler", f"Ein Fehler ist aufgetreten:\n\n{exc_value}")
        except Exception:
            pass

    sys.excepthook = handle_exception

    try:
        print("[4/5] Erstelle Fenster...", flush=True)
        window = MainWindow()
        print("[5/5] Fenster bereit. Zeige GUI.", flush=True)
        window.show()
    except Exception as e:
        print(f"FEHLER beim Erstellen des Fensters: {e}", file=sys.stderr)
        traceback.print_exc()
        try:
            QMessageBox.critical(None, "Startfehler",
                f"Das Fenster konnte nicht erstellt werden:\n\n{e}\n\n"
                f"Details:\n{traceback.format_exc()}")
        except Exception:
            pass
        input("Druecke Enter zum Beenden...")
        return 1

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Voice Transcriber - Live Whisper Transkription mit Post-Processing."""

import sys
import os
import traceback

# Suppress HuggingFace symlink warning on Windows
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"


def main():
    from PyQt6.QtWidgets import QApplication, QMessageBox
    from ui.main_window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("Voice Transcriber")

    # Global exception handler so the app doesn't silently crash
    def handle_exception(exc_type, exc_value, exc_tb):
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        print(f"Unbehandelte Ausnahme:\n{error_msg}", file=sys.stderr)
        try:
            QMessageBox.critical(None, "Fehler", f"Ein Fehler ist aufgetreten:\n\n{exc_value}")
        except Exception:
            pass

    sys.excepthook = handle_exception

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

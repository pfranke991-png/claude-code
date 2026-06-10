#!/bin/bash
echo "============================================"
echo " Voice Transcriber — NanoGPT Edition"
echo " Installation der Abhaengigkeiten"
echo "============================================"
echo ""

# Python pruefen
if ! command -v python3 &> /dev/null; then
    echo "FEHLER: Python3 nicht gefunden!"
    echo "Bitte Python 3.10+ installieren."
    exit 1
fi

echo "Python gefunden: $(python3 --version)"
echo ""

# Pip upgraden
python3 -m pip install --upgrade pip

# Pakete installieren
python3 -m pip install customtkinter openai openai-whisper sounddevice soundfile numpy pyperclip

# PyTorch (CPU)
echo ""
echo "Installiere PyTorch (CPU) ..."
python3 -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

echo ""
echo "============================================"
echo " Installation abgeschlossen!"
echo " Starte die App mit:"
echo "   python3 voice_transcriber.py"
echo "============================================"

@echo off
title Voice Transcriber — Installation
echo ============================================
echo  Voice Transcriber — NanoGPT Edition
echo  Installation der Abhaengigkeiten
echo ============================================
echo.

:: Python-Version pruefen
python --version >nul 2>&1
if errorlevel 1 (
    echo FEHLER: Python nicht gefunden!
    echo Bitte Python 3.10+ von https://python.org installieren.
    pause
    exit /b 1
)

echo Python gefunden. Installiere Pakete...
echo.

:: Pakete installieren
pip install --upgrade pip
pip install customtkinter>=5.2.2
pip install openai>=1.30.0
pip install openai-whisper>=20231117
pip install sounddevice>=0.4.6
pip install soundfile>=0.12.1
pip install numpy>=1.24.0
pip install pyperclip>=1.8.2

:: PyTorch (CPU-Version, leichter)
echo.
echo Installiere PyTorch (CPU)...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

echo.
echo ============================================
echo  Installation abgeschlossen!
echo  Starte die App mit:
echo    python voice_transcriber.py
echo ============================================
pause

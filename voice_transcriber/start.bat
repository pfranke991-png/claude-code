@echo off
cd /d "%~dp0"
python voice_transcriber.py
if errorlevel 1 (
    echo.
    echo Fehler beim Starten. Installiere zuerst mit install_windows.bat
    pause
)

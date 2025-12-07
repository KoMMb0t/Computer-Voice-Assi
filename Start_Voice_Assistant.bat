@echo off
REM ============================================================
REM Computer Voice Assistant - Starter
REM ============================================================

echo.
echo ============================================================
echo    COMPUTER VOICE ASSISTANT - STARTER
echo ============================================================
echo.

REM Wechsle ins Projektverzeichnis
cd /d "%~dp0"

REM Prüfe ob virtuelle Umgebung existiert
if not exist ".venv\Scripts\activate.bat" (
    echo [FEHLER] Virtuelle Umgebung nicht gefunden!
    echo Bitte zuerst einrichten mit: python -m venv .venv
    echo.
    pause
    exit /b 1
)

REM Aktiviere virtuelle Umgebung
echo [INFO] Aktiviere virtuelle Umgebung...
call .venv\Scripts\activate.bat

REM Prüfe ob Python verfügbar ist
python --version >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] Python nicht gefunden!
    echo.
    pause
    exit /b 1
)

REM Starte Voice Assistant
echo [INFO] Starte Voice Assistant...
echo.
python 04_voice_assistant_computer.py

REM Falls Fehler auftreten, Fenster offen lassen
if errorlevel 1 (
    echo.
    echo [FEHLER] Voice Assistant konnte nicht gestartet werden!
    echo.
    pause
)

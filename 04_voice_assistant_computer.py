#!/usr/bin/env python3
"""
Voice Assistant v3.0 - "Computer" Wake-Word Edition
Trainiertes Custom Wake-Word: "Computer" via Porcupine
Modell-Pfad: ./models/computer.ppn

Datum: 05. Dezember 2025
Projekt: Computer Voice Assistant
GitHub: https://github.com/KoMMb0t/voice_assi
"""

import time
import json
import subprocess
import webbrowser
import sounddevice as sd
import numpy as np
import edge_tts
import asyncio
import os
import pygame
import webrtcvad
from dotenv import load_dotenv

# CHANGED FOR COMPUTER WAKE-WORD: Porcupine statt OpenWakeWord
import pvporcupine

# Vosk für Speech-to-Text
from vosk import Model as VoskModel, KaldiRecognizer

# ============================================================
# KONFIGURATION
# ============================================================

# Lade Environment Variables
load_dotenv()

# Wake-Word Konfiguration - CHANGED FOR COMPUTER WAKE-WORD
WAKE_WORD = "computer"  # GEÄNDERT von "hey jarvis"
PICOVOICE_ACCESS_KEY = os.getenv('PICOVOICE_ACCESS_KEY')  # NEU
PORCUPINE_MODEL_PATH = "models/computer.ppn"  # NEU
PORCUPINE_SENSITIVITY = 0.5  # NEU: 0.0-1.0 (höher = empfindlicher)

# Audio Konfiguration
# SAMPLE_RATE und CHUNK_SAMPLES werden von Porcupine bestimmt
SILENCE_TIMEOUT = 2.0
MAX_RECORD_TIME = 30

# TTS Konfiguration
TTS_VOICE = "de-DE-KatjaNeural"

# Cooldown-Konfiguration - CHANGED FOR COMPUTER WAKE-WORD
COOLDOWN_SECONDS = 2.0  # Verhindert Doppel-Erkennungen

# ============================================================
# GLOBALE VARIABLEN
# ============================================================

# Initialisiere pygame mixer für TTS
pygame.mixer.init()

# Letzte Wake-Word-Erkennung (für Cooldown)
last_wake_detection_time = 0

# ============================================================
# TEXT-TO-SPEECH
# ============================================================

async def speak_async(text):
    """Spricht Text mit Edge TTS."""
    print(f"💬 [SPEAK] {text}")
    communicate = edge_tts.Communicate(text, TTS_VOICE)
    temp_file = "temp_speech.mp3"
    await communicate.save(temp_file)
    
    # Spiele mit pygame ab
    pygame.mixer.music.load(temp_file)
    pygame.mixer.music.play()
    
    # Warte bis Audio fertig ist
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    
    # WICHTIG: Entlade die Datei aus pygame
    pygame.mixer.music.unload()
    
    # Lösche temporäre Datei
    try:
        time.sleep(0.3)
        os.remove(temp_file)
    except Exception as e:
        # Falls Löschen fehlschlägt, ignorieren
        pass


def speak(text):
    """Synchrone Wrapper-Funktion für speak_async."""
    asyncio.run(speak_async(text))


# ============================================================
# BEFEHLSAUSFÜHRUNG
# ============================================================

def execute_command(command_text):
    """Führt einen Befehl aus."""
    command_lower = command_text.lower()
    
    print(f"\n⚙️  [ACTION] Verarbeite: '{command_text}'")
    
    # Programme öffnen
    if "taschenrechner" in command_lower or "rechner" in command_lower:
        speak("Öffne den Taschenrechner")
        subprocess.Popen("calc.exe")
    
    elif "editor" in command_lower or "notepad" in command_lower:
        speak("Öffne Notepad")
        subprocess.Popen("notepad.exe")
    
    elif "explorer" in command_lower or "dateien" in command_lower:
        speak("Öffne den Explorer")
        subprocess.Popen("explorer.exe")
    
    elif "firefox" in command_lower:
        speak("Öffne Firefox")
        try:
            subprocess.Popen(r"C:\Program Files\Mozilla Firefox\firefox.exe")
        except:
            speak("Firefox nicht gefunden")
    
    # Webseiten öffnen
    elif "youtube" in command_lower:
        speak("Öffne YouTube")
        webbrowser.open("https://www.youtube.com")
    
    elif "chatgpt" in command_lower or "chat gpt" in command_lower:
        speak("Öffne ChatGPT")
        webbrowser.open("https://chat.openai.com")
    
    elif "google" in command_lower:
        speak("Öffne Google")
        webbrowser.open("https://www.google.com")
    
    elif "gmail" in command_lower or "e-mail" in command_lower or "email" in command_lower:
        speak("Öffne Gmail")
        webbrowser.open("https://mail.google.com")
    
    elif "github" in command_lower:
        speak("Öffne GitHub")
        webbrowser.open("https://github.com")
    
    elif "wikipedia" in command_lower:
        speak("Öffne Wikipedia")
        webbrowser.open("https://de.wikipedia.org")
    
    elif "browser" in command_lower or "internet" in command_lower:
        speak("Öffne den Browser")
        webbrowser.open("https://www.google.com")
    
    # Datum & Uhrzeit
    elif "uhrzeit" in command_lower or "spät" in command_lower or "wie viel uhr" in command_lower:
        from datetime import datetime
        now = datetime.now()
        time_str = now.strftime("%H:%M")
        speak(f"Es ist {time_str} Uhr")
    
    elif "datum" in command_lower or "welcher tag" in command_lower:
        from datetime import datetime
        now = datetime.now()
        
        # Deutsche Wochentage
        weekdays_de = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", 
                       "Freitag", "Samstag", "Sonntag"]
        weekday = weekdays_de[now.weekday()]
        
        # Deutsche Monate
        months_de = ["Januar", "Februar", "März", "April", "Mai", "Juni",
                     "Juli", "August", "September", "Oktober", "November", "Dezember"]
        month = months_de[now.month - 1]
        
        date_str = f"{weekday}, der {now.day}. {month} {now.year}"
        speak(f"Heute ist {date_str}")
    
    # Höflichkeits-Befehle
    elif "danke" in command_lower or "dankeschön" in command_lower:
        speak("Gern geschehen!")
    
    elif "hallo" in command_lower or "guten morgen" in command_lower or "guten tag" in command_lower:
        speak("Hallo! Wie kann ich helfen?")
    
    elif "abbrechen" in command_lower or "stopp" in command_lower or "nichts" in command_lower:
        speak("Okay")
    
    # Hilfe
    elif "hilfe" in command_lower or "was kannst du" in command_lower:
        speak("Ich kann Programme öffnen, Webseiten öffnen, Datum und Uhrzeit sagen. "
              "Sage zum Beispiel: Öffne YouTube, oder: Wie spät ist es?")
    
    # Nicht erkannt
    else:
        speak("Befehl nicht erkannt")


# ============================================================
# WAKE-WORD DETECTION (PORCUPINE)
# ============================================================

def initialize_porcupine():
    """Initialisiert Porcupine Wake-Word Detector."""
    try:
        porcupine = pvporcupine.create(
            access_key=PICOVOICE_ACCESS_KEY,
            keyword_paths=[PORCUPINE_MODEL_PATH],
            sensitivities=[PORCUPINE_SENSITIVITY]
        )
        print(f"✅ Porcupine initialisiert")
        print(f"   Version: {porcupine.version}")
        print(f"   Sample Rate: {porcupine.sample_rate} Hz")
        print(f"   Frame Length: {porcupine.frame_length}")
        print(f"   Sensitivity: {PORCUPINE_SENSITIVITY}")
        return porcupine
    except Exception as e:
        print(f"❌ Fehler beim Initialisieren von Porcupine: {e}")
        print(f"   Überprüfe:")
        print(f"   1. .env Datei mit PICOVOICE_ACCESS_KEY vorhanden")
        print(f"   2. {PORCUPINE_MODEL_PATH} existiert")
        return None


def listen_for_wake_word(porcupine):
    """Hört auf das Wake Word mit Porcupine."""
    global last_wake_detection_time
    
    print(f"\n🎤 [LISTEN] Warte auf Wake-Word '{WAKE_WORD.upper()}'...")
    
    detected = False
    
    def callback(indata, frames, time_info, status):
        nonlocal detected
        global last_wake_detection_time
        
        if status:
            print(f"⚠️  Audio Status: {status}")
        
        # Konvertiere zu int16 für Porcupine
        audio_frame = (indata[:, 0] * 32767).astype(np.int16)
        
        # Wake-Word Detection
        keyword_index = porcupine.process(audio_frame)
        
        if keyword_index >= 0:
            # Cooldown-Check - CHANGED FOR COMPUTER WAKE-WORD
            current_time = time.time()
            if current_time - last_wake_detection_time > COOLDOWN_SECONDS:
                detected = True
                last_wake_detection_time = current_time
                print(f"\n🚀 '{WAKE_WORD.upper()}' erkannt!")
            else:
                # Ignoriere (zu kurz nach letzter Erkennung)
                print("⏸️  (Cooldown aktiv, ignoriere)", end='\r')
    
    with sd.InputStream(
        channels=1,
        samplerate=porcupine.sample_rate,
        blocksize=porcupine.frame_length,
        dtype=np.float32,
        callback=callback
    ):
        while not detected:
            time.sleep(0.1)
    
    return True


# ============================================================
# SPEECH-TO-TEXT (VOSK)
# ============================================================

def initialize_vosk():
    """Initialisiert Vosk Speech-to-Text Modell."""
    try:
        print("Lade Speech-to-Text-Modell (Vosk)...")
        vosk_model = VoskModel(lang="de")
        print("✅ Vosk initialisiert")
        return vosk_model
    except Exception as e:
        print(f"❌ Fehler beim Initialisieren von Vosk: {e}")
        print(f"   Führe 'python download_models.py' aus")
        return None


def record_command_with_vad(vosk_model, sample_rate):
    """Nimmt Audio auf bis Stille erkannt wird (mit VAD)."""
    print(f"🎤 [RECORD] Höre zu (spreche jetzt)...")
    
    recognizer = KaldiRecognizer(vosk_model, sample_rate)
    recognizer.SetWords(True)
    
    # VAD für Stille-Erkennung
    vad = webrtcvad.Vad(3)  # Aggressivität 3 (höchste)
    
    audio_buffer = []
    last_speech_time = time.time()
    recording_started = False
    start_time = time.time()
    
    def callback(indata, frames, time_info, status):
        nonlocal last_speech_time, recording_started
        
        # Konvertiere zu int16
        audio_frame = (indata[:, 0] * 32767).astype(np.int16)
        audio_bytes = bytes(audio_frame)
        audio_buffer.append(audio_bytes)
        
        # VAD-Check (10ms Frames für VAD)
        frame_duration_ms = 30  # 30ms Frames
        
        try:
            is_speech = vad.is_speech(audio_bytes, sample_rate)
            if is_speech:
                last_speech_time = time.time()
                recording_started = True
                print(".", end="", flush=True)
        except:
            pass
        
        # Vosk STT
        if recognizer.AcceptWaveform(audio_bytes):
            result = json.loads(recognizer.Result())
            if result.get("text", ""):
                last_speech_time = time.time()
                recording_started = True
    
    with sd.InputStream(
        samplerate=sample_rate,
        channels=1,
        dtype=np.float32,
        blocksize=int(sample_rate * 0.03),  # 30ms blocks
        callback=callback
    ):
        while True:
            current_time = time.time()
            
            # Stille erkannt
            if recording_started and (current_time - last_speech_time) > SILENCE_TIMEOUT:
                print("\n✅ [RECORD] Stille erkannt - Aufnahme beendet")
                break
            
            # Max Zeit erreicht
            if (current_time - start_time) > MAX_RECORD_TIME:
                print("\n⏱️  [RECORD] Maximale Aufnahmezeit erreicht")
                break
            
            time.sleep(0.1)
    
    return b''.join(audio_buffer)


# ============================================================
# MAIN LOOP
# ============================================================

def main():
    """Hauptfunktion."""
    print("=" * 60)
    print("🤖 VOICE ASSISTANT v3.0 - COMPUTER WAKE-WORD")
    print("=" * 60)
    print()
    
    # Initialisiere Komponenten
    speak("Initialisiere System")
    
    porcupine = initialize_porcupine()
    if not porcupine:
        print("\n❌ Konnte Porcupine nicht initialisieren. Beende.")
        return
    
    vosk_model = initialize_vosk()
    if not vosk_model:
        print("\n❌ Konnte Vosk nicht initialisieren. Beende.")
        porcupine.delete()
        return
    
    print("\n" + "=" * 60)
    print("✅ SYSTEM BEREIT!")
    print("=" * 60)
    speak("System bereit")
    
    try:
        while True:
            # Warte auf Wake-Word
            if listen_for_wake_word(porcupine):
                
                # Bestätigung
                speak("Ja?")
                
                # Aufnahme mit VAD
                audio_data = record_command_with_vad(vosk_model, porcupine.sample_rate)
                
                # Speech-to-Text
                print("🔄 [STT] Verarbeite Sprache...")
                recognizer = KaldiRecognizer(vosk_model, porcupine.sample_rate)
                
                if recognizer.AcceptWaveform(audio_data):
                    result = json.loads(recognizer.Result())
                else:
                    result = json.loads(recognizer.FinalResult())
                
                command = result.get("text", "")
                
                if command:
                    print(f"📝 [STT] Erkannt: \"{command}\"")
                    execute_command(command)
                else:
                    print("❌ [STT] Nichts verstanden")
                    speak("Befehl nicht verstanden")
                
                # Cooldown
                print(f"\n⏸️  Cooldown ({COOLDOWN_SECONDS}s)...")
                time.sleep(COOLDOWN_SECONDS)
                print("✅ Bereit für nächsten Befehl")
    
    except KeyboardInterrupt:
        print("\n\n👋 Beende Voice Assistant...")
        speak("Auf Wiedersehen")
    
    finally:
        # Cleanup
        porcupine.delete()
        pygame.mixer.quit()
        print("\n✅ Porcupine beendet")
        print("=" * 60)
        print("🤖 VOICE ASSISTANT BEENDET")
        print("=" * 60)


if __name__ == "__main__":
    main()

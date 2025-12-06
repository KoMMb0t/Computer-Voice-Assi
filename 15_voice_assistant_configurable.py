#!/usr/bin/env python3
"""
Voice Assistant v4.0 - Configurable Edition
Alle Hard-coded Werte in config.ini ausgelagert

Datum: 06. Dezember 2025
Projekt: Computer Voice Assistant
GitHub: https://github.com/KoMMb0t/Computer-Voice-Assi
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
import configparser
import sys

# Porcupine für Wake-Word
import pvporcupine

# Vosk für Speech-to-Text
from vosk import Model as VoskModel, KaldiRecognizer

# ============================================================
# CONFIGURATION LOADER
# ============================================================

class Config:
    """Lädt und verwaltet Konfiguration aus config.ini."""
    
    def __init__(self, config_file="config.ini"):
        self.config = configparser.ConfigParser()
        
        # Prüfe ob config.ini existiert
        if not os.path.exists(config_file):
            print(f"❌ Fehler: {config_file} nicht gefunden!")
            print(f"💡 Erstelle Standard-Konfiguration...")
            self.create_default_config(config_file)
        
        # Lade Konfiguration
        self.config.read(config_file, encoding='utf-8')
        print(f"✅ Konfiguration geladen: {config_file}")
    
    def create_default_config(self, config_file):
        """Erstellt Standard-Konfigurationsdatei."""
        config = configparser.ConfigParser()
        
        # [WakeWord] Section
        config['WakeWord'] = {
            'wake_word': 'computer',
            'picovoice_access_key': 'YOUR_PICOVOICE_ACCESS_KEY_HERE',
            'porcupine_model_path': 'models/computer.ppn',
            'sensitivity': '0.5',
            'cooldown_seconds': '2.0'
        }
        
        # [Audio] Section
        config['Audio'] = {
            'silence_timeout': '2.0',
            'max_record_time': '30',
            'vad_aggressiveness': '3'
        }
        
        # [TTS] Section
        config['TTS'] = {
            'voice': 'de-DE-KatjaNeural',
            'rate': '+0%',
            'volume': '+0%'
        }
        
        # [STT] Section
        config['STT'] = {
            'model_path': 'models/vosk-model-small-de-0.15',
            'language': 'de'
        }
        
        # [Commands] Section
        config['Commands'] = {
            'enable_web_commands': 'true',
            'enable_app_commands': 'true',
            'enable_system_commands': 'true'
        }
        
        # [Advanced] Section
        config['Advanced'] = {
            'debug_mode': 'false',
            'log_file': 'voice_assistant.log',
            'save_recordings': 'false',
            'recordings_dir': 'recordings'
        }
        
        # Speichere
        with open(config_file, 'w', encoding='utf-8') as f:
            config.write(f)
        
        print(f"✅ Standard-Konfiguration erstellt: {config_file}")
        print(f"⚠️  WICHTIG: Bitte trage deinen Picovoice Access Key in {config_file} ein!")
    
    # Getter-Methoden
    def get(self, section, key, fallback=None):
        """Generischer Getter."""
        return self.config.get(section, key, fallback=fallback)
    
    def getint(self, section, key, fallback=None):
        """Getter für Integer."""
        return self.config.getint(section, key, fallback=fallback)
    
    def getfloat(self, section, key, fallback=None):
        """Getter für Float."""
        return self.config.getfloat(section, key, fallback=fallback)
    
    def getboolean(self, section, key, fallback=None):
        """Getter für Boolean."""
        return self.config.getboolean(section, key, fallback=fallback)


# ============================================================
# GLOBALE VARIABLEN
# ============================================================

# Lade Konfiguration
cfg = Config()

# Initialisiere pygame mixer für TTS
pygame.mixer.init()

# Letzte Wake-Word-Erkennung (für Cooldown)
last_wake_detection_time = 0

# ============================================================
# TEXT-TO-SPEECH
# ============================================================

async def speak_async(text):
    """Spricht Text mit Edge TTS."""
    if cfg.getboolean('Advanced', 'debug_mode', fallback=False):
        print(f"💬 [SPEAK] {text}")
    
    voice = cfg.get('TTS', 'voice', fallback='de-DE-KatjaNeural')
    
    communicate = edge_tts.Communicate(text, voice)
    temp_file = "temp_speech.mp3"
    await communicate.save(temp_file)
    
    # Spiele mit pygame ab
    pygame.mixer.music.load(temp_file)
    pygame.mixer.music.play()
    
    # Warte bis Audio fertig ist
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    
    # Entlade die Datei
    pygame.mixer.music.unload()
    
    # Lösche temporäre Datei
    try:
        time.sleep(0.3)
        os.remove(temp_file)
    except:
        pass


def speak(text):
    """Synchrone Wrapper-Funktion für speak_async."""
    asyncio.run(speak_async(text))


# ============================================================
# WAKE-WORD DETECTION (PORCUPINE)
# ============================================================

def initialize_porcupine():
    """Initialisiert Porcupine Wake-Word Detection."""
    access_key = cfg.get('WakeWord', 'picovoice_access_key')
    model_path = cfg.get('WakeWord', 'porcupine_model_path')
    sensitivity = cfg.getfloat('WakeWord', 'sensitivity', fallback=0.5)
    
    if not access_key or access_key == "YOUR_PICOVOICE_ACCESS_KEY_HERE":
        print("❌ Fehler: Picovoice Access Key nicht konfiguriert!")
        print("💡 Bitte trage deinen Key in config.ini ein.")
        sys.exit(1)
    
    if not os.path.exists(model_path):
        print(f"❌ Fehler: Porcupine-Modell nicht gefunden: {model_path}")
        print(f"💡 Bitte trainiere das Wake-Word und speichere es unter {model_path}")
        sys.exit(1)
    
    try:
        porcupine = pvporcupine.create(
            access_key=access_key,
            keyword_paths=[model_path],
            sensitivities=[sensitivity]
        )
        print(f"✅ Porcupine initialisiert (Sensitivity: {sensitivity})")
        return porcupine
    except Exception as e:
        print(f"❌ Fehler beim Initialisieren von Porcupine: {e}")
        sys.exit(1)


# ============================================================
# SPEECH-TO-TEXT (VOSK)
# ============================================================

def initialize_vosk():
    """Initialisiert Vosk Speech-to-Text."""
    model_path = cfg.get('STT', 'model_path')
    
    if not os.path.exists(model_path):
        print(f"❌ Fehler: Vosk-Modell nicht gefunden: {model_path}")
        print(f"💡 Bitte lade das Modell herunter und speichere es unter {model_path}")
        sys.exit(1)
    
    try:
        model = VoskModel(model_path)
        print(f"✅ Vosk initialisiert")
        return model
    except Exception as e:
        print(f"❌ Fehler beim Initialisieren von Vosk: {e}")
        sys.exit(1)


# ============================================================
# VOICE ACTIVITY DETECTION (VAD)
# ============================================================

def initialize_vad():
    """Initialisiert WebRTC VAD."""
    aggressiveness = cfg.getint('Audio', 'vad_aggressiveness', fallback=3)
    vad = webrtcvad.Vad(aggressiveness)
    print(f"✅ VAD initialisiert (Aggressiveness: {aggressiveness})")
    return vad


# ============================================================
# COMMAND EXECUTION
# ============================================================

def execute_command(command_text):
    """Führt Befehle basierend auf erkanntem Text aus."""
    text = command_text.lower().strip()
    
    debug = cfg.getboolean('Advanced', 'debug_mode', fallback=False)
    
    if debug:
        print(f"🔍 [COMMAND] Verarbeite: '{text}'")
    
    # Höflichkeits-Befehle
    if text in ["danke", "dankeschön", "vielen dank"]:
        speak("Gern geschehen!")
        return True
    
    if text in ["hallo", "hi", "hey"]:
        speak("Hallo! Wie kann ich helfen?")
        return True
    
    if text in ["abbrechen", "stopp", "stop"]:
        speak("Okay, abgebrochen.")
        return True
    
    # Web-Befehle
    if cfg.getboolean('Commands', 'enable_web_commands', fallback=True):
        if "youtube" in text:
            speak("Öffne YouTube")
            webbrowser.open("https://www.youtube.com")
            return True
        
        if "chatgpt" in text or "chat gpt" in text:
            speak("Öffne ChatGPT")
            webbrowser.open("https://chat.openai.com")
            return True
        
        if "google" in text:
            speak("Öffne Google")
            webbrowser.open("https://www.google.com")
            return True
        
        if "gmail" in text or "e-mail" in text or "email" in text:
            speak("Öffne Gmail")
            webbrowser.open("https://mail.google.com")
            return True
        
        if "github" in text:
            speak("Öffne GitHub")
            webbrowser.open("https://github.com")
            return True
        
        if "wikipedia" in text:
            speak("Öffne Wikipedia")
            webbrowser.open("https://de.wikipedia.org")
            return True
    
    # App-Befehle (Windows)
    if cfg.getboolean('Commands', 'enable_app_commands', fallback=True):
        if "rechner" in text or "taschenrechner" in text or "calculator" in text:
            speak("Öffne Taschenrechner")
            subprocess.Popen("calc.exe")
            return True
        
        if "editor" in text or "notepad" in text:
            speak("Öffne Editor")
            subprocess.Popen("notepad.exe")
            return True
        
        if "explorer" in text or "datei explorer" in text:
            speak("Öffne Explorer")
            subprocess.Popen("explorer.exe")
            return True
        
        if "firefox" in text:
            speak("Öffne Firefox")
            subprocess.Popen("firefox.exe")
            return True
    
    # System-Befehle
    if cfg.getboolean('Commands', 'enable_system_commands', fallback=True):
        if "datum" in text or "welcher tag" in text:
            from datetime import datetime
            now = datetime.now()
            weekdays = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", 
                       "Freitag", "Samstag", "Sonntag"]
            months = ["Januar", "Februar", "März", "April", "Mai", "Juni",
                     "Juli", "August", "September", "Oktober", "November", "Dezember"]
            
            weekday = weekdays[now.weekday()]
            day = now.day
            month = months[now.month - 1]
            year = now.year
            
            speak(f"Heute ist {weekday}, der {day}. {month} {year}")
            return True
        
        if "uhrzeit" in text or "wie spät" in text:
            from datetime import datetime
            now = datetime.now()
            hour = now.hour
            minute = now.minute
            speak(f"Es ist {hour} Uhr {minute}")
            return True
        
        if "hilfe" in text or "help" in text or "was kannst du" in text:
            speak("Ich kann Webseiten öffnen, Programme starten, die Uhrzeit sagen und vieles mehr. Probiere es einfach aus!")
            return True
    
    # Unbekannter Befehl
    speak("Entschuldigung, das habe ich nicht verstanden.")
    return False


# ============================================================
# MAIN LOOP
# ============================================================

def main():
    """Hauptschleife des Voice Assistants."""
    global last_wake_detection_time
    
    print("=" * 60)
    print("🎤 VOICE ASSISTANT v4.0 - CONFIGURABLE EDITION")
    print("=" * 60)
    
    # Initialisiere Komponenten
    porcupine = initialize_porcupine()
    vosk_model = initialize_vosk()
    vad = initialize_vad()
    
    # Audio-Parameter von Porcupine
    sample_rate = porcupine.sample_rate
    frame_length = porcupine.frame_length
    
    # Konfiguration
    wake_word = cfg.get('WakeWord', 'wake_word', fallback='computer')
    cooldown = cfg.getfloat('WakeWord', 'cooldown_seconds', fallback=2.0)
    silence_timeout = cfg.getfloat('Audio', 'silence_timeout', fallback=2.0)
    max_record_time = cfg.getfloat('Audio', 'max_record_time', fallback=30)
    debug = cfg.getboolean('Advanced', 'debug_mode', fallback=False)
    
    print(f"Wake-Word: '{wake_word}'")
    print(f"Sample Rate: {sample_rate} Hz")
    print(f"Frame Length: {frame_length}")
    print(f"Cooldown: {cooldown}s")
    print(f"Debug Mode: {debug}")
    print("=" * 60)
    print(f"🎧 Warte auf Wake-Word: '{wake_word}'...")
    print("=" * 60)
    
    try:
        with sd.InputStream(samplerate=sample_rate, 
                           channels=1, 
                           blocksize=frame_length,
                           dtype='int16') as stream:
            
            while True:
                # Lese Audio-Frame
                audio_frame, _ = stream.read(frame_length)
                audio_frame = audio_frame.flatten()
                
                # Wake-Word Detection
                keyword_index = porcupine.process(audio_frame)
                
                if keyword_index >= 0:
                    # Cooldown-Check
                    current_time = time.time()
                    if current_time - last_wake_detection_time < cooldown:
                        if debug:
                            print(f"⏸️  Cooldown aktiv ({current_time - last_wake_detection_time:.1f}s)")
                        continue
                    
                    last_wake_detection_time = current_time
                    
                    print(f"\n✅ Wake-Word erkannt: '{wake_word}'")
                    speak("Ja?")
                    
                    # Speech-to-Text
                    print("🎤 Höre zu...")
                    
                    recognizer = KaldiRecognizer(vosk_model, sample_rate)
                    recognizer.SetWords(True)
                    
                    frames = []
                    silence_frames = 0
                    max_silence_frames = int(silence_timeout * sample_rate / frame_length)
                    max_frames = int(max_record_time * sample_rate / frame_length)
                    
                    recording_started = False
                    
                    for _ in range(max_frames):
                        audio_frame, _ = stream.read(frame_length)
                        audio_frame = audio_frame.flatten()
                        
                        # VAD
                        is_speech = vad.is_speech(audio_frame.tobytes(), sample_rate)
                        
                        if is_speech:
                            recording_started = True
                            silence_frames = 0
                            frames.append(audio_frame)
                        elif recording_started:
                            silence_frames += 1
                            frames.append(audio_frame)
                            
                            if silence_frames >= max_silence_frames:
                                if debug:
                                    print(f"🔇 Stille erkannt ({silence_timeout}s)")
                                break
                    
                    if not frames:
                        print("❌ Keine Sprache erkannt")
                        continue
                    
                    # STT
                    audio_data = np.concatenate(frames)
                    recognizer.AcceptWaveform(audio_data.tobytes())
                    result = json.loads(recognizer.FinalResult())
                    
                    text = result.get("text", "").strip()
                    
                    if text:
                        print(f"📝 Erkannt: '{text}'")
                        execute_command(text)
                    else:
                        print("❌ Nichts verstanden")
                        speak("Entschuldigung, ich habe nichts verstanden.")
                    
                    print(f"\n🎧 Warte auf Wake-Word: '{wake_word}'...")
    
    except KeyboardInterrupt:
        print("\n\n👋 Voice Assistant beendet")
    
    finally:
        porcupine.delete()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()

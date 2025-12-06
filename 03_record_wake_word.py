#!/usr/bin/env python3
"""
Voice Assistant - Wake-Word Recording Script
Automatisierte Aufnahme von Wake-Word Samples für Training

Datum: 05. Dezember 2025
Projekt: Computer Voice Assistant
"""

import sounddevice as sd
import numpy as np
import wave
import time
import os
import sys
from datetime import datetime
from pathlib import Path
import argparse

# ============================================================
# KONFIGURATION
# ============================================================

SAMPLE_RATE = 16000  # Hz (Standard für Wake-Word Training)
DURATION = 2.0  # Sekunden pro Aufnahme
CHANNELS = 1  # Mono
DTYPE = np.int16

# Output-Verzeichnisse
BASE_DIR = Path("wake_word_recordings")
POSITIVE_DIR = BASE_DIR / "positive"
NEGATIVE_DIR = BASE_DIR / "negative"
BACKGROUND_DIR = BASE_DIR / "background"

# Aufnahme-Modi und Ziele
RECORDING_MODES = {
    "normal": {
        "name": "Normal",
        "count": 100,
        "instruction": "Sprich 'Computer' in normaler Lautstärke und Geschwindigkeit"
    },
    "loud": {
        "name": "Laut",
        "count": 30,
        "instruction": "Sprich 'Computer' LAUT"
    },
    "quiet": {
        "name": "Leise",
        "count": 30,
        "instruction": "Sprich 'Computer' leise (fast geflüstert)"
    },
    "fast": {
        "name": "Schnell",
        "count": 20,
        "instruction": "Sprich 'Computer' schnell"
    },
    "slow": {
        "name": "Langsam",
        "count": 20,
        "instruction": "Sprich 'Computer' langsam und deutlich"
    }
}

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def create_directories():
    """Erstellt notwendige Verzeichnisse."""
    POSITIVE_DIR.mkdir(parents=True, exist_ok=True)
    NEGATIVE_DIR.mkdir(parents=True, exist_ok=True)
    BACKGROUND_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✅ Verzeichnisse erstellt: {BASE_DIR}")


def get_next_filename(directory, prefix, extension=".wav"):
    """Ermittelt den nächsten verfügbaren Dateinamen."""
    existing_files = list(directory.glob(f"{prefix}_*.wav"))
    if not existing_files:
        return directory / f"{prefix}_001{extension}"
    
    # Finde höchste Nummer
    numbers = []
    for f in existing_files:
        try:
            num = int(f.stem.split('_')[-1])
            numbers.append(num)
        except ValueError:
            continue
    
    next_num = max(numbers) + 1 if numbers else 1
    return directory / f"{prefix}_{next_num:03d}{extension}"


def save_wav(filename, audio_data, sample_rate=SAMPLE_RATE):
    """Speichert Audio-Daten als WAV-Datei."""
    with wave.open(str(filename), 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)  # 16-bit = 2 bytes
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data.tobytes())


def check_audio_quality(audio_data):
    """Überprüft die Qualität der Aufnahme."""
    max_amplitude = np.max(np.abs(audio_data))
    mean_amplitude = np.mean(np.abs(audio_data))
    
    # Qualitäts-Checks
    if max_amplitude < 1000:
        return "too_quiet", "⚠️  ZU LEISE! Bitte lauter sprechen."
    elif max_amplitude > 30000:
        return "too_loud", "⚠️  ZU LAUT! Mikrofon übersteuert."
    elif mean_amplitude < 100:
        return "too_short", "⚠️  ZU KURZ oder zu leise! Bitte deutlich 'Computer' sagen."
    else:
        return "good", "✅ Gute Qualität"


def countdown(seconds=3):
    """Countdown vor Aufnahme."""
    for i in range(seconds, 0, -1):
        print(f"   {i}...", end='\r')
        time.sleep(1)
    print("   🎤 JETZT!", end='\r')


def display_progress(current, total, mode_name):
    """Zeigt Fortschrittsbalken an."""
    percentage = (current / total) * 100
    bar_length = 40
    filled = int(bar_length * current / total)
    bar = '█' * filled + '░' * (bar_length - filled)
    print(f"\n[{bar}] {current}/{total} ({percentage:.1f}%) - {mode_name}")


# ============================================================
# RECORDING FUNCTIONS
# ============================================================

def record_sample(instruction, countdown_enabled=True):
    """Nimmt ein einzelnes Sample auf."""
    if countdown_enabled:
        print(f"\n📝 {instruction}")
        countdown()
    
    # Aufnahme
    recording = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype=DTYPE
    )
    sd.wait()
    
    return recording.flatten()


def record_positive_samples():
    """Nimmt positive Samples (Wake-Word) auf."""
    print("\n" + "="*60)
    print("🎤 POSITIVE SAMPLES - 'Computer' Wake-Word")
    print("="*60)
    
    total_count = sum(mode["count"] for mode in RECORDING_MODES.values())
    current_count = 0
    
    for mode_key, mode_config in RECORDING_MODES.items():
        print(f"\n{'='*60}")
        print(f"Modus: {mode_config['name']}")
        print(f"Ziel: {mode_config['count']} Aufnahmen")
        print(f"{'='*60}")
        
        for i in range(mode_config['count']):
            # Fortschritt anzeigen
            display_progress(current_count, total_count, mode_config['name'])
            
            # Aufnahme
            audio_data = record_sample(mode_config['instruction'])
            
            # Qualitäts-Check
            quality, message = check_audio_quality(audio_data)
            print(f"   {message}")
            
            if quality == "good":
                # Speichern
                filename = get_next_filename(POSITIVE_DIR, f"computer_{mode_key}")
                save_wav(filename, audio_data)
                print(f"   💾 Gespeichert: {filename.name}")
                current_count += 1
            else:
                # Wiederholen
                print("   🔄 Bitte wiederholen...")
                i -= 1  # Zähler nicht erhöhen
                time.sleep(1)
                continue
            
            # Kurze Pause zwischen Aufnahmen
            time.sleep(0.5)
        
        # Pause zwischen Modi
        if mode_key != list(RECORDING_MODES.keys())[-1]:
            print(f"\n✅ {mode_config['name']}-Modus abgeschlossen!")
            print("⏸️  Pause 5 Sekunden...")
            time.sleep(5)
    
    print(f"\n{'='*60}")
    print(f"✅ ALLE POSITIVEN SAMPLES AUFGENOMMEN!")
    print(f"   Gesamt: {current_count} Aufnahmen")
    print(f"{'='*60}")


def record_negative_samples():
    """Nimmt negative Samples (andere Wörter) auf."""
    print("\n" + "="*60)
    print("🎤 NEGATIVE SAMPLES - Andere Wörter")
    print("="*60)
    
    negative_words = [
        "Hallo", "Computer", "Jarvis", "Alexa", "Google",
        "Komputer", "Commuter", "Puter", "Rechner", "PC",
        "Laptop", "Tastatur", "Maus", "Monitor", "Drucker",
        "Internet", "Browser", "Programm", "Software", "Hardware"
    ]
    
    samples_per_word = 10
    total_count = len(negative_words) * samples_per_word
    current_count = 0
    
    print(f"Ziel: {total_count} negative Samples")
    print(f"Wörter: {len(negative_words)}")
    print(f"Pro Wort: {samples_per_word} Aufnahmen\n")
    
    for word in negative_words:
        print(f"\n--- Wort: '{word}' ---")
        
        for i in range(samples_per_word):
            display_progress(current_count, total_count, f"Negativ: {word}")
            
            instruction = f"Sprich: '{word}'"
            audio_data = record_sample(instruction, countdown_enabled=(i == 0))
            
            # Speichern (ohne Qualitäts-Check für negative Samples)
            filename = get_next_filename(NEGATIVE_DIR, f"negative_{word.lower()}")
            save_wav(filename, audio_data)
            print(f"   💾 Gespeichert: {filename.name}")
            
            current_count += 1
            time.sleep(0.3)
    
    print(f"\n{'='*60}")
    print(f"✅ ALLE NEGATIVEN SAMPLES AUFGENOMMEN!")
    print(f"   Gesamt: {current_count} Aufnahmen")
    print(f"{'='*60}")


def record_background_noise():
    """Nimmt Hintergrundgeräusche auf."""
    print("\n" + "="*60)
    print("🎤 BACKGROUND NOISE - Hintergrundgeräusche")
    print("="*60)
    
    noise_types = [
        ("silence", "Stille (kein Sprechen)", 20),
        ("typing", "Tippen auf Tastatur", 10),
        ("music", "Musik im Hintergrund", 10),
        ("conversation", "Gespräche im Hintergrund", 10),
        ("tv", "TV/Radio im Hintergrund", 10)
    ]
    
    total_count = sum(count for _, _, count in noise_types)
    current_count = 0
    
    print(f"Ziel: {total_count} Background Samples\n")
    
    for noise_key, description, count in noise_types:
        print(f"\n--- {description} ---")
        
        for i in range(count):
            display_progress(current_count, total_count, description)
            
            instruction = f"{description} - NICHT sprechen!"
            audio_data = record_sample(instruction, countdown_enabled=(i == 0))
            
            filename = get_next_filename(BACKGROUND_DIR, f"bg_{noise_key}")
            save_wav(filename, audio_data)
            print(f"   💾 Gespeichert: {filename.name}")
            
            current_count += 1
            time.sleep(0.3)
    
    print(f"\n{'='*60}")
    print(f"✅ ALLE BACKGROUND SAMPLES AUFGENOMMEN!")
    print(f"   Gesamt: {current_count} Aufnahmen")
    print(f"{'='*60}")


# ============================================================
# MENU SYSTEM
# ============================================================

def display_menu():
    """Zeigt Hauptmenü an."""
    print("\n" + "="*60)
    print("🎙️  WAKE-WORD RECORDING TOOL")
    print("="*60)
    print("\n1. Positive Samples aufnehmen (200x 'Computer')")
    print("2. Negative Samples aufnehmen (200x andere Wörter)")
    print("3. Background Noise aufnehmen (60x Hintergrundgeräusche)")
    print("4. Alles aufnehmen (Komplett-Durchlauf)")
    print("5. Mikrofon testen")
    print("6. Statistik anzeigen")
    print("7. Beenden")
    print("\n" + "="*60)


def test_microphone():
    """Testet das Mikrofon."""
    print("\n" + "="*60)
    print("🎤 MIKROFON-TEST")
    print("="*60)
    
    print("\n📋 Verfügbare Audio-Geräte:")
    print(sd.query_devices())
    
    print("\n🎤 Aufnahme-Test (5 Sekunden)...")
    print("Sprich etwas ins Mikrofon!\n")
    
    countdown(3)
    
    recording = sd.rec(
        int(5 * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype=DTYPE
    )
    sd.wait()
    
    audio_data = recording.flatten()
    
    # Analyse
    max_amp = np.max(np.abs(audio_data))
    mean_amp = np.mean(np.abs(audio_data))
    
    print("\n📊 Analyse:")
    print(f"   Max Amplitude: {max_amp}")
    print(f"   Durchschnitt: {mean_amp:.2f}")
    
    if max_amp < 1000:
        print("\n⚠️  WARNUNG: Mikrofon sehr leise!")
        print("   → Überprüfe Mikrofon-Einstellungen in Windows")
        print("   → Erhöhe Mikrofon-Lautstärke auf 80-100%")
    elif max_amp > 30000:
        print("\n⚠️  WARNUNG: Mikrofon übersteuert!")
        print("   → Reduziere Mikrofon-Lautstärke")
    else:
        print("\n✅ Mikrofon funktioniert korrekt!")
    
    # Speichern für Überprüfung
    test_file = BASE_DIR / "microphone_test.wav"
    save_wav(test_file, audio_data)
    print(f"\n💾 Test-Aufnahme gespeichert: {test_file}")


def show_statistics():
    """Zeigt Statistiken der aufgenommenen Samples."""
    print("\n" + "="*60)
    print("📊 STATISTIK")
    print("="*60)
    
    # Zähle Dateien
    positive_count = len(list(POSITIVE_DIR.glob("*.wav")))
    negative_count = len(list(NEGATIVE_DIR.glob("*.wav")))
    background_count = len(list(BACKGROUND_DIR.glob("*.wav")))
    total_count = positive_count + negative_count + background_count
    
    # Ziele
    positive_target = sum(mode["count"] for mode in RECORDING_MODES.values())
    negative_target = 200
    background_target = 60
    total_target = positive_target + negative_target + background_target
    
    print(f"\n📁 Positive Samples (Wake-Word):")
    print(f"   Aufgenommen: {positive_count}/{positive_target}")
    print(f"   Fortschritt: {(positive_count/positive_target*100):.1f}%")
    
    print(f"\n📁 Negative Samples (andere Wörter):")
    print(f"   Aufgenommen: {negative_count}/{negative_target}")
    print(f"   Fortschritt: {(negative_count/negative_target*100):.1f}%")
    
    print(f"\n📁 Background Noise:")
    print(f"   Aufgenommen: {background_count}/{background_target}")
    print(f"   Fortschritt: {(background_count/background_target*100):.1f}%")
    
    print(f"\n📊 GESAMT:")
    print(f"   Aufgenommen: {total_count}/{total_target}")
    print(f"   Fortschritt: {(total_count/total_target*100):.1f}%")
    
    # Speicherplatz
    total_size = sum(
        f.stat().st_size for f in BASE_DIR.rglob("*.wav")
    ) / (1024 * 1024)  # MB
    
    print(f"\n💾 Speicherplatz: {total_size:.2f} MB")
    
    if total_count >= total_target:
        print("\n🎉 ALLE AUFNAHMEN ABGESCHLOSSEN!")
        print("   Bereit für Training!")


# ============================================================
# MAIN
# ============================================================

def main():
    """Hauptfunktion."""
    # Erstelle Verzeichnisse
    create_directories()
    
    parser = argparse.ArgumentParser(description="Wake-Word Recording Tool v1.1")
    parser.add_argument("--mode", choices=["positive", "negative", "background", "all", "test", "stats"], help="Aufnahmemodus")
    parser.add_argument("--non-interactive", action="store_true", help="Nicht-interaktiver Modus für Skripte")
    args = parser.parse_args()

    if args.mode:
        if args.mode == "positive":
            record_positive_samples()
        elif args.mode == "negative":
            record_negative_samples()
        elif args.mode == "background":
            record_background_noise()
        elif args.mode == "all":
            print("\n🚀 KOMPLETT-DURCHLAUF GESTARTET")
            record_positive_samples()
            record_negative_samples()
            record_background_noise()
            print("\n🎉 KOMPLETT-DURCHLAUF ABGESCHLOSSEN!")
        elif args.mode == "test":
            test_microphone()
        elif args.mode == "stats":
            show_statistics()
        return

    # Interaktiver Modus
    while True:
        display_menu()
        
        try:
            choice = input("\nWähle Option (1-7): ").strip()
            
            if choice == "1":
                record_positive_samples()
            elif choice == "2":
                record_negative_samples()
            elif choice == "3":
                record_background_noise()
            elif choice == "4":
                print("\n🚀 KOMPLETT-DURCHLAUF GESTARTET")
                print("Dies wird ca. 2-3 Stunden dauern.\n")
                confirm = input("Fortfahren? (ja/nein): ").strip().lower()
                if confirm in ["ja", "j", "yes", "y"]:
                    record_positive_samples()
                    input("\n⏸️  Pause. Drücke Enter für negative Samples...")
                    record_negative_samples()
                    input("\n⏸️  Pause. Drücke Enter für background noise...")
                    record_background_noise()
                    print("\n🎉 KOMPLETT-DURCHLAUF ABGESCHLOSSEN!")
            elif choice == "5":
                test_microphone()
            elif choice == "6":
                show_statistics()
            elif choice == "7":
                print("\n👋 Auf Wiedersehen!")
                break
            else:
                print("\n❌ Ungültige Eingabe. Bitte 1-7 wählen.")
        
        except KeyboardInterrupt:
            print("\n\n⏸️  Unterbrochen. Fortschritt wurde gespeichert.")
            print("Starte das Skript erneut, um fortzufahren.")
            break
        except Exception as e:
            print(f"\n❌ Fehler: {e}")
            print("Bitte versuche es erneut.")


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║       🎙️  WAKE-WORD RECORDING TOOL v1.0                ║
    ║                                                          ║
    ║       Projekt: Computer Voice Assistant                 ║
    ║       Datum: 05. Dezember 2025                          ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    main()

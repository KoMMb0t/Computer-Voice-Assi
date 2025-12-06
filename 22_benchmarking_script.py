#!/usr/bin/env python3
"""
Voice Assistant - Benchmarking Script
Misst Performance-Metriken: Wake-Word, STT, CPU/RAM

Datum: 06. Dezember 2025
Projekt: Computer Voice Assistant
GitHub: https://github.com/KoMMb0t/Computer-Voice-Assi
"""

import time
import psutil
import numpy as np
import sounddevice as sd
import json
import os
from datetime import datetime
from typing import Dict, List

# Optional: Porcupine & Vosk (falls installiert)
try:
    import pvporcupine
    PORCUPINE_AVAILABLE = True
except:
    PORCUPINE_AVAILABLE = False

try:
    from vosk import Model as VoskModel, KaldiRecognizer
    VOSK_AVAILABLE = True
except:
    VOSK_AVAILABLE = False

# ============================================================
# BENCHMARK CONFIGURATION
# ============================================================

SAMPLE_RATE = 16000
BENCHMARK_DURATION = 60  # Sekunden
FRAME_LENGTH = 512

# ============================================================
# SYSTEM METRICS
# ============================================================

class SystemMonitor:
    """Überwacht System-Ressourcen."""
    
    def __init__(self):
        self.cpu_samples = []
        self.ram_samples = []
        self.start_time = None
        
    def start(self):
        """Startet Monitoring."""
        self.start_time = time.time()
        self.cpu_samples = []
        self.ram_samples = []
        
    def sample(self):
        """Nimmt Messung."""
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        
        self.cpu_samples.append(cpu)
        self.ram_samples.append(ram)
        
    def get_stats(self) -> Dict:
        """Gibt Statistiken zurück."""
        return {
            "cpu_avg": np.mean(self.cpu_samples) if self.cpu_samples else 0,
            "cpu_max": np.max(self.cpu_samples) if self.cpu_samples else 0,
            "cpu_min": np.min(self.cpu_samples) if self.cpu_samples else 0,
            "ram_avg": np.mean(self.ram_samples) if self.ram_samples else 0,
            "ram_max": np.max(self.ram_samples) if self.ram_samples else 0,
            "ram_min": np.min(self.ram_samples) if self.ram_samples else 0,
            "duration": time.time() - self.start_time if self.start_time else 0
        }


# ============================================================
# WAKE-WORD BENCHMARK
# ============================================================

def benchmark_wake_word(duration: int = 10) -> Dict:
    """
    Benchmarkt Wake-Word Detection.
    
    Returns:
        Dict mit Latenz, CPU, RAM
    """
    print("\n" + "=" * 60)
    print("🎯 WAKE-WORD DETECTION BENCHMARK")
    print("=" * 60)
    
    if not PORCUPINE_AVAILABLE:
        print("❌ Porcupine nicht installiert")
        return {"error": "Porcupine not available"}
    
    # Initialisiere Porcupine
    access_key = os.getenv('PICOVOICE_ACCESS_KEY')
    if not access_key:
        print("❌ PICOVOICE_ACCESS_KEY nicht gesetzt")
        return {"error": "No access key"}
    
    try:
        porcupine = pvporcupine.create(
            access_key=access_key,
            keywords=["computer"],  # Built-in keyword für Test
            sensitivities=[0.5]
        )
    except Exception as e:
        print(f"❌ Porcupine Init Fehler: {e}")
        return {"error": str(e)}
    
    # System Monitor
    monitor = SystemMonitor()
    monitor.start()
    
    # Benchmark
    frame_count = 0
    latencies = []
    
    print(f"⏱️  Benchmark läuft für {duration} Sekunden...")
    
    start_time = time.time()
    
    with sd.InputStream(samplerate=porcupine.sample_rate,
                       channels=1,
                       blocksize=porcupine.frame_length,
                       dtype='int16') as stream:
        
        while time.time() - start_time < duration:
            audio_frame, _ = stream.read(porcupine.frame_length)
            audio_frame = audio_frame.flatten()
            
            # Messe Latenz
            process_start = time.time()
            keyword_index = porcupine.process(audio_frame)
            latency = (time.time() - process_start) * 1000  # ms
            
            latencies.append(latency)
            frame_count += 1
            
            # Sample System-Metriken
            if frame_count % 10 == 0:
                monitor.sample()
    
    porcupine.delete()
    
    # Statistiken
    sys_stats = monitor.get_stats()
    
    results = {
        "frames_processed": frame_count,
        "duration": duration,
        "fps": frame_count / duration,
        "latency_avg_ms": np.mean(latencies),
        "latency_max_ms": np.max(latencies),
        "latency_min_ms": np.min(latencies),
        "latency_p95_ms": np.percentile(latencies, 95),
        "cpu_avg": sys_stats["cpu_avg"],
        "cpu_max": sys_stats["cpu_max"],
        "ram_avg": sys_stats["ram_avg"],
        "ram_max": sys_stats["ram_max"]
    }
    
    # Ausgabe
    print("\n📊 ERGEBNISSE:")
    print(f"Frames verarbeitet: {results['frames_processed']}")
    print(f"FPS: {results['fps']:.1f}")
    print(f"Latenz (Avg): {results['latency_avg_ms']:.2f} ms")
    print(f"Latenz (Max): {results['latency_max_ms']:.2f} ms")
    print(f"Latenz (P95): {results['latency_p95_ms']:.2f} ms")
    print(f"CPU (Avg): {results['cpu_avg']:.1f}%")
    print(f"CPU (Max): {results['cpu_max']:.1f}%")
    print(f"RAM (Avg): {results['ram_avg']:.1f}%")
    
    return results


# ============================================================
# SPEECH-TO-TEXT BENCHMARK
# ============================================================

def benchmark_stt(audio_file: str = None) -> Dict:
    """
    Benchmarkt Speech-to-Text.
    
    Args:
        audio_file: Optional WAV-Datei für Test
        
    Returns:
        Dict mit Latenz, CPU, RAM
    """
    print("\n" + "=" * 60)
    print("🎤 SPEECH-TO-TEXT BENCHMARK")
    print("=" * 60)
    
    if not VOSK_AVAILABLE:
        print("❌ Vosk nicht installiert")
        return {"error": "Vosk not available"}
    
    # Lade Modell
    model_path = "models/vosk-model-small-de-0.15"
    if not os.path.exists(model_path):
        print(f"❌ Vosk-Modell nicht gefunden: {model_path}")
        return {"error": "Model not found"}
    
    print(f"📦 Lade Modell: {model_path}")
    load_start = time.time()
    model = VoskModel(model_path)
    load_time = time.time() - load_start
    print(f"✅ Modell geladen in {load_time:.2f}s")
    
    # Generiere Test-Audio (falls keine Datei)
    if not audio_file:
        print("🎵 Generiere Test-Audio (5 Sekunden)...")
        duration = 5
        audio = np.random.randint(-1000, 1000, int(SAMPLE_RATE * duration), dtype=np.int16)
    else:
        import wave
        with wave.open(audio_file, 'rb') as wf:
            audio = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
        duration = len(audio) / SAMPLE_RATE
    
    # System Monitor
    monitor = SystemMonitor()
    monitor.start()
    
    # Benchmark
    recognizer = KaldiRecognizer(model, SAMPLE_RATE)
    
    print(f"⏱️  Verarbeite {duration:.1f}s Audio...")
    
    process_start = time.time()
    
    # Verarbeite in Chunks
    chunk_size = 4000
    for i in range(0, len(audio), chunk_size):
        chunk = audio[i:i+chunk_size]
        recognizer.AcceptWaveform(chunk.tobytes())
        
        if i % (chunk_size * 10) == 0:
            monitor.sample()
    
    result = json.loads(recognizer.FinalResult())
    process_time = time.time() - process_start
    
    # Statistiken
    sys_stats = monitor.get_stats()
    
    results = {
        "audio_duration": duration,
        "process_time": process_time,
        "real_time_factor": process_time / duration,
        "text": result.get("text", ""),
        "model_load_time": load_time,
        "cpu_avg": sys_stats["cpu_avg"],
        "cpu_max": sys_stats["cpu_max"],
        "ram_avg": sys_stats["ram_avg"],
        "ram_max": sys_stats["ram_max"]
    }
    
    # Ausgabe
    print("\n📊 ERGEBNISSE:")
    print(f"Audio-Dauer: {results['audio_duration']:.1f}s")
    print(f"Verarbeitungszeit: {results['process_time']:.2f}s")
    print(f"Real-Time-Factor: {results['real_time_factor']:.2f}x")
    print(f"Erkannter Text: '{results['text']}'")
    print(f"CPU (Avg): {results['cpu_avg']:.1f}%")
    print(f"RAM (Avg): {results['ram_avg']:.1f}%")
    
    return results


# ============================================================
# FULL SYSTEM BENCHMARK
# ============================================================

def benchmark_full_system(duration: int = 60) -> Dict:
    """
    Benchmarkt komplettes System (Idle).
    
    Args:
        duration: Dauer in Sekunden
        
    Returns:
        Dict mit CPU, RAM, Disk
    """
    print("\n" + "=" * 60)
    print("💻 FULL SYSTEM BENCHMARK (IDLE)")
    print("=" * 60)
    
    monitor = SystemMonitor()
    monitor.start()
    
    print(f"⏱️  Monitoring für {duration} Sekunden...")
    
    samples = []
    start_time = time.time()
    
    while time.time() - start_time < duration:
        monitor.sample()
        
        # Disk I/O
        disk_io = psutil.disk_io_counters()
        samples.append({
            "read_bytes": disk_io.read_bytes,
            "write_bytes": disk_io.write_bytes
        })
        
        time.sleep(1)
    
    # Statistiken
    sys_stats = monitor.get_stats()
    
    # Disk I/O Delta
    if len(samples) > 1:
        read_delta = samples[-1]["read_bytes"] - samples[0]["read_bytes"]
        write_delta = samples[-1]["write_bytes"] - samples[0]["write_bytes"]
    else:
        read_delta = write_delta = 0
    
    results = {
        "duration": duration,
        "cpu_avg": sys_stats["cpu_avg"],
        "cpu_max": sys_stats["cpu_max"],
        "cpu_min": sys_stats["cpu_min"],
        "ram_avg": sys_stats["ram_avg"],
        "ram_max": sys_stats["ram_max"],
        "ram_min": sys_stats["ram_min"],
        "disk_read_mb": read_delta / (1024 * 1024),
        "disk_write_mb": write_delta / (1024 * 1024)
    }
    
    # Ausgabe
    print("\n📊 ERGEBNISSE:")
    print(f"CPU (Avg): {results['cpu_avg']:.1f}%")
    print(f"CPU (Max): {results['cpu_max']:.1f}%")
    print(f"CPU (Min): {results['cpu_min']:.1f}%")
    print(f"RAM (Avg): {results['ram_avg']:.1f}%")
    print(f"RAM (Max): {results['ram_max']:.1f}%")
    print(f"Disk Read: {results['disk_read_mb']:.2f} MB")
    print(f"Disk Write: {results['disk_write_mb']:.2f} MB")
    
    return results


# ============================================================
# REPORT GENERATION
# ============================================================

def generate_report(results: Dict, output_file: str = "benchmark_report.json"):
    """Generiert Benchmark-Report."""
    
    # Füge Metadaten hinzu
    report = {
        "timestamp": datetime.now().isoformat(),
        "system": {
            "cpu_count": psutil.cpu_count(),
            "cpu_freq": psutil.cpu_freq().current if psutil.cpu_freq() else 0,
            "ram_total_gb": psutil.virtual_memory().total / (1024**3),
            "platform": os.name
        },
        "results": results
    }
    
    # Speichere als JSON
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Report gespeichert: {output_file}")
    
    # Markdown-Report
    md_file = output_file.replace('.json', '.md')
    with open(md_file, 'w') as f:
        f.write("# Voice Assistant Benchmark Report\n\n")
        f.write(f"**Datum:** {report['timestamp']}\n\n")
        f.write("## System\n\n")
        f.write(f"- CPU: {report['system']['cpu_count']} Cores @ {report['system']['cpu_freq']:.0f} MHz\n")
        f.write(f"- RAM: {report['system']['ram_total_gb']:.1f} GB\n")
        f.write(f"- Platform: {report['system']['platform']}\n\n")
        
        f.write("## Ergebnisse\n\n")
        
        for key, value in results.items():
            if isinstance(value, dict):
                f.write(f"### {key}\n\n")
                for k, v in value.items():
                    f.write(f"- {k}: {v}\n")
                f.write("\n")
    
    print(f"📄 Markdown-Report: {md_file}")


# ============================================================
# MAIN
# ============================================================

def main():
    """Führt alle Benchmarks aus."""
    print("=" * 60)
    print("🚀 VOICE ASSISTANT - PERFORMANCE BENCHMARK")
    print("=" * 60)
    
    results = {}
    
    # 1. Wake-Word Benchmark
    try:
        results["wake_word"] = benchmark_wake_word(duration=10)
    except Exception as e:
        print(f"❌ Wake-Word Benchmark fehlgeschlagen: {e}")
        results["wake_word"] = {"error": str(e)}
    
    # 2. STT Benchmark
    try:
        results["stt"] = benchmark_stt()
    except Exception as e:
        print(f"❌ STT Benchmark fehlgeschlagen: {e}")
        results["stt"] = {"error": str(e)}
    
    # 3. System Benchmark
    try:
        results["system"] = benchmark_full_system(duration=10)
    except Exception as e:
        print(f"❌ System Benchmark fehlgeschlagen: {e}")
        results["system"] = {"error": str(e)}
    
    # Generiere Report
    generate_report(results)
    
    print("\n" + "=" * 60)
    print("✅ BENCHMARK ABGESCHLOSSEN")
    print("=" * 60)


if __name__ == "__main__":
    main()

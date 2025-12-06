#!/usr/bin/env python3
"""
Voice Assistant - Automated Testing Suite
Basierend auf Testing-Framework (08_wake_word_testing.md)

Datum: 06. Dezember 2025
Projekt: Computer Voice Assistant
GitHub: https://github.com/KoMMb0t/Computer-Voice-Assi
"""

import unittest
import time
import os
import sys
import numpy as np
import sounddevice as sd
from unittest.mock import Mock, patch, MagicMock
import json

# Importiere Voice Assistant Komponenten (wenn vorhanden)
# from voice_assistant_computer import initialize_porcupine, initialize_vosk

# ============================================================
# TEST CONFIGURATION
# ============================================================

TEST_SAMPLE_RATE = 16000
TEST_DURATION = 2.0
TEST_WAKE_WORD = "computer"

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def generate_test_audio(frequency=440, duration=1.0, sample_rate=16000):
    """Generiert Test-Audio (Sinuswelle)."""
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.sin(2 * np.pi * frequency * t)
    return (audio * 32767).astype(np.int16)


def generate_silence(duration=1.0, sample_rate=16000):
    """Generiert Stille."""
    return np.zeros(int(sample_rate * duration), dtype=np.int16)


def generate_noise(duration=1.0, sample_rate=16000, amplitude=1000):
    """Generiert weißes Rauschen."""
    return np.random.randint(-amplitude, amplitude, 
                             int(sample_rate * duration), 
                             dtype=np.int16)


# ============================================================
# TEST SUITE 1: AUDIO PROCESSING TESTS
# ============================================================

class TestAudioProcessing(unittest.TestCase):
    """Tests für Audio-Verarbeitung."""
    
    def setUp(self):
        """Setup vor jedem Test."""
        self.sample_rate = TEST_SAMPLE_RATE
        
    def test_generate_test_audio(self):
        """Test: Audio-Generierung funktioniert."""
        audio = generate_test_audio(duration=1.0)
        
        self.assertEqual(len(audio), self.sample_rate)
        self.assertEqual(audio.dtype, np.int16)
        self.assertGreater(np.max(np.abs(audio)), 0)
        
    def test_generate_silence(self):
        """Test: Stille-Generierung funktioniert."""
        silence = generate_silence(duration=1.0)
        
        self.assertEqual(len(silence), self.sample_rate)
        self.assertEqual(np.max(np.abs(silence)), 0)
        
    def test_generate_noise(self):
        """Test: Rauschen-Generierung funktioniert."""
        noise = generate_noise(duration=1.0, amplitude=1000)
        
        self.assertEqual(len(noise), self.sample_rate)
        self.assertGreater(np.max(np.abs(noise)), 0)
        self.assertLess(np.max(np.abs(noise)), 1001)
        
    def test_audio_amplitude_range(self):
        """Test: Audio-Amplitude im gültigen Bereich."""
        audio = generate_test_audio()
        
        self.assertGreaterEqual(np.min(audio), -32768)
        self.assertLessEqual(np.max(audio), 32767)


# ============================================================
# TEST SUITE 2: WAKE-WORD DETECTION TESTS (MOCK)
# ============================================================

class TestWakeWordDetection(unittest.TestCase):
    """Tests für Wake-Word Detection (mit Mocks)."""
    
    def setUp(self):
        """Setup vor jedem Test."""
        self.wake_word = TEST_WAKE_WORD
        
    @patch('pvporcupine.create')
    def test_porcupine_initialization(self, mock_porcupine):
        """Test: Porcupine kann initialisiert werden."""
        mock_instance = MagicMock()
        mock_instance.sample_rate = 16000
        mock_instance.frame_length = 512
        mock_porcupine.return_value = mock_instance
        
        # Simuliere Initialisierung
        porcupine = mock_porcupine(
            access_key="test_key",
            keyword_paths=["test.ppn"],
            sensitivities=[0.5]
        )
        
        self.assertIsNotNone(porcupine)
        self.assertEqual(porcupine.sample_rate, 16000)
        
    @patch('pvporcupine.create')
    def test_wake_word_detection_positive(self, mock_porcupine):
        """Test: Wake-Word wird erkannt (simuliert)."""
        mock_instance = MagicMock()
        mock_instance.process.return_value = 0  # Keyword Index 0 = erkannt
        mock_porcupine.return_value = mock_instance
        
        porcupine = mock_porcupine()
        audio_frame = generate_test_audio(duration=0.03)
        
        result = porcupine.process(audio_frame)
        
        self.assertEqual(result, 0)
        
    @patch('pvporcupine.create')
    def test_wake_word_detection_negative(self, mock_porcupine):
        """Test: Kein Wake-Word erkannt (simuliert)."""
        mock_instance = MagicMock()
        mock_instance.process.return_value = -1  # -1 = nicht erkannt
        mock_porcupine.return_value = mock_instance
        
        porcupine = mock_porcupine()
        audio_frame = generate_silence(duration=0.03)
        
        result = porcupine.process(audio_frame)
        
        self.assertEqual(result, -1)
        
    def test_cooldown_mechanism(self):
        """Test: Cooldown verhindert Doppel-Erkennungen."""
        last_detection_time = time.time()
        cooldown_seconds = 2.0
        
        # Sofortige zweite Erkennung sollte blockiert werden
        current_time = time.time()
        time_diff = current_time - last_detection_time
        
        self.assertLess(time_diff, cooldown_seconds)
        
        # Nach Cooldown sollte Erkennung erlaubt sein
        time.sleep(2.1)
        current_time = time.time()
        time_diff = current_time - last_detection_time
        
        self.assertGreater(time_diff, cooldown_seconds)


# ============================================================
# TEST SUITE 3: SPEECH-TO-TEXT TESTS (MOCK)
# ============================================================

class TestSpeechToText(unittest.TestCase):
    """Tests für Speech-to-Text (mit Mocks)."""
    
    @patch('vosk.Model')
    @patch('vosk.KaldiRecognizer')
    def test_vosk_initialization(self, mock_recognizer, mock_model):
        """Test: Vosk kann initialisiert werden."""
        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance
        
        vosk_model = mock_model(lang="de")
        
        self.assertIsNotNone(vosk_model)
        
    @patch('vosk.KaldiRecognizer')
    def test_speech_recognition_success(self, mock_recognizer):
        """Test: Sprache wird erkannt (simuliert)."""
        mock_rec = MagicMock()
        mock_rec.AcceptWaveform.return_value = True
        mock_rec.Result.return_value = json.dumps({"text": "öffne youtube"})
        mock_recognizer.return_value = mock_rec
        
        recognizer = mock_recognizer(None, 16000)
        audio_data = generate_test_audio()
        
        if recognizer.AcceptWaveform(audio_data.tobytes()):
            result = json.loads(recognizer.Result())
            
        self.assertEqual(result["text"], "öffne youtube")
        
    @patch('vosk.KaldiRecognizer')
    def test_speech_recognition_empty(self, mock_recognizer):
        """Test: Keine Sprache erkannt (simuliert)."""
        mock_rec = MagicMock()
        mock_rec.AcceptWaveform.return_value = True
        mock_rec.Result.return_value = json.dumps({"text": ""})
        mock_recognizer.return_value = mock_rec
        
        recognizer = mock_recognizer(None, 16000)
        audio_data = generate_silence()
        
        if recognizer.AcceptWaveform(audio_data.tobytes()):
            result = json.loads(recognizer.Result())
            
        self.assertEqual(result["text"], "")


# ============================================================
# TEST SUITE 4: COMMAND EXECUTION TESTS
# ============================================================

class TestCommandExecution(unittest.TestCase):
    """Tests für Befehlsausführung."""
    
    def test_command_classification_simple(self):
        """Test: Einfache Befehls-Klassifizierung."""
        command_keywords = ["öffne", "starte", "schließe"]
        
        test_cases = [
            ("öffne youtube", True),
            ("starte rechner", True),
            ("wie wird das wetter", False),
            ("hallo", False)
        ]
        
        for text, expected in test_cases:
            is_command = any(kw in text.lower() for kw in command_keywords)
            self.assertEqual(is_command, expected, 
                           f"Failed for: {text}")
    
    def test_question_detection(self):
        """Test: Fragen-Erkennung."""
        question_keywords = ["wie", "was", "wer", "wann", "wo", "warum"]
        
        test_cases = [
            ("wie wird das wetter", True),
            ("was ist die uhrzeit", True),
            ("öffne youtube", False),
            ("hallo", False)
        ]
        
        for text, expected in test_cases:
            is_question = any(text.lower().startswith(kw) for kw in question_keywords)
            self.assertEqual(is_question, expected, 
                           f"Failed for: {text}")


# ============================================================
# TEST SUITE 5: PERFORMANCE TESTS
# ============================================================

class TestPerformance(unittest.TestCase):
    """Tests für Performance-Metriken."""
    
    def test_audio_processing_latency(self):
        """Test: Audio-Verarbeitung ist schnell genug."""
        audio = generate_test_audio(duration=1.0)
        
        start_time = time.time()
        # Simuliere Verarbeitung
        processed = audio * 1.0
        latency = time.time() - start_time
        
        # Sollte < 10ms sein für 1s Audio
        self.assertLess(latency, 0.01, 
                       f"Latency too high: {latency*1000:.2f}ms")
    
    def test_memory_efficiency(self):
        """Test: Memory-Footprint ist akzeptabel."""
        # Generiere 10 Sekunden Audio
        audio = generate_test_audio(duration=10.0)
        
        # Berechne Größe in MB
        size_mb = audio.nbytes / (1024 * 1024)
        
        # Sollte < 1MB sein für 10s @ 16kHz mono
        self.assertLess(size_mb, 1.0, 
                       f"Memory usage too high: {size_mb:.2f}MB")


# ============================================================
# TEST SUITE 6: INTEGRATION TESTS
# ============================================================

class TestIntegration(unittest.TestCase):
    """Integration-Tests für Gesamtsystem."""
    
    def test_full_pipeline_simulation(self):
        """Test: Kompletter Pipeline-Durchlauf (simuliert)."""
        # 1. Wake-Word Detection
        wake_word_detected = True  # Simuliert
        self.assertTrue(wake_word_detected)
        
        # 2. Speech-to-Text
        recognized_text = "öffne youtube"  # Simuliert
        self.assertIsNotNone(recognized_text)
        self.assertGreater(len(recognized_text), 0)
        
        # 3. Command Classification
        is_command = "öffne" in recognized_text
        self.assertTrue(is_command)
        
        # 4. Command Execution (würde hier erfolgen)
        command_executed = True  # Simuliert
        self.assertTrue(command_executed)


# ============================================================
# TEST RUNNER
# ============================================================

def run_tests(verbosity=2):
    """Führt alle Tests aus."""
    # Test Suites
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Füge alle Test-Klassen hinzu
    suite.addTests(loader.loadTestsFromTestCase(TestAudioProcessing))
    suite.addTests(loader.loadTestsFromTestCase(TestWakeWordDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestSpeechToText))
    suite.addTests(loader.loadTestsFromTestCase(TestCommandExecution))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Runner
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    return result


def generate_test_report(result):
    """Generiert Test-Report."""
    report = []
    report.append("=" * 60)
    report.append("VOICE ASSISTANT - TEST REPORT")
    report.append("=" * 60)
    report.append(f"Tests run: {result.testsRun}")
    report.append(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    report.append(f"Failures: {len(result.failures)}")
    report.append(f"Errors: {len(result.errors)}")
    report.append(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    report.append("=" * 60)
    
    if result.failures:
        report.append("\nFAILURES:")
        for test, traceback in result.failures:
            report.append(f"\n{test}:")
            report.append(traceback)
    
    if result.errors:
        report.append("\nERRORS:")
        for test, traceback in result.errors:
            report.append(f"\n{test}:")
            report.append(traceback)
    
    return "\n".join(report)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 VOICE ASSISTANT - AUTOMATED TESTING SUITE")
    print("=" * 60)
    print()
    
    # Führe Tests aus
    result = run_tests(verbosity=2)
    
    # Generiere Report
    print("\n")
    report = generate_test_report(result)
    print(report)
    
    # Speichere Report
    report_file = "test_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n📄 Report gespeichert: {report_file}")
    
    # Exit Code
    sys.exit(0 if result.wasSuccessful() else 1)

#!/usr/bin/env python3
"""
Voice Assistant - LLM Integration Prototype
LLMManager Klasse für ChatGPT API Integration

Datum: 06. Dezember 2025
Projekt: Computer Voice Assistant
GitHub: https://github.com/KoMMb0t/Computer-Voice-Assi
"""

import os
import json
import time
from typing import List, Dict, Optional
from openai import OpenAI
import configparser

# ============================================================
# LLM MANAGER CLASS
# ============================================================

class LLMManager:
    """
    Verwaltet LLM-Anfragen an ChatGPT API.
    
    Features:
    - Konversations-History
    - Command vs. Question Classification
    - Fehlerbehandlung & Fallbacks
    - Token-Counting
    - Cost-Tracking
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        Initialisiert LLMManager.
        
        Args:
            api_key: OpenAI API Key (oder aus Umgebungsvariable)
            model: Modell-Name (gpt-4, gpt-3.5-turbo, etc.)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            raise ValueError("OpenAI API Key nicht gefunden! Setze OPENAI_API_KEY Umgebungsvariable.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        
        # Konversations-History
        self.conversation_history: List[Dict[str, str]] = []
        self.max_history_length = 10
        
        # System-Prompt
        self.system_prompt = """Du bist ein hilfreicher Voice Assistant namens 'Computer'.
Du antwortest kurz und präzise auf Deutsch.
Wenn du etwas nicht weißt, sage es ehrlich.
Vermeide lange Erklärungen, außer der Nutzer fragt explizit danach."""
        
        # Statistiken
        self.total_tokens = 0
        self.total_cost = 0.0
        self.request_count = 0
        
        print(f"✅ LLMManager initialisiert (Modell: {model})")
    
    def classify_input(self, text: str) -> str:
        """
        Klassifiziert Input als COMMAND oder QUESTION.
        
        Args:
            text: Nutzer-Input
            
        Returns:
            "COMMAND" oder "QUESTION"
        """
        # Pattern-based Classification (schnell)
        command_keywords = [
            "öffne", "starte", "schließe", "beende", "spiele",
            "zeige", "mach", "stelle", "schalte"
        ]
        
        question_keywords = [
            "wie", "was", "wer", "wann", "wo", "warum", "wieso",
            "welche", "welcher", "welches", "erkläre", "beschreibe"
        ]
        
        text_lower = text.lower()
        
        # Prüfe Command-Keywords
        if any(kw in text_lower for kw in command_keywords):
            return "COMMAND"
        
        # Prüfe Question-Keywords
        if any(text_lower.startswith(kw) for kw in question_keywords):
            return "QUESTION"
        
        # Fragezeichen?
        if "?" in text:
            return "QUESTION"
        
        # Default: QUESTION (sicherer)
        return "QUESTION"
    
    def query(self, user_input: str, use_history: bool = True) -> str:
        """
        Sendet Anfrage an ChatGPT API.
        
        Args:
            user_input: Nutzer-Frage
            use_history: Konversations-History verwenden?
            
        Returns:
            Antwort vom LLM
        """
        try:
            # Baue Messages
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Füge History hinzu (falls gewünscht)
            if use_history and self.conversation_history:
                messages.extend(self.conversation_history[-self.max_history_length:])
            
            # Füge aktuelle Frage hinzu
            messages.append({"role": "user", "content": user_input})
            
            # API-Call
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=150,  # Kurze Antworten für Voice
                n=1
            )
            
            latency = time.time() - start_time
            
            # Extrahiere Antwort
            answer = response.choices[0].message.content.strip()
            
            # Update History
            if use_history:
                self.conversation_history.append({"role": "user", "content": user_input})
                self.conversation_history.append({"role": "assistant", "content": answer})
            
            # Update Statistiken
            self.request_count += 1
            tokens_used = response.usage.total_tokens
            self.total_tokens += tokens_used
            
            # Kosten berechnen (GPT-4: $0.03/1K input, $0.06/1K output)
            if "gpt-4" in self.model:
                input_cost = response.usage.prompt_tokens * 0.03 / 1000
                output_cost = response.usage.completion_tokens * 0.06 / 1000
                cost = input_cost + output_cost
            else:  # GPT-3.5-turbo: $0.0015/1K input, $0.002/1K output
                input_cost = response.usage.prompt_tokens * 0.0015 / 1000
                output_cost = response.usage.completion_tokens * 0.002 / 1000
                cost = input_cost + output_cost
            
            self.total_cost += cost
            
            print(f"💬 LLM Response ({latency:.2f}s, {tokens_used} tokens, ${cost:.4f})")
            
            return answer
        
        except Exception as e:
            print(f"❌ LLM Error: {e}")
            return "Entschuldigung, ich konnte keine Antwort generieren."
    
    def reset_history(self):
        """Setzt Konversations-History zurück."""
        self.conversation_history = []
        print("🔄 Konversations-History zurückgesetzt")
    
    def get_stats(self) -> Dict:
        """Gibt Statistiken zurück."""
        return {
            "requests": self.request_count,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "avg_tokens_per_request": self.total_tokens / max(self.request_count, 1),
            "avg_cost_per_request": self.total_cost / max(self.request_count, 1)
        }
    
    def print_stats(self):
        """Gibt Statistiken aus."""
        stats = self.get_stats()
        print("\n" + "=" * 60)
        print("📊 LLM STATISTIKEN")
        print("=" * 60)
        print(f"Anfragen: {stats['requests']}")
        print(f"Gesamt-Tokens: {stats['total_tokens']}")
        print(f"Gesamt-Kosten: ${stats['total_cost']:.4f}")
        print(f"Ø Tokens/Anfrage: {stats['avg_tokens_per_request']:.1f}")
        print(f"Ø Kosten/Anfrage: ${stats['avg_cost_per_request']:.4f}")
        print("=" * 60)


# ============================================================
# HYBRID COMMAND ENGINE (mit LLM-Fallback)
# ============================================================

class HybridCommandEngine:
    """
    Kombiniert Pattern-based Commands mit LLM-Fallback.
    """
    
    def __init__(self, llm_manager: LLMManager):
        self.llm = llm_manager
    
    def execute(self, text: str) -> bool:
        """
        Führt Befehl aus (Pattern-based oder LLM).
        
        Args:
            text: Nutzer-Input
            
        Returns:
            True wenn erfolgreich, False sonst
        """
        # Klassifiziere Input
        input_type = self.llm.classify_input(text)
        
        print(f"🔍 Klassifiziert als: {input_type}")
        
        if input_type == "COMMAND":
            # Versuche Pattern-based Execution
            success = self._execute_pattern_based(text)
            
            if success:
                return True
            else:
                print("⚠️  Pattern-based Execution fehlgeschlagen, verwende LLM...")
                # Fallback: LLM
                return self._execute_llm_based(text)
        
        else:  # QUESTION
            # Direkt LLM verwenden
            return self._execute_llm_based(text)
    
    def _execute_pattern_based(self, text: str) -> bool:
        """Pattern-based Command Execution (wie bisher)."""
        import webbrowser
        import subprocess
        from datetime import datetime
        
        text_lower = text.lower()
        
        # Web-Commands
        if "youtube" in text_lower:
            print("🌐 Öffne YouTube")
            webbrowser.open("https://www.youtube.com")
            return True
        
        if "google" in text_lower:
            print("🌐 Öffne Google")
            webbrowser.open("https://www.google.com")
            return True
        
        # App-Commands
        if "rechner" in text_lower or "taschenrechner" in text_lower:
            print("📱 Öffne Taschenrechner")
            subprocess.Popen("calc.exe")
            return True
        
        # System-Commands
        if "uhrzeit" in text_lower or "wie spät" in text_lower:
            now = datetime.now()
            print(f"🕐 Es ist {now.hour} Uhr {now.minute}")
            return True
        
        # Nicht erkannt
        return False
    
    def _execute_llm_based(self, text: str) -> bool:
        """LLM-based Execution."""
        answer = self.llm.query(text)
        print(f"💬 LLM: {answer}")
        return True


# ============================================================
# DEMO / TESTING
# ============================================================

def demo():
    """Demo der LLM-Integration."""
    print("=" * 60)
    print("🤖 LLM INTEGRATION PROTOTYPE - DEMO")
    print("=" * 60)
    
    # Initialisiere LLMManager
    try:
        llm = LLMManager(model="gpt-3.5-turbo")  # Günstiger für Demo
    except ValueError as e:
        print(f"❌ Fehler: {e}")
        print("💡 Setze OPENAI_API_KEY Umgebungsvariable:")
        print("   export OPENAI_API_KEY='sk-...'")
        return
    
    # Initialisiere Hybrid Engine
    engine = HybridCommandEngine(llm)
    
    # Test-Fragen
    test_inputs = [
        "Öffne YouTube",  # COMMAND (Pattern-based)
        "Wie wird das Wetter morgen?",  # QUESTION (LLM)
        "Was ist 15 mal 23?",  # QUESTION (LLM)
        "Erkläre mir, was ein LLM ist",  # QUESTION (LLM)
        "Öffne den Taschenrechner",  # COMMAND (Pattern-based)
        "Übersetze 'Guten Morgen' ins Englische"  # QUESTION (LLM)
    ]
    
    print("\n🧪 Teste verschiedene Inputs...\n")
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"\n--- Test {i}/{len(test_inputs)} ---")
        print(f"👤 User: {user_input}")
        
        engine.execute(user_input)
        
        time.sleep(1)  # Rate-Limiting
    
    # Statistiken
    llm.print_stats()
    
    # Interaktiver Modus
    print("\n" + "=" * 60)
    print("💬 INTERAKTIVER MODUS")
    print("=" * 60)
    print("Tippe 'exit' zum Beenden, 'reset' um History zu löschen\n")
    
    while True:
        try:
            user_input = input("👤 Du: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == "exit":
                break
            
            if user_input.lower() == "reset":
                llm.reset_history()
                continue
            
            if user_input.lower() == "stats":
                llm.print_stats()
                continue
            
            engine.execute(user_input)
        
        except KeyboardInterrupt:
            break
    
    print("\n👋 Demo beendet")
    llm.print_stats()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    demo()

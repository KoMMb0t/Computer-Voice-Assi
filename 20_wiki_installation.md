# Installation

Detaillierte Anleitung zur Installation des Computer Voice Assistant.

---

## Voraussetzungen

### Hardware

**Minimum:**
- CPU: Dual-Core 1.5 GHz
- RAM: 4 GB
- Mikrofon: USB oder integriert
- Lautsprecher: 3.5mm oder USB

**Empfohlen:**
- CPU: Quad-Core 2.0 GHz+
- RAM: 8 GB+
- Mikrofon: USB mit Rauschunterdrückung
- Lautsprecher: USB oder Bluetooth

### Software

- **Windows:** 10/11 (64-bit)
- **Linux:** Ubuntu 22.04+, Debian 12+, Raspberry Pi OS
- **Python:** 3.9+ (3.11 empfohlen)
- **Internet:** Für TTS & LLM (optional)

---

## Windows Installation

### 1. Python installieren

Download: https://www.python.org/downloads/

**Wichtig:** Aktiviere "Add Python to PATH" während Installation!

Prüfe Installation:
```powershell
python --version
pip --version
```

### 2. Git installieren (optional)

Download: https://git-scm.com/download/win

Oder verwende GitHub Desktop: https://desktop.github.com

### 3. Projekt klonen

**Mit Git:**
```powershell
git clone https://github.com/KoMMb0t/Computer-Voice-Assi.git
cd Computer-Voice-Assi
```

**Ohne Git:**
1. Gehe zu https://github.com/KoMMb0t/Computer-Voice-Assi
2. Klicke "Code" → "Download ZIP"
3. Entpacke ZIP
4. Öffne PowerShell in Projekt-Ordner

### 4. Virtual Environment erstellen

```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 5. Dependencies installieren

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

**Falls Fehler:**
```powershell
# PyAudio Fehler? Installiere manuell:
pip install pipwin
pipwin install pyaudio
```

### 6. Picovoice Access Key

1. Registriere dich: https://console.picovoice.ai
2. Erstelle neues Projekt
3. Kopiere Access Key
4. Erstelle `.env` Datei:

```powershell
echo PICOVOICE_ACCESS_KEY=your_key_here > .env
```

### 7. Wake-Word trainieren

1. Gehe zu https://console.picovoice.ai
2. Klicke "Porcupine" → "Train Wake Word"
3. Name: "computer"
4. Sprache: Deutsch (oder English)
5. Klicke "Train"
6. Download `computer.ppn`
7. Erstelle Ordner `models/` im Projekt
8. Kopiere `computer.ppn` nach `models/computer.ppn`

### 8. Vosk Modell herunterladen

**Option 1: Automatisch (empfohlen)**
```powershell
python download_vosk_model.py
```

**Option 2: Manuell**
1. Download: https://alphacephei.com/vosk/models/vosk-model-small-de-0.15.zip
2. Entpacke in `models/vosk-model-small-de-0.15/`

### 9. Konfiguration anpassen

Bearbeite `config.ini`:
```ini
[WakeWord]
picovoice_access_key = YOUR_KEY_HERE
porcupine_model_path = models/computer.ppn

[STT]
model_path = models/vosk-model-small-de-0.15
```

### 10. Starten!

```powershell
python 15_voice_assistant_configurable.py
```

---

## Linux Installation (Ubuntu/Debian)

### 1. System aktualisieren

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Python & Dependencies

```bash
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    portaudio19-dev \
    python3-pyaudio \
    libasound2-dev \
    ffmpeg \
    git
```

### 3. Projekt klonen

```bash
git clone https://github.com/KoMMb0t/Computer-Voice-Assi.git
cd Computer-Voice-Assi
```

### 4. Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 5. Dependencies installieren

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 6-10: Wie Windows

(Picovoice Key, Wake-Word Training, Vosk Modell, Config, Start)

---

## Raspberry Pi Installation

Siehe [Cross-Platform Guide](Cross-Platform) für detaillierte Anleitung.

**Quick Start:**
```bash
# System Update
sudo apt update && sudo apt upgrade -y

# Dependencies
sudo apt install -y python3-pip portaudio19-dev git

# Projekt
git clone https://github.com/KoMMb0t/Computer-Voice-Assi.git
cd Computer-Voice-Assi

# Virtual Environment
python3 -m venv venv
source venv/bin/activate

# Install
pip install -r requirements.txt

# Konfigurieren & Starten
nano config.ini
python3 15_voice_assistant_configurable.py
```

---

## Troubleshooting

### Problem: "Python not found"

**Windows:**
```powershell
# Installiere Python von python.org
# Aktiviere "Add to PATH"
```

**Linux:**
```bash
sudo apt install python3
```

### Problem: "pip not found"

```bash
# Linux
sudo apt install python3-pip

# Windows
python -m ensurepip --upgrade
```

### Problem: "PortAudio not found"

**Linux:**
```bash
sudo apt install portaudio19-dev
pip install --force-reinstall sounddevice
```

**Windows:**
```powershell
pip install pipwin
pipwin install pyaudio
```

### Problem: "No module named 'pvporcupine'"

```bash
pip install pvporcupine
```

### Problem: "Invalid Picovoice Access Key"

1. Prüfe `.env` Datei
2. Kopiere Key erneut von https://console.picovoice.ai
3. Stelle sicher, dass keine Leerzeichen im Key sind

### Problem: "Vosk model not found"

```bash
# Prüfe Pfad in config.ini
# Sollte sein: models/vosk-model-small-de-0.15

# Download erneut
cd models/
wget https://alphacephei.com/vosk/models/vosk-model-small-de-0.15.zip
unzip vosk-model-small-de-0.15.zip
```

---

## Nächste Schritte

Nach erfolgreicher Installation:

1. ✅ Teste Mikrofon: `python test_microphone.py`
2. ✅ Teste TTS: `python test_tts.py`
3. ✅ Lerne [Befehle](Befehle)
4. ✅ Konfiguriere [LLM-Integration](LLM-Integration)
5. ✅ Richte [Home Assistant](Home-Assistant) ein

---

**Bei Problemen:** [GitHub Issues](https://github.com/KoMMb0t/Computer-Voice-Assi/issues)

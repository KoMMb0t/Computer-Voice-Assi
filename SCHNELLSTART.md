# 🚀 SCHNELLSTART: Wake-Word Training

**Computer Voice Assistant - SCHNELLSTART.md - 08.12.2025**

---

## ✅ Was ist fertig?

Ich habe 3 neue Dateien für dich erstellt und auf GitHub gepusht:

1. **`upload_to_huggingface.py`** - Dataset Upload zu Hugging Face
2. **`train_wake_word_local.py`** - Training auf Shadow PC
3. **`TRAINING_GUIDE.md`** - Ausführliche Anleitung

---

## 🎯 Nächste Schritte

### **Option A: Nur Training auf Shadow PC** (empfohlen)

Wenn du das Training einfach nur starten willst:

1. **Kopiere `wake_word_recordings` Ordner auf Shadow PC** (via Shadow Drive)
2. **Kopiere `train_wake_word_local.py` auf Shadow PC**
3. **Auf Shadow PC: Öffne PowerShell/CMD**
4. **Installiere Dependencies:**

```bash
pip install tensorflow librosa soundfile scikit-learn matplotlib tqdm
```

5. **Starte Training:**

```bash
python train_wake_word_local.py --recordings-dir C:\Pfad\zu\wake_word_recordings
```

**Fertig!** Das Training läuft jetzt 3-8 Stunden.

---

### **Option B: Mit Hugging Face Upload** (für Backup)

Wenn du dein Dataset zusätzlich auf Hugging Face hochladen willst:

#### **Schritt 1: Hugging Face Token holen**

1. Gehe zu: https://huggingface.co/settings/tokens
2. Klicke "New token"
3. Name: `wake-word-training`
4. Role: `write`
5. Kopiere den Token (sieht aus wie `hf_...`)

#### **Schritt 2: Dataset hochladen**

**Auf deinem normalen PC (wo die Aufnahmen sind):**

```powershell
# In PowerShell im Projektordner
.\.venv\Scripts\Activate
pip install huggingface_hub
python upload_to_huggingface.py --token DEIN_TOKEN --dataset-name DEIN_USERNAME/computer-wake-word
```

**Ersetze:**
- `DEIN_TOKEN` mit deinem Hugging Face Token
- `DEIN_USERNAME` mit deinem Hugging Face Usernamen

#### **Schritt 3: Training auf Shadow PC**

Siehe **Option A** oben!

---

## 📁 Was bekommst du nach dem Training?

Im Ordner `models` findest du:

- **`computer_wake_word_model.h5`** ← Dein fertiges Modell!
- **`best_model.h5`** ← Bestes Modell während Training
- **`computer_wake_word_model.tflite`** ← Für Raspberry Pi/Mobile
- **`training_history.png`** ← Graphen zum Training

---

## 🔗 Links

- **GitHub Repository:** https://github.com/KoMMb0t/Computer-Voice-Assi
- **Ausführliche Anleitung:** `TRAINING_GUIDE.md`
- **Hugging Face:** https://huggingface.co

---

## ❓ Fragen?

- Lies `TRAINING_GUIDE.md` für Details
- Oder frag mich einfach! 😊

---

**Seite 1/1**

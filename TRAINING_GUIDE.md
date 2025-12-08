---

# 🚀 OpenWakeWord Training Guide

**Computer Voice Assistant - TRAINING_GUIDE.md - 08.12.2025**

---

## 🎯 Ziel

Dieses Dokument erklärt, wie du dein eigenes "Computer" Wake-Word Modell trainierst, indem du:

1.  **Dein Dataset zu Hugging Face hochlädst** (als Backup & für die Community)
2.  **Das Modell auf deinem Shadow PC trainierst** (schnell & zuverlässig)

---

## 📋 Phasen

1.  **Phase 1: Dataset zu Hugging Face hochladen** (5-10 Minuten)
2.  **Phase 2: Training auf Shadow PC starten** (3-8 Stunden)

---

## ☁️ Phase 1: Dataset zu Hugging Face hochladen

### **Schritt 1: Hugging Face Token erstellen**

1.  **Gehe zu:** https://huggingface.co/settings/tokens
2.  **Klicke:** "New token"
3.  **Name:** `wake-word-training`
4.  **Role:** `write`
5.  **Klicke:** "Generate a token"
6.  **Kopiere den Token!** (Sieht aus wie `hf_...`)

### **Schritt 2: Upload-Skript ausführen**

**Auf deinem normalen PC (wo die Aufnahmen sind):**

1.  **Öffne ein Terminal** im Projektordner (`C:\Users\ModBot\2 Computer-Voice-Assi`)
2.  **Aktiviere die virtuelle Umgebung:** `.\.venv\Scripts\Activate`
3.  **Installiere Hugging Face Hub:** `pip install huggingface_hub`
4.  **Führe das Upload-Skript aus:**

    ```bash
    python upload_to_huggingface.py --token DEIN_HUGGINGFACE_TOKEN --dataset-name DEIN_USERNAME/computer-wake-word
    ```

    **Ersetze:**
    - `DEIN_HUGGINGFACE_TOKEN` mit deinem kopierten Token
    - `DEIN_USERNAME` mit deinem Hugging Face Usernamen

5.  **Warte 5-15 Minuten** bis der Upload fertig ist!

**Ergebnis:** Dein Dataset ist jetzt auf Hugging Face! 🎉

---

## 🎮 Phase 2: Training auf Shadow PC

### **Schritt 1: Aufnahmen auf Shadow PC übertragen**

1.  **Auf deinem normalen PC:** Kopiere den Ordner `wake_word_recordings` in dein **Shadow Drive**.
2.  **Auf deinem Shadow PC:** Der Ordner erscheint automatisch im Shadow Drive.
3.  **Kopiere den Ordner** vom Shadow Drive auf den Desktop (oder wo du ihn haben willst).

### **Schritt 2: Python & Dependencies installieren**

**Auf deinem Shadow PC:**

1.  **Installiere Python 3.8+** (falls nicht vorhanden)
2.  **Installiere TensorFlow mit GPU-Support** (wichtig!):
    - Folge der offiziellen Anleitung: https://www.tensorflow.org/install/gpu
    - (CUDA Toolkit & cuDNN installieren)
3.  **Öffne ein Terminal**
4.  **Installiere die Dependencies:**

    ```bash
    pip install tensorflow librosa soundfile scikit-learn matplotlib tqdm
    ```

### **Schritt 3: Training-Skript starten**

1.  **Kopiere das Skript `train_wake_word_local.py`** auf deinen Shadow PC.
2.  **Öffne ein Terminal** im Ordner, wo das Skript liegt.
3.  **Führe das Training-Skript aus:**

    ```bash
    python train_wake_word_local.py --recordings-dir PFAD_ZU_DEINEN_AUFNAHMEN
    ```

    **Ersetze:**
    - `PFAD_ZU_DEINEN_AUFNAHMEN` mit dem Pfad zum `wake_word_recordings` Ordner (z.B. `C:\Users\Shadow\Desktop\wake_word_recordings`)

4.  **Warte 3-8 Stunden!** ⏳

---

## 💾 Ergebnis

Nach dem Training findest du im Ordner `models`:

- **`computer_wake_word_model.h5`** (Dein fertiges Modell!)
- **`training_history.png`** (Graphen zum Training)

**Dieses Modell kannst du dann in den Voice Assistant einbauen!** 🚀

---

**Seite 1/1**

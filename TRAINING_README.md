# 🎤 Wake-Word Training Scripts

## 📦 Neue Dateien

1. **`upload_to_huggingface.py`** - Upload Dataset zu Hugging Face
2. **`train_wake_word_local.py`** - Training auf Shadow PC
3. **`TRAINING_GUIDE.md`** - Schritt-für-Schritt Anleitung

## 🚀 Quick Start

### 1. Dataset zu Hugging Face hochladen

```bash
pip install huggingface_hub
python upload_to_huggingface.py --token DEIN_TOKEN --dataset-name USERNAME/computer-wake-word
```

### 2. Modell auf Shadow PC trainieren

```bash
pip install tensorflow librosa soundfile scikit-learn matplotlib tqdm
python train_wake_word_local.py --recordings-dir ./wake_word_recordings
```

## 📖 Vollständige Anleitung

Siehe **`TRAINING_GUIDE.md`** für detaillierte Schritt-für-Schritt Anweisungen!

---

**Erstellt: 08.12.2025**

#!/usr/bin/env python3
"""
Hugging Face Dataset Upload Script
===================================

Lädt Wake-Word Aufnahmen als Dataset zu Hugging Face hoch.

Voraussetzungen:
- Hugging Face Account
- Hugging Face Token (von https://huggingface.co/settings/tokens)
- huggingface_hub installiert: pip install huggingface_hub

Usage:
    python upload_to_huggingface.py --token YOUR_HF_TOKEN --dataset-name your-username/computer-wake-word
"""

import os
import argparse
from pathlib import Path
from huggingface_hub import HfApi, create_repo
from tqdm import tqdm


def upload_dataset_to_huggingface(
    recordings_dir: str,
    dataset_name: str,
    token: str,
    private: bool = False
):
    """
    Lädt Wake-Word Aufnahmen zu Hugging Face hoch.
    
    Args:
        recordings_dir: Pfad zum wake_word_recordings Ordner
        dataset_name: Name des Datasets (z.B. "username/computer-wake-word")
        token: Hugging Face Access Token
        private: Ob das Dataset privat sein soll (default: False)
    """
    
    print("=" * 60)
    print("🤗 Hugging Face Dataset Upload")
    print("=" * 60)
    
    # Prüfe ob Ordner existiert
    recordings_path = Path(recordings_dir)
    if not recordings_path.exists():
        raise ValueError(f"❌ Ordner nicht gefunden: {recordings_dir}")
    
    # Prüfe Unterordner
    positive_path = recordings_path / "positive"
    negative_path = recordings_path / "negative"
    background_path = recordings_path / "background_noise"
    
    if not positive_path.exists():
        raise ValueError(f"❌ Ordner nicht gefunden: {positive_path}")
    if not negative_path.exists():
        raise ValueError(f"❌ Ordner nicht gefunden: {negative_path}")
    if not background_path.exists():
        raise ValueError(f"❌ Ordner nicht gefunden: {background_path}")
    
    # Zähle Dateien
    positive_files = list(positive_path.glob("*.wav"))
    negative_files = list(negative_path.glob("*.wav"))
    background_files = list(background_path.glob("*.wav"))
    
    print(f"\n📊 Dataset-Statistiken:")
    print(f"   Positive Samples: {len(positive_files)}")
    print(f"   Negative Samples: {len(negative_files)}")
    print(f"   Background Noise: {len(background_files)}")
    print(f"   Gesamt: {len(positive_files) + len(negative_files) + len(background_files)} Dateien")
    
    # Berechne Größe
    total_size = sum(f.stat().st_size for f in positive_files + negative_files + background_files)
    print(f"   Größe: {total_size / 1024 / 1024:.2f} MB")
    
    # Initialisiere Hugging Face API
    api = HfApi(token=token)
    
    # Erstelle Repository
    print(f"\n📦 Erstelle Repository: {dataset_name}")
    try:
        create_repo(
            repo_id=dataset_name,
            token=token,
            repo_type="dataset",
            private=private,
            exist_ok=True
        )
        print("✅ Repository erstellt!")
    except Exception as e:
        print(f"⚠️  Repository existiert bereits oder Fehler: {e}")
    
    # Erstelle README
    readme_content = f"""---
license: mit
task_categories:
- audio-classification
language:
- de
tags:
- wake-word
- voice-assistant
- audio
size_categories:
- 1K<n<10K
---

# Computer Wake-Word Dataset

Dieses Dataset enthält Aufnahmen für das Training eines "Computer" Wake-Word Modells.

## Dataset-Struktur

```
wake_word_recordings/
├── positive/          # {len(positive_files)} Aufnahmen des Wake-Words "computer"
├── negative/          # {len(negative_files)} Aufnahmen anderer Wörter
└── background_noise/  # {len(background_files)} Hintergrundgeräusche
```

## Statistiken

- **Positive Samples:** {len(positive_files)}
- **Negative Samples:** {len(negative_files)}
- **Background Noise:** {len(background_files)}
- **Gesamt:** {len(positive_files) + len(negative_files) + len(background_files)} Dateien
- **Größe:** {total_size / 1024 / 1024:.2f} MB

## Verwendung

```python
from datasets import load_dataset

dataset = load_dataset("{dataset_name}")
```

## Lizenz

MIT License
"""
    
    readme_path = recordings_path / "README.md"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("\n📝 README.md erstellt!")
    
    # Upload Dateien
    print("\n📤 Lade Dateien hoch...")
    print("   (Das kann 5-15 Minuten dauern)")
    
    try:
        # Upload kompletten Ordner
        api.upload_folder(
            folder_path=str(recordings_path),
            repo_id=dataset_name,
            repo_type="dataset",
            token=token
        )
        
        print("\n✅ Upload erfolgreich!")
        print(f"\n🔗 Dataset URL: https://huggingface.co/datasets/{dataset_name}")
        
    except Exception as e:
        print(f"\n❌ Fehler beim Upload: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(
        description="Lädt Wake-Word Aufnahmen zu Hugging Face hoch"
    )
    parser.add_argument(
        "--recordings-dir",
        type=str,
        default="./wake_word_recordings",
        help="Pfad zum wake_word_recordings Ordner"
    )
    parser.add_argument(
        "--dataset-name",
        type=str,
        required=True,
        help="Name des Datasets (z.B. 'username/computer-wake-word')"
    )
    parser.add_argument(
        "--token",
        type=str,
        required=True,
        help="Hugging Face Access Token"
    )
    parser.add_argument(
        "--private",
        action="store_true",
        help="Dataset als privat markieren"
    )
    
    args = parser.parse_args()
    
    upload_dataset_to_huggingface(
        recordings_dir=args.recordings_dir,
        dataset_name=args.dataset_name,
        token=args.token,
        private=args.private
    )


if __name__ == "__main__":
    main()

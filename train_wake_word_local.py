#!/usr/bin/env python3
"""
OpenWakeWord Local Training Script
===================================

Trainiert ein Wake-Word Modell lokal (z.B. auf Shadow PC).

Voraussetzungen:
- Python 3.8+
- TensorFlow 2.x
- Dependencies: pip install tensorflow librosa soundfile scikit-learn matplotlib tqdm

Usage:
    python train_wake_word_local.py --recordings-dir ./wake_word_recordings --output-dir ./models
"""

import os
import argparse
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from sklearn.model_selection import train_test_split
from tqdm import tqdm
import matplotlib.pyplot as plt

# TensorFlow Import
try:
    import tensorflow as tf
    from tensorflow import keras
    print(f"✅ TensorFlow {tf.__version__} geladen")
    
    # GPU Check
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        print(f"✅ GPU gefunden: {len(gpus)} Device(s)")
        for gpu in gpus:
            print(f"   {gpu}")
    else:
        print("⚠️  Keine GPU gefunden - Training läuft auf CPU (langsamer)")
        
except ImportError:
    print("❌ TensorFlow nicht gefunden!")
    print("   Installiere mit: pip install tensorflow")
    exit(1)


# Parameter
SAMPLE_RATE = 16000
DURATION = 2  # Sekunden
N_MELS = 40
N_FFT = 512
HOP_LENGTH = 160


def load_audio(file_path, duration=2, sr=16000):
    """Lädt Audio-Datei und normalisiert auf feste Länge."""
    try:
        audio, _ = librosa.load(file_path, sr=sr, duration=duration)
        # Pad oder trim auf exakte Länge
        target_length = sr * duration
        if len(audio) < target_length:
            audio = np.pad(audio, (0, target_length - len(audio)))
        else:
            audio = audio[:target_length]
        return audio
    except Exception as e:
        print(f"⚠️  Fehler beim Laden von {file_path}: {e}")
        return None


def extract_melspectrogram(audio, sr=16000, n_mels=40, n_fft=512, hop_length=160):
    """Extrahiert Mel-Spektrogramm aus Audio."""
    mel_spec = librosa.feature.melspectrogram(
        y=audio, sr=sr, n_mels=n_mels, n_fft=n_fft, hop_length=hop_length
    )
    mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
    return mel_spec_db


def create_dataset(positive_path, negative_path, background_path):
    """Erstellt Dataset aus Aufnahmen."""
    X = []
    y = []
    
    # Positive Samples (Label 1)
    print("\n📂 Lade positive Samples...")
    positive_files = list(Path(positive_path).glob("*.wav"))
    for file_path in tqdm(positive_files, desc="Positive"):
        audio = load_audio(str(file_path))
        if audio is not None:
            mel_spec = extract_melspectrogram(audio)
            X.append(mel_spec)
            y.append(1)
    
    # Negative Samples (Label 0)
    print("\n📂 Lade negative Samples...")
    negative_files = list(Path(negative_path).glob("*.wav"))
    for file_path in tqdm(negative_files, desc="Negative"):
        audio = load_audio(str(file_path))
        if audio is not None:
            mel_spec = extract_melspectrogram(audio)
            X.append(mel_spec)
            y.append(0)
    
    # Background Noise (Label 0)
    print("\n📂 Lade background noise...")
    background_files = list(Path(background_path).glob("*.wav"))
    for file_path in tqdm(background_files, desc="Background"):
        audio = load_audio(str(file_path))
        if audio is not None:
            mel_spec = extract_melspectrogram(audio)
            X.append(mel_spec)
            y.append(0)
    
    X = np.array(X)
    y = np.array(y)
    
    print(f"\n✅ Dataset erstellt!")
    print(f"   Shape: {X.shape}")
    print(f"   Positive: {np.sum(y == 1)}")
    print(f"   Negative: {np.sum(y == 0)}")
    
    return X, y


def create_model(input_shape):
    """Erstellt ein CNN-Modell für Wake-Word Detection."""
    model = keras.Sequential([
        keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
        keras.layers.MaxPooling2D((2, 2)),
        keras.layers.Conv2D(64, (3, 3), activation='relu'),
        keras.layers.MaxPooling2D((2, 2)),
        keras.layers.Conv2D(128, (3, 3), activation='relu'),
        keras.layers.GlobalAveragePooling2D(),
        keras.layers.Dense(128, activation='relu'),
        keras.layers.Dropout(0.5),
        keras.layers.Dense(1, activation='sigmoid')
    ])
    
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    return model


def plot_training_history(history, output_dir):
    """Erstellt Plots der Training-History."""
    plt.figure(figsize=(12, 4))
    
    # Accuracy Plot
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'], label='Training')
    plt.plot(history.history['val_accuracy'], label='Validation')
    plt.title('Model Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.grid(True)
    
    # Loss Plot
    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'], label='Training')
    plt.plot(history.history['val_loss'], label='Validation')
    plt.title('Model Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plot_path = Path(output_dir) / "training_history.png"
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"\n📊 Training-Plots gespeichert: {plot_path}")
    plt.close()


def train_wake_word_model(recordings_dir, output_dir, epochs=100, batch_size=32):
    """Hauptfunktion für Training."""
    
    print("=" * 60)
    print("🎤 OpenWakeWord Training")
    print("=" * 60)
    
    # Pfade
    recordings_path = Path(recordings_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    positive_path = recordings_path / "positive"
    negative_path = recordings_path / "negative"
    background_path = recordings_path / "background_noise"
    
    # Prüfe Ordner
    if not positive_path.exists():
        raise ValueError(f"❌ Ordner nicht gefunden: {positive_path}")
    if not negative_path.exists():
        raise ValueError(f"❌ Ordner nicht gefunden: {negative_path}")
    if not background_path.exists():
        raise ValueError(f"❌ Ordner nicht gefunden: {background_path}")
    
    # Dataset erstellen
    X, y = create_dataset(positive_path, negative_path, background_path)
    
    # Reshape für CNN (Samples, Height, Width, Channels)
    X = X[..., np.newaxis]
    
    # Train/Test Split (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\n🔀 Dataset aufgeteilt:")
    print(f"   Training: {X_train.shape[0]} Samples")
    print(f"   Test: {X_test.shape[0]} Samples")
    
    # Modell erstellen
    print("\n🧠 Erstelle Modell...")
    model = create_model(X_train.shape[1:])
    model.summary()
    
    # Callbacks
    early_stopping = keras.callbacks.EarlyStopping(
        monitor='val_loss',
        patience=10,
        restore_best_weights=True,
        verbose=1
    )
    
    reduce_lr = keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=5,
        min_lr=1e-7,
        verbose=1
    )
    
    checkpoint_path = output_path / "best_model.h5"
    model_checkpoint = keras.callbacks.ModelCheckpoint(
        str(checkpoint_path),
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1
    )
    
    # Training starten
    print("\n🚀 Training startet...")
    print(f"   Epochs: {epochs}")
    print(f"   Batch Size: {batch_size}")
    print(f"   GPU: {'Ja' if tf.config.list_physical_devices('GPU') else 'Nein (CPU)'}")
    print()
    
    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=[early_stopping, reduce_lr, model_checkpoint],
        verbose=1
    )
    
    print("\n✅ Training abgeschlossen!")
    
    # Test Accuracy
    test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)
    print(f"\n📊 Test Accuracy: {test_acc*100:.2f}%")
    print(f"📊 Test Loss: {test_loss:.4f}")
    
    # Plots erstellen
    plot_training_history(history, output_path)
    
    # Modell speichern
    final_model_path = output_path / "computer_wake_word_model.h5"
    model.save(str(final_model_path))
    print(f"\n💾 Finales Modell gespeichert: {final_model_path}")
    
    # TensorFlow Lite Konvertierung (für Raspberry Pi / Mobile)
    try:
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        tflite_model = converter.convert()
        
        tflite_path = output_path / "computer_wake_word_model.tflite"
        with open(tflite_path, 'wb') as f:
            f.write(tflite_model)
        
        print(f"💾 TFLite Modell gespeichert: {tflite_path}")
        print(f"   (Für Raspberry Pi / Mobile Geräte)")
    except Exception as e:
        print(f"⚠️  TFLite Konvertierung fehlgeschlagen: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 TRAINING ERFOLGREICH ABGESCHLOSSEN!")
    print("=" * 60)
    print(f"\n📁 Alle Dateien in: {output_path}")
    print(f"   - computer_wake_word_model.h5 (Hauptmodell)")
    print(f"   - best_model.h5 (Bestes Modell während Training)")
    print(f"   - computer_wake_word_model.tflite (TFLite für Mobile)")
    print(f"   - training_history.png (Plots)")


def main():
    parser = argparse.ArgumentParser(
        description="Trainiert ein Wake-Word Modell lokal"
    )
    parser.add_argument(
        "--recordings-dir",
        type=str,
        default="./wake_word_recordings",
        help="Pfad zum wake_word_recordings Ordner"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./models",
        help="Pfad zum Output-Ordner für Modelle"
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=100,
        help="Anzahl der Trainings-Epochen (default: 100)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Batch Size für Training (default: 32)"
    )
    
    args = parser.parse_args()
    
    train_wake_word_model(
        recordings_dir=args.recordings_dir,
        output_dir=args.output_dir,
        epochs=args.epochs,
        batch_size=args.batch_size
    )


if __name__ == "__main__":
    main()

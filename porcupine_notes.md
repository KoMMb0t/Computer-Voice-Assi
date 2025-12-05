# Porcupine Training & Integration Notes

## Requirements
- Python 3.9+ (Projekt hat 3.11 ✅)
- PIP
- Picovoice Account & AccessKey
- Windows x86_64 supported ✅

## Installation
```bash
pip3 install pvporcupine
```

## Training Process (Picovoice Console)
1. Sign up at https://console.picovoice.ai/
2. Navigate to Porcupine page
3. Select language (English for "Computer")
4. Type wake word phrase: "Computer"
5. Test with microphone button
6. Click "Train" button
7. Select platform (Windows)
8. Download .ppn file

## Code Integration
```python
import pvporcupine

# Create instance with custom wake word
porcupine = pvporcupine.create(
    access_key='YOUR_ACCESS_KEY',
    keyword_paths=['path/to/computer.ppn']
)

# Process audio
while True:
    keyword_index = porcupine.process(audio_frame)
    if keyword_index >= 0:
        # Wake word detected!
        print("Computer wake word detected!")
```

## Demo Usage
```bash
# Install demo
pip3 install pvporcupinedemo

# Run with built-in keyword
porcupine_demo_mic --access_key YOUR_KEY --keywords porcupine

# Run with custom keyword
porcupine_demo_mic --access_key YOUR_KEY --keyword_paths path/to/computer.ppn
```

## Key Points
- No data collection needed (transfer learning)
- Training takes seconds
- .ppn file is platform-specific
- AccessKey must be kept secret
- Free tier available for development

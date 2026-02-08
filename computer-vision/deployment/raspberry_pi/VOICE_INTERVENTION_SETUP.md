# Voice Intervention - Installation Guide

## 🔊 Required Libraries

Install these for voice intervention functionality:

```bash
# Navigate to project root
cd /Users/stutithummala/guardian-angel-ugahacks11

# Activate virtual environment
source .venv/bin/activate

# Install voice intervention dependencies
pip install pyttsx3
pip install SpeechRecognition
pip install pyaudio
```

### ⚠️ PyAudio Installation (macOS)

PyAudio might require additional setup on macOS:

```bash
# Install portaudio first via Homebrew
brew install portaudio

# Then install pyaudio
pip install pyaudio
```

If you still have issues:
```bash
pip install --global-option='build_ext' --global-option='-I/opt/homebrew/include' --global-option='-L/opt/homebrew/lib' pyaudio
```

## ✅ Verify Installation

```bash
python -c "import pyttsx3; import speech_recognition; print('Voice libraries installed!')"
```

## 🎯 How It Works

### When a Fall is Detected:

1. **📹 Recording completes** (15 seconds total)
2. **🔊 System speaks**: "A fall was detected. Are you okay? Please speak now if you are able to."
3. **🎤 Listens** for 10 seconds
4. **📝 Transcribes** any speech using Google Speech Recognition
5. **📤 Uploads** to backend with voice response included

### Voice Response Values:

- **Actual speech**: User said something (e.g., "I'm okay", "Help me")
- **"NO_RESPONSE"**: No voice detected within timeout
- **"UNCLEAR"**: Voice detected but couldn't understand
- **"ERROR"**: Technical error during listening

## 🎛️ Configuration

In `fall-detector-with-recording.py`:

```python
# Enable/disable voice intervention
ENABLE_VOICE_INTERVENTION = True

# Adjust timing
VOICE_LISTEN_TIMEOUT = 10  # Seconds to wait for response
VOICE_PHRASE_TIME_LIMIT = 10  # Max recording time
```

## 📊 Backend Integration

The voice response is sent to your backend:

```json
{
  "timestamp": "2026-02-07T21:30:15.123456",
  "confidence": 0.95,
  "clip_path": "fall_20260207_213015.mp4",
  "device_id": "webcam-01",
  "voice_response": "I'm okay"
}
```

## 🧪 Testing

1. **Start the detector**:
   ```bash
   cd computer-vision/deployment/raspberry_pi
   source ../../../.venv/bin/activate
   python fall-detector-with-recording.py --source webcam
   ```

2. **Simulate a fall** and hold the pose

3. **Wait for recording to complete** (15 seconds)

4. **Listen for the voice prompt** from your laptop speakers

5. **Speak into the microphone** when prompted

6. **Check the logs** for:
   ```
   🔊 Speaking: 'A fall was detected. Are you okay?...'
   🎤 Listening for voice response...
   🗣️  Heard: 'I'm okay'
   📤 Including voice response: I'm okay
   ```

## 🔕 Disable Voice Intervention

Set in the Python file:
```python
ENABLE_VOICE_INTERVENTION = False
```

Or the libraries won't be used even if installed.

## 🎤 Privacy Note

Speech-to-text uses Google's Speech Recognition API by default. Audio is sent to Google for processing. For offline/private speech recognition, you can modify the code to use:

- **Sphinx** (offline, less accurate)
- **Whisper** (OpenAI, can run locally)
- **Vosk** (offline, multilingual)

Modify the `listen_for_response()` function to use a different engine.

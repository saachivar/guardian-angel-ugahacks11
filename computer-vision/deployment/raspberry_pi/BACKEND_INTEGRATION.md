# Backend Integration Guide

## Overview
The fall detector now automatically uploads fall events and video recordings to your FastAPI backend.

## Configuration

### 1. Update `.env` file
```bash
cd computer-vision/deployment/raspberry_pi
nano .env
```

Update these values:
```env
# Your FastAPI backend URL
BACKEND_API_URL=http://localhost:8000

# Unique device identifier (e.g., webcam-01, device-01, etc.)
DEVICE_ID=webcam-01
```

### 2. Backend API Endpoints Used

**POST `/events`** - Creates a fall event
```json
{
  "timestamp": "2026-02-07T17:57:30.123456",
  "confidence": 0.95,
  "clip_path": "fall_20260207_175730.mp4",
  "device_id": "webcam-01"
}
```

## How It Works

### When a Fall is Detected:
1. ⚠️ Fall probability exceeds 70%
2. 🔄 System verifies for 8 consecutive frames (~1.6 seconds)
3. 🚨 Fall confirmed
4. 📹 Recording starts (writes 5s pre-fall buffer)
5. ⏱️ Records for 10 more seconds
6. 💾 Saves video to `fall_recordings/fall_YYYYMMDD_HHMMSS.mp4`
7. 📤 **Uploads event data to backend API**
8. ✅ Backend receives:
   - ISO timestamp of fall
   - Confidence score (0.0 - 1.0)
   - Video filename
   - Device ID

## Testing Backend Integration

### 1. Start Your Backend
```bash
cd Backend
# Start your FastAPI server
uvicorn main:app --reload
```

### 2. Start Fall Detector
```bash
cd computer-vision/deployment/raspberry_pi
source ../../../.venv/bin/activate
python fall-detector-with-recording.py --source webcam
```

### 3. Check Logs
Watch for these messages:
- `📹 RECORDING STARTED: fall_20260207_175730.mp4`
- `✅ RECORDING COMPLETE: fall_20260207_175730.mp4`
- `📤 Uploading to backend: http://localhost:8000`
- `✅ Event created on backend: {...}`

### 4. Verify Backend
```bash
# List all events
curl http://localhost:8000/events

# Get specific event
curl http://localhost:8000/events/{event_id}

# Download video
curl http://localhost:8000/clips/fall_20260207_175730.mp4
```

## Logs

All activity is logged to:
- **Terminal**: Real-time output
- **File**: `fall_detection_log.txt`

Example log during fall with backend upload:
```
[2026-02-07 17:57:30] 🚨 FALL CONFIRMED! Timestamp: 2026-02-07T17:57:30.123456, Confidence: 95.32% (verified over 8 frames)
[2026-02-07 17:57:30] 📹 RECORDING STARTED: fall_recordings/fall_20260207_175730.mp4 (will record 10s post-fall)
[2026-02-07 17:57:30] 📼 Wrote 25 buffered frames (5s pre-fall footage)
[2026-02-07 17:57:40] ✅ RECORDING COMPLETE: fall_recordings/fall_20260207_175730.mp4 (15s total: 5s pre + 10s post)
[2026-02-07 17:57:40] 📤 Uploading to backend: http://localhost:8000
[2026-02-07 17:57:40] ✅ Event created on backend: {"id": "...", "timestamp": "..."}
[2026-02-07 17:57:40] 📹 Video ready for retrieval: fall_20260207_175730.mp4
```

## Disable Backend Upload

To run without backend integration:
```python
# In fall-detector-with-recording.py
ENABLE_BACKEND_UPLOAD = False
```

Or comment out in code temporarily.

## Troubleshooting

### Connection Refused
- Check backend is running: `curl http://localhost:8000`
- Verify BACKEND_API_URL in `.env`

### 422 Validation Error
- Check backend expects the correct JSON schema
- Verify timestamp format is ISO 8601

### Upload Timeout
- Default timeout is 30 seconds
- Check network connectivity
- Verify backend can handle the request

## Production Deployment

For production (deployed backend):
```env
# Update .env with your production backend URL
BACKEND_API_URL=https://your-backend-domain.com
DEVICE_ID=webcam-main
```

Make sure your backend is accessible from your laptop's network!

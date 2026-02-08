# Guardian Angel - Data Receiver Service

## Purpose
This is a separate lightweight backend service that receives fall detection data from external sources (Raspberry Pi, sensors, etc.) and forwards it to the main backend which handles Twilio calls and database storage.

## Architecture
```
Raspberry Pi → Receiver Backend (Port 8001) → Main Backend (Port 8000) → Twilio Calls
                                            ↓
                                         MongoDB
```

## Why Separate Services?
- **Separation of concerns**: Receiver handles data ingestion, main backend handles business logic
- **Scalability**: Can add multiple receiver instances for different locations
- **Security**: Can add authentication/validation here before forwarding
- **Flexibility**: Easy to add preprocessing, filtering, or batching

## Setup

### 1. Install Dependencies
```bash
cd /Users/anishakumar/ugahacks2026/receiver-backend
pip3 install -r requirements.txt
```

### 2. Start the Receiver Service
```bash
python3 receiver.py
```

Or with uvicorn:
```bash
uvicorn receiver:app --reload --host 0.0.0.0 --port 8001
```

**The receiver runs on port 8001** (main backend uses 8000)

### 3. Make Sure Main Backend is Running
```bash
# In another terminal
cd /Users/anishakumar/ugahacks2026/backend
python3 -m uvicorn main:app --reload --port 8000
```

## Usage

### From Raspberry Pi or Other Server (WITH VIDEO FILE)

**This is the PRIMARY method - matches your other server's format!**

**Python Example:**
```python
import requests
from datetime import datetime

FLUTTER_SERVER_URL = "http://192.168.1.100:8001/upload"

def send_fall_detection(video_path, device_id, confidence):
    timestamp = datetime.now().isoformat()
    filename = video_path.split('/')[-1]
    
    try:
        with open(video_path, "rb") as f:
            files = {"file": (filename, f, "video/mp4")}
            data = {
                "device_id": device_id,
                "confidence": confidence,
                "timestamp": timestamp
                # auto_call defaults to True
            }
            # POST to Flutter server
            resp = requests.post(FLUTTER_SERVER_URL, files=files, data=data, timeout=10)
            resp.raise_for_status()
            flutter_response = resp.json()
            
            print("✅ Success:", flutter_response)
            return flutter_response
            
    except Exception as e:
        flutter_response = {"error": str(e)}
        print("❌ Error:", flutter_response)
        return flutter_response

# Example usage
send_fall_detection(
    video_path="/path/to/fall_video.mp4",
    device_id="raspberry_pi_kitchen",
    confidence=0.95
)
```

**cURL Example:**
```bash
curl -X POST "http://192.168.1.100:8001/upload" \
  -F "file=@fall_video.mp4" \
  -F "device_id=raspberry_pi_kitchen" \
  -F "confidence=0.95" \
  -F "timestamp=2026-02-08T00:30:00" \
  -F "auto_call=true"
```

### From Raspberry Pi (JSON only, no video)

**Use this if you DON'T have a video file to upload:**

**Python Example:**
```python
import requests

RECEIVER_URL = "http://192.168.1.100:8001/receive-fall-detection"

def report_fall(confidence, video_path, location):
    data = {
        "confidence": confidence,
        "clip_path": video_path,
        "device_id": "raspberry_pi_kitchen",
        "auto_call": True,  # Trigger emergency calls
        "location": location
    }
    
    try:
        response = requests.post(RECEIVER_URL, json=data)
        if response.status_code == 200:
            print("✅ Fall reported successfully!")
            print(response.json())
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Connection failed: {e}")

# Example usage
report_fall(
    confidence=0.95,
    video_path="clips/fall_2026_02_08_14_30.mp4",
    location="Kitchen"
)
```

**cURL Example:**
```bash
curl -X POST "http://192.168.1.100:8001/receive-fall-detection" \
  -H "Content-Type: application/json" \
  -d '{
    "confidence": 0.95,
    "clip_path": "clips/fall_test.mp4",
    "device_id": "raspberry_pi_living_room",
    "auto_call": true,
    "location": "Living Room"
  }'
```

## API Endpoints

### POST /upload (PRIMARY ENDPOINT)
**Receives fall detection with video file upload - matches your other server's format**

This endpoint accepts multipart form data with a video file, exactly matching the format from your other server.

**Request Format (multipart/form-data):**
```python
files = {"file": (filename, file_object, "video/mp4")}
data = {
    "device_id": "raspberry_pi_01",
    "confidence": 0.95,
    "timestamp": "2026-02-08T00:30:00",  # Optional
    "auto_call": True                    # Optional, default: true
}
requests.post(url, files=files, data=data)
```

**Response:**
```json
{
  "status": "success",
  "message": "Fall detection received, video saved, and forwarded to backend",
  "received_at": "2026-02-08T00:30:15.123456",
  "video_saved_to": "/path/to/clips/raspberry_pi_01_2026-02-08.mp4",
  "video_size_bytes": 1234567,
  "backend_response": {
    "status": "success",
    "id": "65c4e5f6g7h8i9j0",
    "emergency_calls": [
      {
        "success": true,
        "contact": "Stuti Thummala",
        "phone": "+14708073876",
        "execution_sid": "FN1234567890"
      }
    ]
  }
}
```

### POST /receive-fall-detection (JSON Only)
Receives fall detection data and forwards to main backend.

**Request Body:**
```json
{
  "confidence": 0.95,
  "clip_path": "clips/fall.mp4",
  "device_id": "raspberry_pi_kitchen",
  "timestamp": "2026-02-08T00:30:00",  // Optional
  "auto_call": true,                    // Optional, default: true
  "location": "Kitchen"                 // Optional
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Fall detection received and forwarded",
  "received_at": "2026-02-08T00:30:15.123456",
  "backend_response": {
    "status": "success",
    "id": "65c4e5f6g7h8i9j0",
    "emergency_calls": [
      {
        "success": true,
        "contact": "Stuti Thummala",
        "phone": "+14708073876"
      }
    ]
  }
}
```

### POST /test
Test endpoint that sends a dummy fall detection (auto_call=false).

```bash
curl -X POST "http://localhost:8001/test"
```

### GET /health
Health check that verifies both receiver and main backend are running.

```bash
curl "http://localhost:8001/health"
```

### GET /
Simple status check.

```bash
curl "http://localhost:8001/"
```

## Testing the Full Flow

### Terminal 1 - Main Backend (with Twilio)
```bash
cd /Users/anishakumar/ugahacks2026/backend
python3 -m uvicorn main:app --reload --port 8000
```

### Terminal 2 - Receiver Backend
```bash
cd /Users/anishakumar/ugahacks2026/receiver-backend
python3 receiver.py
```

### Terminal 3 - Test Upload (Matches Other Server Format)
```bash
cd /Users/anishakumar/ugahacks2026/receiver-backend
python3 test_upload.py
```

This will:
1. Create a test video file
2. Upload it to the receiver (port 8001)
3. Receiver saves the video to `clips/` folder
4. Receiver forwards data to main backend (port 8000)
5. Main backend triggers Twilio calls
6. You'll see detailed logs of the entire process

**Expected output:**
```
🚨 Sending fall detection with video...
   Device ID: raspberry_pi_test
   Confidence: 0.95
   Video file: test_fall_video.mp4

📤 Sending to: http://localhost:8001/upload
✅ SUCCESS!
   Status: success
   Video saved to: /path/to/clips/raspberry_pi_test_2026-02-08.mp4
   
📞 Emergency calls made:
   ✅ Stuti Thummala at +14708073876
   ✅ Saachi Varshney at +14705536461
```

## Configuration

To change the main backend URL, edit `receiver.py`:
```python
# Line 17
MAIN_BACKEND_URL = "http://localhost:8000/events"

# Change to your main backend's address if it's on a different machine
MAIN_BACKEND_URL = "http://192.168.1.50:8000/events"
```

## Logs

The receiver provides detailed logging:
- 📥 Received fall detection data
- 📤 Forwarding to main backend
- ✅ Success messages
- 📞 Emergency call confirmations
- ❌ Error messages

**Example Log Output:**
```
INFO: 📥 Received fall detection from raspberry_pi_kitchen
INFO:    Confidence: 0.95
INFO:    Clip: clips/fall_2026_02_08.mp4
INFO:    Auto-call: True
INFO: 📤 Forwarding to main backend: http://localhost:8000/events
INFO: ✅ Successfully forwarded to main backend
INFO: 📞 Called Stuti Thummala at +14708073876
INFO: 📞 Called Saachi Varshney at +14705536461
```

## Troubleshooting

**Error: "Main backend is not available"**
- Make sure the main backend is running on port 8000
- Check: `curl http://localhost:8000/`

**Error: "Connection refused"**
- Verify receiver is running: `lsof -i :8001`
- Check firewall settings
- Use `--host 0.0.0.0` to accept external connections

**No Twilio calls being made**
- Check main backend has `.env` file with credentials
- Verify `auto_call: true` in request
- Check main backend logs for Twilio errors

## Production Deployment

For production, add:
1. **Authentication**: Verify requests are from trusted sources
2. **Rate limiting**: Prevent spam/abuse
3. **HTTPS**: Use SSL certificates
4. **Monitoring**: Add health checks and alerts
5. **Load balancing**: Multiple receiver instances

## Network Setup

**Same Machine (Development):**
- Main Backend: `http://localhost:8000`
- Receiver: `http://localhost:8001`

**Different Machines (Production):**
- Main Backend: `http://192.168.1.50:8000`
- Receiver: `http://192.168.1.51:8001`
- Update `MAIN_BACKEND_URL` in receiver.py

---

**Your receiver backend is ready to accept fall detection data from any source! 🚀**

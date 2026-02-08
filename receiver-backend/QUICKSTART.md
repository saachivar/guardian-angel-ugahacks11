# 🚀 QUICK START - Receiver Backend

## What This Does
Receives fall detection data WITH VIDEO from your other server (Raspberry Pi) and forwards it to the main backend which triggers Twilio emergency calls.

## Setup (One-Time)

```bash
cd /Users/anishakumar/ugahacks2026/receiver-backend
pip3 install -r requirements.txt
```

## Running It

### Step 1: Start Main Backend (Terminal 1)
```bash
cd /Users/anishakumar/ugahacks2026/backend
python3 -m uvicorn main:app --reload --port 8000
```

### Step 2: Start Receiver Backend (Terminal 2)
```bash
cd /Users/anishakumar/ugahacks2026/receiver-backend
python3 receiver.py
```

## Your Other Server's Code

**Your other server should POST to:** `http://YOUR_IP:8001/upload`

**Their exact code will work:**
```python
FLUTTER_SERVER_URL = "http://192.168.1.100:8001/upload"

with open(path, "rb") as f:
    files = {"file": (filename, f, "video/mp4")}
    data = {
        "device_id": device_id,
        "confidence": confidence,
        "timestamp": timestamp
    }
    resp = requests.post(FLUTTER_SERVER_URL, files=files, data=data, timeout=10)
    resp.raise_for_status()
    flutter_response = resp.json()
```

## Testing

```bash
# Test that it works
python3 test_upload.py
```

## What Happens

1. ✅ Other server uploads video to receiver (port 8001)
2. ✅ Receiver saves video to `clips/` folder
3. ✅ Receiver forwards to main backend (port 8000)
4. ✅ Main backend triggers Twilio calls to Stuti & Saachi
5. ✅ Response sent back with call status

## Find Your IP Address

```bash
# On Mac
ipconfig getifaddr en0

# Example: 192.168.1.100
```

Then tell your other server to use: `http://192.168.1.100:8001/upload`

## Troubleshooting

**"Connection refused"**
- Make sure receiver is running on port 8001
- Check: `lsof -i :8001`

**"Main backend not available"**
- Make sure main backend is running on port 8000
- Check: `curl http://localhost:8000/`

**"No Twilio calls"**
- Check main backend has `.env` file with credentials
- Check receiver logs show "Emergency calls made"

## Logs

You'll see detailed logs like:
```
📥 NEW FALL DETECTION RECEIVED
   Device: raspberry_pi_kitchen
   Confidence: 0.95
   Video file: fall_2026_02_08.mp4
💾 Saving video to: clips/raspberry_pi_kitchen_2026-02-08.mp4
✅ Video saved successfully
📤 Forwarding to main backend
✅ Successfully forwarded
📞 EMERGENCY CALLS INITIATED:
   ✅ Called Stuti Thummala at +14708073876
   ✅ Called Saachi Varshney at +14705536461
```

## Files

- `receiver.py` - Main receiver service
- `test_upload.py` - Test script
- `clips/` - Uploaded videos saved here
- `README.md` - Full documentation

---

**That's it! Your receiver is ready to accept data from the other server! 🎉**

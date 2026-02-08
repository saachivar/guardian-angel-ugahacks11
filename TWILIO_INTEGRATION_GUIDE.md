# 🚨 TWILIO AUTO-CALL INTEGRATION - QUICK START

## ✅ SETUP COMPLETE - Here's What You Have:

### 1. **Your Credentials are Safe** 📁
- Real credentials are in `/backend/.env` (NOT in Git)
- This file stays on your local machine only
- Backend automatically loads them when it starts

### 2. **How It Works** 🔄

#### A. SIMULATED FALL (Current Demo Version):
```dart
// In Flutter app (main.dart), when you click "Simulate Fall Detection":
void _simulateFallDetection() {
  setState(() {
    _hasActiveAlert = true;
    _liveStatus = 'Fall Detected';
  });
  _pulseController.repeat();
  HapticFeedback.heavyImpact();
  
  // TODO: Add HTTP call to backend here
  _triggerBackendCall();
}
```

#### B. BACKEND RECEIVES FALL + AUTO-CALLS:
```python
# Backend (main.py) - POST /events with auto_call=true
@app.post("/events")
def create_event(event: dict):
    # When auto_call is True:
    if event.get("auto_call", False):
        # Calls Stuti (Primary)
        make_emergency_call("+14708073876", "Stuti Thummala")
        # Calls Saachi (Secondary)
        make_emergency_call("+14705536461", "Saachi Varshney")
```

### 3. **What You Need to Add** 🛠️

Add this import to your Flutter `main.dart`:
```dart
import 'package:http/http.dart' as http;
import 'dart:convert';
```

Add this method to `_LiveAlertsHomeState` class:
```dart
Future<void> _triggerBackendCall() async {
  try {
    final response = await http.post(
      Uri.parse('http://localhost:8000/events'),  // Change to your Mac's IP for iPhone
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'confidence': 0.95,
        'clip_path': 'clips/simulated_fall.mp4',
        'device_id': 'mobile_app',
        'auto_call': true,  // 🚨 This triggers the Twilio calls!
      }),
    );
    
    if (response.statusCode == 200) {
      print('✅ Backend notified - Emergency calls initiated!');
    }
  } catch (e) {
    print('❌ Failed to reach backend: $e');
  }
}
```

Then update `_simulateFallDetection()`:
```dart
void _simulateFallDetection() {
  if (mounted) {
    setState(() {
      _hasActiveAlert = true;
      _liveStatus = 'Fall Detected';
      _lastActivity = 'Kitchen - Just now';
    });
    _pulseController.repeat();
    HapticFeedback.heavyImpact();
    
    // 🔥 NEW: Call backend to trigger Twilio
    _triggerBackendCall();
  }
}
```

### 4. **Running the Full Demo** 🎬

**Terminal 1 - Start Backend:**
```bash
cd /Users/anishakumar/ugahacks2026/backend
python3 -m uvicorn main:app --reload --port 8000
```

**Terminal 2 - Run Flutter App:**
```bash
cd /Users/anishakumar/ugahacks2026/frontend
flutter run -d 00008140-000819110CBB801C  # Your iPhone
```

**iPhone - Test the Flow:**
1. Login (hairydawg / goDawgs!)
2. Click "Simulate Fall Detection" button (if you add it to UI)
3. OR wait for real fall from Raspberry Pi

**What Happens:**
1. ✅ App shows red emergency alert
2. ✅ Backend receives POST /events with auto_call=true
3. ✅ Twilio automatically calls Stuti (+1 470-807-3876)
4. ✅ Twilio automatically calls Saachi (+1 470-553-6461)
5. ✅ They hear: "Anisha Dhawan has fallen down. Please check your Guardian Angel app."

### 5. **For Final Version (Raspberry Pi Integration)** 🍓

Your Raspberry Pi fall detector should POST to the backend:
```python
# On Raspberry Pi
import requests

def on_fall_detected(confidence, video_clip_path):
    response = requests.post(
        'http://YOUR_BACKEND_IP:8000/events',
        json={
            'confidence': confidence,
            'clip_path': video_clip_path,
            'device_id': 'raspberry_pi_kitchen',
            'auto_call': True  # Auto-trigger calls
        }
    )
```

### 6. **Testing Twilio Calls Manually** ☎️

```bash
# Test primary contact (Stuti)
curl -X POST "http://localhost:8000/test-call?contact=primary"

# Test secondary contact (Saachi)  
curl -X POST "http://localhost:8000/test-call?contact=secondary"

# Test both
curl -X POST "http://localhost:8000/test-call?contact=both"
```

### 7. **What's in Your Files** 📂

- ✅ `/backend/.env` - Your real Twilio credentials (LOCAL ONLY)
- ✅ `/backend/.env.example` - Template for others
- ✅ `/backend/main.py` - FastAPI backend with Twilio integration
- ✅ `/backend/CREDENTIALS_README.md` - This guide
- ✅ `/backend/TWILIO_SETUP.md` - Detailed Twilio docs
- ✅ `/frontend/lib/main.dart` - Flutter app ready for integration

### 8. **Next Steps** ✨

1. Add `http` package to `pubspec.yaml`:
   ```yaml
   dependencies:
     http: ^1.1.0
   ```

2. Run `flutter pub get`

3. Add the `_triggerBackendCall()` method shown above

4. Test the complete flow!

---

**🎉 You're all set! The backend will automatically call Stuti and Saachi whenever a fall is detected with `auto_call: true`!**

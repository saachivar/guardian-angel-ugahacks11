# 🚨 Guardian Angel - Twilio Emergency Calling Implementation

## ✅ **What's Been Implemented**

Your backend now has **automatic emergency calling** using Twilio Studio Flow! When a fall is detected, it will:
1. Call **Stuti Thummala** (Primary Contact) at `+1 (706) 555-0199`
2. Call **Saachi Varshney** (Secondary Contact) at `+1 (678) 555-0156`  
3. Play automated message: *"Anisha Dhawan has fallen down. Please check your Guardian Angel app."*

---

## 📋 **Configuration Details**

### **Twilio Credentials (Use Environment Variables)**
```python
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = "+18442398571"  # Your Twilio number
TWILIO_FLOW_SID = os.getenv("TWILIO_FLOW_SID")  # Your Studio Flow
```

### **Contact Information**
```python
PRIMARY_CONTACT = {
    "name": "Stuti Thummala",
    "phone": "+17065550199"
}
SECONDARY_CONTACT = {
    "name": "Saachi Varshney", 
    "phone": "+16785550156"
}
PATIENT_NAME = "Anisha Dhawan"
```

---

## 🔌 **API Endpoints**

### **1. Create Fall Event with Auto-Calling**
```bash
POST http://localhost:8000/events
Content-Type: application/json

{
    "timestamp": "2026-02-07T20:00:00",
    "confidence": 0.95,
    "clip_path": "clips/fall1.mp4",
    "device_id": "pi01",
    "auto_call": true  ⬅️ SET THIS TO TRUE TO TRIGGER CALLS
}
```

**Response:**
```json
{
    "status": "success",
    "id": "65c4e5f6g7h8i9j0",
    "event": { ... },
    "emergency_calls": [
        {
            "success": true,
            "execution_sid": "FN1234567890...",
            "contact": "Stuti Thummala",
            "phone": "+17065550199"
        },
        {
            "success": true,
            "execution_sid": "FN0987654321...",
            "contact": "Saachi Varshney",
            "phone": "+16785550156"
        }
    ]
}
```

### **2. Test Emergency Calling (Manual)**
```bash
# Test primary contact only
POST http://localhost:8000/test-call?contact=primary

# Test secondary contact only
POST http://localhost:8000/test-call?contact=secondary

# Test both contacts
POST http://localhost:8000/test-call?contact=both
```

---

## 🧪 **How to Test**

### **Option 1: Using the Test Script**
```bash
cd /Users/anishakumar/ugahacks2026/backend
python3 test_twilio.py
```

This interactive script will:
- Check if backend is running
- Test individual contacts
- Test full fall event with auto-calling

### **Option 2: Using curl**
```bash
# Test just primary contact
curl -X POST "http://localhost:8000/test-call?contact=primary"

# Create a fall event with auto-calling
curl -X POST "http://localhost:8000/events" \
  -H "Content-Type: application/json" \
  -d '{
    "confidence": 0.95,
    "clip_path": "clips/demo.mp4",
    "device_id": "pi01",
    "auto_call": true
  }'
```

### **Option 3: From Flutter App**
Add this to your Flutter app when fall is detected:

```dart
Future<void> reportFallWithCalling() async {
  final response = await http.post(
    Uri.parse('http://YOUR_IP:8000/events'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({
      'confidence': 0.95,
      'clip_path': 'clips/fall.mp4',
      'device_id': 'mobile_app',
      'auto_call': true,  // ⬅️ Triggers emergency calls!
    }),
  );
  
  if (response.statusCode == 200) {
    print('Fall reported and emergency calls initiated!');
  }
}
```

---

## 🎤 **Twilio Studio Flow Setup**

Your Twilio Studio Flow (`FW71009c7b10b67b3b164e81543a9c0b5c`) should be configured to:

1. **Answer the call**
2. **Play TTS message**: "Anisha Dhawan has fallen down. Please check your Guardian Angel app."
3. **Optionally**: Add menu options like "Press 1 to confirm, Press 2 for false alarm"

**To edit your flow:**
1. Go to: https://console.twilio.com/us1/develop/studio/flows/FW71009c7b10b67b3b164e81543a9c0b5c
2. Drag a "Say/Play" widget
3. Set text to: `{{flow.data.patient_name | default: "Anisha Dhawan"}} has fallen down. Please check your Guardian Angel app.`
4. Publish the flow

---

## 🚀 **Running the Backend**

```bash
# Navigate to backend directory
cd /Users/anishakumar/ugahacks2026/backend

# Start the server
PYTHONPATH=/Users/anishakumar/ugahacks2026/backend python3 -m uvicorn main:app --reload --port 8000
```

**Backend will be available at:**
- Local: http://127.0.0.1:8000
- Network: http://YOUR_IP:8000
- API Docs: http://127.0.0.1:8000/docs (Swagger UI)

---

## 📱 **Integration with Raspberry Pi**

Update your Raspberry Pi fall detector to call the backend with `auto_call: true`:

```python
# In fall-detector.py
import requests

def report_fall(confidence):
    url = "http://YOUR_BACKEND_IP:8000/events"
    data = {
        "confidence": confidence,
        "clip_path": f"clips/fall_{timestamp}.mp4",
        "device_id": "raspberry_pi_01",
        "auto_call": True  # ⬅️ Automatically call caregivers!
    }
    
    response = requests.post(url, json=data)
    if response.status_code == 200:
        print("✅ Fall reported and emergency calls initiated!")
        print(response.json())
```

---

## 🔧 **Customization Options**

### **Change Phone Numbers**
Edit in `/Users/anishakumar/ugahacks2026/backend/main.py`:
```python
PRIMARY_CONTACT = {
    "name": "Your Name",
    "phone": "+1XXXXXXXXXX"
}
```

### **Change TTS Message**
Edit your Twilio Studio Flow to customize the message.

### **Add More Contacts**
Add a `TERTIARY_CONTACT` and call it in the `make_emergency_call()` function.

### **Add Delay Between Calls**
```python
import time

# In create_event() function
primary_result = make_emergency_call(PRIMARY_CONTACT["phone"], PRIMARY_CONTACT["name"])
time.sleep(5)  # Wait 5 seconds
secondary_result = make_emergency_call(SECONDARY_CONTACT["phone"], SECONDARY_CONTACT["name"])
```

---

## 📊 **Monitoring**

### **Check Twilio Call Logs**
https://console.twilio.com/us1/monitor/logs/calls

### **Check Backend Logs**
Look for these messages in terminal:
```
✅ Emergency call initiated to Stuti Thummala (+17065550199): FN1234567890...
✅ Emergency call initiated to Saachi Varshney (+16785550156): FN0987654321...
```

### **Error Handling**
If a call fails, you'll see:
```
❌ Failed to call Stuti Thummala: [Error message]
```

---

## 🎯 **Demo Flow for Hackathon**

1. **Show monitoring state** - App displays "All Clear"
2. **Simulate fall** - Use demo controls or Raspberry Pi
3. **Backend receives fall event** - With `auto_call: true`
4. **Automatic calls initiated** - Twilio calls both contacts
5. **Show app notification** - Flutter displays alert
6. **Demonstrate call** - Show phone ringing with TTS message
7. **Mark as resolved** - Close the incident

---

## 🐛 **Troubleshooting**

### **Issue: No calls being made**
- Check backend logs for errors
- Verify Twilio credentials are correct
- Check Twilio account balance (trial accounts need credit)
- Verify phone numbers are in E.164 format (`+1XXXXXXXXXX`)

### **Issue: Backend not starting**
```bash
# Install dependencies
pip3 install -r requirements.txt

# Check for port conflicts
lsof -ti:8000 | xargs kill -9

# Restart backend
PYTHONPATH=/Users/anishakumar/ugahacks2026/backend python3 -m uvicorn main:app --reload --port 8000
```

### **Issue: Calls go to voicemail**
- This is expected for demo purposes
- Twilio will leave the message on voicemail

---

## 🎓 **What You Need from Twilio Website**

✅ **Already Have:**
- Account SID
- Auth Token  
- Twilio Phone Number (`+18442398571`)
- Studio Flow SID (`FW71009c7b10b67b3b164e81543a9c0b5c`)

❓ **Might Need to Configure:**
- **Studio Flow TTS Message**: Make sure it says "Anisha Dhawan has fallen down..."
- **Verify Phone Numbers**: If using trial account, verify the caregiver phone numbers

**To verify numbers (Trial accounts only):**
1. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/verified
2. Add `+17065550199` and `+16785550156`
3. Twilio will send verification codes

---

## ✨ **Next Steps**

1. ✅ **Backend is ready** - Twilio integration complete
2. 🔄 **Test the system** - Run `python3 test_twilio.py`
3. 📱 **Integrate with Flutter** - Add API calls when fall detected
4. 🎥 **Connect Raspberry Pi** - Update fall detector to POST to backend
5. 🎤 **Verify Studio Flow** - Make sure TTS message is correct
6. 🎯 **Practice demo flow** - End-to-end fall detection → call

---

**Your backend is now LIVE and ready to make emergency calls! 🚨📞**

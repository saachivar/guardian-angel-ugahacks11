"""
Test script that matches the EXACT format from the other server
This simulates how the Raspberry Pi / other server will send data
"""

import requests
import os
from datetime import datetime

# UPDATE THIS: Your receiver backend's IP address and port
FLUTTER_SERVER_URL = "http://localhost:8001/upload"

def send_fall_with_video(video_path, device_id, confidence):
    """
    Send fall detection with video file - EXACT format from other server
    
    This matches their code:
        files = {"file": (filename, f, "video/mp4")}
        data = {"device_id": device_id, "confidence": confidence, "timestamp": timestamp}
        resp = requests.post(FLUTTER_SERVER_URL, files=files, data=data, timeout=10)
    """
    
    timestamp = datetime.now().isoformat()
    filename = os.path.basename(video_path)
    
    print("🚨 Sending fall detection with video...")
    print(f"   Device ID: {device_id}")
    print(f"   Confidence: {confidence}")
    print(f"   Timestamp: {timestamp}")
    print(f"   Video file: {filename}")
    print()
    
    try:
        with open(video_path, "rb") as f:
            files = {"file": (filename, f, "video/mp4")}
            data = {
                "device_id": device_id,
                "confidence": confidence,
                "timestamp": timestamp,
                "auto_call": True  # Optional - defaults to True anyway
            }
            
            # POST to Flutter server (receiver backend)
            print(f"📤 Sending to: {FLUTTER_SERVER_URL}")
            resp = requests.post(FLUTTER_SERVER_URL, files=files, data=data, timeout=10)
            resp.raise_for_status()
            flutter_response = resp.json()
            
            print("✅ SUCCESS!")
            print(f"   Status: {flutter_response.get('status')}")
            print(f"   Message: {flutter_response.get('message')}")
            print(f"   Video saved to: {flutter_response.get('video_saved_to')}")
            print(f"   Video size: {flutter_response.get('video_size_bytes')} bytes")
            
            # Check if emergency calls were made
            backend_resp = flutter_response.get('backend_response', {})
            calls = backend_resp.get('emergency_calls', [])
            
            if calls:
                print()
                print("📞 Emergency calls made:")
                for call in calls:
                    if call.get('success'):
                        print(f"   ✅ {call['contact']} at {call['phone']}")
                    else:
                        print(f"   ❌ Failed: {call['contact']}")
            
            return flutter_response
            
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error {e.response.status_code}")
        print(f"   {e.response.text}")
        flutter_response = {"error": str(e)}
        return flutter_response
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        flutter_response = {"error": str(e)}
        return flutter_response

def create_test_video():
    """Create a small test video file if needed"""
    test_video_path = "test_fall_video.mp4"
    
    if not os.path.exists(test_video_path):
        print("📹 Creating test video file...")
        # Create a minimal valid MP4 file (just for testing)
        with open(test_video_path, "wb") as f:
            # This is a minimal MP4 header - just for testing
            f.write(b'\x00\x00\x00\x20ftypisom\x00\x00\x02\x00')
            f.write(b'isomiso2mp41\x00\x00\x00\x08free')
            f.write(b'\x00' * 100)  # Some data
        print(f"✅ Created {test_video_path}")
    
    return test_video_path

if __name__ == "__main__":
    print("=" * 60)
    print("Guardian Angel - Test Upload (Matches Other Server Format)")
    print("=" * 60)
    print()
    
    # Create or use test video
    video_path = create_test_video()
    
    # Test sending
    result = send_fall_with_video(
        video_path=video_path,
        device_id="raspberry_pi_test",
        confidence=0.95
    )
    
    print()
    print("=" * 60)
    if result.get("status") == "success":
        print("🎉 Test completed successfully!")
    elif "error" in result:
        print("⚠️  Test failed - check errors above")
        print()
        print("Make sure:")
        print("1. Receiver backend is running: python3 receiver.py")
        print("2. Main backend is running on port 8000")
        print(f"3. URL is correct: {FLUTTER_SERVER_URL}")
    print("=" * 60)

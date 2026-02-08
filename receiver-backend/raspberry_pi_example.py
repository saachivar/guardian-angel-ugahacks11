"""
Example: How to send fall detection data from Raspberry Pi to the receiver backend
"""

import requests
import time
from datetime import datetime

# UPDATE THIS: Your receiver backend's IP address
RECEIVER_URL = "http://192.168.1.100:8001/receive-fall-detection"

def send_fall_detection(confidence, video_path, location="Unknown"):
    """
    Send fall detection data to the receiver backend
    
    Args:
        confidence (float): Detection confidence (0.0 to 1.0)
        video_path (str): Path to the video clip
        location (str): Location where fall was detected
    """
    
    data = {
        "confidence": confidence,
        "clip_path": video_path,
        "device_id": "raspberry_pi_01",  # Change this for each device
        "timestamp": datetime.now().isoformat(),
        "auto_call": True,  # Set to False for testing without calls
        "location": location
    }
    
    print(f"🚨 Sending fall detection...")
    print(f"   Confidence: {confidence}")
    print(f"   Location: {location}")
    print(f"   Video: {video_path}")
    
    try:
        response = requests.post(RECEIVER_URL, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"   Status: {result['status']}")
            
            # Check if emergency calls were made
            backend_resp = result.get('backend_response', {})
            calls = backend_resp.get('emergency_calls', [])
            
            if calls:
                print("📞 Emergency calls:")
                for call in calls:
                    if call.get('success'):
                        print(f"   ✅ Called {call['contact']} at {call['phone']}")
                    else:
                        print(f"   ❌ Failed to call {call['contact']}")
            
            return True
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to receiver backend!")
        print(f"   Is it running at {RECEIVER_URL}?")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timeout!")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_connection():
    """Test if receiver backend is reachable"""
    try:
        response = requests.get(RECEIVER_URL.replace('/receive-fall-detection', '/health'), timeout=5)
        if response.status_code == 200:
            health = response.json()
            print("✅ Receiver backend is online!")
            print(f"   Receiver: {health['receiver_status']}")
            print(f"   Main Backend: {health['main_backend_status']}")
            return True
        else:
            print(f"⚠️  Receiver responded with {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot reach receiver: {e}")
        return False

# Example usage
if __name__ == "__main__":
    print("=" * 50)
    print("Guardian Angel - Raspberry Pi Test Script")
    print("=" * 50)
    print()
    
    # Test connection first
    print("1. Testing connection...")
    if test_connection():
        print()
        print("2. Sending test fall detection...")
        time.sleep(1)
        
        # Send a test fall detection
        success = send_fall_detection(
            confidence=0.95,
            video_path="clips/test_fall_2026_02_08.mp4",
            location="Kitchen"
        )
        
        if success:
            print()
            print("🎉 Test completed successfully!")
        else:
            print()
            print("⚠️  Test failed - check the errors above")
    else:
        print()
        print("❌ Connection test failed!")
        print("   Make sure:")
        print("   1. Receiver backend is running on port 8001")
        print("   2. Main backend is running on port 8000")
        print("   3. IP address in RECEIVER_URL is correct")

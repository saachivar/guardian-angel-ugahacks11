#!/usr/bin/env python3
"""Quick test to check if camera is available."""

import cv2
import sys

def test_camera(index=0):
    """Test if camera at given index works and show details."""
    print(f"\n{'='*60}")
    print(f"Camera Index: {index}")
    print('='*60)
    
    cap = cv2.VideoCapture(index)
    
    if not cap.isOpened():
        print(f"❌ Not available\n")
        return False
    
    # Get camera properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    backend = cap.getBackendName()
    
    # Try to read a frame
    ret, frame = cap.read()
    cap.release()
    
    if not ret or frame is None:
        print(f"❌ Opened but cannot read frames\n")
        return False
    
    actual_h, actual_w = frame.shape[:2]
    
    print(f"✅ Status: Working")
    print(f"📐 Resolution: {actual_w}×{actual_h}")
    print(f"🎥 FPS: {fps}")
    print(f"🔧 Backend: {backend}")
    print(f"💡 Type: ", end="")
    
    # Try to guess camera type based on resolution
    if actual_w == 1920 and actual_h == 1080:
        print("HD (1080p) - Likely external webcam or iPhone Continuity")
    elif actual_w == 1280 and actual_h == 720:
        print("HD (720p) - Standard webcam")
    elif actual_w == 640 and actual_h == 480:
        print("VGA - Basic webcam")
    else:
        print(f"Custom")
    
    return True

def find_all_cameras(max_index=5):
    """Find all available cameras."""
    print("\n🔍 Scanning for available cameras...")
    print("(This helps identify which index is your Logitech camera)\n")
    
    available = []
    
    for i in range(max_index):
        if test_camera(i):
            available.append(i)
    
    print("\n" + "="*60)
    if available:
        print(f"✅ FOUND {len(available)} CAMERA(S): {available}")
        print("="*60)
        print("\n📝 To use a specific camera:")
        print(f"   python fall-detector.py --source webcam")
        print("\n   Then edit CAMERA_INDEX in fall-detector.py to change camera")
        print(f"\n💡 TIP: Logitech cameras usually show as 1080p external webcams")
        print("   Built-in Mac cameras are typically index 0")
        print("   iPhone Continuity Camera also shows at 1080p")
    else:
        print("❌ NO CAMERAS FOUND")
        print("="*60)
        print("\nTroubleshooting:")
        print("1. Check if camera is connected via USB")
        print("2. Grant camera permissions: System Settings > Privacy & Security")
        print("3. Try: sudo killall VDCAssistant")
    
    return available

if __name__ == "__main__":
    cameras = find_all_cameras()
    sys.exit(0 if cameras else 1)

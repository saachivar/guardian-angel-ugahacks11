#!/usr/bin/env python3
"""Preview each camera to identify your Logitech."""

import cv2
import sys

def preview_camera(index):
    """Show live preview of camera."""
    print(f"\n{'='*60}")
    print(f"📹 PREVIEWING CAMERA {index}")
    print(f"{'='*60}")
    print("Press 'q' to close preview and try next camera")
    print("Press ESC to exit completely\n")
    
    cap = cv2.VideoCapture(index)
    
    if not cap.isOpened():
        print(f"❌ Camera {index} not available\n")
        return False
    
    # Set lower resolution for preview
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    window_name = f"Camera {index} Preview - Press 'q' for next, ESC to exit"
    cv2.namedWindow(window_name)
    
    print(f"✅ Showing Camera {index}...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame")
            break
        
        # Add text overlay
        cv2.putText(frame, f"CAMERA INDEX: {index}", (10, 30), 
                   cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, "Press 'q' for next camera", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        cv2.imshow(window_name, frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print(f"Moving to next camera...\n")
            break
        elif key == 27:  # ESC
            print(f"Exiting...\n")
            cap.release()
            cv2.destroyAllWindows()
            return False
    
    cap.release()
    cv2.destroyAllWindows()
    return True

def main():
    """Preview all available cameras."""
    print("\n🎥 LOGITECH CAMERA IDENTIFIER")
    print("="*60)
    print("This will show you a live preview of each camera.")
    print("Look at the video to identify which one is your Logitech.\n")
    
    cameras = [0, 1, 2]  # Known available cameras
    
    for cam_idx in cameras:
        if not preview_camera(cam_idx):
            break
    
    print("\n" + "="*60)
    print("📝 RESULT:")
    print("="*60)
    camera_choice = input("\nWhich camera index is your Logitech? (0, 1, or 2): ")
    
    try:
        chosen = int(camera_choice)
        if chosen in cameras:
            print(f"\n✅ Great! Your Logitech is Camera {chosen}")
            print(f"\n📝 To use it for fall detection:")
            print(f"   Edit fall-detector.py and change:")
            print(f"   CAMERA_INDEX = {chosen}")
            print(f"\n   Or run: python fall-detector.py --source webcam")
            print(f"   (then edit the CAMERA_INDEX variable in the script)")
        else:
            print(f"❌ Invalid camera index: {chosen}")
    except ValueError:
        print("❌ Invalid input")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled by user")
        cv2.destroyAllWindows()

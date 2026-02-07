#!/usr/bin/env python3
"""
Simple pose detection test - shows if MediaPipe can see a person.
"""

import cv2
from mediapipe.tasks.python.vision import PoseLandmarker, PoseLandmarkerOptions, RunningMode
from mediapipe.tasks.python.core.base_options import BaseOptions
from mediapipe import Image
from mediapipe.tasks.python.vision.core import image as mp_image_core

print("\n" + "="*70)
print("🔍 POSE DETECTION TEST")
print("="*70)
print("This will show if MediaPipe can detect a person.\n")

# Load pose detector
base_options = BaseOptions(model_asset_path='pose_landmarker_lite.task')
options = PoseLandmarkerOptions(
    base_options=base_options,
    running_mode=RunningMode.IMAGE,
    min_pose_detection_confidence=0.5,
    min_pose_presence_confidence=0.5,
    min_tracking_confidence=0.5
)
landmarker = PoseLandmarker.create_from_options(options)

# Open camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Cannot open camera")
    exit(1)

print("✅ Camera opened")
print("\n📹 Showing camera feed...")
print("Watch the TERMINAL for detection status")
print("Press 'q' to quit\n")

frame_count = 0
detections = 0

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Convert to RGB
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = Image(image_format=mp_image_core.ImageFormat.SRGB, data=rgb)
        
        # Detect pose
        result = landmarker.detect(mp_image)
        
        # Check detection
        person_detected = False
        num_landmarks = 0
        
        if hasattr(result, 'pose_landmarks') and result.pose_landmarks:
            if len(result.pose_landmarks) > 0:
                person_detected = True
                detections += 1
                landmarks = result.pose_landmarks[0]
                num_landmarks = len(landmarks)
        
        # Print every 30 frames
        if frame_count % 30 == 0:
            rate = (detections / frame_count) * 100
            status = "✅ DETECTED" if person_detected else "❌ NOT DETECTED"
            print(f"Frame {frame_count}: {status} | Rate: {rate:.1f}% | Landmarks: {num_landmarks}")
        
        # Draw on frame
        display = frame.copy()
        
        # Big status overlay
        if person_detected:
            # Draw skeleton
            h, w = display.shape[:2]
            for lm in landmarks:
                cx = int(lm.x * w)
                cy = int(lm.y * h)
                cv2.circle(display, (cx, cy), 5, (0, 255, 0), -1)
            
            cv2.putText(display, "PERSON DETECTED!", (50, 80),
                       cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 255, 0), 3)
        else:
            cv2.putText(display, "NO PERSON DETECTED", (50, 80),
                       cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 0, 255), 3)
            cv2.putText(display, "Move closer or improve lighting", (50, 130),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        cv2.putText(display, f"Landmarks: {num_landmarks}", (50, 180),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        cv2.imshow("Pose Detection Test (Press 'q' to quit)", display)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("\n👋 Interrupted")
finally:
    landmarker.close()
    cap.release()
    cv2.destroyAllWindows()
    
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    print(f"Total frames: {frame_count}")
    print(f"Detections: {detections}")
    if frame_count > 0:
        print(f"Detection rate: {(detections/frame_count)*100:.1f}%")
    print("\n💡 For fall detection to work, detection rate should be > 80%")
    print("="*70 + "\n")

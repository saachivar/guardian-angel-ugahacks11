#!/usr/bin/env python3
"""
Debug version of fall detector with verbose terminal output.
Shows pose detection status in real-time.
"""

import cv2
import numpy as np
import time
from collections import deque
import os

# Import MediaPipe
from mediapipe.tasks.python.vision import PoseLandmarker, PoseLandmarkerOptions, RunningMode
from mediapipe.tasks.python.core.base_options import BaseOptions
from mediapipe import Image
from mediapipe.tasks.python.vision.core import image as mp_image_core

# Import TFLite
try:
    import tflite_runtime.interpreter as tflite
except:
    import tensorflow as tf
    class _TFWrapper:
        Interpreter = tf.lite.Interpreter
    tflite = _TFWrapper

print("\n" + "="*70)
print("🚀 FALL DETECTOR - DEBUG MODE")
print("="*70)
print("This version shows detailed status in the terminal.")
print("Press 'q' in the video window to quit.\n")

# Config
CAMERA_INDEX = 0
MODEL_PATH = 'fall_detection_transformer.tflite'
POSE_MODEL_PATH = 'pose_landmarker_lite.task'
INPUT_TIMESTEPS = 30
FALL_THRESHOLD = 0.90

# Initialize
print("Loading models...")
interpreter = tflite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
print(f"✅ Fall detection model loaded")

base_options = BaseOptions(model_asset_path=POSE_MODEL_PATH)
options = PoseLandmarkerOptions(
    base_options=base_options,
    running_mode=RunningMode.VIDEO,
    min_pose_detection_confidence=0.5,
    min_pose_presence_confidence=0.5,
    min_tracking_confidence=0.5
)
landmarker = PoseLandmarker.create_from_options(options)
print(f"✅ Pose detection model loaded")

# Open camera
cap = cv2.VideoCapture(CAMERA_INDEX)
if not cap.isOpened():
    print(f"❌ Cannot open camera {CAMERA_INDEX}")
    exit(1)

fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
print(f"✅ Camera opened (FPS: {fps})")

print("\n" + "="*70)
print("🎥 STARTING DETECTION")
print("="*70)
print("Watch the terminal for detection status...\n")

feature_sequence = deque(maxlen=INPUT_TIMESTEPS)
frame_count = 0
poses_detected = 0
falls_detected = 0

try:
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("❌ Failed to grab frame")
            break
        
        frame_count += 1
        
        # Convert to RGB for MediaPipe
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = Image(image_format=mp_image_core.ImageFormat.SRGB, data=rgb)
        timestamp_ms = int((frame_count / fps) * 1000)
        
        # Detect pose
        try:
            result = landmarker.detect_for_video(mp_image, timestamp_ms)
        except:
            result = landmarker.detect(mp_image)
        
        # Check if person detected
        person_detected = False
        num_landmarks = 0
        landmarks = []
        
        if hasattr(result, 'pose_landmarks') and result.pose_landmarks:
            if len(result.pose_landmarks) > 0:
                person_detected = True
                poses_detected += 1
                # MediaPipe Tasks API returns list directly
                landmarks = result.pose_landmarks[0]
                num_landmarks = len(landmarks)
        
        # Print status every 30 frames
        if frame_count % 30 == 0:
            detection_rate = (poses_detected / frame_count) * 100
            print(f"\n📊 Frame {frame_count}:")
            print(f"   Person detected: {'✅ YES' if person_detected else '❌ NO'}")
            if person_detected:
                print(f"   Landmarks: {num_landmarks}")
            print(f"   Detection rate: {detection_rate:.1f}%")
            print(f"   Sequence buffer: {len(feature_sequence)}/{INPUT_TIMESTEPS}")
            
            if len(feature_sequence) == INPUT_TIMESTEPS:
                print(f"   Status: 🟢 READY FOR FALL DETECTION")
            else:
                print(f"   Status: 🟡 Collecting data... ({len(feature_sequence)}/{INPUT_TIMESTEPS})")
        
        # Simple visualization
        display_frame = frame.copy()
        
        # Draw pose if detected
        if person_detected:
            h, w = display_frame.shape[:2]
            for lm in landmarks:
                cx = int(lm.x * w)
                cy = int(lm.y * h)
                cv2.circle(display_frame, (cx, cy), 3, (0, 255, 0), -1)
        
        # Add status text
        status_text = "Person: " + ("DETECTED" if person_detected else "NOT DETECTED")
        cv2.putText(display_frame, status_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, 
                   (0, 255, 0) if person_detected else (0, 0, 255), 2)
        
        buffer_text = f"Buffer: {len(feature_sequence)}/{INPUT_TIMESTEPS}"
        cv2.putText(display_frame, buffer_text, (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow("Fall Detector - Debug Mode (Press 'q' to quit)", display_frame)
        
        # Dummy feature extraction (simplified for debug)
        if person_detected:
            dummy_features = np.random.rand(51).astype(np.float32)
            feature_sequence.append(dummy_features)
        
        # Check for quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("\n👋 Quitting...")
            break

except KeyboardInterrupt:
    print("\n\n👋 Interrupted by user")
finally:
    landmarker.close()
    cap.release()
    cv2.destroyAllWindows()
    
    print("\n" + "="*70)
    print("📈 SESSION SUMMARY")
    print("="*70)
    print(f"Total frames processed: {frame_count}")
    print(f"Poses detected: {poses_detected}")
    if frame_count > 0:
        print(f"Detection rate: {(poses_detected/frame_count)*100:.1f}%")
    print(f"Falls detected: {falls_detected}")
    print("="*70 + "\n")

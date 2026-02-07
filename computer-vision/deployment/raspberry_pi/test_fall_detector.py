#!/usr/bin/env python3
"""
Fall detector with LOWER THRESHOLD (70%) for testing.
Shows real-time fall probability scores.
"""

import cv2
import numpy as np
import time
from collections import deque
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import from main fall detector
from mediapipe.tasks.python.vision import PoseLandmarker, PoseLandmarkerOptions, RunningMode
from mediapipe.tasks.python.core.base_options import BaseOptions
from mediapipe import Image
from mediapipe.tasks.python.vision.core import image as mp_image_core

try:
    import tflite_runtime.interpreter as tflite
except:
    import tensorflow as tf
    class _TFWrapper:
        Interpreter = tf.lite.Interpreter
    tflite = _TFWrapper

print("\n" + "="*70)
print("🧪 FALL DETECTOR - TESTING MODE")
print("="*70)
print("⚠️  LOWER THRESHOLD: 70% (vs 90% in production)")
print("📊 Shows real-time fall probability scores")
print("="*70 + "\n")

# Configuration - TESTING SETTINGS
CAMERA_INDEX = 0
FALL_THRESHOLD = 0.70  # ⚠️ LOWERED from 0.90 for testing
INPUT_TIMESTEPS = 30
NUM_FEATURES = 51

# Load models
print("Loading models...")
interpreter = tflite.Interpreter(model_path='fall_detection_transformer.tflite')
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

base_options = BaseOptions(model_asset_path='pose_landmarker_lite.task')
options = PoseLandmarkerOptions(
    base_options=base_options,
    running_mode=RunningMode.VIDEO,
    min_pose_detection_confidence=0.5,
    min_pose_presence_confidence=0.5,
    min_tracking_confidence=0.5
)
landmarker = PoseLandmarker.create_from_options(options)
print("✅ Models loaded\n")

# Open camera
cap = cv2.VideoCapture(CAMERA_INDEX)
if not cap.isOpened():
    print("❌ Cannot open camera")
    exit(1)

fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
print(f"✅ Camera opened (FPS: {fps})")
print("\n" + "="*70)
print("🎬 INSTRUCTIONS:")
print("="*70)
print("1. Wait for 'READY' status (buffer fills to 30 frames)")
print("2. Stand upright")
print("3. Quickly drop to the floor (simulate falling)")
print("4. Lie flat for 2-3 seconds")
print("5. Watch for FALL ALERT!")
print("\nPress 'q' to quit")
print("="*70 + "\n")

# Keypoint mapping (simplified from main script)
MEDIAPIPE_TO_KEYPOINT = {
    0: 8,   # Nose
    2: 3,   # Left Eye
    5: 12,  # Right Eye
    7: 1,   # Left Ear
    8: 10,  # Right Ear
    11: 6,  # Left Shoulder
    12: 15, # Right Shoulder
    13: 2,  # Left Elbow
    14: 11, # Right Elbow
    15: 7,  # Left Wrist
    16: 16, # Right Wrist
    23: 4,  # Left Hip
    24: 13, # Right Hip
    25: 5,  # Left Knee
    26: 14, # Right Knee
    27: 0,  # Left Ankle
    28: 9,  # Right Ankle
}

feature_sequence = deque(maxlen=INPUT_TIMESTEPS)
frame_count = 0
max_fall_prob = 0.0
fall_count = 0

try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Pose detection
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = Image(image_format=mp_image_core.ImageFormat.SRGB, data=rgb)
        timestamp_ms = int((frame_count / fps) * 1000)
        
        try:
            result = landmarker.detect_for_video(mp_image, timestamp_ms)
        except:
            result = landmarker.detect(mp_image)
        
        # Extract features (simplified)
        features = np.zeros(NUM_FEATURES, dtype=np.float32)
        person_detected = False
        
        if hasattr(result, 'pose_landmarks') and result.pose_landmarks and len(result.pose_landmarks) > 0:
            person_detected = True
            landmarks = result.pose_landmarks[0]
            
            for mp_idx, feat_idx in MEDIAPIPE_TO_KEYPOINT.items():
                if mp_idx < len(landmarks):
                    lm = landmarks[mp_idx]
                    features[feat_idx * 3] = lm.x
                    features[feat_idx * 3 + 1] = lm.y
                    features[feat_idx * 3 + 2] = getattr(lm, 'visibility', 1.0)
        
        if person_detected:
            feature_sequence.append(features)
        
        # Prediction
        fall_probability = 0.0
        status = "Collecting..."
        color = (255, 255, 0)  # Yellow
        
        if len(feature_sequence) == INPUT_TIMESTEPS:
            model_input = np.array(feature_sequence, dtype=np.float32)
            model_input = np.expand_dims(model_input, axis=0)
            
            interpreter.set_tensor(input_details[0]['index'], model_input)
            interpreter.invoke()
            output = interpreter.get_tensor(output_details[0]['index'])
            
            fall_probability = float(output[0][0])
            max_fall_prob = max(max_fall_prob, fall_probability)
            
            if fall_probability >= FALL_THRESHOLD:
                status = "🚨 FALL DETECTED! 🚨"
                color = (0, 0, 255)  # Red
                fall_count += 1
                print(f"\n{'='*70}")
                print(f"🚨 FALL DETECTED at frame {frame_count}!")
                print(f"   Fall probability: {fall_probability*100:.1f}%")
                print(f"   Threshold: {FALL_THRESHOLD*100:.0f}%")
                print(f"{'='*70}\n")
            else:
                status = f"NO FALL ({fall_probability*100:.1f}%)"
                color = (0, 255, 0) if fall_probability < 0.5 else (0, 165, 255)  # Green or Orange
        
        # Visualization
        display = frame.copy()
        h, w = display.shape[:2]
        
        # Draw skeleton if detected
        if person_detected:
            for lm in landmarks:
                cx = int(lm.x * w)
                cy = int(lm.y * h)
                cv2.circle(display, (cx, cy), 4, (0, 255, 0), -1)
        
        # Status bar at top
        cv2.rectangle(display, (0, 0), (w, 120), (0, 0, 0), -1)
        
        cv2.putText(display, status, (20, 40),
                   cv2.FONT_HERSHEY_DUPLEX, 1.2, color, 2)
        
        # Progress bar for fall probability
        bar_width = int((w - 40) * fall_probability)
        if len(feature_sequence) == INPUT_TIMESTEPS:
            cv2.rectangle(display, (20, 60), (20 + bar_width, 85),
                         color, -1)
            cv2.rectangle(display, (20, 60), (w - 20, 85),
                         (255, 255, 255), 2)
            
            prob_text = f"Fall Probability: {fall_probability*100:.1f}%"
            cv2.putText(display, prob_text, (20, 105),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Buffer status
        buffer_text = f"Buffer: {len(feature_sequence)}/{INPUT_TIMESTEPS}"
        if len(feature_sequence) < INPUT_TIMESTEPS:
            cv2.putText(display, buffer_text, (20, 105),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        cv2.imshow("Fall Detector - Testing Mode (Press 'q' to quit)", display)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("\n👋 Interrupted")
finally:
    landmarker.close()
    cap.release()
    cv2.destroyAllWindows()
    
    print("\n" + "="*70)
    print("📊 SESSION SUMMARY")
    print("="*70)
    print(f"Frames processed: {frame_count}")
    print(f"Falls detected: {fall_count}")
    print(f"Max fall probability: {max_fall_prob*100:.1f}%")
    print(f"Threshold used: {FALL_THRESHOLD*100:.0f}%")
    
    if max_fall_prob < 0.50:
        print("\n💡 SUGGESTION: Falls not detected or very low probability")
        print("   Try more dramatic fall motion (faster drop to floor)")
    elif max_fall_prob < FALL_THRESHOLD:
        print(f"\n💡 SUGGESTION: Highest score was {max_fall_prob*100:.1f}%")
        print(f"   Just below {FALL_THRESHOLD*100:.0f}% threshold")
        print("   Try more sudden/dramatic falls, or lower threshold further")
    else:
        print("\n✅ Falls successfully detected!")
    
    print("="*70 + "\n")

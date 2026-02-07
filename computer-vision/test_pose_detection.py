#!/usr/bin/env python3
"""Test if PoseLandmarker can detect poses in example video."""
from mediapipe.tasks.python.vision import PoseLandmarker, PoseLandmarkerOptions, RunningMode
from mediapipe.tasks.python.core.base_options import BaseOptions
from mediapipe import Image
from mediapipe.tasks.python.vision.core import image as mp_image_core
import cv2
import numpy as np

# Load video
cap = cv2.VideoCapture('deployment/huggingface_space/fall_example_1.mp4')
ok, bgr = cap.read()
cap.release()

if not ok:
    print('Failed to read frame')
    exit(1)

print(f'Frame shape: {bgr.shape}, dtype: {bgr.dtype}')

# Try with IMAGE mode first
base_opts = BaseOptions(model_asset_path='deployment/raspberry_pi/pose_landmarker_lite.task')
opts = PoseLandmarkerOptions(base_options=base_opts, running_mode=RunningMode.IMAGE)
landmarker = PoseLandmarker.create_from_options(opts)

# Convert to RGB and ensure contiguous
rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
rgb = np.ascontiguousarray(rgb)
print(f'RGB shape: {rgb.shape}, dtype: {rgb.dtype}, contiguous: {rgb.flags["C_CONTIGUOUS"]}')

# Create MediaPipe Image
mp_image = Image(image_format=mp_image_core.ImageFormat.SRGB, data=rgb)

# Detect
result = landmarker.detect(mp_image)

print(f'\nResult type: {type(result)}')
print(f'Has pose_landmarks: {hasattr(result, "pose_landmarks")}')
if hasattr(result, 'pose_landmarks'):
    print(f'pose_landmarks type: {type(result.pose_landmarks)}')
    print(f'Number of poses: {len(result.pose_landmarks) if result.pose_landmarks else 0}')
    if result.pose_landmarks and len(result.pose_landmarks) > 0:
        first_pose = result.pose_landmarks[0]
        print(f'First pose type: {type(first_pose)}')
        print(f'First pose length: {len(first_pose)}')
        print(f'\n✓ SUCCESS: First pose has {len(first_pose)} landmarks')
        first_lm = first_pose[0]
        print(f'  First landmark (nose): x={first_lm.x:.3f}, y={first_lm.y:.3f}, visibility={getattr(first_lm, "visibility", "N/A")}')
    else:
        print('\n✗ FAIL: NO POSES DETECTED!')

landmarker.close()

#!/usr/bin/env python3
"""
Quick diagnostic to check if fall detection is working properly.
Shows what the system sees and helps debug issues.
"""

import cv2
import numpy as np
import time

def check_fall_detection_status():
    """Check if fall detection setup is correct."""
    print("\n" + "="*70)
    print("🔍 FALL DETECTION DIAGNOSTIC")
    print("="*70 + "\n")
    
    # Check 1: Model file exists
    import os
    print("1. Checking for model file...")
    model_path = 'fall_detection_transformer.tflite'
    if os.path.exists(model_path):
        size_mb = os.path.getsize(model_path) / (1024 * 1024)
        print(f"   ✅ Model found: {model_path} ({size_mb:.1f} MB)")
    else:
        print(f"   ❌ Model NOT found: {model_path}")
        return False
    
    # Check 2: Pose model exists
    print("\n2. Checking for pose detection model...")
    pose_path = 'pose_landmarker_lite.task'
    if os.path.exists(pose_path):
        size_mb = os.path.getsize(pose_path) / (1024 * 1024)
        print(f"   ✅ Pose model found: {pose_path} ({size_mb:.1f} MB)")
    else:
        print(f"   ❌ Pose model NOT found: {pose_path}")
        return False
    
    # Check 3: Camera
    print("\n3. Checking camera...")
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print(f"   ✅ Camera working: {frame.shape[1]}×{frame.shape[0]}")
        cap.release()
    else:
        print("   ❌ Camera not accessible")
        return False
    
    print("\n" + "="*70)
    print("✅ ALL CHECKS PASSED!")
    print("="*70)
    
    return True

def explain_how_it_works():
    """Explain what the fall detector is looking for."""
    print("\n" + "="*70)
    print("📖 HOW FALL DETECTION WORKS")
    print("="*70 + "\n")
    
    print("1. INITIALIZATION PHASE (First ~2 seconds)")
    print("   - System needs to collect 30 frames of pose data")
    print("   - You'll see: 'Collecting data...' or similar")
    print("   - Just stand normally in view of camera")
    print()
    
    print("2. DETECTION PHASE (After 30 frames collected)")
    print("   - System analyzes your pose continuously")
    print("   - Shows: 'NO_FALL (Conf: X.XX)' normally")
    print("   - If fall detected: 'FALL (Conf: X.XX)' and red alert")
    print()
    
    print("3. WHAT COUNTS AS A FALL?")
    print("   The model looks for these patterns:")
    print("   ✓ Person going from standing/sitting to lying down quickly")
    print("   ✓ Sudden change in body orientation (vertical to horizontal)")
    print("   ✓ Hip/knee/ankle positions changing to floor level")
    print("   ✓ Loss of upright posture")
    print()
    
    print("4. DETECTION THRESHOLD")
    print("   - Confidence must be > 90% to trigger alert")
    print("   - This prevents false alarms")
    print("   - Trade-off: some falls might not trigger if not clear enough")
    print()
    
    print("5. IMPORTANT NOTES")
    print("   ⚠️ You MUST be in camera view")
    print("   ⚠️ Skeleton overlay should be visible on your body")
    print("   ⚠️ Good lighting helps pose detection")
    print("   ⚠️ Model trained on specific fall types - may not detect all falls")
    print()

def testing_instructions():
    """Show how to test the fall detector."""
    print("\n" + "="*70)
    print("🧪 HOW TO TEST FALL DETECTION")
    print("="*70 + "\n")
    
    print("Method 1: SIMULATE A FALL (Safest)")
    print("-" * 70)
    print("1. Stand in front of camera, facing it")
    print("2. Wait for 'Collecting data...' to finish")
    print("3. Slowly lower yourself to the ground (simulate falling)")
    print("4. Lie on floor for 2-3 seconds")
    print("5. Watch for red 'FALL DETECTED!' alert")
    print()
    
    print("Method 2: CHECK STATUS TEXT")
    print("-" * 70)
    print("Look at the TOP RIGHT corner of the video window:")
    print("- 'Collecting data...' → System is initializing")
    print("- 'NO_FALL (Conf: 0.XX)' → System active, no fall detected")
    print("- 'FALL (Conf: 0.XX)' → Fall detected!")
    print()
    
    print("Method 3: CHECK SKELETON")
    print("-" * 70)
    print("You should see:")
    print("✓ Colored dots on your joints (shoulders, elbows, knees, etc.)")
    print("✓ Lines connecting the dots (skeleton)")
    print()
    print("If NO skeleton visible:")
    print("✗ Person not detected - adjust lighting, position, or distance")
    print()
    
    print("Method 4: CHECK LOGS")
    print("-" * 70)
    print("Look at the terminal output:")
    print("- Should see frame processing messages")
    print("- Fall events logged to: fall_detection_log.txt")
    print()

def common_issues():
    """List common issues and solutions."""
    print("\n" + "="*70)
    print("⚠️ COMMON ISSUES & SOLUTIONS")
    print("="*70 + "\n")
    
    print("Issue 1: No skeleton visible on video")
    print("   → Person too far or too close")
    print("   → Poor lighting")
    print("   → Person not fully in frame")
    print("   Solution: Adjust position, improve lighting")
    print()
    
    print("Issue 2: Status stuck at 'Collecting data...'")
    print("   → No pose detected in frames")
    print("   Solution: Make sure you're visible and skeleton appears")
    print()
    
    print("Issue 3: Falls not detected")
    print("   → Confidence threshold too high (90%)")
    print("   → Fall motion too slow/gentle")
    print("   → Fall type not in training data")
    print("   Solution: Try more dramatic fall simulation")
    print()
    
    print("Issue 4: Too many false alarms")
    print("   → Bending down triggers detection")
    print("   → Sitting/lying normally triggers it")
    print("   Solution: Adjust FALL_CONFIDENCE_THRESHOLD in code")
    print()
    
    print("Issue 5: Window doesn't show up")
    print("   → cv2.imshow() not working on your system")
    print("   Solution: Check terminal output for status")
    print()

def main():
    """Run full diagnostic."""
    if not check_fall_detection_status():
        print("\n❌ Setup incomplete. Fix issues above before testing.")
        return
    
    explain_how_it_works()
    testing_instructions()
    common_issues()
    
    print("\n" + "="*70)
    print("🚀 READY TO TEST")
    print("="*70)
    print("\nRun: python fall-detector.py --source webcam")
    print("\nThen try simulating a fall as described above.")
    print("Press 'q' in the video window to quit anytime.\n")

if __name__ == "__main__":
    main()

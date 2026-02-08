#!/usr/bin/env python3
"""
Example: Using the latest fall detection video in computer vision processing
"""

import sys
from pathlib import Path

# Add the computer-vision directory to path
sys.path.insert(0, str(Path(__file__).parent))

from monitor_clips import get_latest_clip_path, get_clip_metadata


def process_latest_fall_detection():
    """
    Example function showing how to access and process the latest video
    """
    print("🎥 Fall Detection Video Processor")
    print("=" * 60)
    
    # Get the latest video path
    latest_video = get_latest_clip_path()
    
    if not latest_video:
        print("❌ No video available yet")
        print("   Make sure the clips monitor is running:")
        print("   python3 computer-vision/monitor_clips.py")
        return None
    
    # Get metadata
    metadata = get_clip_metadata()
    print(f"✅ Latest video found:")
    print(f"   Path: {metadata['path']}")
    print(f"   Size: {metadata['size_mb']} MB")
    print(f"   Last updated: {metadata['modified']}")
    print()
    
    # Here you would do your actual computer vision processing
    print("🔍 Processing video for fall detection analysis...")
    
    # Example: Load video with OpenCV (if you have the pose detection code)
    try:
        import cv2
        
        cap = cv2.VideoCapture(str(latest_video))
        if not cap.isOpened():
            print("❌ Could not open video file")
            return None
        
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = frame_count / fps if fps > 0 else 0
        
        print(f"   Frames: {frame_count}")
        print(f"   FPS: {fps:.2f}")
        print(f"   Duration: {duration:.2f} seconds")
        
        cap.release()
        
        # TODO: Add your pose detection / fall analysis here
        # from core.pose_detector import PoseDetector
        # from core.fall_classifier import FallClassifier
        # detector = PoseDetector()
        # classifier = FallClassifier()
        # ... process video ...
        
        print("✅ Video processing complete")
        return metadata
        
    except ImportError:
        print("ℹ️  OpenCV not available, skipping detailed analysis")
        print("   Install with: pip install opencv-python")
        return metadata


if __name__ == "__main__":
    process_latest_fall_detection()

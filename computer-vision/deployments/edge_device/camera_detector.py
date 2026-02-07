"""
Real-time Fall Detection for Edge Devices (Raspberry Pi).

This module provides real-time fall detection using a webcam or camera
on edge devices like Raspberry Pi.
"""
import os
import sys
from pathlib import Path
import cv2
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.settings import (
    ModelConfig,
    PoseDetectionConfig,
    FallDetectionConfig,
    VideoProcessingConfig
)
from core.pose_detector import PoseDetector
from core.fall_classifier import FallClassifier, KeypointFeatureExtractor
from core.video_processor import VideoProcessor, FallEvent


class RealTimeFallDetector:
    """Real-time fall detection for live camera feed."""
    
    def __init__(self, camera_index: int = 0):
        """
        Initialize real-time fall detector.
        
        Args:
            camera_index: Camera device index (default 0)
        """
        # Load configurations
        self.model_config = ModelConfig()
        self.pose_config = PoseDetectionConfig()
        self.fall_config = FallDetectionConfig()
        self.video_config = VideoProcessingConfig()
        
        # Initialize components
        self.feature_extractor = KeypointFeatureExtractor(
            self.pose_config,
            self.model_config
        )
        self.fall_classifier = FallClassifier(
            config=self.fall_config,
            model_config=self.model_config
        )
        self.video_processor = VideoProcessor(self.video_config)
        
        # Camera setup
        self.camera_index = camera_index
        self.camera_capture = None
        self.fps_estimate = 25.0
        
        # Fall detection state
        self.fall_event_cooldown_frames = 10
        self.frames_since_last_fall = self.fall_event_cooldown_frames
        self.last_fall_time = 0
        
        # Performance monitoring
        self.frame_times = []
        
        print("=" * 60)
        print("Real-Time Fall Detection System")
        print("=" * 60)
        print(f"Camera Index: {self.camera_index}")
        print(f"Fall Threshold: {self.fall_config.confidence_threshold:.1%}")
        print("=" * 60)
    
    def initialize_camera(self):
        """Initialize camera capture."""
        self.camera_capture = cv2.VideoCapture(self.camera_index)
        
        if not self.camera_capture.isOpened():
            raise RuntimeError(f"Failed to open camera {self.camera_index}")
        
        # Get camera FPS
        self.fps_estimate = self.camera_capture.get(cv2.CAP_PROP_FPS)
        if self.fps_estimate == 0 or self.fps_estimate < 1:
            self.fps_estimate = 25.0
        
        print(f"Camera initialized - FPS: {self.fps_estimate:.1f}")
    
    def run(self):
        """Run real-time fall detection loop."""
        # Initialize camera
        self.initialize_camera()
        
        frame_number = 0
        
        try:
            with PoseDetector(
                config=self.pose_config,
                use_video_mode=True
            ) as pose_detector:
                
                print("\nStarting detection... Press 'q' to quit")
                
                while True:
                    start_time = time.time()
                    
                    # Capture frame
                    success, frame_bgr = self.camera_capture.read()
                    if not success:
                        print("Failed to capture frame")
                        break
                    
                    # Detect pose
                    detection_result = pose_detector.process_frame(
                        frame_bgr,
                        frame_number,
                        self.fps_estimate
                    )
                    
                    # Extract features
                    normalized_features = self.feature_extractor.process_detection(
                        detection_result
                    )
                    
                    # Add to classifier
                    self.fall_classifier.add_features(normalized_features)
                    
                    # Predict
                    fall_probability = self.fall_classifier.predict()
                    is_fall_detected = False
                    
                    if fall_probability is not None:
                        is_fall_detected = (
                            self.fall_classifier.is_fall_detected(fall_probability) and
                            self.frames_since_last_fall >= self.fall_event_cooldown_frames
                        )
                        
                        if is_fall_detected:
                            timestamp = frame_number / self.fps_estimate
                            print(f"\n*** FALL DETECTED ***")
                            print(f"  Frame: {frame_number}")
                            print(f"  Time: {timestamp:.1f}s")
                            print(f"  Confidence: {fall_probability:.1%}\n")
                            
                            self.frames_since_last_fall = 0
                            self.last_fall_time = time.time()
                    
                    # Draw visualizations
                    if detection_result.has_landmarks():
                        self.video_processor.visualizer.draw_landmarks(
                            frame_bgr,
                            detection_result.landmarks
                        )
                    
                    # Draw status
                    self.video_processor.visualizer.draw_status_overlay(
                        frame_bgr,
                        fall_probability=fall_probability,
                        is_fall=is_fall_detected
                    )
                    
                    # Calculate and display FPS
                    frame_time = time.time() - start_time
                    self.frame_times.append(frame_time)
                    if len(self.frame_times) > 30:
                        self.frame_times.pop(0)
                    
                    avg_fps = 1.0 / (sum(self.frame_times) / len(self.frame_times))
                    cv2.putText(
                        frame_bgr,
                        f"FPS: {avg_fps:.1f}",
                        (10, frame_bgr.shape[0] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (255, 255, 255),
                        1
                    )
                    
                    # Display frame
                    cv2.imshow("Fall Detection", frame_bgr)
                    
                    # Check for quit
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        print("Quitting...")
                        break
                    
                    frame_number += 1
                    self.frames_since_last_fall += 1
        
        finally:
            # Clean up
            if self.camera_capture is not None:
                self.camera_capture.release()
            cv2.destroyAllWindows()
            print("\nDetection stopped")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Real-time fall detection")
    parser.add_argument(
        '--camera',
        type=int,
        default=0,
        help='Camera device index (default: 0)'
    )
    
    args = parser.parse_args()
    
    detector = RealTimeFallDetector(camera_index=args.camera)
    detector.run()


if __name__ == "__main__":
    main()

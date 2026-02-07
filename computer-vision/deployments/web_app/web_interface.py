"""
Fall Detection Web Application using Gradio.

This module provides a web interface for uploading and processing videos
to detect falls using pose estimation and a trained TensorFlow Lite model.
"""
import os
import sys
import shutil
import time
from pathlib import Path
import cv2
import gradio as gr

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


class FallDetectionApp:
    """Main application class for fall detection web interface."""
    
    def __init__(self):
        """Initialize the fall detection application."""
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
        
        # Fall detection parameters
        self.fall_event_cooldown_frames = 10
        
        print("=" * 60)
        print("Fall Detection Application Initialized")
        print("=" * 60)
        print(f"Model: {self.model_config.fall_detection_model_path}")
        print(f"Pose Model: {self.pose_config.keypoint_indices}")
        print(f"Sequence Length: {self.model_config.sequence_length}")
        print(f"Fall Threshold: {self.fall_config.confidence_threshold:.1%}")
        print("=" * 60)
    
    def process_video(
        self,
        uploaded_video_path: str
    ) -> tuple:
        """
        Process an uploaded video file for fall detection.
        
        Args:
            uploaded_video_path: Path to the uploaded video file
            
        Returns:
            Tuple of (output_video_path, summary_text)
        """
        if uploaded_video_path is None:
            return None, "Please upload a video file."
        
        print(f"\nProcessing uploaded video: {uploaded_video_path}")
        
        # Copy video to local workspace (Gradio may provide temporary path)
        timestamp_ms = int(time.time() * 1000)
        base_name = os.path.basename(uploaded_video_path)
        local_video_path = os.path.join(os.getcwd(), f"{timestamp_ms}_{base_name}")
        
        try:
            shutil.copy2(uploaded_video_path, local_video_path)
            print(f"Copied video to: {local_video_path}")
        except Exception as error:
            error_message = f"Error copying video file: {error}"
            print(error_message)
            return None, error_message
        
        try:
            # Process the video
            output_video_path, fall_events = self._process_video_internal(
                local_video_path
            )
            
            # Generate summary
            summary = self._generate_summary(fall_events)
            
            return output_video_path, summary
            
        except Exception as error:
            error_message = f"Error processing video: {error}"
            print(error_message)
            import traceback
            traceback.print_exc()
            return None, error_message
            
        finally:
            # Clean up temporary video file
            if os.path.exists(local_video_path):
                try:
                    os.remove(local_video_path)
                except Exception:
                    pass  # Ignore cleanup errors
    
    def _process_video_internal(
        self,
        video_path: str
    ) -> tuple:
        """
        Internal video processing logic.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Tuple of (output_video_path, list of FallEvent objects)
        """
        # Open video
        video_capture = cv2.VideoCapture(video_path)
        if not video_capture.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        
        # Read video properties
        frame_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = video_capture.get(cv2.CAP_PROP_FPS)
        if fps == 0 or fps < 1:
            fps = self.video_config.default_fps
        
        # Create output video writer
        output_path = self.video_processor.generate_output_path()
        video_writer = self.video_processor.create_video_writer(
            output_path,
            frame_width,
            frame_height,
            fps
        )
        
        # Initialize detection state
        self.fall_classifier.reset_buffer()
        fall_events = []
        frames_since_last_fall = self.fall_event_cooldown_frames  # Allow first detection
        
        # Process each frame
        frame_number = 0
        
        with PoseDetector(
            config=self.pose_config,
            use_video_mode=True
        ) as pose_detector:
            
            while True:
                success, frame_bgr = video_capture.read()
                if not success:
                    break
                
                # Detect pose
                detection_result = pose_detector.process_frame(
                    frame_bgr,
                    frame_number,
                    fps
                )
                
                # Extract and normalize features
                normalized_features = self.feature_extractor.process_detection(
                    detection_result
                )
                
                # Add features to classifier buffer
                self.fall_classifier.add_features(normalized_features)
                
                # Predict fall probability
                fall_probability = self.fall_classifier.predict()
                is_fall_detected = False
                
                if fall_probability is not None:
                    is_fall_detected = (
                        self.fall_classifier.is_fall_detected(fall_probability) and
                        frames_since_last_fall >= self.fall_event_cooldown_frames
                    )
                    
                    if is_fall_detected:
                        # Record fall event
                        timestamp_seconds = frame_number / fps
                        fall_event = FallEvent(
                            frame_number=frame_number,
                            timestamp_seconds=timestamp_seconds,
                            confidence=fall_probability
                        )
                        fall_events.append(fall_event)
                        frames_since_last_fall = 0
                        print(f"  {fall_event}")
                
                # Draw pose skeleton
                if detection_result.has_landmarks():
                    self.video_processor.visualizer.draw_landmarks(
                        frame_bgr,
                        detection_result.landmarks,
                        draw_connections=True
                    )
                
                # Draw status overlay
                self.video_processor.visualizer.draw_status_overlay(
                    frame_bgr,
                    fall_probability=fall_probability,
                    is_fall=is_fall_detected,
                    frame_number=frame_number
                )
                
                # Write frame
                video_writer.write(frame_bgr)
                
                frame_number += 1
                frames_since_last_fall += 1
        
        # Clean up
        video_capture.release()
        video_writer.release()
        
        print(f"\nProcessed {frame_number} frames")
        print(f"Output saved to: {output_path}")
        
        return output_path, fall_events
    
    def _generate_summary(self, fall_events: list) -> str:
        """
        Generate summary text for detected falls.
        
        Args:
            fall_events: List of FallEvent objects
            
        Returns:
            Summary text
        """
        if len(fall_events) == 0:
            return "No falls detected in the video."
        
        summary_lines = [
            f"Detected {len(fall_events)} fall event(s):",
            ""
        ]
        
        for idx, fall_event in enumerate(fall_events, 1):
            summary_lines.append(f"{idx}. {fall_event}")
        
        return "\n".join(summary_lines)


def create_gradio_interface():
    """
    Create and configure the Gradio interface.
    
    Returns:
        Gradio interface object
    """
    # Initialize application
    app = FallDetectionApp()
    
    # Create Gradio interface
    interface = gr.Interface(
        fn=app.process_video,
        inputs=gr.Video(label="Upload Video"),
        outputs=[
            gr.Video(label="Processed Video"),
            gr.Textbox(label="Detection Summary", lines=10)
        ],
        title="Fall Detection System",
        description=(
            "Upload a video to detect falls using pose estimation. "
            "The system analyzes body pose over time and alerts when a fall is detected."
        ),
        examples=[
            ["fall_example_1.mp4"],
            ["fall_example_2.mp4"]
        ] if os.path.exists("fall_example_1.mp4") else None,
        cache_examples=False
    )
    
    return interface


if __name__ == "__main__":
    # Create and launch interface
    interface = create_gradio_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )

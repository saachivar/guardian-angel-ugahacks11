"""
Video processing utilities for fall detection.

This module provides high-level functions for processing videos,
drawing visualizations, and managing video I/O.
"""
import os
import time
from typing import Optional, Tuple, List
from dataclasses import dataclass
import cv2
import numpy as np

from config.settings import VideoProcessingConfig, POSE_CONNECTIONS
from core.pose_detector import PoseLandmark


@dataclass
class FallEvent:
    """Represents a detected fall event."""
    frame_number: int
    timestamp_seconds: float
    confidence: float
    
    def __str__(self):
        return f"Fall at frame {self.frame_number} (~{self.timestamp_seconds:.1f}s) - Confidence: {self.confidence:.2%}"


class SkeletonVisualizer:
    """Handles drawing pose landmarks and connections on images."""
    
    def __init__(self, config: Optional[VideoProcessingConfig] = None):
        """
        Initialize visualizer.
        
        Args:
            config: Video processing configuration
        """
        self.config = config or VideoProcessingConfig()
    
    def draw_landmarks(
        self,
        image_bgr: np.ndarray,
        landmarks: List[PoseLandmark],
        draw_connections: bool = True
    ):
        """
        Draw pose landmarks and connections on image.
        
        Args:
            image_bgr: BGR image to draw on (modified in-place)
            landmarks: List of pose landmarks
            draw_connections: Whether to draw skeleton connections
        """
        if len(landmarks) == 0:
            return
        
        image_height, image_width = image_bgr.shape[:2]
        
        # Draw connections first (so they appear behind landmarks)
        if draw_connections and self.config.draw_connections:
            self._draw_connections(
                image_bgr,
                landmarks,
                image_width,
                image_height
            )
        
        # Draw landmarks
        if self.config.draw_landmarks:
            self._draw_landmark_points(
                image_bgr,
                landmarks,
                image_width,
                image_height
            )
    
    def _draw_connections(
        self,
        image_bgr: np.ndarray,
        landmarks: List[PoseLandmark],
        image_width: int,
        image_height: int
    ):
        """Draw skeleton connections between landmarks."""
        for connection_start, connection_end in POSE_CONNECTIONS:
            if connection_start < len(landmarks) and connection_end < len(landmarks):
                start_point = landmarks[connection_start].to_pixel_coordinates(
                    image_width, image_height
                )
                end_point = landmarks[connection_end].to_pixel_coordinates(
                    image_width, image_height
                )
                
                cv2.line(
                    image_bgr,
                    start_point,
                    end_point,
                    self.config.connection_color,
                    self.config.connection_thickness
                )
    
    def _draw_landmark_points(
        self,
        image_bgr: np.ndarray,
        landmarks: List[PoseLandmark],
        image_width: int,
        image_height: int
    ):
        """Draw individual landmark points."""
        for landmark in landmarks:
            center_point = landmark.to_pixel_coordinates(image_width, image_height)
            cv2.circle(
                image_bgr,
                center_point,
                self.config.landmark_radius,
                self.config.landmark_color,
                -1  # Filled circle
            )
    
    def draw_status_overlay(
        self,
        image_bgr: np.ndarray,
        fall_probability: Optional[float] = None,
        is_fall: bool = False,
        frame_number: Optional[int] = None
    ):
        """
        Draw status information overlay on image.
        
        Args:
            image_bgr: BGR image to draw on (modified in-place)
            fall_probability: Current fall probability (0-1)
            is_fall: Whether fall is currently detected
            frame_number: Current frame number
        """
        image_height, image_width = image_bgr.shape[:2]
        
        # Determine background color and status text
        if is_fall:
            background_color = self.config.background_color_fall
            status_text = "FALL DETECTED!"
        else:
            background_color = self.config.background_color_normal
            status_text = "Normal"
        
        # Draw background rectangle
        overlay_height = 60
        cv2.rectangle(
            image_bgr,
            (0, 0),
            (image_width, overlay_height),
            background_color,
            -1
        )
        
        # Draw status text
        cv2.putText(
            image_bgr,
            status_text,
            (10, 30),
            self.config.font_face,
            self.config.font_scale,
            self.config.text_color,
            self.config.text_thickness
        )
        
        # Draw probability if available
        if fall_probability is not None:
            prob_text = f"Probability: {fall_probability:.1%}"
            cv2.putText(
                image_bgr,
                prob_text,
                (10, 50),
                self.config.font_face,
                self.config.font_scale * 0.8,
                self.config.text_color,
                self.config.text_thickness
            )
        
        # Draw frame number if available
        if frame_number is not None:
            frame_text = f"Frame: {frame_number}"
            text_size = cv2.getTextSize(
                frame_text,
                self.config.font_face,
                self.config.font_scale * 0.8,
                self.config.text_thickness
            )[0]
            text_x = image_width - text_size[0] - 10
            cv2.putText(
                image_bgr,
                frame_text,
                (text_x, 30),
                self.config.font_face,
                self.config.font_scale * 0.8,
                self.config.text_color,
                self.config.text_thickness
            )


class VideoProcessor:
    """High-level video processing for fall detection."""
    
    def __init__(self, config: Optional[VideoProcessingConfig] = None):
        """
        Initialize video processor.
        
        Args:
            config: Video processing configuration
        """
        self.config = config or VideoProcessingConfig()
        self.visualizer = SkeletonVisualizer(config)
    
    def read_video_properties(
        self,
        video_path: str
    ) -> Tuple[int, int, int, float]:
        """
        Read video properties.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Tuple of (width, height, frame_count, fps)
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        if fps == 0 or np.isnan(fps) or fps < 1:
            fps = self.config.default_fps
        
        cap.release()
        
        return width, height, frame_count, fps
    
    def generate_output_path(
        self,
        prefix: str = "processed",
        extension: str = ".mp4"
    ) -> str:
        """
        Generate unique output file path.
        
        Args:
            prefix: Filename prefix
            extension: File extension
            
        Returns:
            Full path to output file
        """
        # Ensure output directory exists
        os.makedirs(self.config.output_directory, exist_ok=True)
        
        # Generate unique filename with timestamp
        timestamp = str(int(time.time() * 1000))
        filename = f"{prefix}_{timestamp}{extension}"
        output_path = os.path.join(self.config.output_directory, filename)
        
        return output_path
    
    def create_video_writer(
        self,
        output_path: str,
        width: int,
        height: int,
        fps: float,
        codec: str = 'mp4v'
    ) -> cv2.VideoWriter:
        """
        Create OpenCV video writer.
        
        Args:
            output_path: Path to output video file
            width: Frame width
            height: Frame height
            fps: Frames per second
            codec: FourCC codec code
            
        Returns:
            VideoWriter object
        """
        fourcc = cv2.VideoWriter_fourcc(*codec)
        writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        if not writer.isOpened():
            raise RuntimeError(f"Failed to create video writer: {output_path}")
        
        return writer
    
    @staticmethod
    def frame_to_timestamp(frame_number: int, fps: float) -> float:
        """Convert frame number to timestamp in seconds."""
        return frame_number / fps
    
    @staticmethod
    def timestamp_to_frame(timestamp_seconds: float, fps: float) -> int:
        """Convert timestamp in seconds to frame number."""
        return int(timestamp_seconds * fps)

"""
Pose detection module using MediaPipe Tasks API.

This module provides a clean interface for detecting human pose landmarks
in images and video frames using MediaPipe's PoseLandmarker.
"""
import os
from typing import List, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from mediapipe.tasks.python.vision import PoseLandmarker, PoseLandmarkerOptions, RunningMode
from mediapipe.tasks.python.core.base_options import BaseOptions
from mediapipe import Image
from mediapipe.tasks.python.vision.core import image as mp_image_core

from config.settings import PoseDetectionConfig


@dataclass
class PoseLandmark:
    """Represents a single pose landmark with 3D coordinates and visibility."""
    x: float
    y: float
    z: float = 0.0
    visibility: float = 1.0
    
    def to_pixel_coordinates(self, image_width: int, image_height: int) -> Tuple[int, int]:
        """Convert normalized coordinates to pixel coordinates."""
        pixel_x = int(self.x * image_width)
        pixel_y = int(self.y * image_height)
        return pixel_x, pixel_y


class PoseDetectionResult:
    """Container for pose detection results."""
    
    def __init__(self, landmarks: List[PoseLandmark]):
        self.landmarks = landmarks
        
    def has_landmarks(self) -> bool:
        """Check if any landmarks were detected."""
        return len(self.landmarks) > 0
    
    def get_landmark(self, index: int) -> Optional[PoseLandmark]:
        """Get landmark by index, or None if index out of range."""
        if 0 <= index < len(self.landmarks):
            return self.landmarks[index]
        return None
    
    def extract_selected_landmarks(
        self,
        indices: Tuple[int, ...],
        sort_by_name: bool = False,
        keypoint_names: Optional[Tuple[str, ...]] = None
    ) -> List[PoseLandmark]:
        """
        Extract specific landmarks by indices.
        
        Args:
            indices: Tuple of landmark indices to extract
            sort_by_name: If True, sort landmarks alphabetically by name
            keypoint_names: Names corresponding to indices (for sorting)
            
        Returns:
            List of selected landmarks
        """
        selected_landmarks = []
        
        if sort_by_name and keypoint_names:
            # Create (name, landmark) pairs and sort
            name_landmark_pairs = []
            for idx, name in zip(indices, keypoint_names):
                landmark = self.get_landmark(idx)
                if landmark:
                    name_landmark_pairs.append((name, landmark))
            
            # Sort by name and extract landmarks
            name_landmark_pairs.sort(key=lambda pair: pair[0])
            selected_landmarks = [landmark for _, landmark in name_landmark_pairs]
        else:
            # Extract in order of indices
            for idx in indices:
                landmark = self.get_landmark(idx)
                if landmark:
                    selected_landmarks.append(landmark)
                    
        return selected_landmarks


class PoseDetector:
    """
    MediaPipe pose detector with context manager support.
    
    This class wraps MediaPipe's PoseLandmarker to provide a clean,
    easy-to-use interface for pose detection.
    """
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        config: Optional[PoseDetectionConfig] = None,
        use_video_mode: bool = True
    ):
        """
        Initialize pose detector.
        
        Args:
            model_path: Path to .task model file (auto-detected if None)
            config: PoseDetectionConfig instance (uses defaults if None)
            use_video_mode: Use VIDEO mode for frame sequences, IMAGE mode otherwise
        """
        self.config = config or PoseDetectionConfig()
        self.use_video_mode = use_video_mode
        self.model_path = model_path or self._find_model_path()
        self._landmarker: Optional[PoseLandmarker] = None
        self._running_mode = RunningMode.VIDEO if use_video_mode else RunningMode.IMAGE
        
    def _find_model_path(self) -> str:
        """Auto-detect pose model path."""
        # Check environment variable first
        env_path = os.environ.get('MP_POSE_MODEL_PATH')
        if env_path and os.path.exists(env_path):
            return env_path
            
        # Search in common locations
        search_directories = [
            os.path.join(os.path.dirname(__file__), '..', 'deployments', 'edge_device', 'models'),
            os.path.join(os.path.dirname(__file__), '..', 'deployments', 'web_app', 'models'),
            os.getcwd()
        ]
        
        for search_dir in search_directories:
            try:
                abs_dir = os.path.abspath(search_dir)
                if not os.path.exists(abs_dir):
                    continue
                    
                for filename in os.listdir(abs_dir):
                    if filename.endswith('.task') and 'pose' in filename.lower():
                        model_path = os.path.join(abs_dir, filename)
                        print(f"Auto-detected pose model: {model_path}")
                        return model_path
            except Exception:
                continue
                
        raise RuntimeError(
            "No MediaPipe .task model found. "
            "Place a pose_landmarker*.task file in deployments/edge_device/models/ "
            "or set MP_POSE_MODEL_PATH environment variable."
        )
    
    def __enter__(self):
        """Initialize the pose landmarker."""
        base_options = BaseOptions(model_asset_path=self.model_path)
        options = PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=self._running_mode,
            min_pose_detection_confidence=self.config.min_detection_confidence,
            min_pose_presence_confidence=self.config.min_pose_presence_confidence,
            min_tracking_confidence=self.config.min_tracking_confidence
        )
        self._landmarker = PoseLandmarker.create_from_options(options)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources."""
        if self._landmarker is not None:
            self._landmarker.close()
            self._landmarker = None
    
    def detect(
        self,
        image_rgb: np.ndarray,
        timestamp_ms: Optional[int] = None
    ) -> PoseDetectionResult:
        """
        Detect pose landmarks in an RGB image.
        
        Args:
            image_rgb: RGB image as numpy array
            timestamp_ms: Timestamp in milliseconds (required for VIDEO mode)
            
        Returns:
            PoseDetectionResult containing detected landmarks
        """
        if self._landmarker is None:
            raise RuntimeError("PoseDetector must be used as context manager (with statement)")
        
        # Convert numpy array to MediaPipe Image
        mp_image = Image(
            image_format=mp_image_core.ImageFormat.SRGB,
            data=image_rgb
        )
        
        # Perform detection based on running mode
        if self._running_mode == RunningMode.VIDEO:
            if timestamp_ms is None:
                timestamp_ms = 0
            detection_result = self._landmarker.detect_for_video(mp_image, timestamp_ms)
        else:
            detection_result = self._landmarker.detect(mp_image)
        
        # Convert MediaPipe results to our PoseLandmark objects
        landmarks = []
        if hasattr(detection_result, 'pose_landmarks') and detection_result.pose_landmarks:
            if len(detection_result.pose_landmarks) > 0:
                # pose_landmarks[0] is a list of NormalizedLandmark objects
                for mediapipe_landmark in detection_result.pose_landmarks[0]:
                    landmark = PoseLandmark(
                        x=mediapipe_landmark.x,
                        y=mediapipe_landmark.y,
                        z=mediapipe_landmark.z,
                        visibility=getattr(mediapipe_landmark, 'visibility', 1.0)
                    )
                    landmarks.append(landmark)
        
        return PoseDetectionResult(landmarks)
    
    def process_frame(
        self,
        frame_bgr: np.ndarray,
        frame_index: int,
        fps: float = 25.0
    ) -> PoseDetectionResult:
        """
        Process a video frame (BGR format from OpenCV).
        
        Args:
            frame_bgr: BGR image from cv2.VideoCapture
            frame_index: Frame number (0-indexed)
            fps: Frames per second for timestamp calculation
            
        Returns:
            PoseDetectionResult containing detected landmarks
        """
        import cv2
        
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        
        # Calculate timestamp
        timestamp_ms = int((frame_index / fps) * 1000)
        
        return self.detect(frame_rgb, timestamp_ms)

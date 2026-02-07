"""
Centralized configuration settings for the fall detection system.
"""
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Tuple, List

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent


@dataclass
class ModelConfig:
    """Configuration for machine learning models."""
    
    # Fall detection model
    fall_detection_model_path: str = str(PROJECT_ROOT / 'deployments' / 'web_app' / 'models' / 'fall_detection_transformer.tflite')
    
    # Pose detection model
    pose_model_path: str = os.environ.get(
        'MP_POSE_MODEL_PATH',
        str(PROJECT_ROOT / 'deployments' / 'edge_device' / 'models' / 'pose_landmarker_lite.task')
    )
    
    # Model input parameters
    sequence_length: int = 30  # Number of frames for fall detection
    num_keypoints: int = 17  # Number of keypoints to extract
    features_per_keypoint: int = 3  # x, y, confidence
    

@dataclass
class PoseDetectionConfig:
    """Configuration for MediaPipe pose detection."""
    
    # Selected keypoint indices from MediaPipe's 33 landmarks
    keypoint_indices: Tuple[int, ...] = (
        0,      # Nose
        2, 5,   # Left Eye, Right Eye (note: skip 1,3,4 inner/outer landmarks)
        7, 8,   # Left Ear, Right Ear
        11, 12, # Left Shoulder, Right Shoulder
        13, 14, # Left Elbow, Right Elbow
        15, 16, # Left Wrist, Right Wrist
        23, 24, # Left Hip, Right Hip
        25, 26, # Left Knee, Right Knee
        27, 28  # Left Ankle, Right Ankle
    )
    
    keypoint_names: Tuple[str, ...] = (
        'nose',
        'left_eye', 'right_eye',
        'left_ear', 'right_ear',
        'left_shoulder', 'right_shoulder',
        'left_elbow', 'right_elbow',
        'left_wrist', 'right_wrist',
        'left_hip', 'right_hip',
        'left_knee', 'right_knee',
        'left_ankle', 'right_ankle'
    )
    
    # Detection parameters
    model_complexity: int = 0  # 0=lite, 1=full, 2=heavy
    min_detection_confidence: float = 0.5
    min_tracking_confidence: float = 0.5
    min_pose_presence_confidence: float = 0.5
    
    # Normalization parameters
    min_confidence_for_normalization: float = 0.3
    static_image_mode: bool = False  # Use VIDEO mode for tracking


@dataclass
class FallDetectionConfig:
    """Configuration for fall detection logic."""
    
    confidence_threshold: float = 0.90  # Minimum probability to classify as fall
    smoothing_window_size: int = 3  # Number of frames for temporal smoothing
    

@dataclass
class VideoProcessingConfig:
    """Configuration for video processing."""
    
    default_fps: float = 25.0  # Default FPS if not available from video
    output_directory: str = str(PROJECT_ROOT / 'outputs' / 'processed_videos')
    
    # Visualization parameters
    draw_landmarks: bool = True
    draw_connections: bool = True
    landmark_color: Tuple[int, int, int] = (0, 0, 255)  # BGR: Red
    connection_color: Tuple[int, int, int] = (0, 255, 0)  # BGR: Green
    landmark_radius: int = 3
    connection_thickness: int = 2
    
    # Text overlay parameters
    font_face: int = 0  # cv2.FONT_HERSHEY_SIMPLEX
    font_scale: float = 0.6
    text_color: Tuple[int, int, int] = (255, 255, 255)  # White
    text_thickness: int = 2
    background_color_normal: Tuple[int, int, int] = (0, 128, 0)  # Green
    background_color_fall: Tuple[int, int, int] = (0, 0, 255)  # Red


@dataclass
class PathConfig:
    """Configuration for system paths."""
    
    project_root: Path = PROJECT_ROOT
    data_directory: Path = PROJECT_ROOT / 'data'
    output_directory: Path = PROJECT_ROOT / 'outputs'
    deployments_directory: Path = PROJECT_ROOT / 'deployments'
    notebooks_directory: Path = PROJECT_ROOT / 'notebooks'
    
    def ensure_directories(self):
        """Create all necessary directories if they don't exist."""
        for directory in [
            self.data_directory,
            self.output_directory / 'processed_videos',
            self.deployments_directory / 'web_app' / 'models',
            self.deployments_directory / 'edge_device' / 'models'
        ]:
            directory.mkdir(parents=True, exist_ok=True)


# MediaPipe pose connections for skeleton visualization
POSE_CONNECTIONS = [
    (0, 1), (0, 2), (1, 3), (2, 4), (5, 6), (5, 7), (7, 9), (6, 8), (8, 10),
    (11, 12), (11, 13), (13, 15), (12, 14), (14, 16), (15, 17), (16, 18),
    (15, 19), (19, 21), (16, 20), (20, 22), (11, 23), (12, 24), (23, 24),
    (23, 25), (24, 26), (25, 27), (26, 28), (27, 29), (28, 30), (29, 31),
    (30, 32)
]

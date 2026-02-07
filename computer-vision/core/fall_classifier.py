"""
Fall detection classifier module.

This module handles fall detection using a pre-trained TensorFlow Lite model
and provides utilities for feature extraction and normalization.
"""
import os
from typing import List, Tuple, Dict, Optional
from collections import deque
import numpy as np

from config.settings import ModelConfig, PoseDetectionConfig, FallDetectionConfig
from core.pose_detector import PoseLandmark, PoseDetectionResult


class KeypointFeatureExtractor:
    """
    Extracts and normalizes keypoint features for fall detection.
    
    This class handles the conversion from pose landmarks to normalized
    feature vectors suitable for the fall detection model.
    """
    
    def __init__(
        self,
        pose_config: Optional[PoseDetectionConfig] = None,
        model_config: Optional[ModelConfig] = None
    ):
        """
        Initialize feature extractor.
        
        Args:
            pose_config: Pose detection configuration
            model_config: Model configuration
        """
        self.pose_config = pose_config or PoseDetectionConfig()
        self.model_config = model_config or ModelConfig()
        
        # Create keypoint name to index mapping (sorted alphabetically)
        self.sorted_keypoint_names = sorted(self.pose_config.keypoint_names)
        self.keypoint_name_to_index = {
            name: idx for idx, name in enumerate(self.sorted_keypoint_names)
        }
        
        # Create MediaPipe index to keypoint name mapping
        self.mediapipe_index_to_name = {
            idx: name for idx, name in zip(
                self.pose_config.keypoint_indices,
                self.pose_config.keypoint_names
            )
        }
        
        self.num_keypoints = len(self.sorted_keypoint_names)
        self.num_features = self.num_keypoints * 3  # x, y, confidence
        
    def get_feature_indices(self, keypoint_name: str) -> Tuple[int, int, int]:
        """
        Get feature vector indices for a keypoint.
        
        Args:
            keypoint_name: Name of the keypoint
            
        Returns:
            Tuple of (x_index, y_index, confidence_index)
        """
        if keypoint_name not in self.keypoint_name_to_index:
            raise ValueError(
                f"Keypoint '{keypoint_name}' not found. "
                f"Available: {list(self.keypoint_name_to_index.keys())}"
            )
        
        keypoint_index = self.keypoint_name_to_index[keypoint_name]
        base_index = keypoint_index * 3
        return base_index, base_index + 1, base_index + 2
    
    def extract_raw_features(
        self,
        detection_result: PoseDetectionResult
    ) -> np.ndarray:
        """
        Extract raw features from pose detection result.
        
        Args:
            detection_result: Pose detection result
            
        Returns:
            Feature vector of shape (num_features,)
        """
        features = np.zeros(self.num_features, dtype=np.float32)
        
        if not detection_result.has_landmarks():
            return features
        
        # Extract selected keypoints and sort by name
        for mediapipe_idx, keypoint_name in self.mediapipe_index_to_name.items():
            landmark = detection_result.get_landmark(mediapipe_idx)
            if landmark is None:
                continue
                
            try:
                x_idx, y_idx, conf_idx = self.get_feature_indices(keypoint_name)
                features[x_idx] = landmark.x
                features[y_idx] = landmark.y
                features[conf_idx] = landmark.visibility
            except ValueError as error:
                print(f"Warning extracting features for {keypoint_name}: {error}")
                
        return features
    
    def normalize_features(
        self,
        raw_features: np.ndarray,
        min_confidence: Optional[float] = None
    ) -> np.ndarray:
        """
        Normalize features using body reference points.
        
        Normalization strategy:
        1. Translate all points relative to mid-hip position
        2. Scale by torso height (shoulder to hip distance)
        
        Args:
            raw_features: Raw feature vector
            min_confidence: Minimum confidence for reference points
            
        Returns:
            Normalized feature vector
        """
        if min_confidence is None:
            min_confidence = self.pose_config.min_confidence_for_normalization
        
        normalized_features = raw_features.copy()
        
        # Get reference keypoint indices
        reference_keypoints = {
            'left_shoulder': 'left_shoulder',
            'right_shoulder': 'right_shoulder',
            'left_hip': 'left_hip',
            'right_hip': 'right_hip'
        }
        
        try:
            # Extract shoulder coordinates
            ls_x_idx, ls_y_idx, ls_conf_idx = self.get_feature_indices(
                reference_keypoints['left_shoulder']
            )
            rs_x_idx, rs_y_idx, rs_conf_idx = self.get_feature_indices(
                reference_keypoints['right_shoulder']
            )
            
            # Extract hip coordinates
            lh_x_idx, lh_y_idx, lh_conf_idx = self.get_feature_indices(
                reference_keypoints['left_hip']
            )
            rh_x_idx, rh_y_idx, rh_conf_idx = self.get_feature_indices(
                reference_keypoints['right_hip']
            )
        except ValueError as error:
            print(f"Warning in normalize_features: {error}")
            return raw_features
        
        # Calculate mid-shoulder position
        ls_conf = raw_features[ls_conf_idx]
        rs_conf = raw_features[rs_conf_idx]
        
        mid_shoulder_x = np.nan
        mid_shoulder_y = np.nan
        
        if ls_conf > min_confidence and rs_conf > min_confidence:
            mid_shoulder_x = (raw_features[ls_x_idx] + raw_features[rs_x_idx]) / 2
            mid_shoulder_y = (raw_features[ls_y_idx] + raw_features[rs_y_idx]) / 2
        elif ls_conf > min_confidence:
            mid_shoulder_x = raw_features[ls_x_idx]
            mid_shoulder_y = raw_features[ls_y_idx]
        elif rs_conf > min_confidence:
            mid_shoulder_x = raw_features[rs_x_idx]
            mid_shoulder_y = raw_features[rs_y_idx]
        
        # Calculate mid-hip position (reference point)
        lh_conf = raw_features[lh_conf_idx]
        rh_conf = raw_features[rh_conf_idx]
        
        mid_hip_x = np.nan
        mid_hip_y = np.nan
        
        if lh_conf > min_confidence and rh_conf > min_confidence:
            mid_hip_x = (raw_features[lh_x_idx] + raw_features[rh_x_idx]) / 2
            mid_hip_y = (raw_features[lh_y_idx] + raw_features[rh_y_idx]) / 2
        elif lh_conf > min_confidence:
            mid_hip_x = raw_features[lh_x_idx]
            mid_hip_y = raw_features[lh_y_idx]
        elif rh_conf > min_confidence:
            mid_hip_x = raw_features[rh_x_idx]
            mid_hip_y = raw_features[rh_y_idx]
        
        # Cannot normalize without reference point
        if np.isnan(mid_hip_x) or np.isnan(mid_hip_y):
            return raw_features
        
        # Calculate torso height for scaling
        torso_height = np.nan
        if not np.isnan(mid_shoulder_y) and not np.isnan(mid_hip_y):
            torso_height = np.abs(mid_shoulder_y - mid_hip_y)
        
        # Only scale if torso height is valid and non-zero
        should_scale = not (np.isnan(torso_height) or torso_height < 1e-5)
        
        # Normalize all keypoints
        for keypoint_name in self.sorted_keypoint_names:
            try:
                x_idx, y_idx, _ = self.get_feature_indices(keypoint_name)
                
                # Translate relative to mid-hip
                normalized_features[x_idx] -= mid_hip_x
                normalized_features[y_idx] -= mid_hip_y
                
                # Scale by torso height
                if should_scale:
                    normalized_features[x_idx] /= torso_height
                    normalized_features[y_idx] /= torso_height
                    
            except ValueError:
                pass  # Skip if keypoint not found
        
        return normalized_features
    
    def process_detection(
        self,
        detection_result: PoseDetectionResult
    ) -> np.ndarray:
        """
        Complete pipeline: extract and normalize features.
        
        Args:
            detection_result: Pose detection result
            
        Returns:
            Normalized feature vector
        """
        raw_features = self.extract_raw_features(detection_result)
        normalized_features = self.normalize_features(raw_features)
        return normalized_features


class FallClassifier:
    """
    Fall detection classifier using TensorFlow Lite model.
    
    This class manages the TFLite model and processes sequences of pose
    features to detect falls.
    """
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        config: Optional[FallDetectionConfig] = None,
        model_config: Optional[ModelConfig] = None
    ):
        """
        Initialize fall classifier.
        
        Args:
            model_path: Path to TFLite model file
            config: Fall detection configuration
            model_config: Model configuration
        """
        self.config = config or FallDetectionConfig()
        self.model_config = model_config or ModelConfig()
        self.model_path = model_path or self.model_config.fall_detection_model_path
        
        # Load TFLite interpreter
        self.interpreter = self._load_model()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        
        # Verify model shape
        expected_shape = tuple(self.input_details[0]['shape'])
        if (expected_shape[1] != self.model_config.sequence_length or
            expected_shape[2] != self.model_config.num_keypoints * 
            self.model_config.features_per_keypoint):
            raise RuntimeError(
                f"Model input shape {expected_shape} does not match config: "
                f"({1}, {self.model_config.sequence_length}, "
                f"{self.model_config.num_keypoints * self.model_config.features_per_keypoint})"
            )
        
        # Feature sequence buffer
        self.feature_buffer = deque(maxlen=self.model_config.sequence_length)
        
    def _load_model(self):
        """Load TFLite model with fallback support."""
        try:
            import tflite_runtime.interpreter as tflite
            print("Using tflite-runtime interpreter")
        except ImportError:
            try:
                import tensorflow as tf
                class TFLiteWrapper:
                    Interpreter = tf.lite.Interpreter
                tflite = TFLiteWrapper
                print("Using TensorFlow's TFLite interpreter")
            except ImportError as error:
                raise RuntimeError(
                    "Neither tflite_runtime nor tensorflow is available"
                ) from error
        
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
        
        interpreter = tflite.Interpreter(model_path=self.model_path)
        interpreter.allocate_tensors()
        print(f"Loaded TFLite model: {self.model_path}")
        
        return interpreter
    
    def add_features(self, features: np.ndarray):
        """Add feature vector to the sequence buffer."""
        self.feature_buffer.append(features)
    
    def reset_buffer(self):
        """Clear the feature sequence buffer."""
        self.feature_buffer.clear()
    
    def predict(self) -> Optional[float]:
        """
        Predict fall probability from current feature sequence.
        
        Returns:
            Fall probability (0-1) or None if buffer not full
        """
        if len(self.feature_buffer) < self.model_config.sequence_length:
            return None
        
        # Prepare input for model
        sequence_array = np.array(self.feature_buffer, dtype=np.float32)
        sequence_array = np.expand_dims(sequence_array, axis=0)  # Add batch dimension
        
        # Run inference
        self.interpreter.set_tensor(self.input_details[0]['index'], sequence_array)
        self.interpreter.invoke()
        
        # Get output
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
        fall_probability = float(output_data[0][0])
        
        return fall_probability
    
    def is_fall_detected(self, probability: float) -> bool:
        """Check if probability exceeds threshold."""
        return probability >= self.config.confidence_threshold

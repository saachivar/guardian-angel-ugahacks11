"""Quick test of refactored modules."""
import sys
sys.path.insert(0, '.')

# Test imports
print('Testing imports...')
from config.settings import ModelConfig, PoseDetectionConfig
print('✓ Config imports successful')

from core.pose_detector import PoseDetector, PoseLandmark
print('✓ Pose detector imports successful')

from core.fall_classifier import FallClassifier, KeypointFeatureExtractor
print('✓ Fall classifier imports successful')

from core.video_processor import VideoProcessor, FallEvent
print('✓ Video processor imports successful')

from utils.keypoint_extractor import KeypointDatasetProcessor
print('✓ Utils imports successful')

print('\n✓ All imports successful!')

# Test configuration
print('\nTesting configuration...')
config = ModelConfig()
print(f'Model path: {config.fall_detection_model_path}')
print(f'Sequence length: {config.sequence_length}')

pose_config = PoseDetectionConfig()
print(f'Number of keypoints: {len(pose_config.keypoint_indices)}')

print('\n✓ All configuration tests passed!')

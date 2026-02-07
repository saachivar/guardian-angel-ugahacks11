"""
Quick test to verify the refactored structure works correctly.

This script tests the core modules and ensures everything imports properly.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all modules import correctly."""
    print("Testing imports...")
    
    try:
        # Config imports
        from config.settings import (
            ModelConfig,
            PoseDetectionConfig,
            FallDetectionConfig,
            VideoProcessingConfig,
            PathConfig
        )
        print("✓ Config modules imported successfully")
        
        # Core imports
        from core.pose_detector import PoseDetector, PoseLandmark
        from core.fall_classifier import FallClassifier, KeypointFeatureExtractor
        from core.video_processor import VideoProcessor, FallEvent
        print("✓ Core modules imported successfully")
        
        # Utils imports
        from utils.keypoint_extractor import KeypointDatasetProcessor
        from utils.visualization import draw_skeleton_on_image
        from utils.data_processing import split_dataset, process_csv_sequences
        print("✓ Utility modules imported successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_configurations():
    """Test configuration objects."""
    print("\nTesting configurations...")
    
    try:
        from config.settings import (
            ModelConfig,
            PoseDetectionConfig,
            FallDetectionConfig
        )
        
        model_config = ModelConfig()
        pose_config = PoseDetectionConfig()
        fall_config = FallDetectionConfig()
        
        # Verify key attributes
        assert model_config.sequence_length == 30
        assert model_config.num_keypoints == 17
        assert len(pose_config.keypoint_indices) == 17
        assert len(pose_config.keypoint_names) == 17
        assert 0.0 <= fall_config.confidence_threshold <= 1.0
        
        print("✓ Configuration objects created successfully")
        print(f"  - Sequence length: {model_config.sequence_length}")
        print(f"  - Number of keypoints: {model_config.num_keypoints}")
        print(f"  - Fall threshold: {fall_config.confidence_threshold:.1%}")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_model_loading():
    """Test model loading."""
    print("\nTesting model loading...")
    
    try:
        from core.fall_classifier import FallClassifier
        from config.settings import ModelConfig
        
        model_config = ModelConfig()
        
        # Check if model file exists
        import os
        if not os.path.exists(model_config.fall_detection_model_path):
            print(f"⚠ Model file not found: {model_config.fall_detection_model_path}")
            print("  (This is expected if you haven't trained a model yet)")
            return True
        
        # Try to load the classifier
        classifier = FallClassifier()
        print("✓ Fall classifier loaded successfully")
        print(f"  - Model path: {model_config.fall_detection_model_path}")
        
        return True
        
    except Exception as e:
        print(f"✗ Model loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_directory_structure():
    """Test that directory structure is correct."""
    print("\nTesting directory structure...")
    
    expected_dirs = [
        "config",
        "core",
        "utils",
        "deployments/web_app",
        "deployments/edge_device",
        "notebooks",
        "outputs/processed_videos"
    ]
    
    expected_files = [
        "config/__init__.py",
        "config/settings.py",
        "core/__init__.py",
        "core/pose_detector.py",
        "core/fall_classifier.py",
        "core/video_processor.py",
        "utils/__init__.py",
        "utils/keypoint_extractor.py",
        "deployments/web_app/web_interface.py",
        "deployments/edge_device/camera_detector.py",
        "demo_video_processing.py",
        "demo_extract_keypoints.py"
    ]
    
    all_exist = True
    
    for dir_path in expected_dirs:
        full_path = project_root / dir_path
        if full_path.exists():
            print(f"✓ {dir_path}/")
        else:
            print(f"✗ {dir_path}/ - NOT FOUND")
            all_exist = False
    
    for file_path in expected_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - NOT FOUND")
            all_exist = False
    
    return all_exist


def main():
    """Run all tests."""
    print("=" * 60)
    print("Fall Detection System - Structure Verification")
    print("=" * 60)
    
    results = []
    
    results.append(("Import Test", test_imports()))
    results.append(("Configuration Test", test_configurations()))
    results.append(("Model Loading Test", test_model_loading()))
    results.append(("Directory Structure Test", test_directory_structure()))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("=" * 60)
    if all_passed:
        print("✓ All tests passed! The refactored structure is ready to use.")
    else:
        print("✗ Some tests failed. Please review the errors above.")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())

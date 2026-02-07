# Fall Detection System v2.0

A comprehensive AI-powered fall detection system using MediaPipe pose estimation and transformer-based classification.

## 🏗️ Project Structure

```
fall-detection-system/
├── config/                      # Configuration modules
│   ├── __init__.py
│   └── settings.py             # Centralized configuration settings
│
├── core/                        # Core detection modules
│   ├── __init__.py
│   ├── pose_detector.py        # MediaPipe pose detection wrapper
│   ├── fall_classifier.py     # Fall classification and feature extraction
│   └── video_processor.py     # Video processing utilities
│
├── utils/                       # Utility modules
│   ├── __init__.py
│   ├── keypoint_extractor.py  # Dataset keypoint extraction
│   ├── visualization.py       # Visualization utilities
│   └── data_processing.py     # Dataset processing tools
│
├── deployments/                 # Deployment configurations
│   ├── web_app/                # Gradio web application
│   │   ├── web_interface.py
│   │   ├── requirements.txt
│   │   └── models/
│   │       └── fall_detection_transformer.tflite
│   │
│   └── edge_device/            # Raspberry Pi / edge deployment
│       ├── camera_detector.py
│       ├── requirements.txt
│       └── models/
│           └── pose_landmarker_lite.task
│
├── notebooks/                   # Jupyter notebooks for training
│   └── *.ipynb
│
├── data/                        # Dataset directory
├── outputs/                     # Generated outputs
│   └── processed_videos/
│
├── tests/                       # Unit tests
├── setup.py                     # Package setup
├── requirements.txt             # Dependencies
└── README.md                    # This file
```

## ✨ Features

- **Real-time Pose Detection**: Uses MediaPipe Tasks API for efficient pose landmark detection
- **Transformer-based Classification**: Advanced neural network for accurate fall detection
- **Multiple Deployment Options**:
  - Web interface via Gradio
  - Real-time camera detection for edge devices
- **Modular Architecture**: Clean separation of concerns with well-defined modules
- **Comprehensive Configuration**: Centralized settings management
- **Production-ready**: Proper error handling, logging, and documentation

## 📦 Installation

### Basic Installation

```bash
# Clone the repository
git clone <repository-url>
cd Fall-Detection

# Install dependencies
pip install -r requirements.txt
```

### Development Installation

```bash
# Install in development mode with all extras
pip install -e ".[web,dev,tensorflow]"
```

## 🚀 Usage

### Web Application (Gradio)

Launch the web interface for video upload and processing:

```bash
cd deployments/web_app
python web_interface.py
```

The interface will be available at `http://localhost:7860`

### Real-time Detection (Edge Devices)

Run real-time fall detection using a camera:

```bash
cd deployments/edge_device
python camera_detector.py --camera 0
```

Press 'q' to quit the detection window.

### As a Python Module

```python
from config.settings import ModelConfig, PoseDetectionConfig
from core.pose_detector import PoseDetector
from core.fall_classifier import FallClassifier, KeypointFeatureExtractor

# Initialize components
pose_config = PoseDetectionConfig()
feature_extractor = KeypointFeatureExtractor(pose_config)
fall_classifier = FallClassifier()

# Process video frame
with PoseDetector(config=pose_config) as detector:
    detection_result = detector.process_frame(frame_bgr, frame_index, fps)
    features = feature_extractor.process_detection(detection_result)
    fall_classifier.add_features(features)
    probability = fall_classifier.predict()
```

## 🎯 Model Information

### Fall Detection Model
- **Architecture**: Transformer-based sequence classifier
- **Input**: 30 frames × 51 features (17 keypoints × 3 values)
- **Output**: Binary classification (Fall / No Fall)
- **Threshold**: 90% confidence for fall detection

### Pose Detection Model
- **Backend**: MediaPipe PoseLandmarker
- **Keypoints**: 17 selected from 33 MediaPipe landmarks
- **Selected Points**: Nose, Eyes, Ears, Shoulders, Elbows, Wrists, Hips, Knees, Ankles

## ⚙️ Configuration

All configuration is centralized in `config/settings.py`:

- **ModelConfig**: Model paths and parameters
- **PoseDetectionConfig**: Pose detection settings
- **FallDetectionConfig**: Fall detection thresholds
- **VideoProcessingConfig**: Video I/O and visualization settings
- **PathConfig**: Project directory structure

Example custom configuration:

```python
from config.settings import FallDetectionConfig

config = FallDetectionConfig(
    confidence_threshold=0.85,  # Adjust sensitivity
    smoothing_window_size=5
)
```

## 📊 Dataset Processing

### Extract Keypoints from Videos

```python
from utils.keypoint_extractor import KeypointDatasetProcessor

processor = KeypointDatasetProcessor()
processor.process_dataset_directory('data/raw')
```

### Split Dataset

```python
from utils.data_processing import split_dataset

split_dataset(
    source_directory='data/processed',
    train_directory='data/train',
    test_directory='data/test',
    train_split=0.8
)
```

## 🧪 Testing

Run the test suite:

```bash
python -m pytest tests/
```

## 📝 Code Quality Improvements

### v2.0 Refactoring Highlights:

1. **Better Variable Naming**:
   - `res` → `detection_result`
   - `lm` → `landmark`
   - `kp_name` → `keypoint_name`

2. **Modular Architecture**:
   - Separated pose detection, classification, and video processing
   - Clear interfaces between components
   - Dependency injection for configuration

3. **Type Hints and Documentation**:
   - Comprehensive docstrings
   - Type annotations throughout
   - Clear parameter descriptions

4. **Configuration Management**:
   - Centralized settings
   - Dataclass-based configs
   - Environment variable support

5. **Error Handling**:
   - Proper exception handling
   - Informative error messages
   - Graceful degradation

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Use meaningful variable names
2. Add type hints to function signatures
3. Write docstrings for public APIs
4. Follow PEP 8 style guidelines
5. Add tests for new features

## 📄 License

[Your License Here]

## 🙏 Acknowledgments

- MediaPipe team for pose detection models
- TensorFlow team for TFLite runtime
- Gradio for the web interface framework

## 📬 Contact

[Your Contact Information]

---

**Version**: 2.0.0  
**Last Updated**: February 2026

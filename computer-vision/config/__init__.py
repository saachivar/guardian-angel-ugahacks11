"""
Configuration package for fall detection system.
"""
from .settings import (
    ModelConfig,
    PoseDetectionConfig,
    FallDetectionConfig,
    VideoProcessingConfig,
    PathConfig
)

__all__ = [
    'ModelConfig',
    'PoseDetectionConfig',
    'FallDetectionConfig',
    'VideoProcessingConfig',
    'PathConfig'
]

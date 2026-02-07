"""
Fall Detection System

A comprehensive fall detection system using MediaPipe pose estimation
and transformer-based classification.
"""
from setuptools import setup, find_packages

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fall-detection-system",
    version="2.0.0",
    author="Fall Detection Team",
    description="AI-powered fall detection using pose estimation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Healthcare Industry",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "mediapipe>=0.10.0",
        "opencv-python>=4.8.0",
        "numpy>=1.24.0",
    ],
    extras_require={
        "web": [
            "gradio>=3.50.0",
        ],
        "tflite": [
            "tflite-runtime>=2.14.0",
        ],
        "tensorflow": [
            "tensorflow>=2.14.0",
        ],
        "dev": [
            "jupyter>=1.0.0",
            "pandas>=2.0.0",
            "matplotlib>=3.7.0",
        ],
    },
)

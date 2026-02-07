"""
Keypoint extraction utilities for dataset processing.

This module provides tools to extract pose keypoints from videos
and save them in CSV format for training.
"""
import os
import csv
from pathlib import Path
from typing import Optional
import cv2

from config.settings import PoseDetectionConfig
from core.pose_detector import PoseDetector


class KeypointDatasetProcessor:
    """
    Process video datasets to extract pose keypoints.
    
    This class handles batch processing of video files to extract
    pose landmarks and save them as CSV files for model training.
    """
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        config: Optional[PoseDetectionConfig] = None
    ):
        """
        Initialize dataset processor.
        
        Args:
            model_path: Path to pose detection model
            config: Pose detection configuration
        """
        self.model_path = model_path
        self.config = config or PoseDetectionConfig()
        
    def extract_keypoints_from_video(
        self,
        video_path: str,
        output_csv_path: str
    ):
        """
        Extract keypoints from a single video file.
        
        Args:
            video_path: Path to input video file
            output_csv_path: Path to output CSV file
        """
        print(f"Processing video: {video_path}")
        
        # Open video
        video_capture = cv2.VideoCapture(video_path)
        if not video_capture.isOpened():
            print(f"Error: Cannot open video {video_path}")
            return
        
        fps = video_capture.get(cv2.CAP_PROP_FPS) or 25.0
        frame_index = 0
        
        # Create pose detector
        with PoseDetector(
            model_path=self.model_path,
            config=self.config,
            use_video_mode=True
        ) as detector:
            
            # Open CSV file for writing
            with open(output_csv_path, 'w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                
                # Write header
                csv_writer.writerow(["Frame", "Keypoint", "X", "Y", "Confidence"])
                
                # Process each frame
                while True:
                    success, frame_bgr = video_capture.read()
                    if not success:
                        break
                    
                    # Detect pose
                    detection_result = detector.process_frame(
                        frame_bgr,
                        frame_index,
                        fps
                    )
                    
                    # Extract selected keypoints
                    if detection_result.has_landmarks():
                        frame_height, frame_width = frame_bgr.shape[:2]
                        
                        for mediapipe_idx, keypoint_name in zip(
                            self.config.keypoint_indices,
                            self.config.keypoint_names
                        ):
                            landmark = detection_result.get_landmark(mediapipe_idx)
                            
                            if landmark:
                                pixel_x, pixel_y = landmark.to_pixel_coordinates(
                                    frame_width,
                                    frame_height
                                )
                                
                                csv_writer.writerow([
                                    frame_index + 1,  # 1-indexed frames
                                    keypoint_name,
                                    pixel_x,
                                    pixel_y,
                                    landmark.visibility
                                ])
                    
                    frame_index += 1
        
        video_capture.release()
        print(f"Saved keypoints to: {output_csv_path}")
    
    def process_dataset_directory(
        self,
        root_directory: str,
        categories: tuple = ('Fall', 'No_Fall'),
        video_subdirectory: str = 'Raw_Video',
        output_subdirectory: str = 'Processed_CSV'
    ):
        """
        Process an entire dataset directory structure.
        
        Expected structure:
        root_directory/
            Fall/
                Raw_Video/
                    video1.mp4
                    video2.mp4
            No_Fall/
                Raw_Video/
                    video1.mp4
                    video2.mp4
        
        Args:
            root_directory: Root directory of dataset
            categories: Category subdirectories to process
            video_subdirectory: Subdirectory containing videos
            output_subdirectory: Subdirectory for output CSV files
        """
        root_path = Path(root_directory)
        print(f"Starting dataset processing in: {root_path}")
        
        for category in categories:
            category_path = root_path / category
            
            if not category_path.exists():
                print(f"Warning: Category directory not found, skipping: {category_path}")
                continue
            
            video_directory = category_path / video_subdirectory
            if not video_directory.exists():
                print(f"Warning: Video directory not found, skipping: {video_directory}")
                continue
            
            # Create output directory
            output_directory = category_path / output_subdirectory
            output_directory.mkdir(parents=True, exist_ok=True)
            
            # Process all video files
            video_extensions = {'.mp4', '.avi', '.mov', '.mkv'}
            video_files = [
                f for f in video_directory.iterdir()
                if f.is_file() and f.suffix.lower() in video_extensions
            ]
            
            print(f"\nProcessing category '{category}': {len(video_files)} videos found")
            
            for video_file in video_files:
                output_csv = output_directory / f"{video_file.stem}.csv"
                
                try:
                    self.extract_keypoints_from_video(
                        str(video_file),
                        str(output_csv)
                    )
                except Exception as error:
                    print(f"Error processing {video_file.name}: {error}")
        
        print("\nDataset processing complete!")

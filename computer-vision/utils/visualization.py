"""
Visualization utilities for pose and fall detection.
"""
import cv2
import numpy as np
from typing import List, Tuple

from config.settings import POSE_CONNECTIONS


def draw_skeleton_on_image(
    image_bgr: np.ndarray,
    landmarks: List[Tuple[float, float]],
    landmark_color: Tuple[int, int, int] = (0, 0, 255),
    connection_color: Tuple[int, int, int] = (0, 255, 0),
    landmark_radius: int = 3,
    connection_thickness: int = 2
):
    """
    Draw pose skeleton on an image.
    
    Args:
        image_bgr: BGR image to draw on (modified in-place)
        landmarks: List of (x, y) normalized coordinates
        landmark_color: BGR color for landmark points
        connection_color: BGR color for connections
        landmark_radius: Radius of landmark circles
        connection_thickness: Thickness of connection lines
    """
    if len(landmarks) == 0:
        return
    
    image_height, image_width = image_bgr.shape[:2]
    
    # Convert normalized coordinates to pixels
    pixel_landmarks = []
    for x_norm, y_norm in landmarks:
        pixel_x = int(x_norm * image_width)
        pixel_y = int(y_norm * image_height)
        pixel_landmarks.append((pixel_x, pixel_y))
    
    # Draw connections
    for start_idx, end_idx in POSE_CONNECTIONS:
        if start_idx < len(pixel_landmarks) and end_idx < len(pixel_landmarks):
            cv2.line(
                image_bgr,
                pixel_landmarks[start_idx],
                pixel_landmarks[end_idx],
                connection_color,
                connection_thickness
            )
    
    # Draw landmarks
    for pixel_x, pixel_y in pixel_landmarks:
        cv2.circle(
            image_bgr,
            (pixel_x, pixel_y),
            landmark_radius,
            landmark_color,
            -1
        )

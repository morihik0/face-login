"""
Face detection service module.

This module provides functions for detecting faces in images,
validating face images, and extracting face encodings.
"""
import logging
import cv2
import numpy as np
import face_recognition

# Configure logger
logger = logging.getLogger(__name__)

class FaceDetectionError(Exception):
    """Exception raised when no faces are detected in an image."""
    pass

class MultipleFacesError(Exception):
    """Exception raised when multiple faces are detected in an image."""
    pass

class ImageQualityError(Exception):
    """Exception raised when the image quality is too low."""
    pass

def detect_faces(image):
    """
    Detect faces in an image.
    
    Args:
        image (numpy.ndarray): OpenCV format image data
        
    Returns:
        list: List of face locations in (top, right, bottom, left) format
        
    Raises:
        ValueError: If the image data is invalid
        FaceDetectionError: If no faces are detected in the image
    """
    if image is None or not isinstance(image, np.ndarray):
        logger.error("Invalid image data provided")
        raise ValueError("Invalid image data provided")
    
    # Convert BGR to RGB (face_recognition uses RGB)
    if len(image.shape) == 3 and image.shape[2] == 3:
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    else:
        rgb_image = image
    
    # Detect faces using face_recognition library
    face_locations = face_recognition.face_locations(rgb_image)
    
    if not face_locations:
        logger.warning("No faces detected in the image")
        raise FaceDetectionError("No faces detected in the image")
    
    logger.info(f"Detected {len(face_locations)} faces in the image")
    return face_locations

def detect_single_face(image):
    """
    Detect a single face in an image.
    
    Args:
        image (numpy.ndarray): OpenCV format image data
        
    Returns:
        tuple: Face location in (top, right, bottom, left) format
        
    Raises:
        ValueError: If the image data is invalid
        FaceDetectionError: If no faces are detected in the image
        MultipleFacesError: If multiple faces are detected in the image
    """
    # Detect all faces in the image
    face_locations = detect_faces(image)
    
    # Check if multiple faces are detected
    if len(face_locations) > 1:
        logger.warning(f"Multiple faces detected in the image: {len(face_locations)}")
        raise MultipleFacesError(f"Multiple faces detected in the image: {len(face_locations)}")
    
    # Return the single face location
    return face_locations[0]
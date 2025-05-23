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

def validate_face_image(image):
    """
    Validate if a face image is suitable for registration or authentication.
    
    Args:
        image (numpy.ndarray): OpenCV format image data
        
    Returns:
        tuple: (is_valid, message) where is_valid is a boolean indicating if the image is valid,
               and message is a string explaining the validation result
        
    Raises:
        ValueError: If the image data is invalid
    """
    if image is None or not isinstance(image, np.ndarray):
        logger.error("Invalid image data provided")
        raise ValueError("Invalid image data provided")
    
    # Check image size
    if image.shape[0] < 100 or image.shape[1] < 100:
        logger.warning("Image is too small")
        return False, "Image is too small (minimum 100x100 pixels)"
    
    # Check image brightness
    if len(image.shape) == 3 and image.shape[2] == 3:
        # Convert to grayscale if it's a color image
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(gray, cv2.COLOR_RGB2GRAY)
    else:
        gray = image
    
    brightness = np.mean(gray)
    if brightness < 50:
        logger.warning(f"Image is too dark (brightness: {brightness:.2f})")
        return False, f"Image is too dark (brightness: {brightness:.2f})"
    elif brightness > 200:
        logger.warning(f"Image is too bright (brightness: {brightness:.2f})")
        return False, f"Image is too bright (brightness: {brightness:.2f})"
    
    # Check for face detection
    try:
        face_locations = detect_faces(image)
    except FaceDetectionError:
        logger.warning("No face detected in the image")
        return False, "No face detected in the image"
    
    # Check for multiple faces
    if len(face_locations) > 1:
        logger.warning(f"Multiple faces detected in the image: {len(face_locations)}")
        return False, f"Multiple faces detected in the image: {len(face_locations)}"
    
    # Check face size relative to image
    face_location = face_locations[0]
    top, right, bottom, left = face_location
    face_height = bottom - top
    face_width = right - left
    
    # Face should be at least 20% of the image height
    min_face_height = image.shape[0] * 0.2
    min_face_width = image.shape[1] * 0.2
    
    if face_height < min_face_height or face_width < min_face_width:
        logger.warning(f"Face is too small in the image (height: {face_height}, width: {face_width})")
        return False, "Face is too small in the image"
    
    # Check if face is too close to the edge
    edge_margin = 10  # pixels
    if (top < edge_margin or left < edge_margin or
        bottom > image.shape[0] - edge_margin or right > image.shape[1] - edge_margin):
        logger.warning("Face is too close to the edge of the image")
        return False, "Face is too close to the edge of the image"
    
    logger.info("Image validation successful")
    return True, "Image is valid for face recognition"
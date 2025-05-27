"""
Face recognition service module.

This module provides functions for face recognition, including
retrieving user encodings, comparing faces, and authenticating users.
"""
import logging
import os
import uuid
import cv2
import numpy as np
import face_recognition
from datetime import datetime
from app.database.models import FaceEncoding, User, AuthLog
from app.config import FACE_RECOGNITION, STORAGE
from app.services.face_detection import extract_face_encoding, FaceDetectionError, MultipleFacesError, ImageQualityError

# Configure logger
logger = logging.getLogger(__name__)

def get_user_encodings(user_id):
    """
    Get all face encodings for a specific user.
    
    Args:
        user_id (int): The ID of the user.
        
    Returns:
        list: A list of face encodings (numpy arrays) for the user.
        
    Raises:
        ValueError: If the user_id is invalid.
    """
    if not user_id or not isinstance(user_id, int):
        logger.error(f"Invalid user_id provided: {user_id}")
        raise ValueError(f"Invalid user_id provided: {user_id}")
    
    # Check if user exists
    user = User.get_by_id(user_id)
    if not user:
        logger.error(f"User not found with ID: {user_id}")
        raise ValueError(f"User not found with ID: {user_id}")
    
    # Get face encodings from database
    face_encoding_objects = FaceEncoding.get_by_user_id(user_id)
    
    if not face_encoding_objects:
        logger.warning(f"No face encodings found for user ID: {user_id}")
        return []
    
    # Extract the encoding arrays from the FaceEncoding objects
    encodings = [obj.encoding for obj in face_encoding_objects if obj.encoding is not None]
    
    logger.info(f"Retrieved {len(encodings)} face encodings for user ID: {user_id}")
    return encodings

def get_recognition_threshold():
    """
    Get the current face recognition threshold value.
    
    Returns:
        float: The current threshold value.
    """
    return FACE_RECOGNITION['threshold']

def compare_faces(known_encodings, face_encoding, tolerance=None):
    """
    Compare a face encoding against a list of known face encodings.
    
    Args:
        known_encodings (list): List of known face encodings (numpy arrays).
        face_encoding (numpy.ndarray): The face encoding to compare.
        tolerance (float, optional): The tolerance for face comparison.
                                    Lower values are more strict. Default is 0.6.
        
    Returns:
        tuple: (match_found, best_match_index, confidence)
            - match_found (bool): True if a match is found, False otherwise.
            - best_match_index (int): Index of the best match in known_encodings, or -1 if no match.
            - confidence (float): Confidence score of the best match (1.0 is perfect match), or 0.0 if no match.
        
    Raises:
        ValueError: If the inputs are invalid.
    """
    # Use the configured threshold if not specified
    if tolerance is None:
        tolerance = get_recognition_threshold()
        
    if not known_encodings or not isinstance(known_encodings, list):
        logger.error("Invalid known_encodings provided: empty or not a list")
        raise ValueError("Invalid known_encodings provided: empty or not a list")
    
    if face_encoding is None or not isinstance(face_encoding, (list, np.ndarray)):
        logger.error("Invalid face_encoding provided")
        raise ValueError("Invalid face_encoding provided")
    
    if not known_encodings:
        logger.warning("No known encodings provided for comparison")
        return False, -1, 0.0
    
    # Convert to numpy arrays if they are lists
    if isinstance(face_encoding, list):
        face_encoding = np.array(face_encoding)
    
    known_encodings_np = []
    for encoding in known_encodings:
        if isinstance(encoding, list):
            known_encodings_np.append(np.array(encoding))
        else:
            known_encodings_np.append(encoding)
    
    # Compare faces
    matches = face_recognition.compare_faces(known_encodings_np, face_encoding, tolerance=tolerance)
    
    # Calculate face distances
    face_distances = face_recognition.face_distance(known_encodings_np, face_encoding)
    
    # Find the best match
    if len(face_distances) > 0:
        best_match_index = np.argmin(face_distances)
        best_match_distance = face_distances[best_match_index]
        
        # Convert distance to confidence (1.0 is perfect match, 0.0 is no match)
        # Using a simple linear conversion: confidence = 1 - distance
        confidence = max(0.0, 1.0 - best_match_distance)
        
        match_found = matches[best_match_index] if len(matches) > 0 else False
        
        logger.info(f"Face comparison result: match_found={match_found}, best_match_index={best_match_index}, confidence={confidence:.4f}")
        return match_found, best_match_index, confidence
    else:
        logger.warning("No face distances calculated")
        return False, -1, 0.0

def register_face(user_id, image):
    """
    Register a face for a user.
    
    Args:
        user_id (int): The ID of the user.
        image (numpy.ndarray): OpenCV format image data.
        
    Returns:
        FaceEncoding: The created face encoding object.
        
    Raises:
        ValueError: If the user_id is invalid or the user has reached the maximum number of faces.
        FaceDetectionError: If no faces are detected in the image.
        MultipleFacesError: If multiple faces are detected in the image.
        ImageQualityError: If the image quality is too low.
    """
    if not user_id or not isinstance(user_id, int):
        logger.error(f"Invalid user_id provided: {user_id}")
        raise ValueError(f"Invalid user_id provided: {user_id}")
    
    # Check if user exists
    user = User.get_by_id(user_id)
    if not user:
        logger.error(f"User not found with ID: {user_id}")
        raise ValueError(f"User not found with ID: {user_id}")
    
    # Check if user has reached the maximum number of faces
    max_faces = FACE_RECOGNITION['max_faces_per_user']
    current_faces_count = FaceEncoding.count_by_user_id(user_id)
    
    if current_faces_count >= max_faces:
        logger.error(f"User {user_id} has reached the maximum number of faces ({max_faces})")
        raise ValueError(f"User has reached the maximum number of faces ({max_faces})")
    
    # Validate image and extract face encoding
    try:
        face_encoding = extract_face_encoding(image)
    except (FaceDetectionError, MultipleFacesError) as e:
        logger.error(f"Face detection error: {str(e)}")
        raise
    except ValueError as e:
        logger.error(f"Invalid image: {str(e)}")
        raise ImageQualityError(f"Invalid image: {str(e)}")
    
    # Save the image file
    face_images_dir = STORAGE['face_images_dir']
    os.makedirs(face_images_dir, exist_ok=True)
    
    # Generate a unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    filename = f"user_{user_id}_{timestamp}_{unique_id}.jpg"
    image_path = os.path.join(face_images_dir, filename)
    
    # Save the image
    cv2.imwrite(image_path, image)
    logger.info(f"Face image saved to {image_path}")
    
    # Save the face encoding to the database
    try:
        face_encoding_obj = FaceEncoding.create(user_id, face_encoding.tolist(), image_path)
        logger.info(f"Face encoding registered for user {user_id}")
        return face_encoding_obj
    except Exception as e:
        # If there's an error saving to the database, delete the image file
        if os.path.exists(image_path):
            os.remove(image_path)
        logger.error(f"Error registering face encoding: {str(e)}")
        raise

def authenticate_face(image):
    """
    Authenticate a face against all registered users.
    
    Args:
        image (numpy.ndarray): OpenCV format image data.
        
    Returns:
        tuple: (success, user_id, confidence)
            - success (bool): True if authentication was successful, False otherwise.
            - user_id (int): The ID of the authenticated user, or None if authentication failed.
            - confidence (float): The confidence score of the authentication (0.0 to 1.0).
        
    Raises:
        FaceDetectionError: If no faces are detected in the image.
        MultipleFacesError: If multiple faces are detected in the image.
        ImageQualityError: If the image quality is too low.
    """
    # Extract face encoding from the image
    try:
        face_encoding = extract_face_encoding(image)
    except (FaceDetectionError, MultipleFacesError) as e:
        logger.error(f"Face detection error during authentication: {str(e)}")
        raise
    except ValueError as e:
        logger.error(f"Invalid image during authentication: {str(e)}")
        raise ImageQualityError(f"Invalid image: {str(e)}")
    
    # Get all users
    users = User.get_all()
    if not users:
        logger.warning("No users found in the database for authentication")
        return False, None, 0.0
    
    best_match_user_id = None
    best_match_confidence = 0.0
    threshold = get_recognition_threshold()
    
    # Compare with each user's face encodings
    for user in users:
        # Get user's face encodings
        user_encodings = get_user_encodings(user.id)
        
        if not user_encodings:
            logger.debug(f"User {user.id} has no face encodings")
            continue
        
        # Compare faces
        match_found, _, confidence = compare_faces(user_encodings, face_encoding, tolerance=threshold)
        
        logger.debug(f"User {user.id} match result: {match_found}, confidence: {confidence:.4f}")
        
        # If match found and confidence is higher than previous matches
        if match_found and confidence > best_match_confidence:
            best_match_user_id = user.id
            best_match_confidence = confidence
    
    # Determine authentication result
    success = best_match_user_id is not None
    
    # Log the authentication attempt
    try:
        AuthLog.create(
            user_id=best_match_user_id,
            success=success,
            confidence=best_match_confidence if success else None
        )
        logger.info(f"Authentication {'successful' if success else 'failed'}, user_id: {best_match_user_id}, confidence: {best_match_confidence:.4f}")
    except Exception as e:
        logger.error(f"Error logging authentication attempt: {str(e)}")
    
    return success, best_match_user_id, best_match_confidence
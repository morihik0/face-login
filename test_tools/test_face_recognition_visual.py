"""
Visual test script for face recognition functions.

This script provides a visual demonstration of the face recognition service,
including face registration and authentication with visual feedback.
"""
import cv2
import numpy as np
import os
import sys
import logging
import sqlite3
from datetime import datetime

from app.database.db import init_db, get_db_connection
from app.database.models import User, FaceEncoding, AuthLog
from app.services.face_detection import (
    detect_faces,
    detect_single_face,
    validate_face_image,
    extract_face_encoding,
    FaceDetectionError,
    MultipleFacesError
)
from app.services.face_recognition import (
    register_face,
    authenticate_face,
    get_recognition_threshold,
    set_recognition_threshold
)
from app.config import DATABASE, STORAGE

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test users data
TEST_USERS = [
    {"name": "Test User 1", "email": "user1@example.com"},
    {"name": "Test User 2", "email": "user2@example.com"},
]

def setup_test_environment():
    """Set up the test environment by initializing the database and creating test users."""
    print("Setting up test environment...")
    
    # Initialize database
    if not init_db():
        print("Failed to initialize database")
        return False
    
    # Create test directory for face images
    os.makedirs(STORAGE['face_images_dir'], exist_ok=True)
    
    # Create test users
    created_users = []
    for user_data in TEST_USERS:
        try:
            # Check if user already exists
            user = User.get_by_email(user_data["email"])
            if user:
                print(f"User {user_data['name']} already exists with ID: {user.id}")
                created_users.append(user)
            else:
                # Create new user
                user = User.create(user_data["name"], user_data["email"])
                print(f"Created user {user.name} with ID: {user.id}")
                created_users.append(user)
        except Exception as e:
            print(f"Error creating user {user_data['name']}: {e}")
    
    return created_users

def register_test_faces(users):
    """Register test faces for the given users."""
    print("\nRegistering test faces...")
    
    # Test images
    test_images = {
        "single_face": "tests/test_images/single_face_test.jpg",
        "test_face": "tests/test_images/test_face.jpg",
    }
    
    # Check if test images exist
    for name, path in test_images.items():
        if not os.path.exists(path):
            print(f"Error: Test image not found at {path}")
            return False
    
    # Register faces for users
    registered_faces = []
    
    # Register single_face.jpg for user 1
    if len(users) > 0:
        user1 = users[0]
        try:
            image = cv2.imread(test_images["single_face"])
            if image is None:
                print(f"Error: Could not read image from {test_images['single_face']}")
                return False
            
            print(f"Registering face for {user1.name} (ID: {user1.id})...")
            face_encoding = register_face(user1.id, image)
            print(f"Face registered successfully with ID: {face_encoding.id}")
            registered_faces.append({
                "user": user1,
                "image_path": test_images["single_face"],
                "encoding_id": face_encoding.id
            })
        except Exception as e:
            print(f"Error registering face for {user1.name}: {e}")
    
    # Register test_face.jpg for user 2
    if len(users) > 1:
        user2 = users[1]
        try:
            image = cv2.imread(test_images["test_face"])
            if image is None:
                print(f"Error: Could not read image from {test_images['test_face']}")
                return False
            
            print(f"Registering face for {user2.name} (ID: {user2.id})...")
            face_encoding = register_face(user2.id, image)
            print(f"Face registered successfully with ID: {face_encoding.id}")
            registered_faces.append({
                "user": user2,
                "image_path": test_images["test_face"],
                "encoding_id": face_encoding.id
            })
        except Exception as e:
            print(f"Error registering face for {user2.name}: {e}")
    
    return registered_faces

def test_authentication(registered_faces):
    """Test face authentication with registered faces and visualize results."""
    print("\nTesting face authentication...")
    
    if not registered_faces:
        print("No registered faces to test authentication with")
        return
    
    # Create output directory for results
    output_dir = "tests/test_images/auth_results"
    os.makedirs(output_dir, exist_ok=True)
    
    # Test authentication with each registered face
    for face_data in registered_faces:
        user = face_data["user"]
        image_path = face_data["image_path"]
        
        print(f"\nTesting authentication with {image_path} (registered to {user.name})...")
        
        # Load the image
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: Could not read image from {image_path}")
            continue
        
        # Authenticate the face
        try:
            success, user_id, confidence = authenticate_face(image)
            
            # Create a copy of the image for visualization
            result_image = image.copy()
            
            # Draw face detection rectangle
            try:
                face_location = detect_single_face(image)
                top, right, bottom, left = face_location
                
                # Draw rectangle around the face
                cv2.rectangle(result_image, (left, top), (right, bottom), (0, 255, 0), 2)
                
                # Add authentication result text
                if success:
                    authenticated_user = User.get_by_id(user_id)
                    text = f"Authenticated: {authenticated_user.name}"
                    color = (0, 255, 0)  # Green for success
                else:
                    text = "Authentication failed"
                    color = (0, 0, 255)  # Red for failure
                
                # Add confidence score
                conf_text = f"Confidence: {confidence:.2f}"
                
                # Put text on the image
                cv2.putText(result_image, text, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                cv2.putText(result_image, conf_text, (left, bottom + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                # Save the result image
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                result_path = os.path.join(output_dir, f"auth_result_{os.path.basename(image_path)}_{timestamp}.jpg")
                cv2.imwrite(result_path, result_image)
                print(f"Authentication result saved to {result_path}")
                
                # Print authentication result
                if success:
                    print(f"Authentication successful! User: {authenticated_user.name}, Confidence: {confidence:.2f}")
                else:
                    print(f"Authentication failed. Confidence: {confidence:.2f}")
                
            except (FaceDetectionError, MultipleFacesError) as e:
                print(f"Error detecting face for visualization: {e}")
            
        except Exception as e:
            print(f"Error during authentication: {e}")
    
    # Test authentication with unregistered face
    unregistered_face_path = "tests/test_images/multi_face.jpg"
    if os.path.exists(unregistered_face_path):
        print(f"\nTesting authentication with unregistered face: {unregistered_face_path}...")
        
        # Load the image
        image = cv2.imread(unregistered_face_path)
        if image is None:
            print(f"Error: Could not read image from {unregistered_face_path}")
            return
        
        # Authenticate the face
        try:
            success, user_id, confidence = authenticate_face(image)
            
            # Create a copy of the image for visualization
            result_image = image.copy()
            
            # Draw face detection rectangles
            try:
                face_locations = detect_faces(image)
                
                for face_location in face_locations:
                    top, right, bottom, left = face_location
                    
                    # Draw rectangle around the face
                    cv2.rectangle(result_image, (left, top), (right, bottom), (0, 0, 255), 2)
                
                # Add authentication result text
                if success:
                    authenticated_user = User.get_by_id(user_id)
                    text = f"Authenticated: {authenticated_user.name}"
                    color = (0, 255, 0)  # Green for success
                else:
                    text = "Authentication failed"
                    color = (0, 0, 255)  # Red for failure
                
                # Add confidence score
                conf_text = f"Confidence: {confidence:.2f}"
                
                # Put text on the image
                cv2.putText(result_image, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                cv2.putText(result_image, conf_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                
                # Save the result image
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                result_path = os.path.join(output_dir, f"auth_result_unregistered_{timestamp}.jpg")
                cv2.imwrite(result_path, result_image)
                print(f"Authentication result saved to {result_path}")
                
                # Print authentication result
                if success:
                    print(f"Authentication successful! User: {authenticated_user.name}, Confidence: {confidence:.2f}")
                    print("Warning: Expected authentication failure for unregistered face")
                else:
                    print(f"Authentication failed as expected. Confidence: {confidence:.2f}")
                
            except Exception as e:
                print(f"Error detecting face for visualization: {e}")
            
        except Exception as e:
            print(f"Error during authentication: {e}")

def test_threshold_adjustment():
    """Test the threshold adjustment feature and visualize its effect on authentication."""
    print("\nTesting threshold adjustment...")
    
    # Test image
    test_image_path = "tests/test_images/test_face.jpg"
    if not os.path.exists(test_image_path):
        print(f"Error: Test image not found at {test_image_path}")
        return
    
    # Load the image
    image = cv2.imread(test_image_path)
    if image is None:
        print(f"Error: Could not read image from {test_image_path}")
        return
    
    # Create output directory for results
    output_dir = "tests/test_images/threshold_results"
    os.makedirs(output_dir, exist_ok=True)
    
    # Test different threshold values
    thresholds = [0.4, 0.6, 0.8]
    
    for threshold in thresholds:
        print(f"\nTesting with threshold: {threshold}")
        
        # Set the threshold
        set_recognition_threshold(threshold)
        current_threshold = get_recognition_threshold()
        print(f"Current threshold: {current_threshold}")
        
        # Authenticate the face
        try:
            success, user_id, confidence = authenticate_face(image)
            
            # Create a copy of the image for visualization
            result_image = image.copy()
            
            # Draw face detection rectangle
            try:
                face_location = detect_single_face(image)
                top, right, bottom, left = face_location
                
                # Draw rectangle around the face
                cv2.rectangle(result_image, (left, top), (right, bottom), (0, 255, 0), 2)
                
                # Add authentication result text
                if success:
                    authenticated_user = User.get_by_id(user_id)
                    text = f"Authenticated: {authenticated_user.name}"
                    color = (0, 255, 0)  # Green for success
                else:
                    text = "Authentication failed"
                    color = (0, 0, 255)  # Red for failure
                
                # Add threshold and confidence information
                threshold_text = f"Threshold: {threshold:.2f}"
                conf_text = f"Confidence: {confidence:.2f}"
                
                # Put text on the image
                cv2.putText(result_image, text, (left, top - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                cv2.putText(result_image, threshold_text, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                cv2.putText(result_image, conf_text, (left, bottom + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                # Save the result image
                result_path = os.path.join(output_dir, f"threshold_{threshold:.2f}_result.jpg")
                cv2.imwrite(result_path, result_image)
                print(f"Threshold test result saved to {result_path}")
                
                # Print authentication result
                if success:
                    print(f"Authentication successful! User: {authenticated_user.name}, Confidence: {confidence:.2f}")
                else:
                    print(f"Authentication failed. Confidence: {confidence:.2f}")
                
            except (FaceDetectionError, MultipleFacesError) as e:
                print(f"Error detecting face for visualization: {e}")
            
        except Exception as e:
            print(f"Error during authentication: {e}")
    
    # Reset threshold to default
    set_recognition_threshold(0.6)
    print(f"Reset threshold to default: {get_recognition_threshold()}")

def main():
    """Main function to run the visual face recognition tests."""
    print("Starting visual face recognition tests...")
    
    # Setup test environment
    users = setup_test_environment()
    if not users:
        print("Failed to set up test environment")
        return
    
    # Register test faces
    registered_faces = register_test_faces(users)
    if not registered_faces:
        print("Failed to register test faces")
        return
    
    # Test authentication
    test_authentication(registered_faces)
    
    # Test threshold adjustment
    test_threshold_adjustment()
    
    print("\nVisual face recognition tests completed!")
    print("Results are saved in the tests/test_images/auth_results and tests/test_images/threshold_results directories.")

if __name__ == "__main__":
    main()
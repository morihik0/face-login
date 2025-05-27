"""
Test script for face detection functions using real test images.
"""
import cv2
import numpy as np
import os
import sys
from app.services.face_detection import (
    detect_faces,
    detect_single_face,
    validate_face_image,
    extract_face_encoding,
    FaceDetectionError,
    MultipleFacesError
)

def main():
    """Main function to test face detection with real images."""
    print("Testing face detection functions with real images...")
    
    # Test with single face image
    single_face_path = 'tests/test_images/single_face_test.jpg'
    if not os.path.exists(single_face_path):
        print(f"Error: Test image not found at {single_face_path}")
        return
    
    print(f"\nTesting with single face image: {single_face_path}")
    single_face_image = cv2.imread(single_face_path)
    if single_face_image is None:
        print(f"Error: Could not read image from {single_face_path}")
        return
    
    print(f"Image shape: {single_face_image.shape}")
    
    try:
        # Test detect_faces
        print("\nTesting detect_faces function...")
        face_locations = detect_faces(single_face_image)
        print(f"Detected {len(face_locations)} faces")
        
        # Draw rectangles around detected faces
        result_image = single_face_image.copy()
        for face_location in face_locations:
            top, right, bottom, left = face_location
            cv2.rectangle(result_image, (left, top), (right, bottom), (0, 255, 0), 2)
        
        # Save result image
        result_path = 'tests/test_images/single_face_result.jpg'
        cv2.imwrite(result_path, result_image)
        print(f"Result saved to {result_path}")
        
        # Test detect_single_face
        print("\nTesting detect_single_face function...")
        face_location = detect_single_face(single_face_image)
        print(f"Detected single face at {face_location}")
        
    except FaceDetectionError as e:
        print(f"FaceDetectionError: {e}")
    except MultipleFacesError as e:
        print(f"MultipleFacesError: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    # Test with multiple faces image
    multi_face_path = 'tests/test_images/multi_face_test.jpg'
    if not os.path.exists(multi_face_path):
        print(f"Error: Test image not found at {multi_face_path}")
        return
    
    print(f"\nTesting with multiple faces image: {multi_face_path}")
    multi_face_image = cv2.imread(multi_face_path)
    if multi_face_image is None:
        print(f"Error: Could not read image from {multi_face_path}")
        return
    
    print(f"Image shape: {multi_face_image.shape}")
    
    try:
        # Test detect_faces
        print("\nTesting detect_faces function...")
        face_locations = detect_faces(multi_face_image)
        print(f"Detected {len(face_locations)} faces")
        
        # Draw rectangles around detected faces
        result_image = multi_face_image.copy()
        for face_location in face_locations:
            top, right, bottom, left = face_location
            cv2.rectangle(result_image, (left, top), (right, bottom), (0, 255, 0), 2)
        
        # Save result image
        result_path = 'tests/test_images/multi_face_result.jpg'
        cv2.imwrite(result_path, result_image)
        print(f"Result saved to {result_path}")
        
        # Test detect_single_face
        print("\nTesting detect_single_face function...")
        try:
            face_location = detect_single_face(multi_face_image)
            print(f"Detected single face at {face_location}")
            print("Warning: Expected MultipleFacesError was not raised")
        except MultipleFacesError as e:
            print(f"MultipleFacesError raised as expected: {e}")
        
    except FaceDetectionError as e:
        print(f"FaceDetectionError: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    # Test with multiple faces image
    multi_face_path = 'tests/test_images/multi_face_test.jpg'
    if not os.path.exists(multi_face_path):
        print(f"Error: Test image not found at {multi_face_path}")
        return
    
    print(f"\nTesting with multiple faces image: {multi_face_path}")
    multi_face_image = cv2.imread(multi_face_path)
    if multi_face_image is None:
        print(f"Error: Could not read image from {multi_face_path}")
        return
    
    print(f"Image shape: {multi_face_image.shape}")
    
    try:
        # Test detect_faces
        print("\nTesting detect_faces function...")
        face_locations = detect_faces(multi_face_image)
        print(f"Detected {len(face_locations)} faces")
        
        # Draw rectangles around detected faces
        result_image = multi_face_image.copy()
        for face_location in face_locations:
            top, right, bottom, left = face_location
            cv2.rectangle(result_image, (left, top), (right, bottom), (0, 255, 0), 2)
        
        # Save result image
        result_path = 'tests/test_images/multi_face_result.jpg'
        cv2.imwrite(result_path, result_image)
        print(f"Result saved to {result_path}")
        
        # Test detect_single_face
        print("\nTesting detect_single_face function...")
        try:
            face_location = detect_single_face(multi_face_image)
            print(f"Detected single face at {face_location}")
            print("Warning: Expected MultipleFacesError was not raised")
        except MultipleFacesError as e:
            print(f"MultipleFacesError raised as expected: {e}")
        
    except FaceDetectionError as e:
        print(f"FaceDetectionError: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    # Test validate_face_image with single face image
    print("\nTesting validate_face_image with single face image...")
    is_valid, message = validate_face_image(single_face_image)
    print(f"Validation result: {is_valid}, Message: {message}")
    
    # Test validate_face_image with multiple faces image
    print("\nTesting validate_face_image with multiple faces image...")
    is_valid, message = validate_face_image(multi_face_image)
    print(f"Validation result: {is_valid}, Message: {message}")
    
    # Test validate_face_image with a small image
    print("\nTesting validate_face_image with a small image...")
    small_image = cv2.resize(single_face_image, (50, 50))
    is_valid, message = validate_face_image(small_image)
    print(f"Validation result: {is_valid}, Message: {message}")
    
    # Test validate_face_image with a dark image
    print("\nTesting validate_face_image with a dark image...")
    dark_image = cv2.convertScaleAbs(single_face_image, alpha=0.2, beta=0)
    is_valid, message = validate_face_image(dark_image)
    print(f"Validation result: {is_valid}, Message: {message}")
    
    # Test extract_face_encoding with single face image
    print("\nTesting extract_face_encoding with single face image...")
    try:
        encoding = extract_face_encoding(single_face_image)
        print(f"Face encoding extracted successfully. Shape: {encoding.shape}")
        print(f"First 10 values: {encoding[:10]}")
    except Exception as e:
        print(f"Error extracting face encoding: {e}")
    
    # Test extract_face_encoding with multiple faces image
    print("\nTesting extract_face_encoding with multiple faces image...")
    try:
        encoding = extract_face_encoding(multi_face_image)
        print(f"Face encoding extracted successfully. Shape: {encoding.shape}")
        print(f"First 10 values: {encoding[:10]}")
    except Exception as e:
        print(f"Error extracting face encoding: {e}")

if __name__ == "__main__":
    main()
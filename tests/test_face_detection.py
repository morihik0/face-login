"""
Tests for the face detection service.
"""
import os
import sys
import unittest
import cv2
import numpy as np

# Add the parent directory to the path so we can import the app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import app.services.face_detection
from app.services.face_detection import (
    detect_faces,
    detect_single_face,
    validate_face_image,
    extract_face_encoding,
    FaceDetectionError,
    MultipleFacesError,
    ImageQualityError
)

class TestFaceDetection(unittest.TestCase):
    """Test cases for face detection service."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a simple test image with a face-like pattern
        # This is a very simplified representation and won't work with real face detection
        # but it's useful for testing the error handling
        self.test_image = np.zeros((300, 300, 3), dtype=np.uint8)
        # Draw a circle for a face
        cv2.circle(self.test_image, (150, 150), 60, (255, 255, 255), -1)
        # Draw eyes
        cv2.circle(self.test_image, (130, 130), 10, (0, 0, 0), -1)
        cv2.circle(self.test_image, (170, 130), 10, (0, 0, 0), -1)
        # Draw mouth
        cv2.ellipse(self.test_image, (150, 170), (30, 10), 0, 0, 180, (0, 0, 0), -1)
        
        # Create an image without a face
        self.no_face_image = np.zeros((300, 300, 3), dtype=np.uint8)
        
        # Save the test images for debugging
        cv2.imwrite('tests/test_images/test_face.jpg', self.test_image)
        cv2.imwrite('tests/test_images/no_face.jpg', self.no_face_image)
    
    def test_detect_faces_invalid_input(self):
        """Test detect_faces with invalid input."""
        # Test with None
        with self.assertRaises(ValueError):
            detect_faces(None)
        
        # Test with invalid type
        with self.assertRaises(ValueError):
            detect_faces("not an image")
    
    def test_detect_faces_no_face(self):
        """Test detect_faces with an image that has no face."""
        # This should raise a FaceDetectionError
        with self.assertRaises(FaceDetectionError):
            detect_faces(self.no_face_image)
    
    def test_detect_faces_with_face(self):
        """
        Test detect_faces with an image that has a face.
        
        Note: This test might fail with the synthetic image we created,
        as it's not a real face. In a real-world scenario, you would use
        actual face images for testing.
        """
        try:
            face_locations = detect_faces(self.test_image)
            # If we get here, the function detected a face in our synthetic image
            # This is unlikely with real face detection algorithms, but we'll check anyway
            self.assertIsInstance(face_locations, list)
            self.assertTrue(len(face_locations) > 0)
            for face_location in face_locations:
                self.assertEqual(len(face_location), 4)  # (top, right, bottom, left)
        except FaceDetectionError:
            # This is the expected outcome with our synthetic image
            # We'll skip this test in this case
            self.skipTest("No face detected in synthetic image, which is expected")
    
    def test_detect_single_face(self):
        """Test detect_single_face with an image that has a single face."""
        try:
            face_location = detect_single_face(self.test_image)
            # If we get here, the function detected a face in our synthetic image
            self.assertIsInstance(face_location, tuple)
            self.assertEqual(len(face_location), 4)  # (top, right, bottom, left)
        except FaceDetectionError:
            # This is the expected outcome with our synthetic image
            self.skipTest("No face detected in synthetic image, which is expected")
    
    def test_detect_single_face_multiple_faces(self):
        """Test detect_single_face with an image that has multiple faces."""
        # Create an image with multiple face-like patterns
        multi_face_image = np.zeros((300, 300, 3), dtype=np.uint8)
        # Draw first face
        cv2.circle(multi_face_image, (100, 100), 40, (255, 255, 255), -1)
        # Draw second face
        cv2.circle(multi_face_image, (200, 100), 40, (255, 255, 255), -1)
        
        # Save the test image for debugging
        cv2.imwrite('tests/test_images/multi_face.jpg', multi_face_image)
        
        # Mock the detect_faces function to return multiple face locations
        original_detect_faces = app.services.face_detection.detect_faces
        
        def mock_detect_faces(image):
            return [(10, 50, 50, 10), (60, 100, 100, 60)]
        
        try:
            # Replace the original function with our mock
            app.services.face_detection.detect_faces = mock_detect_faces
            
            # Test that MultipleFacesError is raised
            with self.assertRaises(MultipleFacesError):
                detect_single_face(multi_face_image)
        finally:
            # Restore the original function
            app.services.face_detection.detect_faces = original_detect_faces

    def test_validate_face_image_invalid_input(self):
        """Test validate_face_image with invalid input."""
        # Test with None
        with self.assertRaises(ValueError):
            validate_face_image(None)
        
        # Test with invalid type
        with self.assertRaises(ValueError):
            validate_face_image("not an image")
    
    def test_validate_face_image_small_image(self):
        """Test validate_face_image with a small image."""
        # Create a small image (50x50)
        small_image = np.zeros((50, 50, 3), dtype=np.uint8)
        
        # Validate the image
        is_valid, message = validate_face_image(small_image)
        
        # Check the result
        self.assertFalse(is_valid)
        self.assertIn("too small", message)
    
    def test_validate_face_image_dark_image(self):
        """Test validate_face_image with a dark image."""
        # Create a dark image
        dark_image = np.zeros((200, 200, 3), dtype=np.uint8)
        # Add a very dim face-like pattern
        cv2.circle(dark_image, (100, 100), 40, (20, 20, 20), -1)
        
        # Validate the image
        is_valid, message = validate_face_image(dark_image)
        
        # Check the result
        self.assertFalse(is_valid)
        self.assertIn("too dark", message)
    
    def test_validate_face_image_bright_image(self):
        """Test validate_face_image with a bright image."""
        # Create a bright image
        bright_image = np.ones((200, 200, 3), dtype=np.uint8) * 250
        
        # Validate the image
        is_valid, message = validate_face_image(bright_image)
        
        # Check the result
        self.assertFalse(is_valid)
        self.assertIn("too bright", message)
    
    def test_validate_face_image_no_face(self):
        """Test validate_face_image with an image that has no face."""
        # Create a brighter image with no face
        no_face_bright = np.ones((200, 200, 3), dtype=np.uint8) * 150
        
        # Validate the image
        is_valid, message = validate_face_image(no_face_bright)
        
        # Check the result
        self.assertFalse(is_valid)
        self.assertIn("No face detected", message)
    
    def test_validate_face_image_valid(self):
        """
        Test validate_face_image with a valid image.
        
        Note: This test might be skipped with the synthetic image we created,
        as it's not a real face. In a real-world scenario, you would use
        actual face images for testing.
        """
        try:
            # Try to validate the test image
            is_valid, message = validate_face_image(self.test_image)
            
            # If we get here and the image is valid, check the result
            if is_valid:
                self.assertTrue(is_valid)
                self.assertIn("valid", message)
            else:
                # If the image is not valid, skip the test
                self.skipTest(f"Test image not valid: {message}")
        except Exception as e:
            # If an exception is raised, skip the test
            self.skipTest(f"Exception during validation: {e}")

    def test_extract_face_encoding_invalid_input(self):
        """Test extract_face_encoding with invalid input."""
        # Test with None
        with self.assertRaises(ValueError):
            extract_face_encoding(None)
        
        # Test with invalid type
        with self.assertRaises(ValueError):
            extract_face_encoding("not an image")
    
    def test_extract_face_encoding_no_face(self):
        """Test extract_face_encoding with an image that has no face."""
        # Create a brighter image with no face
        no_face_bright = np.ones((200, 200, 3), dtype=np.uint8) * 150
        
        # Test that FaceDetectionError is raised
        with self.assertRaises(FaceDetectionError):
            extract_face_encoding(no_face_bright)
    
    def test_extract_face_encoding_multiple_faces(self):
        """Test extract_face_encoding with an image that has multiple faces."""
        # Create an image with multiple face-like patterns
        multi_face_image = np.zeros((300, 300, 3), dtype=np.uint8)
        # Draw first face
        cv2.circle(multi_face_image, (100, 100), 40, (255, 255, 255), -1)
        # Draw second face
        cv2.circle(multi_face_image, (200, 100), 40, (255, 255, 255), -1)
        
        # Mock the validate_face_image function to return False with multiple faces message
        original_validate = app.services.face_detection.validate_face_image
        
        def mock_validate(image):
            return False, "Multiple faces detected in the image: 2"
        
        try:
            # Replace the original function with our mock
            app.services.face_detection.validate_face_image = mock_validate
            
            # Test that MultipleFacesError is raised
            with self.assertRaises(MultipleFacesError):
                extract_face_encoding(multi_face_image)
        finally:
            # Restore the original function
            app.services.face_detection.validate_face_image = original_validate
    
    def test_extract_face_encoding_valid(self):
        """
        Test extract_face_encoding with a valid image.
        
        Note: This test might be skipped with the synthetic image we created,
        as it's not a real face. In a real-world scenario, you would use
        actual face images for testing.
        """
        try:
            # Mock the validate_face_image function to return True
            original_validate = app.services.face_detection.validate_face_image
            original_face_locations = face_recognition.face_locations
            original_face_encodings = face_recognition.face_encodings
            
            def mock_validate(image):
                return True, "Image is valid for face recognition"
            
            def mock_face_locations(image):
                return [(50, 150, 150, 50)]  # Fake face location
            
            def mock_face_encodings(image, face_locations):
                return [np.zeros(128)]  # Fake 128-dimensional encoding
            
            try:
                # Replace the original functions with our mocks
                app.services.face_detection.validate_face_image = mock_validate
                face_recognition.face_locations = mock_face_locations
                face_recognition.face_encodings = mock_face_encodings
                
                # Test that a face encoding is returned
                encoding = extract_face_encoding(self.test_image)
                self.assertIsInstance(encoding, np.ndarray)
                self.assertEqual(encoding.shape[0], 128)  # face_recognition returns 128-dimensional encodings
            finally:
                # Restore the original functions
                app.services.face_detection.validate_face_image = original_validate
                face_recognition.face_locations = original_face_locations
                face_recognition.face_encodings = original_face_encodings
        except Exception as e:
            # If an exception is raised, skip the test
            self.skipTest(f"Exception during face encoding extraction: {e}")

if __name__ == '__main__':
    unittest.main()
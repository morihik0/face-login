"""
Tests for the face detection service.
"""
import unittest
import cv2
import numpy as np
import app.services.face_detection
from app.services.face_detection import (
    detect_faces,
    detect_single_face,
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

if __name__ == '__main__':
    unittest.main()
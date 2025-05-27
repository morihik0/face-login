"""
Tests for the face recognition service.
"""
import os
import sys
import unittest
import numpy as np
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.services.face_recognition import (
    get_user_encodings, compare_faces, get_recognition_threshold,
    register_face, authenticate_face
)
from app.services.face_detection import FaceDetectionError, MultipleFacesError, ImageQualityError
from app.database.models import User, FaceEncoding

class TestFaceRecognitionService(unittest.TestCase):
    """Test cases for the face recognition service."""

    @patch('app.services.face_recognition.User.get_by_id')
    @patch('app.services.face_recognition.FaceEncoding.get_by_user_id')
    def test_get_user_encodings_success(self, mock_get_by_user_id, mock_get_by_id):
        """Test successful retrieval of user encodings."""
        # Mock user
        mock_user = MagicMock()
        mock_user.id = 1
        mock_get_by_id.return_value = mock_user
        
        # Mock face encodings
        mock_encoding1 = MagicMock()
        mock_encoding1.encoding = [0.1, 0.2, 0.3]
        mock_encoding2 = MagicMock()
        mock_encoding2.encoding = [0.4, 0.5, 0.6]
        mock_get_by_user_id.return_value = [mock_encoding1, mock_encoding2]
        
        # Call the function
        result = get_user_encodings(1)
        
        # Assertions
        mock_get_by_id.assert_called_once_with(1)
        mock_get_by_user_id.assert_called_once_with(1)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], [0.1, 0.2, 0.3])
        self.assertEqual(result[1], [0.4, 0.5, 0.6])

    @patch('app.services.face_recognition.User.get_by_id')
    def test_get_user_encodings_user_not_found(self, mock_get_by_id):
        """Test get_user_encodings when user is not found."""
        # Mock user not found
        mock_get_by_id.return_value = None
        
        # Call the function and check for exception
        with self.assertRaises(ValueError) as context:
            get_user_encodings(999)
        
        self.assertIn("User not found", str(context.exception))
        mock_get_by_id.assert_called_once_with(999)

    @patch('app.services.face_recognition.User.get_by_id')
    @patch('app.services.face_recognition.FaceEncoding.get_by_user_id')
    def test_get_user_encodings_no_encodings(self, mock_get_by_user_id, mock_get_by_id):
        """Test get_user_encodings when no encodings are found."""
        # Mock user
        mock_user = MagicMock()
        mock_user.id = 1
        mock_get_by_id.return_value = mock_user
        
        # Mock no face encodings found
        mock_get_by_user_id.return_value = []
        
        # Call the function
        result = get_user_encodings(1)
        
        # Assertions
        mock_get_by_id.assert_called_once_with(1)
        mock_get_by_user_id.assert_called_once_with(1)
        self.assertEqual(result, [])

    def test_get_user_encodings_invalid_user_id(self):
        """Test get_user_encodings with invalid user_id."""
        # Test with None
        with self.assertRaises(ValueError) as context:
            get_user_encodings(None)
        self.assertIn("Invalid user_id", str(context.exception))
        
        # Test with string
        with self.assertRaises(ValueError) as context:
            get_user_encodings("invalid")
        self.assertIn("Invalid user_id", str(context.exception))
    
    @patch('app.services.face_recognition.face_recognition.compare_faces')
    @patch('app.services.face_recognition.face_recognition.face_distance')
    def test_compare_faces_match(self, mock_face_distance, mock_compare_faces):
        """Test compare_faces when there is a match."""
        # Mock data
        known_encodings = [np.array([0.1, 0.2, 0.3]), np.array([0.4, 0.5, 0.6])]
        face_encoding = np.array([0.1, 0.2, 0.3])
        
        # Mock face_recognition.compare_faces to return a match
        mock_compare_faces.return_value = [True, False]
        
        # Mock face_recognition.face_distance to return distances
        mock_face_distance.return_value = np.array([0.1, 0.8])
        
        # Call the function
        match_found, best_match_index, confidence = compare_faces(known_encodings, face_encoding)
        
        # Assertions
        mock_compare_faces.assert_called_once()
        mock_face_distance.assert_called_once()
        self.assertTrue(match_found)
        self.assertEqual(best_match_index, 0)
        self.assertAlmostEqual(confidence, 0.9, places=1)
    
    @patch('app.services.face_recognition.face_recognition.compare_faces')
    @patch('app.services.face_recognition.face_recognition.face_distance')
    def test_compare_faces_no_match(self, mock_face_distance, mock_compare_faces):
        """Test compare_faces when there is no match."""
        # Mock data
        known_encodings = [np.array([0.1, 0.2, 0.3]), np.array([0.4, 0.5, 0.6])]
        face_encoding = np.array([0.7, 0.8, 0.9])
        
        # Mock face_recognition.compare_faces to return no match
        mock_compare_faces.return_value = [False, False]
        
        # Mock face_recognition.face_distance to return distances
        mock_face_distance.return_value = np.array([0.7, 0.6])
        
        # Call the function
        match_found, best_match_index, confidence = compare_faces(known_encodings, face_encoding)
        
        # Assertions
        mock_compare_faces.assert_called_once()
        mock_face_distance.assert_called_once()
        self.assertFalse(match_found)
        self.assertEqual(best_match_index, 1)  # Second encoding is closer but still not a match
        self.assertAlmostEqual(confidence, 0.4, places=1)
    
    def test_compare_faces_empty_known_encodings(self):
        """Test compare_faces with empty known_encodings."""
        # Call the function with empty known_encodings
        with self.assertRaises(ValueError) as context:
            compare_faces([], np.array([0.1, 0.2, 0.3]))
        
        self.assertIn("Invalid known_encodings", str(context.exception))
    
    def test_compare_faces_invalid_face_encoding(self):
        """Test compare_faces with invalid face_encoding."""
        # Call the function with invalid face_encoding
        with self.assertRaises(ValueError) as context:
            compare_faces([np.array([0.1, 0.2, 0.3])], None)
        
        self.assertIn("Invalid face_encoding", str(context.exception))
    
    @patch('app.services.face_recognition.FACE_RECOGNITION', {'threshold': 0.6})
    def test_get_recognition_threshold(self):
        """Test getting the recognition threshold."""
        # Call the function
        threshold = get_recognition_threshold()
        
        # Assertions
        self.assertEqual(threshold, 0.6)
    
    @patch('app.services.face_recognition.get_recognition_threshold')
    @patch('app.services.face_recognition.face_recognition.compare_faces')
    @patch('app.services.face_recognition.face_recognition.face_distance')
    def test_compare_faces_with_default_threshold(self, mock_face_distance, mock_compare_faces, mock_get_threshold):
        """Test compare_faces using the default threshold from config."""
        # Mock data
        known_encodings = [np.array([0.1, 0.2, 0.3])]
        face_encoding = np.array([0.1, 0.2, 0.3])
        
        # Mock get_recognition_threshold to return a specific value
        mock_get_threshold.return_value = 0.5
        
        # Mock face_recognition.compare_faces to return a match
        mock_compare_faces.return_value = [True]
        
        # Mock face_recognition.face_distance to return distances
        mock_face_distance.return_value = np.array([0.1])
        
        # Call the function without specifying tolerance
        compare_faces(known_encodings, face_encoding)
        
        # Verify that compare_faces was called with the default threshold
        mock_compare_faces.assert_called_once_with(known_encodings, face_encoding, tolerance=0.5)

    @patch('app.services.face_recognition.User.get_by_id')
    @patch('app.services.face_recognition.FaceEncoding.count_by_user_id')
    @patch('app.services.face_recognition.extract_face_encoding')
    @patch('app.services.face_recognition.cv2.imwrite')
    @patch('app.services.face_recognition.os.makedirs')
    @patch('app.services.face_recognition.FaceEncoding.create')
    def test_register_face_success(self, mock_create, mock_makedirs, mock_imwrite,
                                  mock_extract_encoding, mock_count, mock_get_by_id):
        """Test successful face registration."""
        # Mock user
        mock_user = MagicMock()
        mock_user.id = 1
        mock_get_by_id.return_value = mock_user
        
        # Mock face count
        mock_count.return_value = 2  # User has 2 faces registered, max is 5
        
        # Mock face encoding extraction
        mock_encoding = np.array([0.1, 0.2, 0.3])
        mock_extract_encoding.return_value = mock_encoding
        
        # Mock image save
        mock_imwrite.return_value = True
        
        # Mock face encoding creation
        mock_face_encoding = MagicMock()
        mock_face_encoding.id = 1
        mock_face_encoding.user_id = 1
        mock_face_encoding.encoding = [0.1, 0.2, 0.3]
        mock_create.return_value = mock_face_encoding
        
        # Call the function
        image = np.zeros((100, 100, 3), dtype=np.uint8)  # Dummy image
        result = register_face(1, image)
        
        # Assertions
        mock_get_by_id.assert_called_once_with(1)
        mock_count.assert_called_once_with(1)
        mock_extract_encoding.assert_called_once_with(image)
        mock_makedirs.assert_called_once()
        mock_imwrite.assert_called_once()
        mock_create.assert_called_once()
        self.assertEqual(result, mock_face_encoding)
    
    @patch('app.services.face_recognition.User.get_by_id')
    def test_register_face_user_not_found(self, mock_get_by_id):
        """Test register_face when user is not found."""
        # Mock user not found
        mock_get_by_id.return_value = None
        
        # Call the function and check for exception
        image = np.zeros((100, 100, 3), dtype=np.uint8)  # Dummy image
        with self.assertRaises(ValueError) as context:
            register_face(999, image)
        
        self.assertIn("User not found", str(context.exception))
        mock_get_by_id.assert_called_once_with(999)
    
    @patch('app.services.face_recognition.User.get_by_id')
    @patch('app.services.face_recognition.FaceEncoding.count_by_user_id')
    @patch('app.services.face_recognition.FACE_RECOGNITION', {'max_faces_per_user': 5})
    def test_register_face_max_faces_reached(self, mock_count, mock_get_by_id):
        """Test register_face when max faces limit is reached."""
        # Mock user
        mock_user = MagicMock()
        mock_user.id = 1
        mock_get_by_id.return_value = mock_user
        
        # Mock face count at maximum
        mock_count.return_value = 5  # User has 5 faces registered, max is 5
        
        # Call the function and check for exception
        image = np.zeros((100, 100, 3), dtype=np.uint8)  # Dummy image
        with self.assertRaises(ValueError) as context:
            register_face(1, image)
        
        self.assertIn("maximum number of faces", str(context.exception))
        mock_get_by_id.assert_called_once_with(1)
        mock_count.assert_called_once_with(1)
    
    @patch('app.services.face_recognition.User.get_by_id')
    @patch('app.services.face_recognition.FaceEncoding.count_by_user_id')
    @patch('app.services.face_recognition.extract_face_encoding')
    def test_register_face_detection_error(self, mock_extract_encoding, mock_count, mock_get_by_id):
        """Test register_face when face detection fails."""
        # Mock user
        mock_user = MagicMock()
        mock_user.id = 1
        mock_get_by_id.return_value = mock_user
        
        # Mock face count
        mock_count.return_value = 2  # User has 2 faces registered, max is 5
        
        # Mock face detection error
        mock_extract_encoding.side_effect = FaceDetectionError("No faces detected")
        
        # Call the function and check for exception
        image = np.zeros((100, 100, 3), dtype=np.uint8)  # Dummy image
        with self.assertRaises(FaceDetectionError) as context:
            register_face(1, image)
        
        self.assertIn("No faces detected", str(context.exception))
        mock_get_by_id.assert_called_once_with(1)
        mock_count.assert_called_once_with(1)
        mock_extract_encoding.assert_called_once_with(image)

    @patch('app.services.face_recognition.extract_face_encoding')
    @patch('app.services.face_recognition.User.get_all')
    @patch('app.services.face_recognition.get_user_encodings')
    @patch('app.services.face_recognition.compare_faces')
    @patch('app.services.face_recognition.AuthLog.create')
    def test_authenticate_face_success(self, mock_create_log, mock_compare_faces,
                                      mock_get_encodings, mock_get_all, mock_extract_encoding):
        """Test successful face authentication."""
        # Mock face encoding extraction
        mock_encoding = np.array([0.1, 0.2, 0.3])
        mock_extract_encoding.return_value = mock_encoding
        
        # Mock users
        mock_user1 = MagicMock()
        mock_user1.id = 1
        mock_user2 = MagicMock()
        mock_user2.id = 2
        mock_get_all.return_value = [mock_user1, mock_user2]
        
        # Mock user encodings
        mock_get_encodings.side_effect = lambda user_id: [np.array([0.1, 0.2, 0.3])] if user_id == 1 else []
        
        # Mock face comparison - match with user 1
        def mock_compare_side_effect(encodings, encoding, tolerance):
            if len(encodings) > 0 and np.array_equal(encodings[0], np.array([0.1, 0.2, 0.3])):
                return (True, 0, 0.9)
            return (False, -1, 0.0)
        
        mock_compare_faces.side_effect = mock_compare_side_effect
        
        # Call the function
        image = np.zeros((100, 100, 3), dtype=np.uint8)  # Dummy image
        success, user_id, confidence = authenticate_face(image)
        
        # Assertions
        mock_extract_encoding.assert_called_once_with(image)
        mock_get_all.assert_called_once()
        self.assertEqual(mock_get_encodings.call_count, 2)  # Called for both users
        self.assertEqual(mock_compare_faces.call_count, 1)  # Only called for user 1 (user 2 has no encodings)
        mock_create_log.assert_called_once()
        self.assertTrue(success)
        self.assertEqual(user_id, 1)
        self.assertAlmostEqual(confidence, 0.9)
    
    @patch('app.services.face_recognition.extract_face_encoding')
    @patch('app.services.face_recognition.User.get_all')
    @patch('app.services.face_recognition.get_user_encodings')
    @patch('app.services.face_recognition.compare_faces')
    @patch('app.services.face_recognition.AuthLog.create')
    def test_authenticate_face_no_match(self, mock_create_log, mock_compare_faces,
                                       mock_get_encodings, mock_get_all, mock_extract_encoding):
        """Test face authentication with no matching user."""
        # Mock face encoding extraction
        mock_encoding = np.array([0.7, 0.8, 0.9])
        mock_extract_encoding.return_value = mock_encoding
        
        # Mock users
        mock_user1 = MagicMock()
        mock_user1.id = 1
        mock_get_all.return_value = [mock_user1]
        
        # Mock user encodings
        mock_get_encodings.return_value = [np.array([0.1, 0.2, 0.3])]
        
        # Mock face comparison - no match
        mock_compare_faces.return_value = (False, -1, 0.3)
        
        # Call the function
        image = np.zeros((100, 100, 3), dtype=np.uint8)  # Dummy image
        success, user_id, confidence = authenticate_face(image)
        
        # Assertions
        mock_extract_encoding.assert_called_once_with(image)
        mock_get_all.assert_called_once()
        mock_get_encodings.assert_called_once_with(1)
        mock_compare_faces.assert_called_once()
        mock_create_log.assert_called_once()
        self.assertFalse(success)
        self.assertIsNone(user_id)
        self.assertAlmostEqual(confidence, 0.0)
    
    @patch('app.services.face_recognition.extract_face_encoding')
    @patch('app.services.face_recognition.User.get_all')
    def test_authenticate_face_no_users(self, mock_get_all, mock_extract_encoding):
        """Test face authentication when no users exist."""
        # Mock face encoding extraction
        mock_encoding = np.array([0.1, 0.2, 0.3])
        mock_extract_encoding.return_value = mock_encoding
        
        # Mock no users
        mock_get_all.return_value = []
        
        # Call the function
        image = np.zeros((100, 100, 3), dtype=np.uint8)  # Dummy image
        success, user_id, confidence = authenticate_face(image)
        
        # Assertions
        mock_extract_encoding.assert_called_once_with(image)
        mock_get_all.assert_called_once()
        self.assertFalse(success)
        self.assertIsNone(user_id)
        self.assertAlmostEqual(confidence, 0.0)
    
    @patch('app.services.face_recognition.extract_face_encoding')
    def test_authenticate_face_detection_error(self, mock_extract_encoding):
        """Test face authentication when face detection fails."""
        # Mock face detection error
        mock_extract_encoding.side_effect = FaceDetectionError("No faces detected")
        
        # Call the function and check for exception
        image = np.zeros((100, 100, 3), dtype=np.uint8)  # Dummy image
        with self.assertRaises(FaceDetectionError) as context:
            authenticate_face(image)
        
        self.assertIn("No faces detected", str(context.exception))
        mock_extract_encoding.assert_called_once_with(image)

if __name__ == '__main__':
    unittest.main()
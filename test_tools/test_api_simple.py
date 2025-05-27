"""
Simple API test script to verify endpoints are working.
"""
import requests
import base64
import json
import numpy as np
from PIL import Image
import io

# Base URL for the API
BASE_URL = "http://localhost:5001/api"

def create_test_user():
    """Create a test user."""
    print("\n=== Creating Test User ===")
    user_data = {
        "name": "API Test User",
        "email": "apitest@example.com"
    }
    response = requests.post(f"{BASE_URL}/users", json=user_data)
    if response.status_code == 201:
        user_id = response.json()['data']['user']['id']
        print(f"✓ Created user with ID: {user_id}")
        return user_id
    else:
        print(f"✗ Failed to create user: {response.json()}")
        return None

def test_face_registration(user_id):
    """Test face registration with a real image."""
    print("\n=== Testing Face Registration ===")
    
    # Load and prepare the test image
    image_path = "tests/test_images/single_face_test.jpg"
    
    try:
        # Read the image file
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        
        # Encode to base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Register the face
        registration_data = {
            "user_id": user_id,
            "image": image_base64
        }
        
        response = requests.post(f"{BASE_URL}/recognition/register", json=registration_data)
        
        if response.status_code == 201:
            print(f"✓ Successfully registered face for user {user_id}")
            print(f"  Response: {response.json()['message']}")
            return True
        else:
            print(f"✗ Failed to register face: {response.json()}")
            return False
            
    except Exception as e:
        print(f"✗ Error during face registration: {e}")
        return False

def test_face_authentication():
    """Test face authentication."""
    print("\n=== Testing Face Authentication ===")
    
    # Load the same test image
    image_path = "tests/test_images/single_face_test.jpg"
    
    try:
        # Read the image file
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        
        # Encode to base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Authenticate the face
        auth_data = {
            "image": image_base64
        }
        
        response = requests.post(f"{BASE_URL}/recognition/authenticate", json=auth_data)
        
        if response.status_code == 200:
            data = response.json()['data']
            print(f"✓ Authentication successful!")
            print(f"  User: {data['user']['name']} (ID: {data['user']['id']})")
            print(f"  Confidence: {data['confidence']:.2f}")
            return True
        else:
            print(f"✗ Authentication failed: {response.json()}")
            return False
            
    except Exception as e:
        print(f"✗ Error during authentication: {e}")
        return False

def test_auth_history(user_id):
    """Test authentication history retrieval."""
    print("\n=== Testing Authentication History ===")
    
    response = requests.get(f"{BASE_URL}/recognition/history", params={"user_id": user_id, "limit": 5})
    
    if response.status_code == 200:
        history = response.json()['data']['history']
        print(f"✓ Retrieved {len(history)} authentication log(s)")
        for log in history:
            status = "Success" if log['success'] else "Failed"
            confidence = f"{log['confidence']:.2f}" if log['confidence'] else "N/A"
            print(f"  - {log['timestamp']}: {status} (Confidence: {confidence})")
        return True
    else:
        print(f"✗ Failed to retrieve history: {response.json()}")
        return False

def cleanup_test_user(user_id):
    """Delete the test user."""
    print("\n=== Cleaning Up ===")
    response = requests.delete(f"{BASE_URL}/users/{user_id}")
    if response.status_code == 200:
        print(f"✓ Deleted test user {user_id}")
    else:
        print(f"✗ Failed to delete user: {response.json()}")

def main():
    """Run the API tests."""
    print("Starting Simple API Tests")
    print("=" * 50)
    
    try:
        # Create a test user
        user_id = create_test_user()
        if not user_id:
            print("\nTests aborted: Could not create test user")
            return
        
        # Test face registration
        if test_face_registration(user_id):
            # Test face authentication
            test_face_authentication()
            
            # Check authentication history
            test_auth_history(user_id)
        
        # Clean up
        cleanup_test_user(user_id)
        
        print("\n" + "=" * 50)
        print("API Tests Completed")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to the API.")
        print("  Make sure the Flask application is running on port 5001")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")

if __name__ == "__main__":
    main()
"""
Test script for API endpoints.
"""
import requests
import base64
import json
from pathlib import Path

# Base URL for the API
BASE_URL = "http://localhost:5001/api"

def test_user_endpoints():
    """Test user management endpoints."""
    print("\n=== Testing User Management Endpoints ===")
    
    # Test creating a user
    print("\n1. Creating a new user...")
    user_data = {
        "name": "Test User",
        "email": "test@example.com"
    }
    response = requests.post(f"{BASE_URL}/users", json=user_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        user_id = response.json()['data']['user']['id']
        print(f"Created user with ID: {user_id}")
        
        # Test getting all users
        print("\n2. Getting all users...")
        response = requests.get(f"{BASE_URL}/users")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Test getting a specific user
        print(f"\n3. Getting user with ID {user_id}...")
        response = requests.get(f"{BASE_URL}/users/{user_id}")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Test updating a user
        print(f"\n4. Updating user with ID {user_id}...")
        update_data = {
            "name": "Updated Test User"
        }
        response = requests.put(f"{BASE_URL}/users/{user_id}", json=update_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        return user_id
    
    return None

def test_face_registration(user_id):
    """Test face registration endpoint."""
    print("\n=== Testing Face Registration Endpoint ===")
    
    # Check if test image exists
    test_image_path = Path("tests/test_images/single_face_test.jpg")
    if not test_image_path.exists():
        print(f"Test image not found at {test_image_path}")
        return False
    
    # Read and encode the image
    with open(test_image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    # Register the face
    print(f"\nRegistering face for user ID {user_id}...")
    registration_data = {
        "user_id": user_id,
        "image": image_data
    }
    response = requests.post(f"{BASE_URL}/recognition/register", json=registration_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 201

def test_face_authentication():
    """Test face authentication endpoint."""
    print("\n=== Testing Face Authentication Endpoint ===")
    
    # Check if test image exists
    test_image_path = Path("tests/test_images/single_face_test.jpg")
    if not test_image_path.exists():
        print(f"Test image not found at {test_image_path}")
        return
    
    # Read and encode the image
    with open(test_image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    # Authenticate the face
    print("\nAuthenticating face...")
    auth_data = {
        "image": image_data
    }
    response = requests.post(f"{BASE_URL}/recognition/authenticate", json=auth_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_auth_history(user_id=None):
    """Test authentication history endpoint."""
    print("\n=== Testing Authentication History Endpoint ===")
    
    # Test getting all history
    print("\n1. Getting all authentication history...")
    response = requests.get(f"{BASE_URL}/recognition/history")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test getting user-specific history
    if user_id:
        print(f"\n2. Getting authentication history for user ID {user_id}...")
        response = requests.get(f"{BASE_URL}/recognition/history", params={"user_id": user_id})
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_cleanup(user_id):
    """Clean up test data."""
    print("\n=== Cleaning Up Test Data ===")
    
    if user_id:
        print(f"\nDeleting user with ID {user_id}...")
        response = requests.delete(f"{BASE_URL}/users/{user_id}")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

def main():
    """Run all API tests."""
    print("Starting API endpoint tests...")
    print(f"API Base URL: {BASE_URL}")
    
    try:
        # Test user endpoints and get user ID
        user_id = test_user_endpoints()
        
        if user_id:
            # Test face registration
            if test_face_registration(user_id):
                # Test face authentication
                test_face_authentication()
                
                # Test authentication history
                test_auth_history(user_id)
            
            # Clean up
            test_cleanup(user_id)
        
        print("\n=== API Tests Completed ===")
        
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to the API. Make sure the Flask application is running.")
    except Exception as e:
        print(f"\nError during testing: {e}")

if __name__ == "__main__":
    main()
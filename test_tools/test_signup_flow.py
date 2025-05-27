"""
Test the new user signup flow with face registration
"""
import requests
import json
import base64
from pathlib import Path
import time

BASE_URL = "http://localhost:5001/api"

def test_signup_flow():
    """Test the complete signup flow"""
    print("🆕 Testing New User Signup Flow")
    print("=" * 50)
    
    # Test data
    test_user = {
        "name": "新規テストユーザー",
        "email": f"newuser_{int(time.time())}@example.com"
    }
    
    # Load test image
    test_image_path = Path("tests/test_images/single_face_test.jpg")
    if not test_image_path.exists():
        print("❌ Test image not found")
        return
    
    with open(test_image_path, "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode('utf-8')
    
    # Step 1: Check email availability
    print("\n1. Testing email availability check...")
    email_check_response = requests.post(
        f"{BASE_URL}/public/check-email",
        json={"email": test_user["email"]}
    )
    
    print(f"Status: {email_check_response.status_code}")
    email_data = email_check_response.json()
    print(f"Response: {json.dumps(email_data, indent=2, ensure_ascii=False)}")
    
    if email_check_response.status_code == 200 and email_data['data']['available']:
        print("✅ Email is available")
    else:
        print("❌ Email check failed")
        return
    
    # Step 2: Register user with face
    print("\n2. Testing user registration with face...")
    signup_data = {
        **test_user,
        "image": image_base64
    }
    
    signup_response = requests.post(
        f"{BASE_URL}/public/register-user-with-face",
        json=signup_data
    )
    
    print(f"Status: {signup_response.status_code}")
    signup_result = signup_response.json()
    print(f"Response: {json.dumps(signup_result, indent=2, ensure_ascii=False)}")
    
    if signup_response.status_code != 201:
        print("❌ User registration failed")
        return
    
    user_id = signup_result['data']['user']['id']
    access_token = signup_result['data']['access_token']
    print(f"✅ User registered successfully with ID: {user_id}")
    print(f"   Access token: {access_token[:30]}...")
    
    # Step 3: Test immediate authentication with the token
    print("\n3. Testing immediate authentication with token...")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    me_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"Status: {me_response.status_code}")
    if me_response.status_code == 200:
        me_data = me_response.json()
        print(f"Current user: {me_data['data']['user']['name']}")
        print("✅ Immediate login successful")
    else:
        print("❌ Immediate login failed")
    
    # Step 4: Test face authentication
    print("\n4. Testing face authentication...")
    auth_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"image": image_base64}
    )
    
    print(f"Status: {auth_response.status_code}")
    if auth_response.status_code == 200:
        auth_data = auth_response.json()
        authenticated_user = auth_data['data']['user']
        confidence = auth_data['data']['confidence']
        print(f"Authenticated as: {authenticated_user['name']}")
        print(f"Confidence: {confidence:.4f}")
        print("✅ Face authentication successful")
    else:
        print("❌ Face authentication failed")
    
    # Step 5: Test duplicate email registration
    print("\n5. Testing duplicate email registration...")
    duplicate_response = requests.post(
        f"{BASE_URL}/public/register-user-with-face",
        json=signup_data
    )
    
    print(f"Status: {duplicate_response.status_code}")
    if duplicate_response.status_code == 409:
        print("✅ Duplicate email correctly rejected")
    else:
        print("❌ Duplicate email handling failed")
    
    # Step 6: Clean up - delete test user
    print("\n6. Cleaning up test user...")
    delete_response = requests.delete(
        f"{BASE_URL}/users/{user_id}",
        headers=headers
    )
    
    print(f"Status: {delete_response.status_code}")
    if delete_response.status_code == 200:
        print("✅ Test user deleted successfully")
    else:
        print("❌ Failed to delete test user")
    
    print("\n" + "=" * 50)
    print("🎉 Signup flow test completed!")

def test_error_cases():
    """Test error cases for the signup flow"""
    print("\n🚨 Testing Error Cases")
    print("=" * 30)
    
    # Test 1: Missing data
    print("\n1. Testing missing data...")
    response = requests.post(f"{BASE_URL}/public/register-user-with-face", json={})
    print(f"Status: {response.status_code} (Expected: 400)")
    
    # Test 2: Invalid email format
    print("\n2. Testing invalid email...")
    response = requests.post(
        f"{BASE_URL}/public/register-user-with-face",
        json={
            "name": "Test User",
            "email": "invalid-email",
            "image": "fake-image-data"
        }
    )
    print(f"Status: {response.status_code} (Expected: 400)")
    
    # Test 3: Invalid image data
    print("\n3. Testing invalid image...")
    response = requests.post(
        f"{BASE_URL}/public/register-user-with-face",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "image": "invalid-base64-data"
        }
    )
    print(f"Status: {response.status_code} (Expected: 400)")
    
    print("✅ Error case testing completed")

if __name__ == "__main__":
    test_signup_flow()
    test_error_cases()
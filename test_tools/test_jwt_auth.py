"""
Test JWT authentication endpoints
"""
import requests
import json
import base64
from pathlib import Path

BASE_URL = "http://localhost:5001/api"

def test_auth_flow():
    """Test the complete authentication flow"""
    print("🔐 Testing JWT Authentication Flow")
    print("=" * 50)
    
    # Step 1: Login with face authentication
    print("\n1. Testing face authentication login...")
    
    # Load test image
    test_image_path = Path("tests/test_images/single_face_test.jpg")
    if not test_image_path.exists():
        print("❌ Test image not found")
        return
    
    with open(test_image_path, "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode('utf-8')
    
    # Login request
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"image": image_base64}
    )
    
    print(f"Status: {login_response.status_code}")
    login_data = login_response.json()
    print(f"Response: {json.dumps(login_data, indent=2)}")
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return
    
    # Extract tokens
    access_token = login_data['data']['access_token']
    refresh_token = login_data['data']['refresh_token']
    print(f"\n✅ Login successful!")
    print(f"User: {login_data['data']['user']['name']}")
    print(f"Access token: {access_token[:20]}...")
    
    # Step 2: Test authenticated endpoint
    print("\n2. Testing authenticated endpoint (get current user)...")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    me_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    
    print(f"Status: {me_response.status_code}")
    print(f"Response: {json.dumps(me_response.json(), indent=2)}")
    
    # Step 3: Test protected user endpoint
    print("\n3. Testing protected user endpoint...")
    
    users_response = requests.get(f"{BASE_URL}/users", headers=headers)
    print(f"Status: {users_response.status_code}")
    
    # Step 4: Test without token
    print("\n4. Testing endpoint without token...")
    
    no_auth_response = requests.get(f"{BASE_URL}/auth/me")
    print(f"Status: {no_auth_response.status_code}")
    print(f"Response: {json.dumps(no_auth_response.json(), indent=2)}")
    
    # Step 5: Test token refresh
    print("\n5. Testing token refresh...")
    
    refresh_headers = {"Authorization": f"Bearer {refresh_token}"}
    refresh_response = requests.post(f"{BASE_URL}/auth/refresh", headers=refresh_headers)
    
    print(f"Status: {refresh_response.status_code}")
    if refresh_response.status_code == 200:
        new_access_token = refresh_response.json()['data']['access_token']
        print(f"✅ New access token: {new_access_token[:20]}...")
    
    # Step 6: Test logout
    print("\n6. Testing logout...")
    
    logout_response = requests.post(f"{BASE_URL}/auth/logout", headers=headers)
    print(f"Status: {logout_response.status_code}")
    print(f"Response: {json.dumps(logout_response.json(), indent=2)}")
    
    print("\n" + "=" * 50)
    print("✅ JWT Authentication test completed!")

if __name__ == "__main__":
    test_auth_flow()
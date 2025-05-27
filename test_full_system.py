"""
Comprehensive system test for Face Login API
"""
import requests
import json
import base64
from pathlib import Path
import time

# API base URL
BASE_URL = "http://localhost:5001/api"

# Test results
results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

def test_api(name, method, endpoint, data=None, expected_status=200):
    """Test an API endpoint"""
    print(f"\n🧪 Testing: {name}")
    print(f"   {method} {endpoint}")
    
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}")
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", json=data)
        elif method == "PUT":
            response = requests.put(f"{BASE_URL}{endpoint}", json=data)
        elif method == "DELETE":
            response = requests.delete(f"{BASE_URL}{endpoint}")
        
        success = response.status_code == expected_status
        
        if success:
            print(f"   ✅ Status: {response.status_code} (Expected: {expected_status})")
            results["passed"] += 1
        else:
            print(f"   ❌ Status: {response.status_code} (Expected: {expected_status})")
            results["failed"] += 1
        
        # Print response
        try:
            print(f"   Response: {json.dumps(response.json(), indent=2)[:200]}...")
        except:
            print(f"   Response: {response.text[:200]}...")
        
        results["tests"].append({
            "name": name,
            "endpoint": endpoint,
            "status": response.status_code,
            "success": success
        })
        
        return response
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        results["failed"] += 1
        results["tests"].append({
            "name": name,
            "endpoint": endpoint,
            "error": str(e),
            "success": False
        })
        return None

def load_test_image():
    """Load a test image and convert to base64"""
    test_image_path = Path("tests/test_images/single_face_test.jpg")
    if test_image_path.exists():
        with open(test_image_path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
    return None

def main():
    print("=" * 60)
    print("🚀 Face Login System - Comprehensive API Test")
    print("=" * 60)
    
    # Test 1: Check API is running
    print("\n📍 Checking API Status...")
    response = requests.get(f"http://localhost:5001/")
    if response.status_code == 200:
        print("✅ API is running")
    else:
        print("❌ API is not responding")
        return
    
    # Test 2: User Management APIs
    print("\n📋 Testing User Management APIs")
    
    # Get all users
    test_api("Get all users", "GET", "/users")
    
    # Create a new user
    new_user_data = {
        "name": "Test User API",
        "email": f"testapi_{int(time.time())}@example.com"
    }
    create_response = test_api("Create new user", "POST", "/users", new_user_data, 201)
    
    if create_response and create_response.status_code == 201:
        user_id = create_response.json()['data']['user']['id']
        
        # Get specific user
        test_api(f"Get user {user_id}", "GET", f"/users/{user_id}")
        
        # Update user
        update_data = {"name": "Updated Test User"}
        test_api(f"Update user {user_id}", "PUT", f"/users/{user_id}", update_data)
        
        # Test 3: Face Recognition APIs
        print("\n📸 Testing Face Recognition APIs")
        
        # Load test image
        test_image = load_test_image()
        if test_image:
            # Register face
            register_data = {
                "user_id": user_id,
                "image": test_image
            }
            register_response = test_api("Register face", "POST", "/recognition/register", register_data, 201)
            
            if register_response and register_response.status_code == 201:
                # Authenticate face
                auth_data = {"image": test_image}
                test_api("Authenticate face", "POST", "/recognition/authenticate", auth_data)
                
                # Get authentication history
                test_api("Get auth history", "GET", "/recognition/history?limit=5")
                test_api(f"Get user {user_id} auth history", "GET", f"/recognition/history?user_id={user_id}")
        else:
            print("   ⚠️  No test image found, skipping face recognition tests")
        
        # Delete user
        test_api(f"Delete user {user_id}", "DELETE", f"/users/{user_id}")
    
    # Test 4: Error Handling
    print("\n🚨 Testing Error Handling")
    
    # Try to get non-existent user
    test_api("Get non-existent user", "GET", "/users/99999", expected_status=404)
    
    # Try to create user with duplicate email
    test_api("Create duplicate user", "POST", "/users", 
             {"name": "Duplicate", "email": "user1@example.com"}, 
             expected_status=409)
    
    # Try to authenticate without image
    test_api("Authenticate without image", "POST", "/recognition/authenticate", 
             {}, expected_status=400)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"📝 Total Tests: {results['passed'] + results['failed']}")
    print(f"🎯 Success Rate: {(results['passed'] / (results['passed'] + results['failed']) * 100):.1f}%")
    
    # Save results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\n💾 Results saved to test_results.json")

if __name__ == "__main__":
    main()
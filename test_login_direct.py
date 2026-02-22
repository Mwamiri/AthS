#!/usr/bin/env python3
"""
Direct test of login functionality without Flask routing
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'backend'))

# Simple test
print("Testing AthSys Login System")
print("=" * 50)

# Test 1: Check if models import
try:
    from models import User, Base, SessionLocal
    print("✓ Database models imported successfully")
except Exception as e:
    print(f"✗ Error importing models: {e}")
    sys.exit(1)

# Test 2: Create in-memory test user
try:
    # Create a test user in memory
    test_user = User()
    test_user.email = "admin@example.com"
    test_user.password = "Admin@123"  # This will be hashed
    test_user.name = "Admin User"
    test_user.role = "admin"
    test_user.status = "active"
    test_user.set_password("Admin@123")
    
    print("✓ Test user created successfully")
    print(f"  Email:   {test_user.email}")
    print(f"  Role:    {test_user.role}")
    print(f"  Hash:    {test_user.password_hash[:20]}...")
except Exception as e:
    print(f"✗ Error creating test user: {e}")
    sys.exit(1)

# Test 3: Verify password checking
try:
    if test_user.check_password("Admin@123"):
        print("✓ Password verification works (correct password)")
    else:
        print("✗ Password verification failed for correct password")
    
    if not test_user.check_password("WrongPassword"):
        print("✓ Password verification works (rejects wrong password)")
    else:
        print("✗ Password verification failed - accepted wrong password!")
except Exception as e:
    print(f"✗ Error verifying password: {e}")
    sys.exit(1)

# Test 4: Check Flask app
try:
    from app import app
    print("✓ Flask app imported successfully")
    
    # List API routes
    api_routes = [str(r.rule) for r in app.url_map.iter_rules() if '/api/' in str(r.rule)]
    print(f"✓ Found {len(api_routes)} API routes:")
    for route in sorted(api_routes)[:10]:
        print(f"  - {route}")
except Exception as e:
    print(f"✗ Error importing Flask app: {e}")
    sys.exit(1)

# Test 5: Test HTTP requests
try:
    import requests
   
    print("\n" + "=" * 50)
    print("Testing HTTP Endpoints")
    print("=" * 50)
    
    # Test root
    resp = requests.get("http://localhost:5000/", timeout=5)
    print(f"GET / -> {resp.status_code}")
    
    # Test API
    resp = requests.get("http://localhost:5000/api/info", timeout=5)
    print(f"GET /api/info -> {resp.status_code}")
    
    # Test login
    resp = requests.post(
        "http://localhost:5000/api/auth/login",
        json={"email": "admin@example.com", "password": "Admin@123"},
        timeout=5
    )
    print(f"POST /api/auth/login -> {resp.status_code}")
    if resp.status_code != 200:
        try:
            resp_json = resp.json()
            print(f"  Response: {resp_json.get('message', resp.text[:100])}")
        except:
            print(f"  Response: {resp.text[:100]}")
        
except requests.exceptions.ConnectionRefusedError:
    print("⚠ Flask server is not running on port 5000")
except Exception as e:
    print(f"✗ Error testing HTTP endpoints: {e}")

print("\n" + "=" * 50)
print("Test Complete")

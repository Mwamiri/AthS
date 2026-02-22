#!/usr/bin/env python3
"""Debug script to check which routes are actually registered in the app"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'backend'))

from app import app

print("=" * 70)
print("DEBUGGING: Flask Route Registration Check")
print("=" * 70)

print("\nRoute Assignment Order (from url_map):")
print("-" * 70)

# Check order
for i, rule in enumerate(app.url_map.iter_rules(), 1):
    methods_str = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
    if not methods_str:
        methods_str = 'GET'
    
    if len(str(rule.rule)) < 60:
        print(f"{i:3d}. {rule.rule:40s} [{methods_str:8s}] -> {rule.endpoint}")

print("\n" + "=" * 70)
print("KEY QUESTIONS:")
print("=" * 70)

# Check if auth routes exist
auth_routes = [r for r in app.url_map.iter_rules() if '/api/auth' in str(r.rule)]
print(f"\n1. Auth routes registered: {len(auth_routes)}")
for r in auth_routes:
    print(f"   - {r.rule}")

# Check if API info exists
info_routes = [r for r in app.url_map.iter_rules() if r.rule == '/api/info']
print(f"\n2. /api/info route exists: {len(info_routes) > 0}")

# Check catch-alls
catchalls = [r for r in app.url_map.iter_rules() if '<' in str(r.rule) and 'api' not in str(r.rule)]
print(f"\n3. Catch-all/wildcard routes: {len(catchalls)}")
for r in catchalls:
    print(f"   - {r.rule} -> {r.endpoint}")

# Check rule matching order
print(f"\n4. Total routes: {len(list(app.url_map.iter_rules()))}")

print("\n" + "=" * 70)
print("TESTING ROUTE MATCHING (using test client):")
print("=" * 70)

with app.test_client() as client:
    # Test /api/info
    try:
        resp = client.get('/api/info')
        print(f"\nGET /api/info -> {resp.status_code}")
        if resp.status_code == 404:
            data = resp.get_json()
            if data:
                print(f"  Error: {data.get('message')}")
    except Exception as e:
        print(f"\n{error }:{e}")
    
    # Test /api/auth/login
    try:
        resp = client.post('/api/auth/login', json={'email': 'test@example.com', 'password': 'test'})
        print(f"POST /api/auth/login -> {resp.status_code}")
        if resp.status_code == 404:
            data = resp.get_json()
            if data:
                print(f"  Error: {data.get('message')}")
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "=" * 70)

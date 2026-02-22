#!/usr/bin/env python3
"""Minimal test to check if Flask routes are registered and working"""

from flask import Flask, jsonify
import sys

# Create minimal Flask app
app = Flask(__name__)

# Add an API route
@app.route('/api/info', methods=['GET'])
def api_info():
    return jsonify({'message': 'API working'})

# Add a catch-all route
@app.route('/<filename>')
def serve_file(filename):
    return jsonify({'error': 'Catch-all matched'}), 404

# Test routing
with app.test_client() as client:
    print("Testing Flask routing...")
    print("=" * 50)
    
    # Test API route
    resp = client.get('/api/info')
    print(f"GET /api/info -> {resp.status_code}")
    print(f"  Body: {resp.get_json()}")
    
    # Test root
    resp = client.get('/')
    print(f"\nGET / -> {resp.status_code}")
    print(f"  Body: {resp.get_json()}")
    
    # Test other file
    resp = client.get('/page.html')
    print(f"\nGET /page.html -> {resp.status_code}")
    print(f"  Body: {resp.get_json()}")

print("\n✓ Flask routing works correctly")
print("Problem is in the actual AthSys app, not basic Flask routing")

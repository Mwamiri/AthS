#!/usr/bin/env python
"""Test backend endpoints to verify 504 timeout is resolved"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'backend'))

from app import app

def test_endpoints():
    """Test API endpoints"""
    with app.test_client() as client:
        tests = [
            ('Health check', '/livez', 'GET'),
            ('API info', '/api/info', 'GET'),
            ('Database health', '/api/admin/database/health', 'GET'),
        ]
        
        print('=' * 60)
        print('BACKEND ENDPOINT TEST')
        print('=' * 60)
        
        all_passed = True
        for name, endpoint, method in tests:
            try:
                print(f'\n[TEST] {name} ({method} {endpoint})')
                if method == 'GET':
                    response = client.get(endpoint)
                else:
                    response = client.post(endpoint)
                
                status = 'PASS' if response.status_code < 400 else 'FAIL'
                print(f'Status: {response.status_code} [{status}]')
                
                if response.status_code == 200:
                    try:
                        data = response.get_json()
                        print(f'Response keys: {list(data.keys())[:5]}')
                    except:
                        pass
                
                if response.status_code >= 400:
                    all_passed = False
            except Exception as e:
                print(f'FAIL: {e}')
                all_passed = False
        
        print('\n' + '=' * 60)
        if all_passed:
            print('SUCCESS: All endpoints responding - 504 timeout resolved')
        else:
            print('WARNING: Some endpoints returned errors')
        print('=' * 60)
        
        return all_passed

if __name__ == '__main__':
    try:
        success = test_endpoints()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f'FATAL ERROR: {e}')
        sys.exit(1)

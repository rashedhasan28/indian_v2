#!/usr/bin/env python3
"""
Test script to verify the clear logs API functionality
"""
import requests
import json

def test_clear_logs():
    # Test the clear logs API endpoint
    url = 'http://localhost:8000/api/clear-logs/'
    
    # Test data
    data = {
        'clear_all': True
    }
    
    # Headers
    headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': 'test-token'  # This will be ignored in test
    }
    
    try:
        print("Testing clear logs API...")
        print(f"URL: {url}")
        print(f"Data: {json.dumps(data, indent=2)}")
        
        response = requests.post(url, json=data, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('success')}")
            print(f"Message: {result.get('message')}")
        else:
            print("Request failed")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_clear_logs() 
#!/usr/bin/env python3
"""
Test script to check authentication status
"""
import requests
from bs4 import BeautifulSoup

def test_auth():
    # Create a session to maintain cookies
    session = requests.Session()
    
    # First, try to access the order execution monitoring page
    url = 'http://localhost:8000/order-execution-monitoring/'
    
    try:
        print("Testing authentication...")
        print(f"URL: {url}")
        
        response = session.get(url)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Length: {len(response.text)}")
        
        if response.status_code == 200:
            # Check if we're on the login page
            if 'Trading Bot Login' in response.text:
                print("❌ Redirected to login page - User not authenticated")
                return False
            elif 'Real-Time Bot Logs' in response.text:
                print("✅ Successfully accessed the page - User is authenticated")
                return True
            else:
                print("❓ Unknown page content")
                return False
        else:
            print(f"❌ Request failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_auth() 
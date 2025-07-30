#!/usr/bin/env python3
"""
Test script to find the correct Upstox API endpoints for historical data
"""

import os
import django
import requests
from datetime import datetime, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot.settings')
django.setup()

from accounts.models import BrokerageIntegration
from accounts.upstox_api import UpstoxAPI

def test_upstox_endpoints():
    """Test different Upstox API endpoints"""
    print("🔍 Testing Upstox API Endpoints")
    print("=" * 50)
    
    # Get active integration
    integration = BrokerageIntegration.objects.filter(
        brokerage__iexact='upstox',
        is_active=True
    ).first()
    
    if not integration:
        print("❌ No active Upstox integration found")
        return
    
    upstox = UpstoxAPI(user=integration.user)
    
    if not upstox.access_token:
        print("❌ No access token available")
        return
    
    headers = upstox._get_headers()
    base_url = "https://api.upstox.com/v2"
    
    # Test different endpoints
    endpoints_to_test = [
        # Historical data endpoints
        f"{base_url}/historical-candle/AWL/1day",
        f"{base_url}/historical-candle/AWL",
        f"{base_url}/historical-candle/INE699H01024/1day",
        f"{base_url}/historical-candle/INE699H01024",
        
        # Alternative endpoints
        f"{base_url}/market-quote/history/AWL",
        f"{base_url}/market-quote/history/INE699H01024",
        f"{base_url}/market-data/historical/AWL",
        f"{base_url}/market-data/historical/INE699H01024",
        
        # Candle data endpoints
        f"{base_url}/candle/AWL/1day",
        f"{base_url}/candle/INE699H01024/1day",
        f"{base_url}/candles/AWL/1day",
        f"{base_url}/candles/INE699H01024/1day",
    ]
    
    params = {
        'api-version': '2.0',
        'from': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
        'to': datetime.now().strftime('%Y-%m-%d')
    }
    
    for endpoint in endpoints_to_test:
        print(f"\n🔗 Testing: {endpoint}")
        try:
            response = requests.get(endpoint, headers=headers, params=params)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS! Found working endpoint: {endpoint}")
                data = response.json()
                print(f"   📊 Data structure: {type(data)}")
                if isinstance(data, dict):
                    print(f"   📋 Keys: {list(data.keys())}")
                return endpoint
            elif response.status_code == 404:
                print(f"   ❌ 404 - Not Found")
            else:
                print(f"   ⚠️ {response.status_code} - {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n❌ No working historical data endpoint found")
    return None

def test_instrument_search():
    """Test instrument search to find correct symbol format"""
    print("\n🔍 Testing Instrument Search")
    print("=" * 50)
    
    integration = BrokerageIntegration.objects.filter(
        brokerage__iexact='upstox',
        is_active=True
    ).first()
    
    if not integration:
        return
    
    upstox = UpstoxAPI(user=integration.user)
    headers = upstox._get_headers()
    
    # Test search for AWL
    search_url = "https://api.upstox.com/v2/search/instruments"
    search_params = {
        'query': 'AWL',
        'api-version': '2.0'
    }
    
    try:
        response = requests.get(search_url, headers=headers, params=search_params)
        print(f"Search response status: {response.status_code}")
        print(f"Search response: {response.text[:500]}...")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search successful")
            print(f"📊 Found instruments: {data}")
        else:
            print(f"❌ Search failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Search error: {e}")

def test_market_quote_endpoints():
    """Test market quote endpoints"""
    print("\n💰 Testing Market Quote Endpoints")
    print("=" * 50)
    
    integration = BrokerageIntegration.objects.filter(
        brokerage__iexact='upstox',
        is_active=True
    ).first()
    
    if not integration:
        return
    
    upstox = UpstoxAPI(user=integration.user)
    headers = upstox._get_headers()
    base_url = "https://api.upstox.com/v2"
    
    quote_endpoints = [
        f"{base_url}/market-quote/ltp?symbol=AWL",
        f"{base_url}/market-quote/ltp?symbol=INE699H01024",
        f"{base_url}/market-quote/quote?symbol=AWL",
        f"{base_url}/market-quote/quote?symbol=INE699H01024",
    ]
    
    for endpoint in quote_endpoints:
        print(f"\n🔗 Testing: {endpoint}")
        try:
            response = requests.get(endpoint, headers=headers)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS!")
            else:
                print(f"   ❌ Failed")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Upstox API Endpoint Discovery")
    print("=" * 60)
    
    # Test different endpoints
    working_endpoint = test_upstox_endpoints()
    
    # Test instrument search
    test_instrument_search()
    
    # Test market quote endpoints
    test_market_quote_endpoints()
    
    if working_endpoint:
        print(f"\n🎉 Found working endpoint: {working_endpoint}")
    else:
        print("\n❌ No working historical data endpoint found")
        print("This might indicate:")
        print("1. Different API version required")
        print("2. Different symbol format needed")
        print("3. Historical data not available for this account type")
        print("4. API permissions issue") 
#!/usr/bin/env python3
"""
Test script to verify Upstox integration functionality
This script will test:
1. Database connection and integration status
2. Upstox API connectivity
3. Market data fetching
4. OHLCV data retrieval
5. Token validation
"""

import os
import sys
import django
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot.settings')
django.setup()

from accounts.models import BrokerageIntegration, MarketData, BotLog
from accounts.upstox_api import UpstoxAPI, TradingBot
from django.contrib.auth.models import User

def test_database_connection():
    """Test database connection and integration status"""
    print("🔍 Testing Database Connection...")
    print("=" * 50)
    
    try:
        # Check if any users exist
        users = User.objects.all()
        print(f"✅ Database connected. Found {users.count()} users")
        
        # Check brokerage integrations
        integrations = BrokerageIntegration.objects.all()
        print(f"📊 Found {integrations.count()} brokerage integrations")
        
        for integration in integrations:
            print(f"\n📋 Integration Details:")
            print(f"   Brokerage: {integration.brokerage}")
            print(f"   User: {integration.user}")
            print(f"   API Key: {integration.api_key[:10]}..." if integration.api_key else "   API Key: None")
            print(f"   Access Token: {'✓ Present' if integration.access_token else '✗ Missing'}")
            print(f"   Refresh Token: {'✓ Present' if integration.refresh_token else '✗ Missing'}")
            print(f"   Is Active: {'✓ Yes' if integration.is_active else '✗ No'}")
            print(f"   Token Expiry: {integration.token_expiry}")
            print(f"   Created: {integration.timestamp}")
        
        return integrations
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return []

def test_upstox_api_connectivity(integration):
    """Test Upstox API connectivity"""
    print(f"\n🔗 Testing Upstox API Connectivity...")
    print("=" * 50)
    
    if not integration:
        print("❌ No integration found to test")
        return False
    
    try:
        # Create UpstoxAPI instance
        upstox = UpstoxAPI(user=integration.user)
        
        if not upstox.access_token:
            print("❌ No access token available")
            return False
        
        print(f"✅ Access token loaded: {upstox.access_token[:20]}...")
        
        # Test profile API
        print("\n👤 Testing Profile API...")
        profile = upstox.get_profile()
        if profile:
            print(f"✅ Profile API working")
            print(f"   Response: {profile}")
        else:
            print("❌ Profile API failed")
            return False
        
        # Test holdings API
        print("\n💼 Testing Holdings API...")
        holdings = upstox.get_holdings()
        if holdings:
            print(f"✅ Holdings API working")
            print(f"   Response: {holdings}")
        else:
            print("❌ Holdings API failed")
        
        # Test margins API
        print("\n💰 Testing Margins API...")
        margins = upstox.get_margins()
        if margins:
            print(f"✅ Margins API working")
            print(f"   Response: {margins}")
        else:
            print("❌ Margins API failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Upstox API test failed: {e}")
        return False

def test_market_data_fetching(integration):
    """Test market data fetching and OHLCV data"""
    print(f"\n📈 Testing Market Data Fetching...")
    print("=" * 50)
    
    if not integration:
        print("❌ No integration found to test")
        return False
    
    try:
        # Create TradingBot instance
        bot = TradingBot(user=integration.user)
        
        # Test symbols to try - using trading symbols from holdings
        test_symbols = [
            'NSE_EQ|AWL',        # AWL (from holdings)
            'NSE_EQ|IREDA',      # IREDA (from holdings)
            'NSE_EQ|MUTHOOTMF',  # MUTHOOTMF (from holdings)
            'NSE_EQ|SEPC',       # SEPC (from holdings)
            'NSE_EQ|BIKAJI',     # BIKAJI (from holdings)
        ]
        
        for symbol in test_symbols:
            print(f"\n🔍 Testing symbol: {symbol}")
            
            # Test live quote
            print("   📊 Testing live quote...")
            quote = bot.upstox.get_live_quote(symbol)
            if quote:
                print(f"   ✅ Live quote working: {quote}")
            else:
                print(f"   ❌ Live quote failed for {symbol}")
                continue
            
            # Test historical data
            print("   📈 Testing historical data...")
            data = bot.get_market_data_for_analysis(symbol, '1D', 30)
            if data is not None:
                print(f"   ✅ Historical data working")
                print(f"   📊 Data shape: {data.shape}")
                print(f"   📅 Date range: {data.index[0]} to {data.index[-1]}")
                print(f"   💰 Latest close: ₹{data['close'].iloc[-1]:.2f}")
                print(f"   📊 Latest volume: {data['volume'].iloc[-1]:,}")
                
                # Check if data was saved to database
                latest_market_data = MarketData.objects.filter(symbol=symbol).order_by('-timestamp').first()
                if latest_market_data:
                    print(f"   💾 Data saved to database: {latest_market_data.timestamp}")
                else:
                    print(f"   ⚠️ Data not saved to database")
                
                return True  # Success with first working symbol
            else:
                print(f"   ❌ Historical data failed for {symbol}")
        
        print("❌ All symbols failed")
        return False
        
    except Exception as e:
        print(f"❌ Market data test failed: {e}")
        return False

def test_bot_logs():
    """Check bot logs for recent activity"""
    print(f"\n📝 Checking Bot Logs...")
    print("=" * 50)
    
    try:
        # Get recent logs
        recent_logs = BotLog.objects.all().order_by('-timestamp')[:10]
        
        if recent_logs:
            print(f"✅ Found {recent_logs.count()} recent logs")
            for log in recent_logs:
                print(f"\n📋 Log Entry:")
                print(f"   Type: {log.log_type}")
                print(f"   Message: {log.message}")
                print(f"   User: {log.user}")
                print(f"   Time: {log.timestamp}")
                if log.details:
                    print(f"   Details: {log.details}")
        else:
            print("⚠️ No recent bot logs found")
        
        # Check for errors
        error_logs = BotLog.objects.filter(log_type='ERROR').order_by('-timestamp')[:5]
        if error_logs:
            print(f"\n❌ Recent Errors ({error_logs.count()}):")
            for log in error_logs:
                print(f"   {log.timestamp}: {log.message}")
        
    except Exception as e:
        print(f"❌ Error checking logs: {e}")

def test_market_data_database():
    """Check market data in database"""
    print(f"\n💾 Checking Market Data Database...")
    print("=" * 50)
    
    try:
        market_data = MarketData.objects.all().order_by('-timestamp')[:10]
        
        if market_data:
            print(f"✅ Found {market_data.count()} recent market data entries")
            for data in market_data:
                print(f"\n📊 Market Data Entry:")
                print(f"   Symbol: {data.symbol}")
                print(f"   Open: ₹{data.open_price}")
                print(f"   High: ₹{data.high_price}")
                print(f"   Low: ₹{data.low_price}")
                print(f"   Close: ₹{data.close_price}")
                print(f"   Volume: {data.volume:,}")
                print(f"   Timestamp: {data.timestamp}")
        else:
            print("⚠️ No market data found in database")
        
    except Exception as e:
        print(f"❌ Error checking market data: {e}")

def main():
    """Main test function"""
    print("🚀 Upstox Integration Test Suite")
    print("=" * 60)
    print(f"Test started at: {datetime.now()}")
    
    # Test 1: Database connection
    integrations = test_database_connection()
    
    if not integrations:
        print("\n❌ No integrations found. Please configure Upstox integration first.")
        return
    
    # Test 2: API connectivity
    for integration in integrations:
        if integration.brokerage.lower() == 'upstox':
            print(f"\n🎯 Testing Upstox integration for user: {integration.user}")
            api_working = test_upstox_api_connectivity(integration)
            
            if api_working:
                # Test 3: Market data fetching
                data_working = test_market_data_fetching(integration)
                
                if data_working:
                    print("\n✅ Upstox integration is WORKING and getting OHLCV data!")
                else:
                    print("\n⚠️ Upstox integration connected but market data fetching failed")
            else:
                print("\n❌ Upstox integration is NOT working")
    
    # Test 4: Check logs
    test_bot_logs()
    
    # Test 5: Check market data database
    test_market_data_database()
    
    print(f"\n🏁 Test completed at: {datetime.now()}")

if __name__ == "__main__":
    main() 
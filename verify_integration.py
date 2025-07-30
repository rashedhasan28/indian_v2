#!/usr/bin/env python3
"""
Quick verification script to test Upstox integration after re-authentication
"""

import os
import django
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot.settings')
django.setup()

from accounts.models import BrokerageIntegration, MarketData
from accounts.upstox_api import UpstoxAPI, TradingBot

def quick_verification():
    """Quick verification of integration status"""
    print("🔍 Quick Integration Verification")
    print("=" * 40)
    
    # Check for active integration
    integration = BrokerageIntegration.objects.filter(
        brokerage__iexact='upstox',
        is_active=True
    ).first()
    
    if not integration:
        print("❌ No active Upstox integration found")
        print("Please re-authenticate at: http://localhost:8000/brokerage-integration/")
        return False
    
    print(f"✅ Found active integration for user: {integration.user}")
    print(f"📅 Token expiry: {integration.token_expiry}")
    print(f"🔄 Has refresh token: {'Yes' if integration.refresh_token else 'No'}")
    
    # Test API connectivity
    try:
        upstox = UpstoxAPI(user=integration.user)
        
        if not upstox.access_token:
            print("❌ No access token available")
            return False
        
        print("🔗 Testing API connectivity...")
        
        # Test profile API
        profile = upstox.get_profile()
        if profile:
            print("✅ Profile API working")
        else:
            print("❌ Profile API failed")
            return False
        
        # Test market data
        print("📈 Testing market data...")
        bot = TradingBot(user=integration.user)
        
        # Test with a symbol from holdings
        data = bot.get_market_data_for_analysis('NSE_EQ|AWL', '1D', 5)
        if data is not None:
            print("✅ Market data working")
            print(f"📊 Got {len(data)} data points")
            print(f"💰 Latest price: ₹{data['close'].iloc[-1]:.2f}")
            
            # Check database
            latest_data = MarketData.objects.filter(symbol='NSE_EQ|AWL').order_by('-timestamp').first()
            if latest_data:
                print("✅ Data saved to database")
            else:
                print("⚠️ Data not saved to database")
            
            return True
        else:
            print("❌ Market data failed")
            return False
            
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False

if __name__ == "__main__":
    success = quick_verification()
    if success:
        print("\n🎉 Integration is WORKING! You can now use automated trading.")
    else:
        print("\n⚠️ Integration needs attention. Please re-authenticate.") 
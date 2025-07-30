#!/usr/bin/env python
"""
Setup script for Upstox integration and testing with correct Indian stock symbols
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import BrokerageIntegration, TradingSetup, Strategy, BotLog
from accounts.upstox_api import TradingBot

def setup_upstox_integration():
    """Setup Upstox integration for testing"""
    
    print("🔧 Setting Up Upstox Integration")
    print("=" * 50)
    
    # Get or create test user
    user, created = User.objects.get_or_create(
        username='test@example.com',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    
    print(f"👤 Using user: {user.email}")
    
    # Check if Upstox integration exists
    integration = BrokerageIntegration.objects.filter(
        user=user, 
        brokerage__iexact='upstox',
        is_active=True
    ).first()
    
    if integration:
        print(f"✅ Found existing Upstox integration")
        print(f"   API Key: {integration.api_key[:10]}...")
        print(f"   Access Token: {'Yes' if integration.access_token else 'No'}")
        print(f"   Token Expiry: {integration.token_expiry}")
        
        if not integration.access_token:
            print("⚠️ No access token found. You need to complete the Upstox authorization.")
            print("   Go to: http://localhost:8000/brokerage-integration/")
            print("   Follow the Upstox authorization process.")
            return False
        else:
            return True
    else:
        print("❌ No Upstox integration found")
        print("📋 To set up Upstox integration:")
        print("   1. Go to: http://localhost:8000/brokerage-integration/")
        print("   2. Enter your Upstox API credentials:")
        print("      - API Key: Your Upstox API key")
        print("      - Secret Key: Your Upstox secret key")
        print("      - Startup URL: http://localhost:8000/capture-upstox-code/")
        print("   3. Complete the Upstox authorization process")
        return False

def create_test_strategies_with_correct_symbols():
    """Create test strategies with correct Indian stock symbols"""
    
    print("\n📊 Creating Test Strategies with Correct Indian Stock Symbols")
    print("=" * 60)
    
    # Get or create test user
    user, created = User.objects.get_or_create(
        username='test@example.com',
        defaults={'email': 'test@example.com'}
    )
    
    # Correct Indian stock symbols for Upstox (NSE format)
    test_setups = [
        {
            'name': 'Reliance RSI Strategy',
            'indicator': 'RSI',
            'timeframe': '1d',
            'symbol': 'NSE_EQ|INE002A01018',  # Reliance Industries
            'quantity': 10
        },
        {
            'name': 'TCS MACD Strategy',
            'indicator': 'MACD',
            'timeframe': '1d',
            'symbol': 'NSE_EQ|INE467B01029',  # TCS
            'quantity': 5
        },
        {
            'name': 'HDFC Bank Moving Average Strategy',
            'indicator': 'Moving Average',
            'timeframe': '1d',
            'symbol': 'NSE_EQ|INE040A01034',  # HDFC Bank
            'quantity': 15
        },
        {
            'name': 'Infosys VWAP Strategy',
            'indicator': 'VWAP',
            'timeframe': '1d',
            'symbol': 'NSE_EQ|INE009A01021',  # Infosys
            'quantity': 8
        }
    ]
    
    created_setups = []
    
    for setup_data in test_setups:
        setup, created = TradingSetup.objects.get_or_create(
            user=user,
            name=setup_data['name'],
            defaults={
                'indicator': setup_data['indicator'],
                'timeframe': setup_data['timeframe'],
                'exchange': 'NSE',
                'type': 'Cash',
                'market': 'Equity',
                'symbol': setup_data['symbol'],
                'quantity': setup_data['quantity']
            }
        )
        
        if created:
            print(f"✅ Created: {setup.name}")
            print(f"   Symbol: {setup.symbol}")
            print(f"   Indicator: {setup.indicator}")
            print(f"   Timeframe: {setup.timeframe}")
        else:
            print(f"📋 Found existing: {setup.name}")
        
        created_setups.append(setup)
    
    return created_setups

def test_bot_with_upstox_data():
    """Test the bot with Upstox data"""
    
    print("\n🧪 Testing Bot with Upstox Data")
    print("=" * 40)
    
    # Get or create test user
    user, created = User.objects.get_or_create(
        username='test@example.com',
        defaults={'email': 'test@example.com'}
    )
    
    bot = TradingBot(user)
    
    # Check if Upstox is available
    if not bot.upstox.access_token:
        print("❌ No Upstox access token available")
        print("   Please complete Upstox integration first")
        return False
    
    # Get test setups
    setups = TradingSetup.objects.filter(user=user)
    
    if not setups.exists():
        print("❌ No trading setups found")
        print("   Please create trading setups first")
        return False
    
    print(f"📊 Testing {setups.count()} trading setups...")
    
    for setup in setups:
        print(f"\n🔍 Testing {setup.name} ({setup.symbol})")
        print("-" * 40)
        
        # Test 1: Get market data from Upstox
        print(f"📈 Getting market data from Upstox...")
        data = bot.get_market_data_for_analysis(setup.symbol, setup.timeframe)
        
        if data is not None:
            print(f"✅ Got {len(data)} data points from Upstox")
            print(f"   Date range: {data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}")
            print(f"   Latest close: ₹{data['close'].iloc[-1]:.2f}")
            print(f"   Data source: Upstox API")
        else:
            print("❌ Failed to get market data from Upstox")
            continue
        
        # Test 2: Generate signal
        print(f"🎯 Generating {setup.indicator} signal...")
        signal = bot.generate_signal(setup)
        
        if signal:
            print(f"✅ Generated signal: {signal.upper()}")
            
            # Test 3: Check if we should execute trade
            if signal in ['buy', 'sell']:
                print(f"💰 Signal is {signal.upper()} - would execute trade")
                print(f"   Symbol: {setup.symbol}")
                print(f"   Quantity: {setup.quantity}")
                print(f"   Current Price: ₹{data['close'].iloc[-1]:.2f}")
                print(f"   Total Value: ₹{data['close'].iloc[-1] * setup.quantity:.2f}")
            else:
                print(f"⏸️ Signal is {signal.upper()} - no trade action")
        else:
            print("❌ Failed to generate signal")
    
    return True

def show_recent_logs():
    """Show recent bot logs"""
    
    print(f"\n📋 Recent Bot Logs:")
    print("-" * 40)
    
    user, created = User.objects.get_or_create(
        username='test@example.com',
        defaults={'email': 'test@example.com'}
    )
    
    recent_logs = BotLog.objects.filter(user=user).order_by('-timestamp')[:15]
    
    for log in recent_logs:
        print(f"{log.timestamp.strftime('%H:%M:%S')} - {log.log_type}: {log.message}")
    
    print(f"\n📊 Total logs: {BotLog.objects.filter(user=user).count()}")

def main():
    """Main function to run all tests"""
    
    print("🚀 Upstox Integration and Bot Testing")
    print("=" * 50)
    
    # Step 1: Check Upstox integration
    upstox_ready = setup_upstox_integration()
    
    if not upstox_ready:
        print("\n⚠️ Upstox integration not ready")
        print("   Please complete the Upstox setup first")
        print("   Then run this script again")
        return
    
    # Step 2: Create test strategies
    setups = create_test_strategies_with_correct_symbols()
    
    # Step 3: Test bot functionality
    test_success = test_bot_with_upstox_data()
    
    # Step 4: Show logs
    show_recent_logs()
    
    if test_success:
        print(f"\n🎉 Bot testing completed successfully!")
        print(f"🌐 Check monitoring page: http://localhost:8000/order-execution-monitoring/")
        print(f"🤖 Start the bot: python run_bot.py --interval 60")
    else:
        print(f"\n❌ Bot testing failed")
        print(f"   Check the logs above for errors")

if __name__ == '__main__':
    main() 
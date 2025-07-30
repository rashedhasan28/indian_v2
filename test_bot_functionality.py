#!/usr/bin/env python
"""
Test script to verify bot functionality:
1. Getting real candle data from Upstox/Yahoo Finance
2. Calculating indicators properly
3. Generating trading signals
4. Logging all activities
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import TradingSetup, Strategy, BotLog
from accounts.upstox_api import TradingBot

def test_bot_functionality():
    """Test the complete bot functionality"""
    
    print("🧪 Testing Bot Functionality")
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
    
    # Create test trading setups for different indicators with working symbols
    test_setups = [
        {
            'name': 'RSI Strategy Test',
            'indicator': 'RSI',
            'timeframe': '1d',
            'symbol': 'RELIANCE.NS'  # Use full Yahoo Finance symbol
        },
        {
            'name': 'MACD Strategy Test', 
            'indicator': 'MACD',
            'timeframe': '1d',
            'symbol': 'TCS.NS'  # Use full Yahoo Finance symbol
        },
        {
            'name': 'Moving Average Strategy Test',
            'indicator': 'Moving Average',
            'timeframe': '1d', 
            'symbol': 'HDFCBANK.NS'  # Use full Yahoo Finance symbol
        }
    ]
    
    bot = TradingBot(user)
    
    for setup_data in test_setups:
        print(f"\n📊 Testing {setup_data['indicator']} for {setup_data['symbol']}")
        print("-" * 40)
        
        # Create trading setup
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
                'quantity': 10
            }
        )
        
        print(f"✅ Created/Found setup: {setup.name}")
        
        # Test 1: Get market data
        print(f"📈 Getting market data for {setup.symbol}...")
        data = bot.get_market_data_for_analysis(setup.symbol, setup.timeframe)
        
        if data is not None:
            print(f"✅ Got {len(data)} data points")
            print(f"   Date range: {data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}")
            print(f"   Latest close: ₹{data['close'].iloc[-1] if 'close' in data.columns else data['Close'].iloc[-1]:.2f}")
            print(f"   Columns: {list(data.columns)}")
        else:
            print("❌ Failed to get market data")
            continue
        
        # Test 2: Generate signal
        print(f"🎯 Generating {setup.indicator} signal...")
        signal = bot.generate_signal(setup)
        
        if signal:
            print(f"✅ Generated signal: {signal.upper()}")
        else:
            print("❌ Failed to generate signal")
            continue
        
        # Test 3: Check if we should execute trade
        if signal in ['buy', 'sell']:
            print(f"💰 Signal is {signal.upper()} - would execute trade")
            print(f"   Symbol: {setup.symbol}")
            print(f"   Quantity: {setup.quantity}")
            print(f"   Current Price: ₹{data['close'].iloc[-1] if 'close' in data.columns else data['Close'].iloc[-1]:.2f}")
        else:
            print(f"⏸️ Signal is {signal.upper()} - no trade action")
    
    # Show recent logs
    print(f"\n📋 Recent Bot Logs:")
    print("-" * 40)
    recent_logs = BotLog.objects.filter(user=user).order_by('-timestamp')[:10]
    
    for log in recent_logs:
        print(f"{log.timestamp.strftime('%H:%M:%S')} - {log.log_type}: {log.message}")
    
    print(f"\n🎉 Bot functionality test completed!")
    print(f"📊 Total logs created: {BotLog.objects.filter(user=user).count()}")
    print(f"🌐 Check monitoring page: http://localhost:8000/order-execution-monitoring/")

def test_upstox_connection():
    """Test Upstox API connection specifically"""
    print("\n🔗 Testing Upstox API Connection")
    print("=" * 40)
    
    user, created = User.objects.get_or_create(
        username='test@example.com',
        defaults={'email': 'test@example.com'}
    )
    
    bot = TradingBot(user)
    
    # Check if Upstox token is available
    if bot.upstox.access_token:
        print("✅ Upstox access token found")
        print(f"   Token: {bot.upstox.access_token[:20]}...")
        
        # Test Upstox API call
        try:
            profile = bot.upstox.get_profile()
            if profile:
                print("✅ Upstox API connection successful")
                print(f"   Profile: {profile.get('data', {}).get('name', 'Unknown')}")
            else:
                print("❌ Upstox API connection failed")
        except Exception as e:
            print(f"❌ Upstox API error: {e}")
    else:
        print("⚠️ No Upstox access token found")
        print("   Will use Yahoo Finance as fallback")

def test_yahoo_finance_directly():
    """Test Yahoo Finance directly to verify data access"""
    print("\n📊 Testing Yahoo Finance Directly")
    print("=" * 40)
    
    try:
        import yfinance as yf
        
        test_symbols = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS']
        
        for symbol in test_symbols:
            print(f"\n🔍 Testing {symbol}...")
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="30d")
            
            if not data.empty:
                print(f"✅ Got {len(data)} data points")
                print(f"   Latest close: ₹{data['Close'].iloc[-1]:.2f}")
                print(f"   Date range: {data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}")
            else:
                print(f"❌ No data for {symbol}")
                
    except Exception as e:
        print(f"❌ Yahoo Finance test failed: {e}")

if __name__ == '__main__':
    test_upstox_connection()
    test_yahoo_finance_directly()
    test_bot_functionality() 
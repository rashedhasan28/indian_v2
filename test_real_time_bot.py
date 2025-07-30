#!/usr/bin/env python3
"""
Test script for real-time trading bot
"""

import os
import django
import time

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot.settings')
django.setup()

from accounts.models import Strategy, TradingSetup, User, BrokerageIntegration
from real_time_trading_bot import RealTimeTradingBot

def test_real_time_bot():
    """Test the real-time trading bot"""
    print("🧪 Testing Real-time Trading Bot")
    print("=" * 50)
    
    # Get user with active integration
    active_integration = BrokerageIntegration.objects.filter(
        brokerage__iexact='upstox',
        is_active=True
    ).first()
    
    if active_integration:
        user = active_integration.user
        print(f"👤 Using user with active integration: {user.email}")
    else:
        user = User.objects.first()  # Fallback to first user
        print(f"⚠️ No active integration found, using first user: {user.email}")
    
    if not user:
        print("❌ No users found")
        return
    
    # Check if user has active strategies
    active_strategies = Strategy.objects.filter(user=user, status='RUNNING')
    if not active_strategies:
        print("⚠️ No active strategies found")
        print("Creating a test strategy...")
        
        # Create a test setup
        setup = TradingSetup.objects.create(
            user=user,
            name="Test Setup",
            indicator="RSI",
            timeframe="1D",
            exchange="NSE",
            type="EQ",
            market="NSE",
            symbol="NSE_EQ|AWL",  # Using a symbol from holdings
            quantity=1,
            is_active=True
        )
        
        # Create a test strategy
        strategy = Strategy.objects.create(
            user=user,
            name="Test Strategy",
            setup=setup,
            status='RUNNING'
        )
        
        print(f"✅ Created test strategy: {strategy.name}")
        print(f"   Symbol: {setup.symbol}")
        print(f"   Indicator: {setup.indicator}")
        print(f"   Quantity: {setup.quantity}")
    else:
        print(f"✅ Found {active_strategies.count()} active strategies")
        for strategy in active_strategies:
            print(f"   - {strategy.name}: {strategy.setup.symbol} ({strategy.setup.indicator})")
    
    # Create and test the bot
    bot = RealTimeTradingBot(user)
    
    print("\n🚀 Starting real-time bot for 30 seconds...")
    print("📊 This will test indicator calculations and signal generation")
    print("💡 No actual trades will be executed in test mode")
    
    # Start the bot
    bot.start_monitoring()
    
    # Let it run for 30 seconds
    time.sleep(30)
    
    # Stop the bot
    bot.stop_monitoring()
    
    print("\n✅ Test completed!")
    print("📝 Check the logs for signal generation and indicator calculations")

if __name__ == "__main__":
    test_real_time_bot() 
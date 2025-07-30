#!/usr/bin/env python
"""
Test script to generate sample bot logs for testing the monitoring interface
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import BotLog, Strategy, TradingSetup

def create_sample_logs():
    """Create sample bot logs for testing"""
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='test@example.com',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    
    # Get or create a test trading setup
    setup, created = TradingSetup.objects.get_or_create(
        user=user,
        name='Test RSI Strategy',
        defaults={
            'indicator': 'RSI',
            'timeframe': '1D',
            'exchange': 'NSE',
            'type': 'Cash',
            'market': 'Equity',
            'symbol': 'RELIANCE',
            'quantity': 10
        }
    )
    
    # Get or create a test strategy
    strategy, created = Strategy.objects.get_or_create(
        user=user,
        name='Test RSI Strategy',
        defaults={
            'setup': setup,
            'status': 'RUNNING'
        }
    )
    
    # Create sample logs
    sample_logs = [
        {
            'log_type': 'STRATEGY_START',
            'message': '🚀 Strategy "Test RSI Strategy" started',
            'details': {'strategy_name': 'Test RSI Strategy', 'symbol': 'RELIANCE'}
        },
        {
            'log_type': 'INFO',
            'message': '🔄 Checking strategy: Test RSI Strategy (RELIANCE)',
            'details': {'strategy_name': 'Test RSI Strategy', 'symbol': 'RELIANCE', 'indicator': 'RSI'}
        },
        {
            'log_type': 'DATA_FETCH',
            'message': '📊 Successfully fetched 30 candles for RELIANCE (1D)',
            'details': {'symbol': 'RELIANCE', 'interval': '1D', 'latest_close': 2456.78, 'data_points': 30}
        },
        {
            'log_type': 'INDICATOR_CALC',
            'message': '📈 Calculating RSI for RELIANCE',
            'details': {'symbol': 'RELIANCE', 'indicator': 'RSI', 'timeframe': '1D', 'data_points': 30}
        },
        {
            'log_type': 'SIGNAL_GENERATED',
            'message': '🎯 Generated BUY signal for RELIANCE using RSI',
            'details': {'symbol': 'RELIANCE', 'indicator': 'RSI', 'signal': 'buy', 'latest_close': 2456.78}
        },
        {
            'log_type': 'TRADE_EXECUTED',
            'message': '✅ Successfully executed BUY order for 10 RELIANCE at ₹2456.78',
            'details': {'symbol': 'RELIANCE', 'trade_type': 'BUY', 'quantity': 10, 'price': 2456.78, 'order_id': 'TEST123'}
        },
        {
            'log_type': 'INFO',
            'message': '🔄 Checking strategy: Test RSI Strategy (RELIANCE)',
            'details': {'strategy_name': 'Test RSI Strategy', 'symbol': 'RELIANCE', 'indicator': 'RSI'}
        },
        {
            'log_type': 'DATA_FETCH',
            'message': '📊 Successfully fetched 30 candles for RELIANCE (1D)',
            'details': {'symbol': 'RELIANCE', 'interval': '1D', 'latest_close': 2460.50, 'data_points': 30}
        },
        {
            'log_type': 'INDICATOR_CALC',
            'message': '📈 Calculating RSI for RELIANCE',
            'details': {'symbol': 'RELIANCE', 'indicator': 'RSI', 'timeframe': '1D', 'data_points': 30}
        },
        {
            'log_type': 'SIGNAL_GENERATED',
            'message': '⏸️ Hold signal for RELIANCE - No action taken',
            'details': {'symbol': 'RELIANCE', 'signal': 'hold', 'indicator': 'RSI'}
        }
    ]
    
    # Create the logs
    for log_data in sample_logs:
        BotLog.objects.create(
            user=user,
            strategy=strategy,
            log_type=log_data['log_type'],
            message=log_data['message'],
            details=log_data['details']
        )
    
    print(f"✅ Created {len(sample_logs)} sample logs for user: {user.email}")
    print(f"📊 Strategy: {strategy.name} ({strategy.status})")
    print(f"📈 Symbol: {setup.symbol}")
    print("\n🎯 Now go to the monitoring page to see the logs!")
    print("🌐 URL: http://localhost:8000/order-execution-monitoring/")

if __name__ == '__main__':
    create_sample_logs() 
#!/usr/bin/env python3
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot.settings')
django.setup()

from accounts.models import Strategy, TradingSetup, User, BrokerageIntegration

print("🔧 Fixing Strategies")
print("=" * 40)

# Get user with active integration
active_integration = BrokerageIntegration.objects.filter(
    brokerage__iexact='upstox',
    is_active=True
).first()

if not active_integration:
    print("❌ No active integration found")
    exit()

user = active_integration.user
print(f"👤 Working with user: {user.email}")

# Get all strategies for this user
strategies = Strategy.objects.filter(user=user)
print(f"📊 Found {strategies.count()} strategies")

# Correct symbols from holdings
correct_symbols = [
    'NSE_EQ|AWL',        # AWL
    'NSE_EQ|IREDA',      # IREDA  
    'NSE_EQ|MUTHOOTMF',  # MUTHOOTMF
    'NSE_EQ|SEPC',       # SEPC
    'NSE_EQ|BIKAJI',     # BIKAJI
    'NSE_EQ|EXXARO',     # EXXARO
]

for i, strategy in enumerate(strategies):
    setup = strategy.setup
    old_symbol = setup.symbol
    
    # Use correct symbol (cycle through available symbols)
    new_symbol = correct_symbols[i % len(correct_symbols)]
    
    print(f"📋 Strategy: {strategy.name}")
    print(f"   Old symbol: {old_symbol}")
    print(f"   New symbol: {new_symbol}")
    
    # Update the symbol
    setup.symbol = new_symbol
    setup.save()
    
    print(f"   ✅ Updated")

print("\n✅ All strategies updated!")
print("🚀 Now run the real-time bot again") 
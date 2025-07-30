#!/usr/bin/env python3
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot.settings')
django.setup()

from accounts.models import BrokerageIntegration
from accounts.upstox_api import UpstoxAPI

print("🔍 Debugging Live Quote Response")
print("=" * 40)

# Get active integration
active_integration = BrokerageIntegration.objects.filter(
    brokerage__iexact='upstox',
    is_active=True
).first()

if not active_integration:
    print("❌ No active integration found")
    exit()

upstox = UpstoxAPI(user=active_integration.user)

# Test symbols
test_symbols = ['NSE_EQ|AWL', 'NSE_EQ|IREDA']

for symbol in test_symbols:
    print(f"\n🔍 Testing symbol: {symbol}")
    
    # Get live quote
    quote = upstox.get_live_quote(symbol)
    
    if quote:
        print(f"✅ Got response: {quote}")
        
        # Check different possible price fields
        data = quote.get('data', {})
        print(f"📊 Data section: {data}")
        
        # Try different price field names
        price_fields = ['ltp', 'last_price', 'close', 'price', 'current_price']
        for field in price_fields:
            if field in data:
                print(f"💰 Found {field}: {data[field]}")
    else:
        print(f"❌ No response for {symbol}") 
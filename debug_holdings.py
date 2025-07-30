#!/usr/bin/env python3
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot.settings')
django.setup()

from accounts.models import BrokerageIntegration
from accounts.upstox_api import UpstoxAPI

print("🔍 Debugging Holdings Data")
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

# Get holdings
holdings = upstox.get_holdings()

if holdings and 'data' in holdings:
    print(f"✅ Got {len(holdings['data'])} holdings")
    
    for holding in holdings['data']:
        print(f"\n📊 Holding:")
        print(f"   Trading Symbol: {holding.get('tradingsymbol')}")
        print(f"   Instrument Token: {holding.get('instrument_token')}")
        print(f"   Last Price: {holding.get('last_price')}")
        print(f"   Close Price: {holding.get('close_price')}")
        print(f"   Quantity: {holding.get('quantity')}")
        
        # Check if this matches our symbols
        if holding.get('tradingsymbol') in ['AWL', 'IREDA', 'MUTHOOTMF', 'SEPC', 'BIKAJI', 'EXXARO']:
            print(f"   ✅ MATCHES our symbols!")
else:
    print("❌ No holdings data") 
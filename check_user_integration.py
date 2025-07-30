#!/usr/bin/env python3
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot.settings')
django.setup()

from accounts.models import BrokerageIntegration, User

print("🔍 Checking User Integration")
print("=" * 40)

# Find active integration
active_integration = BrokerageIntegration.objects.filter(
    brokerage__iexact='upstox',
    is_active=True
).first()

if active_integration:
    print(f"✅ Found active integration for user: {active_integration.user}")
    print(f"   Token: {'Present' if active_integration.access_token else 'Missing'}")
    print(f"   Expiry: {active_integration.token_expiry}")
    
    # Test if this user can access the token
    from accounts.upstox_api import UpstoxAPI
    upstox = UpstoxAPI(user=active_integration.user)
    print(f"   UpstoxAPI token: {'Present' if upstox.access_token else 'Missing'}")
    
else:
    print("❌ No active integration found")

print("\n👥 All users:")
users = User.objects.all()
for user in users:
    integrations = BrokerageIntegration.objects.filter(user=user, brokerage__iexact='upstox')
    print(f"  {user.email}: {integrations.count()} integrations") 
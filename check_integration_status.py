#!/usr/bin/env python3
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot.settings')
django.setup()

from accounts.models import BrokerageIntegration

print("🔍 Checking Integration Status")
print("=" * 40)

integrations = BrokerageIntegration.objects.filter(brokerage__iexact='upstox')
print(f"Found {integrations.count()} Upstox integrations")

for i in integrations:
    print(f"ID: {i.id}")
    print(f"  User: {i.user}")
    print(f"  Active: {i.is_active}")
    print(f"  Token: {'Present' if i.access_token else 'Missing'}")
    print(f"  Refresh Token: {'Present' if i.refresh_token else 'Missing'}")
    print(f"  Expiry: {i.token_expiry}")
    print() 
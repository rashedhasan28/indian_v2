#!/usr/bin/env python3
"""
Script to fix Upstox integration issues
This will:
1. Clear expired tokens
2. Reset integration status
3. Provide instructions for re-authentication
"""

import os
import django
from datetime import datetime, timedelta
from django.db import models

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot.settings')
django.setup()

from accounts.models import BrokerageIntegration, BotLog
from django.contrib.auth.models import User

def clear_expired_integrations():
    """Clear expired or invalid integrations"""
    print("🧹 Clearing Expired Integrations...")
    print("=" * 50)
    
    # Find integrations with expired tokens or missing refresh tokens
    expired_integrations = BrokerageIntegration.objects.filter(
        brokerage__iexact='upstox'
    ).filter(
        models.Q(token_expiry__lt=datetime.now()) |  # Expired tokens
        models.Q(refresh_token__isnull=True) |       # Missing refresh token
        models.Q(refresh_token='')                   # Empty refresh token
    )
    
    print(f"Found {expired_integrations.count()} expired/invalid integrations")
    
    for integration in expired_integrations:
        print(f"\n📋 Integration ID: {integration.id}")
        print(f"   User: {integration.user}")
        print(f"   Created: {integration.timestamp}")
        print(f"   Token Expiry: {integration.token_expiry}")
        print(f"   Has Refresh Token: {'No' if not integration.refresh_token else 'Yes'}")
        
        # Clear tokens and deactivate
        integration.access_token = None
        integration.refresh_token = None
        integration.token_expiry = None
        integration.is_active = False
        integration.save()
        
        print(f"   ✅ Cleared and deactivated")
    
    return expired_integrations.count()

def show_active_integrations():
    """Show currently active integrations"""
    print("\n📊 Current Active Integrations...")
    print("=" * 50)
    
    active_integrations = BrokerageIntegration.objects.filter(
        brokerage__iexact='upstox',
        is_active=True
    )
    
    if active_integrations:
        for integration in active_integrations:
            print(f"\n✅ Active Integration:")
            print(f"   ID: {integration.id}")
            print(f"   User: {integration.user}")
            print(f"   API Key: {integration.api_key[:10]}...")
            print(f"   Token Expiry: {integration.token_expiry}")
            print(f"   Has Refresh Token: {'Yes' if integration.refresh_token else 'No'}")
    else:
        print("❌ No active Upstox integrations found")

def provide_reauthentication_instructions():
    """Provide instructions for re-authentication"""
    print("\n🔄 Re-authentication Instructions...")
    print("=" * 50)
    print("""
To fix your Upstox integration, follow these steps:

1. **Clear Browser Cache**:
   - Clear your browser cache and cookies for Upstox
   - This ensures a fresh authentication flow

2. **Re-authenticate with Upstox**:
   - Go to your Django admin panel: http://localhost:8000/admin/
   - Navigate to Brokerage Integrations
   - Find your Upstox integration
   - Click "Edit" and then "Save" to trigger re-authentication

3. **Alternative Method**:
   - Go to: http://localhost:8000/brokerage-integration/
   - Re-enter your Upstox API credentials
   - Follow the authorization flow

4. **Check Integration Status**:
   - After re-authentication, run the test script again:
   - python test_upstox_integration.py

5. **Verify Token Refresh**:
   - Ensure you get both access_token AND refresh_token
   - The refresh token is crucial for automatic token renewal

**Important Notes**:
- Upstox tokens typically expire in 1 hour
- Without a refresh token, you'll need to re-authenticate manually
- The refresh token allows automatic token renewal
- Make sure your Upstox app has the correct redirect URI configured
""")

def create_test_log():
    """Create a test log entry"""
    BotLog.objects.create(
        log_type='INFO',
        message='🔧 Upstox integration fix script executed',
        details={
            'action': 'clear_expired_tokens',
            'timestamp': datetime.now().isoformat(),
            'instructions': 'Re-authentication required'
        }
    )
    print("\n✅ Created test log entry")

def main():
    """Main function"""
    print("🔧 Upstox Integration Fix Script")
    print("=" * 60)
    print(f"Started at: {datetime.now()}")
    
    # Step 1: Clear expired integrations
    cleared_count = clear_expired_integrations()
    
    # Step 2: Show active integrations
    show_active_integrations()
    
    # Step 3: Provide instructions
    provide_reauthentication_instructions()
    
    # Step 4: Create test log
    create_test_log()
    
    print(f"\n🏁 Fix script completed at: {datetime.now()}")
    
    if cleared_count > 0:
        print(f"\n⚠️ Cleared {cleared_count} expired integrations")
        print("Please follow the re-authentication instructions above")
    else:
        print("\n✅ No expired integrations found")

if __name__ == "__main__":
    main() 
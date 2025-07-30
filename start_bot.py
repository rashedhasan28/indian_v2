#!/usr/bin/env python
"""
Startup script for the Indian Stock Market Trading Bot
"""

import os
import sys
import subprocess
import time

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = [
        'django',
        'requests',
        'pandas',
        'numpy',
        'yfinance'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True

def run_migrations():
    """Run Django migrations"""
    print("🔄 Running database migrations...")
    try:
        subprocess.run([sys.executable, "manage.py", "migrate"], check=True)
        print("✅ Migrations completed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Migration failed")
        return False

def create_superuser():
    """Create a superuser if none exists"""
    print("👤 Checking for superuser...")
    try:
        # Check if superuser exists
        result = subprocess.run([
            sys.executable, "manage.py", "shell", "-c",
            "from django.contrib.auth.models import User; print(User.objects.filter(is_superuser=True).count())"
        ], capture_output=True, text=True, check=True)
        
        if result.stdout.strip() == "0":
            print("📝 No superuser found. Creating one...")
            print("Please enter the following details:")
            subprocess.run([sys.executable, "manage.py", "createsuperuser"])
        else:
            print("✅ Superuser already exists")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to check/create superuser")
        return False

def start_server():
    """Start the Django development server"""
    print("🚀 Starting Django development server...")
    print("📱 The trading bot will be available at: http://localhost:8000")
    print("🔧 Admin panel: http://localhost:8000/admin")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, "manage.py", "runserver"])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")

def start_trading_bot():
    """Start the trading bot in background"""
    print("🤖 Starting trading bot in background...")
    try:
        # Start bot in background
        bot_process = subprocess.Popen([
            sys.executable, "manage.py", "run_trading_bot", "--interval", "60"
        ])
        print(f"✅ Trading bot started (PID: {bot_process.pid})")
        return bot_process
    except Exception as e:
        print(f"❌ Failed to start trading bot: {e}")
        return None

def main():
    """Main startup function"""
    print("=" * 60)
    print("🤖 INDIAN STOCK MARKET TRADING BOT")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("manage.py"):
        print("❌ Please run this script from the project root directory")
        return
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Run migrations
    if not run_migrations():
        return
    
    # Create superuser
    if not create_superuser():
        return
    
    print("\n🎯 Choose an option:")
    print("1. Start Django server only")
    print("2. Start Django server + Trading bot")
    print("3. Start Trading bot only")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        start_server()
    elif choice == "2":
        bot_process = start_trading_bot()
        if bot_process:
            time.sleep(2)  # Give bot time to start
            start_server()
            # Stop bot when server stops
            bot_process.terminate()
            print("🤖 Trading bot stopped")
    elif choice == "3":
        start_trading_bot()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Trading bot stopped by user")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main() 
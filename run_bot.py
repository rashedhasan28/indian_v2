#!/usr/bin/env python
"""
Simple script to run the trading bot
Usage: python run_bot.py [--interval 60] [--user username]
"""

import os
import sys
import django
import argparse

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'indian_stockmarket.settings')
django.setup()

from django.core.management import execute_from_command_line

def main():
    parser = argparse.ArgumentParser(description='Run the trading bot')
    parser.add_argument('--interval', type=int, default=60, 
                       help='Interval in seconds between strategy checks (default: 60)')
    parser.add_argument('--user', type=str, 
                       help='Run bot for specific user only')
    
    args = parser.parse_args()
    
    # Build command arguments
    cmd_args = ['manage.py', 'run_trading_bot', '--interval', str(args.interval)]
    if args.user:
        cmd_args.extend(['--user', args.user])
    
    print(f"Starting trading bot with interval: {args.interval}s")
    if args.user:
        print(f"Running for user: {args.user}")
    
    # Run the management command
    execute_from_command_line(cmd_args)

if __name__ == '__main__':
    main() 
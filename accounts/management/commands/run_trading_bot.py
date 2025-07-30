from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Strategy
from accounts.upstox_api import TradingBot
import time
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Run the trading bot to execute strategies'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=60,
            help='Interval in seconds between strategy checks (default: 60)'
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Run bot for specific user only'
        )

    def handle(self, *args, **options):
        interval = options['interval']
        user_filter = options['user']
        
        self.stdout.write(
            self.style.SUCCESS(f'Starting trading bot with {interval}s interval...')
        )
        
        bot = TradingBot()
        
        while True:
            try:
                # Get running strategies
                strategies = Strategy.objects.filter(status='RUNNING')
                
                if user_filter:
                    strategies = strategies.filter(user__username=user_filter)
                
                if not strategies.exists():
                    self.stdout.write('No running strategies found.')
                    time.sleep(interval)
                    continue
                
                self.stdout.write(f'Checking {strategies.count()} running strategies...')
                
                for strategy in strategies:
                    try:
                        # Set user for the bot
                        bot.user = strategy.user
                        
                        # Run the strategy
                        bot.run_strategy(strategy)
                        
                        self.stdout.write(
                            f'Strategy "{strategy.name}" checked - Signal: {strategy.last_signal or "None"}'
                        )
                        
                    except Exception as e:
                        logger.error(f'Error running strategy {strategy.name}: {str(e)}')
                        self.stdout.write(
                            self.style.ERROR(f'Error running strategy {strategy.name}: {str(e)}')
                        )
                
                # Wait before next check
                time.sleep(interval)
                
            except KeyboardInterrupt:
                self.stdout.write(
                    self.style.WARNING('\nTrading bot stopped by user.')
                )
                break
            except Exception as e:
                logger.error(f'Unexpected error in trading bot: {str(e)}')
                self.stdout.write(
                    self.style.ERROR(f'Unexpected error: {str(e)}')
                )
                time.sleep(interval) 
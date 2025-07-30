#!/usr/bin/env python3
"""
Real-time Trading Bot
Monitors prices continuously and executes trades based on indicator criteria
No data storage - pure real-time analysis and trading
"""

import os
import django
import time
import threading
from datetime import datetime, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot.settings')
django.setup()

from accounts.models import Strategy, TradingSetup, BotLog, Trade
from accounts.upstox_api import TradingBot
from accounts.indicators import (
    rsi_signal, macd_signal, moving_average_signal,
    vwap_signal, adx_signal, supertrend_signal
)

class RealTimeTradingBot:
    def __init__(self, user=None):
        self.user = user
        self.trading_bot = TradingBot(user)
        self.running = False
        self.monitoring_thread = None
        self.last_signals = {}  # Track last signals to avoid duplicate trades
        
    def start_monitoring(self):
        """Start real-time price monitoring"""
        if self.running:
            print("⚠️ Bot is already running")
            return
            
        self.running = True
        self.monitoring_thread = threading.Thread(target=self._monitor_prices)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        BotLog.objects.create(
            user=self.user,
            log_type='STRATEGY_START',
            message='🚀 Real-time trading bot started',
            details={'mode': 'real-time', 'no_data_storage': True}
        )
        
        print("🚀 Real-time trading bot started")
        print("📊 Monitoring prices continuously...")
        print("💡 No data will be saved - pure real-time analysis")
        
    def stop_monitoring(self):
        """Stop real-time price monitoring"""
        self.running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
            
        BotLog.objects.create(
            user=self.user,
            log_type='STRATEGY_STOP',
            message='🛑 Real-time trading bot stopped',
            details={'mode': 'real-time'}
        )
        
        print("🛑 Real-time trading bot stopped")
        
    def _monitor_prices(self):
        """Main monitoring loop"""
        while self.running:
            try:
                # Get active strategies
                active_strategies = Strategy.objects.filter(
                    user=self.user, 
                    status='RUNNING'
                )
                
                if not active_strategies:
                    print("⏸️ No active strategies found")
                    time.sleep(30)  # Check every 30 seconds
                    continue
                
                print(f"🔍 Monitoring {active_strategies.count()} active strategies...")
                
                # Check each strategy
                for strategy in active_strategies:
                    self._check_strategy(strategy)
                
                # Wait before next check (adjust frequency as needed)
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                print(f"❌ Error in monitoring loop: {e}")
                BotLog.objects.create(
                    user=self.user,
                    log_type='ERROR',
                    message=f'❌ Monitoring error: {str(e)}',
                    details={'error': str(e)}
                )
                time.sleep(30)  # Wait longer on error
                
    def _check_strategy(self, strategy):
        """Check a single strategy for trading signals"""
        try:
            setup = strategy.setup
            symbol = setup.symbol
            
            # Get current price data
            data = self.trading_bot.get_market_data_for_analysis(symbol, setup.timeframe)
            if data is None:
                return
                
            current_price = float(data['close'].iloc[-1])
            
            # Calculate indicator signal
            signal = self._calculate_indicator_signal(setup, data)
            if not signal:
                return
                
            # Check if signal changed (avoid duplicate trades)
            last_signal = self.last_signals.get(strategy.id)
            if last_signal == signal:
                return  # Same signal, no action needed
                
            self.last_signals[strategy.id] = signal
            
            # Log signal
            BotLog.objects.create(
                user=self.user,
                strategy=strategy,
                log_type='SIGNAL_GENERATED',
                message=f'🎯 {signal.upper()} signal for {symbol} at ₹{current_price:.2f}',
                details={
                    'symbol': symbol,
                    'indicator': setup.indicator,
                    'signal': signal,
                    'current_price': current_price,
                    'timeframe': setup.timeframe,
                    'mode': 'real-time'
                }
            )
            
            print(f"🎯 {signal.upper()} signal for {symbol} at ₹{current_price:.2f}")
            
            # Execute trade if signal is buy or sell
            if signal in ['buy', 'sell']:
                self._execute_trade(strategy, signal, current_price)
                
        except Exception as e:
            print(f"❌ Error checking strategy {strategy.name}: {e}")
            BotLog.objects.create(
                user=self.user,
                strategy=strategy,
                log_type='ERROR',
                message=f'❌ Strategy check error: {str(e)}',
                details={'error': str(e)}
            )
            
    def _calculate_indicator_signal(self, setup, data):
        """Calculate indicator signal based on setup"""
        try:
            indicator = setup.indicator
            
            if indicator == 'RSI':
                return rsi_signal(data['close'])
            elif indicator == 'MACD':
                return macd_signal(data['close'])
            elif indicator == 'Moving Average':
                return moving_average_signal(data['close'])
            elif indicator == 'VWAP':
                return vwap_signal(data['close'], data['volume'])
            elif indicator == 'ADX':
                return adx_signal(data['high'], data['low'], data['close'])
            elif indicator == 'Supertrend':
                return supertrend_signal(data['high'], data['low'], data['close'])
            else:
                print(f"❌ Unknown indicator: {indicator}")
                return None
                
        except Exception as e:
            print(f"❌ Error calculating {setup.indicator}: {e}")
            return None
            
    def _execute_trade(self, strategy, signal, current_price):
        """Execute trade based on signal"""
        try:
            setup = strategy.setup
            symbol = setup.symbol
            
            # Determine trade type
            trade_type = 'BUY' if signal == 'buy' else 'SELL'
            
            # Calculate total amount
            total_amount = current_price * setup.quantity
            
            # Log trade execution
            BotLog.objects.create(
                user=self.user,
                strategy=strategy,
                log_type='TRADE_EXECUTED',
                message=f'💰 Executing {trade_type} order for {setup.quantity} {symbol} at ₹{current_price:.2f}',
                details={
                    'symbol': symbol,
                    'trade_type': trade_type,
                    'quantity': setup.quantity,
                    'price': current_price,
                    'total_amount': total_amount,
                    'signal': signal,
                    'mode': 'real-time'
                }
            )
            
            print(f"💰 Executing {trade_type} order for {setup.quantity} {symbol} at ₹{current_price:.2f}")
            
            # Create trade record
            trade = Trade.objects.create(
                user=self.user,
                setup=setup,
                symbol=symbol,
                trade_type=trade_type,
                quantity=setup.quantity,
                price=current_price,
                total_amount=total_amount,
                status='PENDING'
            )
            
            # Execute with Upstox API
            order_response = self.trading_bot.upstox.place_order(
                symbol=symbol,
                quantity=setup.quantity,
                side=trade_type.lower(),
                order_type='MARKET'
            )
            
            if order_response and 'data' in order_response:
                trade.upstox_order_id = order_response['data'].get('order_id')
                trade.status = 'EXECUTED'
                trade.executed_at = datetime.now()
                trade.save()
                
                BotLog.objects.create(
                    user=self.user,
                    strategy=strategy,
                    log_type='TRADE_EXECUTED',
                    message=f'✅ Trade executed successfully - Order ID: {trade.upstox_order_id}',
                    details={
                        'order_id': trade.upstox_order_id,
                        'symbol': symbol,
                        'trade_type': trade_type,
                        'quantity': setup.quantity,
                        'price': current_price
                    }
                )
                
                print(f"✅ Trade executed successfully - Order ID: {trade.upstox_order_id}")
            else:
                trade.status = 'FAILED'
                trade.save()
                
                BotLog.objects.create(
                    user=self.user,
                    strategy=strategy,
                    log_type='TRADE_FAILED',
                    message=f'❌ Trade execution failed',
                    details={
                        'symbol': symbol,
                        'trade_type': trade_type,
                        'response': order_response
                    }
                )
                
                print(f"❌ Trade execution failed")
                
        except Exception as e:
            print(f"❌ Error executing trade: {e}")
            BotLog.objects.create(
                user=self.user,
                strategy=strategy,
                log_type='TRADE_FAILED',
                message=f'❌ Trade execution error: {str(e)}',
                details={'error': str(e)}
            )

def start_real_time_bot(user=None):
    """Start the real-time trading bot"""
    bot = RealTimeTradingBot(user)
    bot.start_monitoring()
    return bot

if __name__ == "__main__":
    print("🚀 Starting Real-time Trading Bot")
    print("=" * 50)
    
    # Get user (you can specify a user ID here)
    from django.contrib.auth.models import User
    user = User.objects.first()  # Or specify a particular user
    
    if user:
        print(f"👤 Running for user: {user.email}")
        bot = start_real_time_bot(user)
        
        try:
            # Keep the bot running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping bot...")
            bot.stop_monitoring()
    else:
        print("❌ No users found") 
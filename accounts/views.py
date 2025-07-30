from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import SignIn, BrokerageIntegration, TradingSetup, Trade, Strategy, MarketData, BotLog
from .upstox_api import UpstoxAPI, TradingBot
from .indicators import (
    rsi_signal, macd_signal, moving_average_signal,
    vwap_signal, adx_signal, supertrend_signal
)
import json
import pandas as pd
from datetime import datetime
from decimal import Decimal

def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Calculate Average True Range"""
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(window=period).mean()

def signin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        platform = request.POST.get('platform')
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')
        
        # Create user if doesn't exist
        user, created = User.objects.get_or_create(
            username=email,
            defaults={'email': email}
        )
        
        # Set password for new users
        if created:
            user.set_password(password)
            user.save()
            messages.success(request, f'Account created successfully for {email}. Please login.')
        else:
            messages.info(request, f'Account already exists for {email}. Please login.')
        
        # Save signin record
        SignIn.objects.create(
            email=email,
            password=password,
            platform=platform,
            address=address,
            phone_number=phone_number
        )
        
        return redirect('login')
    return render(request, 'singin.html')

from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Authenticate user
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            auth_login(request, user)
            messages.success(request, f'Logged in as {email}.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials.')
            return redirect('login')
    return render(request, 'login.html')

def logout(request):
    auth_logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('login')

@login_required
def dashboard(request):
    # Get trading statistics
    total_trades = Trade.objects.filter(user=request.user).count()
    total_wins = Trade.objects.filter(user=request.user, status='EXECUTED', trade_type='SELL').count()
    total_losses = Trade.objects.filter(user=request.user, status='EXECUTED', trade_type='BUY').count()
    running_trades = Trade.objects.filter(user=request.user, status='PENDING').count()
    
    # Get recent trades
    recent_trades = Trade.objects.filter(user=request.user).order_by('-created_at')[:10]
    
    # Get active strategies
    active_strategies = Strategy.objects.filter(user=request.user, status='RUNNING')
    
    context = {
        'total_trades': total_trades,
        'total_wins': total_wins,
        'total_losses': total_losses,
        'running_trades': running_trades,
        'recent_trades': recent_trades,
        'active_strategies': active_strategies,
    }
    return render(request, 'dashboard.html', context)

@login_required
def brokerage_integration(request):
    if request.method == 'POST':
        brokerage = request.POST.get('brokerage')
        api_key = request.POST.get('api_key')
        secret_key = request.POST.get('secret_key')
        startup_url = request.POST.get('startup_url')
        
        print(f"DEBUG: Received brokerage={brokerage}, api_key={api_key[:10]}..., startup_url={startup_url}")
        
        # Deactivate other integrations
        BrokerageIntegration.objects.filter(user=request.user).update(is_active=False)
        
        # Store in DB
        integration = BrokerageIntegration.objects.create(
            user=request.user,
            brokerage=brokerage,
            api_key=api_key,
            secret_key=secret_key,
            startup_url=startup_url,
            is_active=True
        )
        
        if brokerage.lower() == 'upstox':
            import urllib.parse
            # Use the startup_url that user provided (should match Upstox app settings)
            login_url = f"https://api.upstox.com/v2/login/authorization/dialog?client_id={api_key}&redirect_uri={urllib.parse.quote(startup_url)}&response_type=code"
            print(f"DEBUG: Redirecting to Upstox login URL: {login_url}")
            request.session['upstox_api_key'] = api_key
            request.session['upstox_secret_key'] = secret_key
            request.session['upstox_redirect_uri'] = startup_url
            request.session['upstox_integration_id'] = integration.id
            return redirect(login_url)
        
        messages.success(request, f'Brokerage integration submitted for {brokerage}.')
        return redirect('brokerage_integration')
    
    # Get current integration
    current_integration = BrokerageIntegration.objects.filter(user=request.user, is_active=True).first()
    
    return render(request, 'brokerage_integration.html', {
        'current_integration': current_integration
    })

def capture_upstox_code(request):
    """Capture the authorization code from Upstox redirect and process it automatically"""
    import requests
    from datetime import datetime, timedelta
    
    # Get the authorization code from URL parameters
    code = request.GET.get('code')
    error = request.GET.get('error')
    
    print(f"DEBUG: Captured code={code}, error={error}")
    
    if error:
        messages.error(request, f'Upstox authorization failed: {error}')
        return redirect('brokerage_integration')
    
    if not code:
        messages.error(request, 'No authorization code received from Upstox.')
        return redirect('brokerage_integration')
    
    # Get integration details from session
    api_key = request.session.get('upstox_api_key')
    secret_key = request.session.get('upstox_secret_key')
    integration_id = request.session.get('upstox_integration_id')
    redirect_uri = request.session.get('upstox_redirect_uri')
    
    if not all([api_key, secret_key, integration_id]):
        messages.error(request, 'Missing integration details. Please try again.')
        return redirect('brokerage_integration')
    
    try:
        # Get the integration from database
        integration = BrokerageIntegration.objects.get(id=integration_id, user=request.user)
        
        # Exchange code for access token
        token_url = "https://api.upstox.com/v2/login/authorization/token"
        payload = {
            "code": code,
            "client_id": api_key,
            "client_secret": secret_key,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        print(f"DEBUG: Exchanging code for token with redirect_uri={redirect_uri}")
        response = requests.post(token_url, data=payload, headers=headers)
        token_data = response.json()
        
        print(f"DEBUG: Token response status={response.status_code}, data={token_data}")
        
        if response.status_code == 200 and 'access_token' in token_data:
            # Update integration with tokens
            integration.access_token = token_data['access_token']
            integration.refresh_token = token_data.get('refresh_token')
            integration.token_expiry = datetime.now() + timedelta(seconds=token_data.get('expires_in', 3600))
            integration.save()
            
            # Clear session data
            for key in ['upstox_api_key', 'upstox_secret_key', 'upstox_redirect_uri', 'upstox_integration_id']:
                request.session.pop(key, None)
            
            messages.success(request, 'Upstox integration successful! Your account is now connected.')
            return redirect('dashboard')
        else:
            error_msg = token_data.get('error_description', token_data.get('error', 'Unknown error'))
            messages.error(request, f'Failed to get access token: {error_msg}')
            return redirect('brokerage_integration')
            
    except BrokerageIntegration.DoesNotExist:
        messages.error(request, 'Integration not found. Please try again.')
        return redirect('brokerage_integration')
    except Exception as e:
        messages.error(request, f'Error processing Upstox response: {str(e)}')
        return redirect('brokerage_integration')

def upstox_callback(request):
    """Legacy callback for manual code submission"""
    import requests
    from datetime import datetime, timedelta
    
    code = request.GET.get('code') or request.POST.get('code')
    
    # Get the latest Upstox integration from DB
    integration = BrokerageIntegration.objects.filter(
        brokerage__iexact='upstox',
        is_active=True
    ).order_by('-timestamp').first()
    
    if not code or not integration:
        from django.http import HttpResponse
        return HttpResponse('Missing code or Upstox integration data in DB.', status=400)
    
    api_key = integration.api_key
    secret_key = integration.secret_key
    redirect_uri = integration.startup_url
    
    token_url = "https://api.upstox.com/v2/login/authorization/token"
    payload = {
        "code": code,
        "client_id": api_key,
        "client_secret": secret_key,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    response = requests.post(token_url, data=payload, headers=headers)
    try:
        token_data = response.json()
        
        if 'access_token' in token_data:
            # Update integration with tokens
            integration.access_token = token_data['access_token']
            integration.refresh_token = token_data.get('refresh_token')
            integration.token_expiry = datetime.now() + timedelta(seconds=token_data.get('expires_in', 3600))
            integration.save()
            
            messages.success(request, 'Upstox integration successful!')
        else:
            messages.error(request, 'Failed to get access token from Upstox.')
            
    except Exception as e:
        token_data = {"error": f"Invalid response from Upstox: {str(e)}"}
        messages.error(request, 'Error processing Upstox response.')
    
    # Store token_data in session for temporary use
    request.session['upstox_token_data'] = token_data
    return render(request, 'upstox_callback.html', {'token_data': token_data})

@login_required
def trading_setup(request):
    indicators = [
        'Moving Average', 'RSI', 'MACD', 'Bollinger Bands', 'Stochastic', 'Supertrend', 'VWAP', 'ADX', 'CCI', 'ATR'
    ]
    timeframes = ['1m', '5m', '15m', '30m', '1h', '1d']
    exchanges = ['NSE', 'BSE', 'MCX']
    types = ['Cash', 'Future', 'Option']
    markets = ['Equity', 'Commodity', 'Currency']
    trade_directions = [
        ('BUY', 'Buy Only'),
        ('SELL', 'Sell Only'),
        ('BOTH', 'Buy & Sell'),
    ]
    
    # Popular symbols for quick selection
    popular_symbols = [
        'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK', 'HINDUNILVR', 'ITC', 'SBIN', 'BHARTIARTL', 'AXISBANK'
    ]

    if request.method == 'POST':
        name = request.POST.get('name')
        indicator = request.POST.get('indicator')
        timeframe = request.POST.get('timeframe')
        exchange = request.POST.get('exchange')
        type_ = request.POST.get('type')
        market = request.POST.get('market')
        symbol = request.POST.get('symbol')
        quantity = request.POST.get('quantity', 1)
        trade_direction = request.POST.get('trade_direction', 'BOTH')
        
        setup = TradingSetup.objects.create(
            user=request.user,
            name=name,
            indicator=indicator,
            timeframe=timeframe,
            exchange=exchange,
            type=type_,
            market=market,
            symbol=symbol,
            quantity=quantity,
            trade_direction=trade_direction
        )
        
        messages.success(request, 'Trading setup saved successfully.')
        return redirect('trading_setup')

    # Get user's existing setups
    user_setups = TradingSetup.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'trading_setup.html', {
        'indicators': indicators,
        'timeframes': timeframes,
        'exchanges': exchanges,
        'types': types,
        'markets': markets,
        'trade_directions': trade_directions,
        'popular_symbols': popular_symbols,
        'user_setups': user_setups
    })

@login_required
def order_execution_monitoring(request):
    # Get user's strategies
    strategies = Strategy.objects.filter(user=request.user).order_by('-created_at')
    
    # Get user's trading setups for creating new strategies
    user_setups = TradingSetup.objects.filter(user=request.user).order_by('-created_at')
    
    # Get recent bot logs for monitoring
    recent_logs = BotLog.objects.filter(user=request.user).order_by('-timestamp')[:50]
    
    if request.method == 'POST':
        action = request.POST.get('action')
        strategy_id = request.POST.get('strategy_id')
        
        try:
            strategy = Strategy.objects.get(id=strategy_id, user=request.user)
            
            if action == 'start':
                strategy.status = 'RUNNING'
                strategy.save()
                
                # Log strategy start
                BotLog.objects.create(
                    user=request.user,
                    strategy=strategy,
                    log_type='STRATEGY_START',
                    message=f"🚀 Strategy '{strategy.name}' started",
                    details={'strategy_name': strategy.name, 'symbol': strategy.setup.symbol}
                )
                
                messages.success(request, f'Strategy "{strategy.name}" started.')
            elif action == 'stop':
                strategy.status = 'STOPPED'
                strategy.save()
                
                # Log strategy stop
                BotLog.objects.create(
                    user=request.user,
                    strategy=strategy,
                    log_type='STRATEGY_STOP',
                    message=f"⏹️ Strategy '{strategy.name}' stopped",
                    details={'strategy_name': strategy.name, 'symbol': strategy.setup.symbol}
                )
                
                messages.success(request, f'Strategy "{strategy.name}" stopped.')
            elif action == 'delete':
                strategy_name = strategy.name
                strategy.delete()
                messages.success(request, f'Strategy "{strategy_name}" deleted.')
                
        except Strategy.DoesNotExist:
            messages.error(request, 'Strategy not found.')
    
    return render(request, 'Order_execution and monitoring .html', {
        'strategies': strategies,
        'user_setups': user_setups,
        'recent_logs': recent_logs
    })

@login_required
def create_strategy(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        setup_id = request.POST.get('setup_id')
        take_profit = request.POST.get('take_profit')
        stop_loss = request.POST.get('stop_loss')
        
        try:
            setup = TradingSetup.objects.get(id=setup_id, user=request.user)
            
            # Convert percentage strings to Decimal objects
            take_profit_decimal = None
            stop_loss_decimal = None
            
            if take_profit and take_profit.strip():
                try:
                    take_profit_decimal = Decimal(take_profit)
                except (ValueError, TypeError):
                    messages.error(request, 'Invalid take profit percentage. Please enter a valid number.')
                    return redirect('order_execution_monitoring')
            
            if stop_loss and stop_loss.strip():
                try:
                    stop_loss_decimal = Decimal(stop_loss)
                except (ValueError, TypeError):
                    messages.error(request, 'Invalid stop loss percentage. Please enter a valid number.')
                    return redirect('order_execution_monitoring')
            
            strategy = Strategy.objects.create(
                user=request.user,
                name=name,
                setup=setup,
                status='STOPPED',
                take_profit_percentage=take_profit_decimal,
                stop_loss_percentage=stop_loss_decimal
            )
            messages.success(request, f'Strategy "{name}" created successfully.')
        except TradingSetup.DoesNotExist:
            messages.error(request, 'Trading setup not found.')
    
    return redirect('order_execution_monitoring')

@csrf_exempt
@login_required
def update_strategy(request):
    """API endpoint to update strategy take profit and stop loss"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            strategy_id = data.get('strategy_id')
            take_profit = data.get('take_profit')
            stop_loss = data.get('stop_loss')
            
            if not strategy_id:
                return JsonResponse({
                    'success': False,
                    'error': 'Strategy ID is required'
                })
            
            # Get the strategy and verify ownership
            strategy = Strategy.objects.get(id=strategy_id, user=request.user)
            
            # Convert percentage strings to Decimal objects
            take_profit_decimal = None
            stop_loss_decimal = None
            
            if take_profit and take_profit.strip():
                try:
                    take_profit_decimal = Decimal(take_profit)
                    if take_profit_decimal < 0 or take_profit_decimal > 100:
                        return JsonResponse({
                            'success': False,
                            'error': 'Take profit percentage must be between 0 and 100'
                        })
                except (ValueError, TypeError):
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid take profit percentage. Please enter a valid number.'
                    })
            
            if stop_loss and stop_loss.strip():
                try:
                    stop_loss_decimal = Decimal(stop_loss)
                    if stop_loss_decimal < 0 or stop_loss_decimal > 100:
                        return JsonResponse({
                            'success': False,
                            'error': 'Stop loss percentage must be between 0 and 100'
                        })
                except (ValueError, TypeError):
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid stop loss percentage. Please enter a valid number.'
                    })
            
            # Update the strategy
            strategy.take_profit_percentage = take_profit_decimal
            strategy.stop_loss_percentage = stop_loss_decimal
            strategy.save()
            
            # Log the update
            BotLog.objects.create(
                user=request.user,
                strategy=strategy,
                log_type='INFO',
                message=f"📝 Strategy '{strategy.name}' updated - TP: {take_profit_decimal}%, SL: {stop_loss_decimal}%",
                details={
                    'strategy_name': strategy.name,
                    'take_profit_percentage': float(take_profit_decimal) if take_profit_decimal else None,
                    'stop_loss_percentage': float(stop_loss_decimal) if stop_loss_decimal else None,
                    'action': 'strategy_update'
                }
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Strategy "{strategy.name}" updated successfully'
            })
            
        except Strategy.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Strategy not found'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
@login_required
def delete_trading_setup(request):
    """API endpoint to delete a trading setup"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            setup_id = data.get('setup_id')
            
            if not setup_id:
                return JsonResponse({
                    'success': False,
                    'error': 'Setup ID is required'
                })
            
            # Get the setup and verify ownership
            setup = TradingSetup.objects.get(id=setup_id, user=request.user)
            setup_name = setup.name
            
            # Check if any strategies are using this setup
            strategies_using_setup = Strategy.objects.filter(setup=setup)
            if strategies_using_setup.exists():
                strategy_names = [s.name for s in strategies_using_setup]
                return JsonResponse({
                    'success': False,
                    'error': f'Cannot delete setup. It is being used by strategies: {", ".join(strategy_names)}'
                })
            
            # Delete the setup
            setup.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Trading setup "{setup_name}" deleted successfully'
            })
            
        except TradingSetup.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Trading setup not found'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
@login_required
def api_get_market_data(request):
    """API endpoint to get market data"""
    if request.method == 'POST':
        data = json.loads(request.body)
        symbol = data.get('symbol')
        
        if symbol:
            bot = TradingBot(request.user)
            market_data = bot.get_market_data_for_analysis(symbol)
            
            if market_data is not None:
                return JsonResponse({
                    'success': True,
                    'data': market_data.tail(20).to_dict('records')
                })
        
        return JsonResponse({'success': False, 'error': 'Failed to get market data'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
@login_required
def api_generate_signal(request):
    """API endpoint to generate trading signal"""
    if request.method == 'POST':
        data = json.loads(request.body)
        setup_id = data.get('setup_id')
        
        try:
            setup = TradingSetup.objects.get(id=setup_id, user=request.user)
            bot = TradingBot(request.user)
            signal = bot.generate_signal(setup)
            
            return JsonResponse({
                'success': True,
                'signal': signal,
                'setup': {
                    'name': setup.name,
                    'symbol': setup.symbol,
                    'indicator': setup.indicator
                }
            })
        except TradingSetup.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Trading setup not found'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def api_get_bot_logs(request):
    """API endpoint to get real-time bot logs - No authentication required"""
    if request.method == 'GET':
        # Get all logs (no user filter)
        logs = BotLog.objects.all().order_by('-timestamp')[:100]
        
        log_data = []
        for log in logs:
            log_data.append({
                'id': log.id,
                'log_type': log.log_type,
                'message': log.message,
                'details': log.details,
                'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'strategy_name': log.strategy.name if log.strategy else None
            })
        
        return JsonResponse({
            'success': True,
            'logs': log_data,
            'total_logs': BotLog.objects.count()
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def api_clear_logs(request):
    """API endpoint to clear logs - No authentication required"""
    if request.method == 'POST':
        try:
            print(f"DEBUG: Received request body: {request.body}")
            data = json.loads(request.body) if request.body else {}
            clear_all = data.get('clear_all', False)
            
            print(f"DEBUG: clear_all parameter: {clear_all}")
            
            if clear_all:
                # Clear ALL logs in the database (no user filter)
                total_before = BotLog.objects.count()
                print(f"DEBUG: Total logs before deletion: {total_before}")
                
                deleted_count = BotLog.objects.all().delete()[0]
                print(f"DEBUG: Deleted {deleted_count} logs")
                
                return JsonResponse({
                    'success': True,
                    'message': f'All logs cleared successfully ({deleted_count} logs deleted)'
                })
            else:
                # Keep only last 1000 logs (original behavior)
                total_logs = BotLog.objects.count()
                if total_logs > 1000:
                    logs_to_delete = BotLog.objects.all().order_by('timestamp')[:total_logs - 1000]
                    deleted_count = logs_to_delete.delete()[0]
                    return JsonResponse({
                        'success': True,
                        'message': f'Old logs cleared successfully ({deleted_count} logs deleted)'
                    })
                else:
                    return JsonResponse({
                        'success': True,
                        'message': 'No logs to clear'
                    })
        except Exception as e:
            print(f"DEBUG: Exception in api_clear_logs: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
@login_required
def api_get_strategy_data(request):
    """API endpoint to get real-time strategy data"""
    if request.method == 'POST':
        data = json.loads(request.body)
        strategy_id = data.get('strategy_id')
        
        try:
            strategy = Strategy.objects.get(id=strategy_id, user=request.user)
            bot = TradingBot(request.user)
            
            # Get current market data
            market_data = bot.get_market_data_for_analysis(strategy.setup.symbol, strategy.setup.timeframe)
            
            if market_data is not None:
                current_price = float(market_data['close'].iloc[-1])
                
                # Calculate indicator value
                indicator_value = None
                indicator_signal = None
                
                try:
                    if strategy.setup.indicator == 'RSI':
                        # Calculate RSI manually
                        if len(market_data) >= 14:
                            delta = market_data['close'].diff()
                            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                            rs = gain / loss
                            rsi = 100 - (100 / (1 + rs))
                            indicator_value = rsi.iloc[-1]
                            # Handle NaN values
                            if pd.isna(indicator_value):
                                indicator_value = 50.0
                        else:
                            # If not enough data, use a simple calculation
                            indicator_value = 50.0  # Neutral RSI
                        indicator_signal = rsi_signal(market_data['close'])
                    elif strategy.setup.indicator == 'MACD':
                        # Calculate MACD manually
                        if len(market_data) >= 26:
                            ema_fast = market_data['close'].ewm(span=12, adjust=False).mean()
                            ema_slow = market_data['close'].ewm(span=26, adjust=False).mean()
                            macd = ema_fast - ema_slow
                            indicator_value = macd.iloc[-1]
                            # Handle NaN values
                            if pd.isna(indicator_value):
                                indicator_value = 0.0
                        else:
                            indicator_value = 0.0  # Neutral MACD
                        indicator_signal = macd_signal(market_data['close'])
                    elif strategy.setup.indicator == 'Moving Average':
                        # Calculate Moving Average manually
                        if len(market_data) >= 20:
                            ma = market_data['close'].rolling(window=20).mean()
                            indicator_value = ma.iloc[-1]
                            # Handle NaN values
                            if pd.isna(indicator_value):
                                indicator_value = market_data['close'].iloc[-1]
                        else:
                            indicator_value = market_data['close'].iloc[-1]  # Use current price
                        indicator_signal = moving_average_signal(market_data['close'])
                    elif strategy.setup.indicator == 'VWAP':
                        # Calculate VWAP manually
                        vwap = (market_data['close'] * market_data['volume']).cumsum() / market_data['volume'].cumsum()
                        indicator_value = vwap.iloc[-1]
                        indicator_signal = vwap_signal(market_data['close'], market_data['volume'])
                    elif strategy.setup.indicator == 'ADX':
                        # Calculate ADX manually
                        plus_dm = market_data['high'].diff()
                        minus_dm = market_data['low'].diff().abs()
                        plus_dm[plus_dm < 0] = 0
                        minus_dm[minus_dm < 0] = 0
                        tr1 = market_data['high'] - market_data['low']
                        tr2 = (market_data['high'] - market_data['close'].shift()).abs()
                        tr3 = (market_data['low'] - market_data['close'].shift()).abs()
                        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
                        atr = tr.rolling(window=14).mean()
                        plus_di = 100 * (plus_dm.rolling(window=14).sum() / atr)
                        minus_di = 100 * (minus_dm.rolling(window=14).sum() / atr)
                        adx = ((plus_di - minus_di).abs() / (plus_di + minus_di)) * 100
                        indicator_value = adx.iloc[-1]
                        indicator_signal = adx_signal(market_data['high'], market_data['low'], market_data['close'])
                    elif strategy.setup.indicator == 'Supertrend':
                        # Calculate Supertrend manually
                        atr = calculate_atr(market_data['high'], market_data['low'], market_data['close'])
                        upper_band = ((market_data['high'] + market_data['low']) / 2) + (3.0 * atr)
                        lower_band = ((market_data['high'] + market_data['low']) / 2) - (3.0 * atr)
                        supertrend = pd.Series(index=market_data['close'].index, dtype=float)
                        direction = pd.Series(index=market_data['close'].index, dtype=int)
                        
                        for i in range(10, len(market_data['close'])):
                            if market_data['close'].iloc[i] > upper_band.iloc[i-1]:
                                direction.iloc[i] = 1
                            elif market_data['close'].iloc[i] < lower_band.iloc[i-1]:
                                direction.iloc[i] = -1
                            else:
                                direction.iloc[i] = direction.iloc[i-1]
                                
                            if direction.iloc[i] == 1 and lower_band.iloc[i] < lower_band.iloc[i-1]:
                                lower_band.iloc[i] = lower_band.iloc[i-1]
                            if direction.iloc[i] == -1 and upper_band.iloc[i] > upper_band.iloc[i-1]:
                                upper_band.iloc[i] = upper_band.iloc[i-1]
                                
                            if direction.iloc[i] == 1:
                                supertrend.iloc[i] = lower_band.iloc[i]
                            else:
                                supertrend.iloc[i] = upper_band.iloc[i]
                        
                        indicator_value = supertrend.iloc[-1]
                        indicator_signal = supertrend_signal(market_data['high'], market_data['low'], market_data['close'])
                        
                except Exception as e:
                    print(f"Error calculating indicator: {e}")
                
                # Get last log for this strategy
                last_log = BotLog.objects.filter(
                    user=request.user,
                    strategy=strategy
                ).order_by('-timestamp').first()
                

                
                return JsonResponse({
                    'success': True,
                    'data': {
                        'strategy_id': strategy.id,
                        'symbol': strategy.setup.symbol,
                        'indicator': strategy.setup.indicator,
                        'trade_direction': strategy.setup.get_trade_direction_display(),
                        'take_profit_percentage': float(strategy.take_profit_percentage) if strategy.take_profit_percentage else None,
                        'stop_loss_percentage': float(strategy.stop_loss_percentage) if strategy.stop_loss_percentage else None,
                        'current_price': current_price,
                        'indicator_value': round(float(indicator_value), 2) if indicator_value is not None else None,
                        'indicator_signal': indicator_signal,
                        'last_signal': strategy.last_signal,
                        'last_check': strategy.last_check.isoformat() if strategy.last_check else None,
                        'status': strategy.status,
                        'last_log': {
                            'message': last_log.message,
                            'timestamp': last_log.timestamp.isoformat(),
                            'log_type': last_log.log_type
                        } if last_log else None,
                        'timestamp': datetime.now().isoformat()
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Failed to get market data'
                })
                
        except Strategy.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Strategy not found'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def trade_history(request):
    """View trade history"""
    trades = Trade.objects.filter(user=request.user).order_by('-created_at')
    
    # Calculate statistics
    total_trades = trades.count()
    executed_trades = trades.filter(status='EXECUTED')
    total_volume = sum(trade.total_amount for trade in executed_trades)
    
    context = {
        'trades': trades,
        'total_trades': total_trades,
        'total_volume': total_volume,
    }
    return render(request, 'trade_history.html', context)

@login_required
def portfolio(request):
    """View portfolio and holdings"""
    upstox = UpstoxAPI(request.user)
    
    # Get holdings from Upstox
    holdings = upstox.get_holdings()
    margins = upstox.get_margins()
    profile = upstox.get_profile()
    
    context = {
        'holdings': holdings,
        'margins': margins,
        'profile': profile,
    }
    return render(request, 'portfolio.html', context)

def debug_brokerage(request):
    """Debug view to check brokerage integration status"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    context = {
        'integrations': BrokerageIntegration.objects.filter(user=request.user),
        'user': request.user,
    }
    
    if request.method == 'POST':
        test_api_key = request.POST.get('test_api_key')
        test_secret_key = request.POST.get('test_secret_key')
        
        if test_api_key and test_secret_key:
            try:
                # Test Upstox API connection
                import requests
                test_url = "https://api.upstox.com/v2/user/profile"
                headers = {
                    'Api-Version': '2.0',
                    'Authorization': f'Bearer {test_api_key}'
                }
                response = requests.get(test_url, headers=headers)
                context['test_result'] = f"Status: {response.status_code}\nResponse: {response.text}"
            except Exception as e:
                context['test_result'] = f"Error: {str(e)}"
    
    return render(request, 'debug_brokerage.html', context)

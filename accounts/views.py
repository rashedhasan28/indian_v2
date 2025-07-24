from django.shortcuts import render, redirect
from django.contrib import messages
from .models import SignIn, BrokerageIntegration

def signin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        platform = request.POST.get('platform')
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')
        # Save to database
        SignIn.objects.create(
            email=email,
            password=password,
            platform=platform,
            address=address,
            phone_number=phone_number
        )
        messages.success(request, f'Signed in as {email} on {platform}.')
        return redirect('login')
    return render(request, 'singin.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        # Here you would add authentication logic
        messages.success(request, f'Logged in as {email}.')
        return redirect('dashboard')
    return render(request, 'login.html')

def dashboard(request):
    return render(request, 'dashboard.html')

def brokerage_integration(request):
    if request.method == 'POST':
        brokerage = request.POST.get('brokerage')
        api_key = request.POST.get('api_key')
        secret_key = request.POST.get('secret_key')
        startup_url = request.POST.get('startup_url')
        # Store in DB
        BrokerageIntegration.objects.create(
            brokerage=brokerage,
            api_key=api_key,
            secret_key=secret_key,
            startup_url=startup_url
        )
        if brokerage.lower() == 'upstock':
            import urllib.parse
            login_url = f"https://api.upstox.com/v2/login/authorization/dialog?client_id={api_key}&redirect_uri={urllib.parse.quote(startup_url)}&response_type=code"
            request.session['upstox_api_key'] = api_key
            request.session['upstox_secret_key'] = secret_key
            request.session['upstox_redirect_uri'] = startup_url
            return redirect(login_url)
        print(f"Brokerage: {brokerage}, API Key: {api_key}, Secret Key: {secret_key}, Startup URL: {startup_url}")
        messages.success(request, f'Brokerage integration submitted for {brokerage}.')
        return redirect('brokerage_integration')
    return render(request, 'brokerage_integration.html')

def upstox_callback(request):
    import requests
    from .models import BrokerageIntegration
    code = request.GET.get('code') or request.POST.get('code')
    # Get the latest Upstock integration from DB
    integration = BrokerageIntegration.objects.filter(brokerage__iexact='upstock').order_by('-timestamp').first()
    if not code or not integration:
        from django.http import HttpResponse
        return HttpResponse('Missing code or Upstock integration data in DB.', status=400)
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
    except Exception:
        token_data = {"error": "Invalid response from Upstox"}
    # Store token_data in session for temporary use
    request.session['upstox_token_data'] = token_data
    return render(request, 'upstox_callback.html', {'token_data': token_data})

from .models import TradingSetup  # Add this import

def trading_setup(request):
    indicators = [
        'Moving Average', 'RSI', 'MACD', 'Bollinger Bands', 'Stochastic', 'Supertrend', 'VWAP', 'ADX', 'CCI', 'ATR'
    ]
    timeframes = ['1m', '5m', '15m', '30m', '1h', '1d']
    exchanges = ['NSE', 'BSE', 'MCX']
    types = ['Cash', 'Future', 'Option']
    markets = ['Equity', 'Commodity', 'Currency']

    if request.method == 'POST':
        indicator = request.POST.get('indicator')
        timeframe = request.POST.get('timeframe')
        exchange = request.POST.get('exchange')
        type_ = request.POST.get('type')
        market = request.POST.get('market')
        TradingSetup.objects.create(
            indicator=indicator,
            timeframe=timeframe,
            exchange=exchange,
            type=type_,
            market=market
        )
        messages.success(request, 'Trading setup saved.')
        return redirect('trading_setup')

    return render(request, 'trading_setup.html', {
        'indicators': indicators,
        'timeframes': timeframes,
        'exchanges': exchanges,
        'types': types,
        'markets': markets
    })



def order_execution_monitoring(request):
    # Example strategies list; replace with DB query if needed
    strategies = [
        {'id': 1, 'name': 'RSI Breakout', 'status': 'Stopped'},
        {'id': 2, 'name': 'MACD Crossover', 'status': 'Stopped'},
        {'id': 3, 'name': 'VWAP Pullback', 'status': 'Stopped'},
    ]
    return render(request, 'Order_execution and monitoring .html', {'strategies': strategies})

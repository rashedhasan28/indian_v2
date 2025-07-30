"""bot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', other_app.views.Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import (
    signin, login, logout, dashboard, brokerage_integration, upstox_callback, capture_upstox_code,
    trading_setup, order_execution_monitoring, create_strategy, delete_trading_setup, update_strategy,
    api_get_market_data, api_generate_signal, api_get_bot_logs, api_clear_logs, api_get_strategy_data,
    trade_history, portfolio, debug_brokerage
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='home'),  # Make dashboard the home page
    path('signin/', signin, name='signin'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('brokerage-integration/', brokerage_integration, name='brokerage_integration'),
    path('upstox-callback/', upstox_callback, name='upstox_callback'),
    path('capture-upstox-code/', capture_upstox_code, name='capture_upstox_code'),
    path('trading-setup/', trading_setup, name='trading_setup'),
    path('order-execution-monitoring/', order_execution_monitoring, name='order_execution_monitoring'),
    path('create-strategy/', create_strategy, name='create_strategy'),
    path('delete-trading-setup/', delete_trading_setup, name='delete_trading_setup'),
    path('update-strategy/', update_strategy, name='update_strategy'),
    path('trade-history/', trade_history, name='trade_history'),
    path('portfolio/', portfolio, name='portfolio'),
    
    # API endpoints
    path('api/market-data/', api_get_market_data, name='api_market_data'),
    path('api/generate-signal/', api_generate_signal, name='api_generate_signal'),
    path('api/bot-logs/', api_get_bot_logs, name='api_bot_logs'),
    path('api/clear-logs/', api_clear_logs, name='api_clear_logs'),
    path('api/strategy-data/', api_get_strategy_data, name='api_strategy_data'),
    
    # Debug endpoints
    path('debug/brokerage/', debug_brokerage, name='debug_brokerage'),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

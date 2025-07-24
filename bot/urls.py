"""bot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from accounts.views import signin, login, dashboard, brokerage_integration, upstox_callback, trading_setup,order_execution_monitoring

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signin/', signin, name='signin'),
    path('login/', login, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('brokerage-integration/', brokerage_integration, name='brokerage_integration'),
    path('upstox-callback/', upstox_callback, name='upstox_callback'),
    path('trading-setup/', trading_setup, name='trading_setup'),
    path('order-execution-monitoring/', order_execution_monitoring, name='order_execution_monitoring'),
]

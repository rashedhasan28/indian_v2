from django.contrib import admin
from .models import SignIn, BrokerageIntegration, TradingSetup, Trade, Strategy, MarketData

@admin.register(SignIn)
class SignInAdmin(admin.ModelAdmin):
    list_display = ('email', 'platform', 'timestamp')
    list_filter = ('platform', 'timestamp')
    search_fields = ('email', 'platform')
    readonly_fields = ('timestamp',)

@admin.register(BrokerageIntegration)
class BrokerageIntegrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'brokerage', 'is_active', 'timestamp')
    list_filter = ('brokerage', 'is_active', 'timestamp')
    search_fields = ('user__username', 'brokerage')
    readonly_fields = ('timestamp',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'brokerage', 'is_active')
        }),
        ('API Credentials', {
            'fields': ('api_key', 'secret_key', 'startup_url')
        }),
        ('Tokens', {
            'fields': ('access_token', 'refresh_token', 'token_expiry'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('timestamp',),
            'classes': ('collapse',)
        })
    )

@admin.register(TradingSetup)
class TradingSetupAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'symbol', 'indicator', 'timeframe', 'is_active', 'created_at')
    list_filter = ('indicator', 'timeframe', 'exchange', 'type', 'market', 'is_active', 'created_at')
    search_fields = ('name', 'symbol', 'user__username')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'symbol', 'quantity', 'is_active')
        }),
        ('Trading Parameters', {
            'fields': ('indicator', 'timeframe', 'exchange', 'type', 'market')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )

@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'trade_type', 'quantity', 'price', 'status', 'user', 'created_at')
    list_filter = ('trade_type', 'status', 'created_at')
    search_fields = ('symbol', 'user__username', 'order_id', 'upstox_order_id')
    readonly_fields = ('created_at', 'executed_at')
    fieldsets = (
        ('Trade Information', {
            'fields': ('user', 'setup', 'symbol', 'trade_type', 'quantity', 'price', 'total_amount')
        }),
        ('Status & Orders', {
            'fields': ('status', 'order_id', 'upstox_order_id')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'executed_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(Strategy)
class StrategyAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'setup', 'status', 'last_signal', 'created_at')
    list_filter = ('status', 'last_signal', 'created_at')
    search_fields = ('name', 'user__username', 'setup__name')
    readonly_fields = ('created_at', 'last_check')
    fieldsets = (
        ('Strategy Information', {
            'fields': ('user', 'name', 'setup', 'status')
        }),
        ('Signal Information', {
            'fields': ('last_signal', 'last_check')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )

@admin.register(MarketData)
class MarketDataAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'close_price', 'volume', 'timestamp')
    list_filter = ('symbol', 'timestamp')
    search_fields = ('symbol',)
    readonly_fields = ('timestamp',)
    fieldsets = (
        ('Market Data', {
            'fields': ('symbol', 'open_price', 'high_price', 'low_price', 'close_price', 'volume')
        }),
        ('Timestamps', {
            'fields': ('timestamp',),
            'classes': ('collapse',)
        })
    )

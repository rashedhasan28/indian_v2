from django.db import models
from django.contrib.auth.models import User

class SignIn(models.Model):
    email = models.EmailField()
    password = models.CharField(max_length=128)
    platform = models.CharField(max_length=20)
    address = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} ({self.platform}) at {self.timestamp}"

class BrokerageIntegration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    brokerage = models.CharField(max_length=100)
    api_key = models.CharField(max_length=255)
    secret_key = models.CharField(max_length=255)
    startup_url = models.URLField()
    access_token = models.TextField(null=True, blank=True)
    refresh_token = models.TextField(null=True, blank=True)
    token_expiry = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brokerage} ({self.api_key}) at {self.timestamp}"

class TradingSetup(models.Model):
    TRADE_DIRECTION_CHOICES = [
        ('BUY', 'Buy Only'),
        ('SELL', 'Sell Only'),
        ('BOTH', 'Buy & Sell'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    indicator = models.CharField(max_length=100)
    timeframe = models.CharField(max_length=10)
    exchange = models.CharField(max_length=10)
    type = models.CharField(max_length=10)
    market = models.CharField(max_length=20)
    symbol = models.CharField(max_length=50)
    quantity = models.IntegerField(default=1)
    trade_direction = models.CharField(max_length=4, choices=TRADE_DIRECTION_CHOICES, default='BOTH')
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.symbol} ({self.indicator})"

class Trade(models.Model):
    TRADE_TYPES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('EXECUTED', 'Executed'),
        ('CANCELLED', 'Cancelled'),
        ('FAILED', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    setup = models.ForeignKey(TradingSetup, on_delete=models.CASCADE, null=True, blank=True)
    symbol = models.CharField(max_length=50)
    trade_type = models.CharField(max_length=4, choices=TRADE_TYPES)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    order_id = models.CharField(max_length=100, null=True, blank=True)
    upstox_order_id = models.CharField(max_length=100, null=True, blank=True)
    executed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.trade_type} {self.quantity} {self.symbol} at {self.price}"

class Strategy(models.Model):
    STATUS_CHOICES = [
        ('STOPPED', 'Stopped'),
        ('RUNNING', 'Running'),
        ('PAUSED', 'Paused'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    setup = models.ForeignKey(TradingSetup, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='STOPPED')
    last_signal = models.CharField(max_length=10, null=True, blank=True)
    last_check = models.DateTimeField(null=True, blank=True)
    take_profit_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Take profit percentage (e.g., 5.00 for 5%)")
    stop_loss_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Stop loss percentage (e.g., 2.00 for 2%)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.status}"

class MarketData(models.Model):
    symbol = models.CharField(max_length=50)
    open_price = models.DecimalField(max_digits=10, decimal_places=2)
    high_price = models.DecimalField(max_digits=10, decimal_places=2)
    low_price = models.DecimalField(max_digits=10, decimal_places=2)
    close_price = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.BigIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.symbol} - {self.close_price} at {self.timestamp}"

class BotLog(models.Model):
    LOG_TYPES = [
        ('DATA_FETCH', 'Data Fetch'),
        ('INDICATOR_CALC', 'Indicator Calculation'),
        ('SIGNAL_GENERATED', 'Signal Generated'),
        ('TRADE_EXECUTED', 'Trade Executed'),
        ('TRADE_FAILED', 'Trade Failed'),
        ('STRATEGY_START', 'Strategy Started'),
        ('STRATEGY_STOP', 'Strategy Stopped'),
        ('ERROR', 'Error'),
        ('INFO', 'Info'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE, null=True, blank=True)
    log_type = models.CharField(max_length=20, choices=LOG_TYPES)
    message = models.TextField()
    details = models.JSONField(null=True, blank=True)  # Store additional data like prices, signals, etc.
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.log_type}: {self.message[:50]} at {self.timestamp}"
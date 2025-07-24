from django.db import models

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
    brokerage = models.CharField(max_length=100)
    api_key = models.CharField(max_length=255)
    secret_key = models.CharField(max_length=255)
    startup_url = models.URLField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brokerage} ({self.api_key}) at {self.timestamp}" 
    
from django.db import models

class TradingSetup(models.Model):
    indicator = models.CharField(max_length=100)
    timeframe = models.CharField(max_length=10)
    exchange = models.CharField(max_length=10)
    type = models.CharField(max_length=10)
    market = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
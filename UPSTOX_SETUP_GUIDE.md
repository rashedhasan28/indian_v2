# 🚀 Upstox Integration Setup Guide

## Overview
This guide will help you set up Upstox API integration to get **real Indian stock market data** for your trading bot.

## Why Upstox API?
- ✅ **Real-time Indian stock data** (NSE, BSE)
- ✅ **Live market quotes** and historical data
- ✅ **Direct order execution** capabilities
- ✅ **Professional-grade data** for accurate trading signals

## Step 1: Get Upstox API Credentials

### 1.1 Create Upstox Developer Account
1. Go to [Upstox Developer Portal](https://developer.upstox.com/)
2. Sign up for a developer account
3. Create a new application

### 1.2 Get API Credentials
1. In your Upstox developer dashboard, note down:
   - **API Key** (Client ID)
   - **Secret Key** (Client Secret)
   - **Redirect URI**: `http://localhost:8000/capture-upstox-code/`

## Step 2: Configure Upstox Integration

### 2.1 Access Brokerage Integration Page
1. Start your Django server: `python manage.py runserver`
2. Go to: `http://localhost:8000/brokerage-integration/`
3. Login with your account

### 2.2 Enter Upstox Credentials
Fill in the form with:
- **Brokerage**: Upstox
- **API Key**: Your Upstox API key
- **Secret Key**: Your Upstox secret key
- **Startup URL**: `http://localhost:8000/capture-upstox-code/`

### 2.3 Complete Authorization
1. Click "Submit" - you'll be redirected to Upstox
2. Login to your Upstox account
3. Authorize the application
4. You'll be redirected back with an access token

## Step 3: Create Trading Strategies with Correct Symbols

### 3.1 Correct Indian Stock Symbols
Use these **Upstox symbol formats** for Indian stocks:

| Stock | Upstox Symbol | Description |
|-------|---------------|-------------|
| Reliance Industries | `NSE_EQ\|INE002A01018` | NSE Equity |
| TCS | `NSE_EQ\|INE467B01029` | NSE Equity |
| HDFC Bank | `NSE_EQ\|INE040A01034` | NSE Equity |
| Infosys | `NSE_EQ\|INE009A01021` | NSE Equity |
| ICICI Bank | `NSE_EQ\|INE090A01021` | NSE Equity |

### 3.2 Create Trading Setup
1. Go to: `http://localhost:8000/trading-setup/`
2. Create a new setup:
   - **Name**: "Reliance RSI Strategy"
   - **Indicator**: RSI
   - **Timeframe**: 1d
   - **Exchange**: NSE
   - **Symbol**: `NSE_EQ|INE002A01018`
   - **Quantity**: 10

### 3.3 Create Strategy
1. Go to: `http://localhost:8000/order-execution-monitoring/`
2. Create strategy from your setup
3. Start the strategy

## Step 4: Test the Integration

### 4.1 Run Test Script
```bash
python setup_upstox_integration.py
```

This will:
- ✅ Check Upstox integration status
- ✅ Create test strategies with correct symbols
- ✅ Test data fetching from Upstox API
- ✅ Test indicator calculations
- ✅ Show real-time logs

### 4.2 Expected Output
```
🔧 Setting Up Upstox Integration
==================================================
✅ Found existing Upstox integration
   API Key: 1234567890...
   Access Token: Yes
   Token Expiry: 2024-01-15 10:30:00

📊 Creating Test Strategies with Correct Indian Stock Symbols
============================================================
✅ Created: Reliance RSI Strategy
   Symbol: NSE_EQ|INE002A01018
   Indicator: RSI
   Timeframe: 1d

🧪 Testing Bot with Upstox Data
========================================
🔍 Testing Reliance RSI Strategy (NSE_EQ|INE002A01018)
----------------------------------------
📈 Getting market data from Upstox...
✅ Got 30 data points from Upstox
   Date range: 2023-12-15 to 2024-01-15
   Latest close: ₹2,450.75
   Data source: Upstox API
🎯 Generating RSI signal...
✅ Generated signal: BUY
💰 Signal is BUY - would execute trade
   Symbol: NSE_EQ|INE002A01018
   Quantity: 10
   Current Price: ₹2,450.75
   Total Value: ₹24,507.50
```

## Step 5: Monitor Real-Time Activity

### 5.1 Check Monitoring Page
Go to: `http://localhost:8000/order-execution-monitoring/`

You should see:
- ✅ **Real-time logs** showing data fetching from Upstox
- ✅ **Indicator calculations** with actual market data
- ✅ **Trading signals** based on real Indian stock prices
- ✅ **Trade execution** logs (if signals are generated)

### 5.2 Sample Logs
```
14:30:15 - DATA_FETCH: ✅ Successfully fetched 30 candles from Upstox for NSE_EQ|INE002A01018 (1d)
14:30:16 - INDICATOR_CALC: 📈 Calculating RSI for NSE_EQ|INE002A01018 (1d)
14:30:17 - SIGNAL_GENERATED: 🎯 Generated BUY signal for NSE_EQ|INE002A01018 using RSI
14:30:18 - TRADE_EXECUTED: 💰 Executed BUY order for NSE_EQ|INE002A01018 (10 shares @ ₹2,450.75)
```

## Step 6: Start Automated Trading

### 6.1 Run the Trading Bot
```bash
python manage.py run_trading_bot --interval 60
```

This will:
- 🔄 Check strategies every 60 seconds
- 📊 Fetch real-time data from Upstox
- 🎯 Calculate indicators and generate signals
- 💰 Execute trades automatically
- 📝 Log all activities in real-time

### 6.2 Monitor Bot Activity
- Watch the monitoring page for live updates
- Check logs for data fetching, signal generation, and trade execution
- Verify that real Indian stock data is being used

## Troubleshooting

### Issue: "No Upstox access token available"
**Solution**: Complete the Upstox authorization process in Step 2.3

### Issue: "Upstox API returned no data"
**Solution**: 
1. Check if the symbol format is correct
2. Verify your Upstox account has market data access
3. Try with different symbols

### Issue: "Invalid response from Upstox API"
**Solution**:
1. Check if your API credentials are correct
2. Verify the redirect URI matches exactly
3. Re-authorize your Upstox integration

### Issue: "Token expired"
**Solution**: 
1. Go to brokerage integration page
2. Re-authorize with Upstox
3. The system will automatically refresh tokens

## Important Notes

### ✅ What Works Now
- **Real Indian stock data** from Upstox API
- **Correct symbol formats** for NSE stocks
- **Live market quotes** and historical data
- **Professional-grade data** for accurate signals
- **Real-time logging** of all activities

### 🔄 Data Flow
1. **Strategy** → Requests data for specific symbol
2. **Upstox API** → Returns real Indian stock data
3. **Indicators** → Calculate using actual market data
4. **Signals** → Generated based on real market conditions
5. **Trades** → Executed with live market prices
6. **Logs** → Record all activities in real-time

### 📊 Monitoring
- All activities are logged with timestamps
- Real-time updates on the monitoring page
- Detailed error messages for troubleshooting
- Performance metrics and trade history

## Next Steps

1. **Test with different symbols** and timeframes
2. **Add more indicators** to your strategies
3. **Set up risk management** parameters
4. **Monitor performance** and optimize strategies
5. **Scale up** with more strategies and symbols

---

**🎉 Congratulations!** Your bot is now getting real Indian stock market data from Upstox and calculating indicators based on actual market conditions! 
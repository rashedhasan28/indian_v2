# Trading Bot - How It Works

## Overview
The trading bot automatically executes trading strategies based on technical indicators. Here's what happens when it's running:

## ✅ What's Working Now

### 1. **Candle Data Collection**
- Fetches historical market data using Yahoo Finance API
- Supports multiple timeframes: 1m, 5m, 15m, 30m, 1h, 1d
- Stores data in the database for analysis

### 2. **Technical Indicators**
The bot calculates these indicators and generates signals:
- **RSI** (Relative Strength Index) - Buy when RSI > 60, Sell when RSI < 40
- **MACD** - Buy when MACD crosses above signal line
- **Moving Average** - Buy when price crosses above MA
- **VWAP** (Volume Weighted Average Price) - Buy when price above VWAP
- **ADX** (Average Directional Index) - Buy when +DI crosses above -DI
- **SuperTrend** - Buy when price above SuperTrend line

### 3. **Strategy Management**
- Create trading setups with specific indicators
- Convert setups into running strategies
- Start/stop strategies as needed
- Track strategy performance

### 4. **Trade Execution**
- Places orders through Upstox API
- Records all trades in database
- Tracks order status and execution

## 🔄 How the Bot Runs

### Step 1: Data Collection
```python
# Gets historical data for the symbol
data = bot.get_market_data_for_analysis(symbol)
```

### Step 2: Signal Generation
```python
# Calculates indicator and generates signal
signal = bot.generate_signal(setup)  # Returns 'buy', 'sell', or 'hold'
```

### Step 3: Trade Execution
```python
# If signal is buy/sell, executes trade
if signal in ['buy', 'sell']:
    trade = bot.execute_trade(setup, signal)
```

## 🚀 How to Run the Bot

### Method 1: Using the Simple Script
```bash
# Run with default 60-second interval
python run_bot.py

# Run with custom interval (30 seconds)
python run_bot.py --interval 30

# Run for specific user only
python run_bot.py --user your_email@example.com
```

### Method 2: Using Django Management Command
```bash
# Run with default settings
python manage.py run_trading_bot

# Run with custom interval
python manage.py run_trading_bot --interval 60

# Run for specific user
python manage.py run_trading_bot --user your_email@example.com
```

## 📊 What the Bot Does Every Cycle

1. **Finds Running Strategies**: Looks for strategies with status = 'RUNNING'
2. **Gets Market Data**: Fetches latest candle data for each strategy's symbol
3. **Calculates Indicators**: Applies the selected technical indicator
4. **Generates Signals**: Determines if it should buy, sell, or hold
5. **Executes Trades**: Places orders if buy/sell signals are generated
6. **Updates Records**: Saves trade details and strategy status
7. **Waits**: Sleeps for the specified interval before next cycle

## ⚠️ Important Notes

### Current Limitations:
1. **Data Source**: Uses Yahoo Finance instead of real-time Upstox data
2. **Manual Start**: Bot must be started manually (no automatic scheduling)
3. **Basic Signals**: Uses simple buy/sell logic (no position sizing or risk management)

### Prerequisites:
1. **Upstox Integration**: Must have valid Upstox API credentials
2. **Active Strategies**: Must have at least one strategy with status = 'RUNNING'
3. **Market Hours**: Bot works best during market hours (9:15 AM - 3:30 PM IST)

## 🔧 Troubleshooting

### Bot Not Running:
- Check if you have running strategies in the database
- Verify Upstox integration is active
- Check logs for error messages

### No Trades Executed:
- Verify indicator settings are appropriate
- Check if signals are being generated (look at strategy.last_signal)
- Ensure Upstox API has sufficient balance

### Data Issues:
- Check internet connection
- Verify symbol format (should be like 'RELIANCE', 'TCS')
- Check if Yahoo Finance has data for the symbol

## 📈 Example Strategy Setup

1. **Create Trading Setup**:
   - Symbol: RELIANCE
   - Indicator: RSI
   - Timeframe: 1D
   - Quantity: 10

2. **Create Strategy**:
   - Name: "Reliance RSI Strategy"
   - Setup: Select the above setup
   - Status: RUNNING

3. **Run Bot**:
   ```bash
   python run_bot.py --interval 300  # Check every 5 minutes
   ```

The bot will now:
- Fetch RELIANCE data every 5 minutes
- Calculate RSI indicator
- Generate buy/sell signals
- Execute trades when conditions are met

## 🛡️ Safety Features

- All trades are recorded in the database
- Failed trades are marked as 'FAILED'
- Bot can be stopped anytime with Ctrl+C
- User-specific strategies (bot only trades for the logged-in user) 
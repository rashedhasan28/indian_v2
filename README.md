# Indian Stock Market Trading Bot

A comprehensive Django-based automated trading platform designed for the Indian stock market with Upstox integration.

## 🚀 Features

### Core Functionality
- **Automated Trading**: Execute trades based on technical indicators
- **Upstox Integration**: Full API integration with Upstox brokerage
- **Technical Analysis**: Multiple indicators (RSI, MACD, Moving Average, VWAP, ADX, Supertrend)
- **Strategy Management**: Create, start, stop, and monitor trading strategies
- **Real-time Monitoring**: Live tracking of trades and portfolio
- **User Dashboard**: Comprehensive trading statistics and performance metrics

### Technical Indicators
- **RSI (Relative Strength Index)**: Overbought/oversold signals
- **MACD (Moving Average Convergence Divergence)**: Trend following momentum
- **Moving Average**: Simple trend analysis
- **VWAP (Volume Weighted Average Price)**: Volume-based price analysis
- **ADX (Average Directional Index)**: Trend strength measurement
- **Supertrend**: Trend-following indicator with stop-loss

### Trading Features
- **Multi-timeframe Support**: 1m, 5m, 15m, 30m, 1h, 1d
- **Multi-exchange Support**: NSE, BSE, MCX
- **Market Types**: Equity, Commodity, Currency
- **Order Types**: Market orders with automatic execution
- **Portfolio Tracking**: Real-time holdings and P&L

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Django 4.1.5
- Upstox API credentials

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd indian_stockmarket-main
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

5. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## 🔧 Configuration

### Upstox API Setup

1. **Get Upstox API Credentials**
   - Register at [Upstox Developer Portal](https://developer.upstox.com/)
   - Create a new application
   - Get your API Key and Secret Key

2. **Configure Brokerage Integration**
   - Go to `/brokerage-integration/`
   - Select "Upstox" as brokerage
   - Enter your API credentials
   - Set redirect URL (e.g., `http://localhost:8000/upstox-callback/`)

3. **Complete OAuth Flow**
   - Click "Get Code" to authorize with Upstox
   - Complete the OAuth process
   - Your access token will be stored automatically

## 📊 Usage

### 1. Create Trading Setup
1. Navigate to **Trading Setup**
2. Fill in the form:
   - **Setup Name**: Descriptive name for your strategy
   - **Symbol**: Stock symbol (e.g., RELIANCE, TCS)
   - **Indicator**: Choose technical indicator
   - **Timeframe**: Select time interval
   - **Exchange**: NSE, BSE, or MCX
   - **Type**: Cash, Future, or Option
   - **Market**: Equity, Commodity, or Currency
   - **Quantity**: Number of shares to trade

### 2. Create Strategy
1. Go to **Strategies** page
2. Click "Create New Strategy"
3. Select your trading setup
4. Give your strategy a name

### 3. Start Trading
1. Click "Start" on your strategy
2. The bot will automatically:
   - Monitor market data
   - Generate trading signals
   - Execute trades when conditions are met

### 4. Monitor Performance
- **Dashboard**: Overview of trading statistics
- **Trade History**: Detailed trade records
- **Portfolio**: Current holdings and P&L

## 🤖 Running the Bot

### Manual Execution
```bash
python manage.py run_trading_bot
```

### With Custom Interval
```bash
python manage.py run_trading_bot --interval 30
```

### For Specific User
```bash
python manage.py run_trading_bot --user username
```

## 📁 Project Structure

```
indian_stockmarket-main/
├── accounts/
│   ├── models.py              # Database models
│   ├── views.py               # View functions
│   ├── upstox_api.py          # Upstox API integration
│   ├── indicators.py          # Technical indicators
│   └── management/
│       └── commands/
│           └── run_trading_bot.py  # Bot execution command
├── bot/
│   ├── settings.py            # Django settings
│   └── urls.py                # URL configuration
├── templates/
│   ├── dashboard.html         # Main dashboard
│   ├── trading_setup.html     # Setup creation
│   ├── trade_history.html     # Trade records
│   └── portfolio.html         # Holdings view
└── requirements.txt           # Python dependencies
```

## 🔒 Security Features

- **CSRF Protection**: All forms protected against CSRF attacks
- **User Authentication**: Login required for all trading operations
- **Secure Token Storage**: API tokens stored securely in database
- **Input Validation**: All user inputs validated and sanitized

## 📈 Technical Indicators

### RSI (Relative Strength Index)
- **Buy Signal**: RSI rises above 60
- **Sell Signal**: RSI falls below 40
- **Hold**: RSI between 40-60

### MACD (Moving Average Convergence Divergence)
- **Buy Signal**: MACD crosses above signal line
- **Sell Signal**: MACD crosses below signal line
- **Hold**: No crossover

### Moving Average
- **Buy Signal**: Price crosses above MA
- **Sell Signal**: Price crosses below MA
- **Hold**: No crossover

### VWAP (Volume Weighted Average Price)
- **Buy Signal**: Price above VWAP
- **Sell Signal**: Price below VWAP
- **Hold**: Price at VWAP

### ADX (Average Directional Index)
- **Buy Signal**: +DI crosses above -DI
- **Sell Signal**: -DI crosses above +DI
- **Hold**: No crossover

### Supertrend
- **Buy Signal**: Price closes above Supertrend line
- **Sell Signal**: Price closes below Supertrend line
- **Hold**: No clear signal

## ⚠️ Important Notes

### Risk Disclaimer
- This is a trading bot for educational purposes
- Always test strategies in paper trading mode first
- Past performance doesn't guarantee future results
- Trading involves risk of financial loss

### API Limitations
- Upstox API has rate limits
- Market data may have delays
- Not all order types are supported
- Trading hours: 9:15 AM - 3:30 PM IST (NSE)

### Best Practices
- Start with small quantities
- Monitor strategies regularly
- Set stop-loss orders
- Diversify your strategies
- Keep track of all trades

## 🐛 Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Check your API credentials
   - Verify redirect URL configuration
   - Ensure Upstox account is active

2. **No Trading Signals**
   - Check market data availability
   - Verify indicator parameters
   - Ensure symbol is correct

3. **Orders Not Executing**
   - Check account balance
   - Verify market hours
   - Check order status in Upstox

### Debug Mode
Enable debug logging in `settings.py`:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
```

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review Django and Upstox documentation
3. Create an issue in the repository

## 📄 License

This project is for educational purposes. Use at your own risk.

---

**Happy Trading! 🚀📈** 
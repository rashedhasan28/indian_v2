#!/usr/bin/env python
"""
Simple test to verify data access with working symbols
"""

import yfinance as yf
import pandas as pd

def test_working_symbols():
    """Test with symbols that should work"""
    
    print("🔍 Testing Data Access with Working Symbols")
    print("=" * 50)
    
    # Test with some known working symbols
    test_symbols = [
        'AAPL',  # Apple (US)
        'MSFT',  # Microsoft (US)
        'GOOGL', # Google (US)
        'RELIANCE.BO',  # Reliance (BSE)
        'TCS.BO',      # TCS (BSE)
        'HDFCBANK.BO'  # HDFC Bank (BSE)
    ]
    
    for symbol in test_symbols:
        print(f"\n📊 Testing {symbol}...")
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="7d")
            
            if not data.empty:
                print(f"✅ Got {len(data)} data points")
                print(f"   Latest close: ${data['Close'].iloc[-1]:.2f}")
                print(f"   Date range: {data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}")
                print(f"   Columns: {list(data.columns)}")
            else:
                print(f"❌ No data for {symbol}")
                
        except Exception as e:
            print(f"❌ Error with {symbol}: {e}")

def test_indian_symbols():
    """Test specifically with Indian stock symbols"""
    
    print("\n🇮🇳 Testing Indian Stock Symbols")
    print("=" * 40)
    
    indian_symbols = [
        'RELIANCE.BO',    # BSE
        'TCS.BO',         # BSE
        'HDFCBANK.BO',    # BSE
        'INFY.BO',        # BSE
        'RELIANCE.NS',    # NSE (try both)
        'TCS.NS',         # NSE
        'HDFCBANK.NS',    # NSE
        'INFY.NS'         # NSE
    ]
    
    working_symbols = []
    
    for symbol in indian_symbols:
        print(f"\n🔍 Testing {symbol}...")
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="5d")
            
            if not data.empty:
                print(f"✅ Got {len(data)} data points")
                print(f"   Latest close: ₹{data['Close'].iloc[-1]:.2f}")
                working_symbols.append(symbol)
            else:
                print(f"❌ No data for {symbol}")
                
        except Exception as e:
            print(f"❌ Error with {symbol}: {e}")
    
    print(f"\n🎯 Working Indian symbols: {working_symbols}")
    return working_symbols

if __name__ == '__main__':
    test_working_symbols()
    working_symbols = test_indian_symbols()
    
    if working_symbols:
        print(f"\n✅ Found {len(working_symbols)} working symbols for Indian stocks")
        print("Use these symbols in your trading setups!")
    else:
        print("\n❌ No working Indian stock symbols found")
        print("This might be a network or API issue") 
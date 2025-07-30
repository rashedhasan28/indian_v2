import numpy as np
import pandas as pd


def rsi_signal(prices: pd.Series, period: int = 14) -> str:
    """
    Calculate RSI and return buy/sell/hold signal based on:
    - Buy: RSI rises above 60
    - Sell: RSI falls below 40
    """
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    latest_rsi = rsi.iloc[-1]
    if latest_rsi > 60:
        return 'buy'
    elif latest_rsi < 40:
        return 'sell'
    else:
        return 'hold'


def macd_signal(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> str:
    """
    Calculate MACD and return buy/sell/hold signal based on:
    - Buy: MACD crosses above signal line
    - Sell: MACD crosses below signal line
    """
    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    if macd.iloc[-2] < signal_line.iloc[-2] and macd.iloc[-1] > signal_line.iloc[-1]:
        return 'buy'
    elif macd.iloc[-2] > signal_line.iloc[-2] and macd.iloc[-1] < signal_line.iloc[-1]:
        return 'sell'
    else:
        return 'hold'


def moving_average_signal(prices: pd.Series, window: int = 20) -> str:
    """
    Calculate Moving Average and return buy/sell/hold signal based on:
    - Buy: Price crosses above MA
    - Sell: Price crosses below MA
    """
    ma = prices.rolling(window=window).mean()
    if prices.iloc[-2] < ma.iloc[-2] and prices.iloc[-1] > ma.iloc[-1]:
        return 'buy'
    elif prices.iloc[-2] > ma.iloc[-2] and prices.iloc[-1] < ma.iloc[-1]:
        return 'sell'
    else:
        return 'hold'


def vwap_signal(prices: pd.Series, volumes: pd.Series) -> str:
    """
    Calculate VWAP and return buy/sell/hold signal based on:
    - Buy: Price above VWAP
    - Sell: Price below VWAP
    """
    vwap = (prices * volumes).cumsum() / volumes.cumsum()
    if prices.iloc[-1] > vwap.iloc[-1]:
        return 'buy'
    elif prices.iloc[-1] < vwap.iloc[-1]:
        return 'sell'
    else:
        return 'hold'


def adx_signal(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> str:
    """
    Calculate ADX and return buy/sell/hold signal based on:
    - Buy: +DI crosses above -DI
    - Sell: -DI crosses above +DI
    """
    plus_dm = high.diff()
    minus_dm = low.diff().abs()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    plus_di = 100 * (plus_dm.rolling(window=period).sum() / atr)
    minus_di = 100 * (minus_dm.rolling(window=period).sum() / atr)
    if plus_di.iloc[-2] < minus_di.iloc[-2] and plus_di.iloc[-1] > minus_di.iloc[-1]:
        return 'buy'
    elif minus_di.iloc[-2] < plus_di.iloc[-2] and minus_di.iloc[-1] > plus_di.iloc[-1]:
        return 'sell'
    else:
        return 'hold'


def supertrend_signal(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 10, multiplier: float = 3.0) -> str:
    """
    Calculate SuperTrend and return buy/sell/hold signal based on:
    - Buy: Price above SuperTrend
    - Sell: Price below SuperTrend
    """
    atr = calculate_atr(high, low, close, period)
    upper_band = ((high + low) / 2) + (multiplier * atr)
    lower_band = ((high + low) / 2) - (multiplier * atr)
    
    supertrend = pd.Series(index=close.index, dtype=float)
    direction = pd.Series(index=close.index, dtype=int)
    
    for i in range(period, len(close)):
        if close.iloc[i] > upper_band.iloc[i-1]:
            direction.iloc[i] = 1
        elif close.iloc[i] < lower_band.iloc[i-1]:
            direction.iloc[i] = -1
        else:
            direction.iloc[i] = direction.iloc[i-1]
            
        if direction.iloc[i] == 1 and lower_band.iloc[i] < lower_band.iloc[i-1]:
            lower_band.iloc[i] = lower_band.iloc[i-1]
        if direction.iloc[i] == -1 and upper_band.iloc[i] > upper_band.iloc[i-1]:
            upper_band.iloc[i] = upper_band.iloc[i-1]
            
        if direction.iloc[i] == 1:
            supertrend.iloc[i] = lower_band.iloc[i]
        else:
            supertrend.iloc[i] = upper_band.iloc[i]
    
    if close.iloc[-1] > supertrend.iloc[-1]:
        return 'buy'
    elif close.iloc[-1] < supertrend.iloc[-1]:
        return 'sell'
    else:
        return 'hold'


def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Calculate Average True Range"""
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(window=period).mean() 
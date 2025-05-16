import pandas as pd
import numpy as np

# === Funzione per il calcolo delle feature avanzate ===
def compute_features(df):
    df = df.copy()

    df['rsi'] = compute_rsi(df['close'])
    df['ema_fast'] = df['close'].ewm(span=12).mean()
    df['ema_slow'] = df['close'].ewm(span=26).mean()
    df['macd'] = df['ema_fast'] - df['ema_slow']
    df['macd_signal'] = df['macd'].ewm(span=9).mean()
    df['macd_delta'] = df['macd'] - df['macd_signal']

    df['rsi_delta'] = df['rsi'].diff()
    df['price_change_%'] = df['close'].pct_change() * 100
    df['volatility'] = df['close'].rolling(window=10).std() / df['close'].rolling(window=10).mean()
    df['roc'] = df['close'].pct_change(periods=5) * 100
    df['volume_relative_%'] = df['volume'] / df['volume'].rolling(window=20).mean() * 100
    df['ma_position'] = df['close'] / df['close'].rolling(window=20).mean()
    df['momentum'] = df['close'] - df['close'].shift(10)

    # === Bande di Bollinger ===
    rolling_mean = df['close'].rolling(window=20).mean()
    rolling_std = df['close'].rolling(window=20).std()
    df['bollinger_upper'] = rolling_mean + (rolling_std * 2)
    df['bollinger_lower'] = rolling_mean - (rolling_std * 2)
    df['bollinger_pos'] = (df['close'] - df['bollinger_lower']) / (df['bollinger_upper'] - df['bollinger_lower'])

    # === Sentiment placeholder ===
    df['sentiment_score'] = 0.0  # da aggiornare più avanti con un modulo dedicato

    return df.dropna()

# === RSI ===
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

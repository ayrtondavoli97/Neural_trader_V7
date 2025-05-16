import pandas as pd
import numpy as np
from datetime import datetime
import random
import os

# === CONFIG ===
DATA_DIR = 'data/dataset/'
OUTPUT_FILE = 'training_memory_long_short.csv'
SAMPLES_PER_CLASS = 500
INCLUDE_NEUTRO = False  # <--- switcha questo a True se vuoi reinserire i neutri

# === Feature Generator ===
def generate_example(signal):
    base_price = random.uniform(1, 100_000)
    rsi = random.uniform(30, 70)
    macd = random.uniform(-5, 5)
    macd_signal = macd + random.uniform(-1, 1)
    ema_trend = 1 if macd > macd_signal else 0
    boll_pos = random.uniform(0, 1)
    momentum = random.uniform(-5, 5)
    volatility = random.uniform(0.001, 0.1)
    volume_rel = random.uniform(20, 200)
    sentiment_score = random.uniform(-1, 1)

    if signal == 'LONG':
        rsi = random.uniform(10, 35)
        macd = random.uniform(0.5, 3)
        macd_signal = macd - random.uniform(0.1, 0.5)
        ema_trend = 1
        sentiment_score = random.uniform(0.2, 1)

    elif signal == 'SHORT':
        rsi = random.uniform(65, 90)
        macd = random.uniform(-3, -0.5)
        macd_signal = macd + random.uniform(0.1, 0.5)
        ema_trend = 0
        sentiment_score = random.uniform(-1, -0.2)

    elif signal == 'NEUTRO':
        rsi = random.uniform(45, 55)
        macd = random.uniform(-0.3, 0.3)
        macd_signal = macd + random.uniform(-0.2, 0.2)
        ema_trend = random.choice([0, 1])
        sentiment_score = random.uniform(-0.2, 0.2)

    return {
        'timestamp': datetime.utcnow(),
        'symbol': random.choice(['BTC-USDT', 'ETH-USDT', 'SOL-USDT']),
        'close': base_price,
        'rsi': rsi,
        'macd': macd,
        'macd_signal': macd_signal,
        'ema_trend': ema_trend,
        'bollinger_pos': boll_pos,
        'momentum': momentum,
        'volatility': volatility,
        'volume_relative_%': volume_rel,
        'sentiment_score': sentiment_score,
        'signal': signal
    }

# === Generazione ===
data = []
target_signals = ['LONG', 'SHORT']
if INCLUDE_NEUTRO:
    target_signals.append('NEUTRO')

for signal in target_signals:
    for _ in range(SAMPLES_PER_CLASS):
        data.append(generate_example(signal))

# === Shuffle ===
df = pd.DataFrame(data)
df = df.sample(frac=1).reset_index(drop=True)

# === Salvataggio ===
os.makedirs(DATA_DIR, exist_ok=True)
full_path = os.path.join(DATA_DIR, OUTPUT_FILE)
df.to_csv(full_path, index=False)
print(f"✅ Dataset salvato in {full_path} con segnali: {target_signals}")

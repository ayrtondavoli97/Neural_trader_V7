import os
import pandas as pd
import requests
from datetime import datetime
import time

# === CONFIG ===
BASE_URL = "https://api.kucoin.com"
SYMBOL_FILE = "configs/pairs_to_track.txt"
REAL_DATA_DIR = "data/real_data"
CANDLE_INTERVAL = "1hour"
CANDLE_LIMIT = 200

os.makedirs(REAL_DATA_DIR, exist_ok=True)

def fetch_candles(symbol):
    url = f"{BASE_URL}/api/v1/market/candles?type={CANDLE_INTERVAL}&symbol={symbol}&limit={CANDLE_LIMIT}"
    try:
        r = requests.get(url)
        r.raise_for_status()
        candles = r.json()['data']
        if not candles:
            return None
        df = pd.DataFrame(candles, columns=[
            "timestamp", "open", "close", "high", "low", "volume", "turnover"])
        df = df.astype(float)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        df = df.sort_values('timestamp')
        df = df[df['volume'] > 0]  # filtra candele vuote
        df['symbol'] = symbol
        df['timeframe'] = '1h'
        return df
    except Exception as e:
        print(f"[ERRORE API] {symbol} → {e}")
        return None

def main():
    with open(SYMBOL_FILE, 'r') as f:
        symbols = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    for symbol in symbols:
        df = fetch_candles(symbol)
        if df is None or df.empty:
            continue

        df = df.tail(100)
        last_ts = df['timestamp'].max()

        out_path = os.path.join(REAL_DATA_DIR, f"{symbol}.csv")

        # Evita overwrite se non ci sono nuovi dati
        if os.path.exists(out_path):
            df_existing = pd.read_csv(out_path)
            if 'timestamp' in df_existing.columns:
                df_existing['timestamp'] = pd.to_datetime(df_existing['timestamp'], errors='coerce')
                last_saved = df_existing['timestamp'].max()
                if pd.notna(last_saved) and last_ts <= last_saved:
                    print(f"[SKIP] Nessun nuovo dato per {symbol}")
                    continue

        print(f"[OK] Dati salvati per {symbol} (ultima candela: {last_ts})")
        df.to_csv(out_path, index=False)
        time.sleep(0.05)

    print("[DONE] Raccolta completata.")

if __name__ == "__main__":
    main()
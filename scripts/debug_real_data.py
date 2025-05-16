import os
import pandas as pd
from datetime import datetime, timedelta

PREDICTIONS_DIR = 'data/predictions/latest'
REAL_DATA_DIR = 'data/real_data'

def debug_real_data():
    files = os.listdir(PREDICTIONS_DIR)
    files = [f for f in files if f.endswith('.csv')]

    now = datetime.utcnow()

    for file in files:
        try:
            pred_df = pd.read_csv(os.path.join(PREDICTIONS_DIR, file))
            if pred_df.empty:
                continue

            row = pred_df.iloc[0]
            symbol = row['symbol']
            prediction_time = pd.to_datetime(row['timestamp'])
            target_time = prediction_time + timedelta(hours=1)

            real_file = os.path.join(REAL_DATA_DIR, f"{symbol.replace('/', '-')}.csv")
            if not os.path.exists(real_file):
                print(f"📁 {symbol} - ❌ file dati reali mancante")
                continue

            real_df = pd.read_csv(real_file)
            real_df['timestamp'] = pd.to_datetime(real_df['timestamp'], errors='coerce')
            real_df = real_df.sort_values('timestamp')

            future_data = real_df[real_df['timestamp'] >= target_time]

            print(f"🔎 {symbol} | pred: {prediction_time} | target: {target_time} | now: {now}")

            if now < target_time:
                print(f"⏳ {symbol} - Troppo presto per valutare score_1h")
            elif future_data.empty:
                print(f"🚫 {symbol} - Nessun dato reale dopo {target_time}")
            else:
                print(f"✅ {symbol} - Dato reale trovato: {future_data.iloc[0]['timestamp']} | Close: {future_data.iloc[0]['close']}")

        except Exception as e:
            print(f"⚠️ Errore con {file}: {e}")

if __name__ == '__main__':
    debug_real_data()

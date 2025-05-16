import pandas as pd
from datetime import timedelta
import os

EVAL_PATH = "data/evaluations/evaluation_2025-05-13_21-28-35.csv"
REAL_DATA_DIR = "data/real_data"
DELAY_HOURS = 0  # Perché lo stai facendo subito

df = pd.read_csv(EVAL_PATH)
df['timestamp'] = pd.to_datetime(df['timestamp'])

def get_real_price(symbol, target_time):
    filepath = os.path.join(REAL_DATA_DIR, f"{symbol}.csv")
    if not os.path.exists(filepath):
        return None
    try:
        real_df = pd.read_csv(filepath)
        real_df['timestamp'] = pd.to_datetime(real_df['timestamp'])
        # Trova la candela >= target_time
        after = real_df[real_df['timestamp'] >= target_time]
        if not after.empty:
            return after.iloc[0]['close']
        return None
    except:
        return None

patched = 0
for i, row in df.iterrows():
    if pd.isna(row.get('real_price')):
        symbol = row['symbol']
        ts = row['timestamp']
        target_time = ts + timedelta(hours=DELAY_HOURS)
        price_now = row['price']
        real_price = get_real_price(symbol, target_time)

        if real_price is not None:
            delta = ((real_price - price_now) / price_now) * 100
            score = 0
            if abs(delta) <= 0.2:
                score = 1  # Flat, considerata buona
            elif row['prediction'] == 'LONG' and delta > 0.2:
                score = 1
            elif row['prediction'] == 'SHORT' and delta < -0.2:
                score = 1

            df.at[i, 'real_price'] = real_price
            df.at[i, 'delta_pct'] = delta
            df.at[i, 'score_3h'] = score
            patched += 1

df.to_csv(EVAL_PATH.replace(".csv", "_PATCHED.csv"), index=False)
print(f"[✅] Patch completata. {patched} righe aggiornate.")

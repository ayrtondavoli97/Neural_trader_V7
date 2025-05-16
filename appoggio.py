import os
import pandas as pd

REAL_DATA_DIR = 'data/real_data'

for filename in os.listdir(REAL_DATA_DIR):
    if not filename.endswith(".csv"):
        continue

    symbol = filename.replace(".csv", "")
    path = os.path.join(REAL_DATA_DIR, filename)

    try:
        df = pd.read_csv(path)
        if 'symbol' not in df.columns:
            df['symbol'] = symbol
            df.to_csv(path, index=False)
            print(f"[✅] Patchato: {filename}")
        else:
            print(f"[SKIP] {filename} già ha colonna symbol.")
    except Exception as e:
        print(f"[❌] Errore su {filename}: {e}")

import os
import pandas as pd
import glob
from datetime import datetime

# === CONFIG ===
PREDICTIONS_LATEST_DIR = 'data/predictions/latest'
EVALUATIONS_DIR = 'data/evaluations'
BASE_TRAINING_SET = 'data/dataset/training_memory_long_short.csv'
EXTENDED_DATASET = 'data/dataset/training_memory_extended.csv'
NEW_DATASET = 'data/dataset/training_memory_new.csv'

def main():
    # === Trova l'ultimo evaluation file ===
    evaluation_files = sorted(glob.glob(os.path.join(EVALUATIONS_DIR, 'evaluation_*.csv')))
    if not evaluation_files:
        print("❌ Nessun file di valutazione trovato.")
        return

    latest_eval_file = evaluation_files[-1]
    print(f"[INFO] Ultimo file di valutazione: {latest_eval_file}")
    eval_df = pd.read_csv(latest_eval_file)

    # === Filtra solo esempi con score valido ===
    valid_examples = []
    for _, row in eval_df.iterrows():
        score = row.get('score')
        if score not in [0, 1]:
            continue

        symbol = row['symbol']
        ts = pd.to_datetime(row['timestamp'], errors='coerce')
        pred_file = os.path.join(PREDICTIONS_LATEST_DIR, f"{symbol}.csv")

        if not os.path.exists(pred_file):
            print(f"[MISS] File mancante: {pred_file}")
            continue

        pred_df = pd.read_csv(pred_file)
        if pred_df.empty:
            print(f"[EMPTY] File vuoto: {pred_file}")
            continue

        pred_df['timestamp'] = pd.to_datetime(pred_df['timestamp'], errors='coerce')
        pred_row = pred_df.loc[(pred_df['timestamp'] - ts).abs() <= pd.Timedelta('1H')]

        if pred_row.empty:
            print(f"[MISS] Nessuna riga con timestamp corrispondente per {symbol}")
            continue

        pred_row = pred_row.iloc[0]
        close_price = pred_row.get('close') or pred_row.get('price')
        if close_price is None:
            print(f"[SKIP] {symbol} manca 'close' e 'price'")
            continue

        try:
            valid_examples.append({
                'symbol': symbol,
                'timestamp': ts,
                'close': close_price,
                'rsi': pred_row.get('rsi', 0),
                'macd': pred_row.get('macd', 0),
                'macd_signal': pred_row.get('macd_signal', 0),
                'ema_trend': pred_row.get('ema_trend', 0),
                'bollinger_pos': pred_row.get('bollinger_pos', 0),
                'momentum': pred_row.get('momentum', 0),
                'volatility': pred_row.get('volatility', 0),
                'volume_relative_%': pred_row.get('volume_relative_%', 0),
                'sentiment_score': pred_row.get('sentiment_score', 0),
                'signal': row['prediction'],
                'score': score,
                'timeframe': '3h'
            })
        except Exception as e:
            print(f"[ERRORE] {symbol}: {e}")
            continue

    if not valid_examples:
        print("⚠️ Nessun esempio valido trovato.")
        return

    df_new = pd.DataFrame(valid_examples)
    df_new['timestamp'] = pd.to_datetime(df_new['timestamp'], errors='coerce')
    df_new.to_csv(NEW_DATASET, index=False)
    print(f"[✅] Salvati {len(df_new)} nuovi esempi in {NEW_DATASET}")

    # === Carica dataset base esteso ===
    if os.path.exists(EXTENDED_DATASET):
        df_ext = pd.read_csv(EXTENDED_DATASET)
        if 'symbol' not in df_ext.columns or 'timestamp' not in df_ext.columns:
            df_ext = pd.DataFrame()  # fallback safe se vuoto/corrotto
        else:
            df_ext['timestamp'] = pd.to_datetime(df_ext['timestamp'], errors='coerce')
    else:
        df_ext = pd.DataFrame()

    # === Evita duplicati ===
    df_new['id'] = df_new['symbol'].astype(str) + "_" + df_new['timestamp'].astype(str)
    if not df_ext.empty:
        df_ext['id'] = df_ext['symbol'].astype(str) + "_" + df_ext['timestamp'].astype(str)
        df_ext = df_ext.drop(columns=['id'], errors='ignore')
    else:
        df_ext = pd.DataFrame(columns=df_new.columns)

    df_new_unique = df_new[~df_new['id'].isin(df_ext.get('id', []))].drop(columns=['id'])

    nuovi_aggiunti = len(df_new_unique)
    if nuovi_aggiunti == 0:
        print(f"[ℹ️] Solo 0 su {len(df_new)} erano realmente nuovi.")
    else:
        print(f"[🔍] Nuovi esempi effettivamente aggiunti: {nuovi_aggiunti}")

    # === Aggiorna dataset esteso ===
    df_updated = pd.concat([df_ext, df_new_unique], ignore_index=True)
    df_updated.to_csv(EXTENDED_DATASET, index=False)
    print(f"[✅] Dataset esteso aggiornato: {len(df_updated)} righe totali")

if __name__ == "__main__":
    main()
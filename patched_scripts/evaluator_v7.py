import os
import glob
import pandas as pd
from datetime import datetime, timedelta
# [TELEGRAM REMOVED] from telegram_notifier import send_telegram_message

# === CONFIG ===
REAL_DATA_DIR = 'data/real_data'
EVALUATIONS_DIR = 'data/evaluations'
PREDICTIONS_DIR = 'data/predictions/historical'
EVALUATED_LOG = os.path.join(EVALUATIONS_DIR, 'evaluated_files.txt')
MISSING_LOG = os.path.join(EVALUATIONS_DIR, 'missing_real_data.txt')

RANGE_HOURS = 3
MIN_DELTA = 0.3
BENCHMARK_SYMBOLS = ['BTC-USDT', 'ETH-USDT']

os.makedirs(EVALUATIONS_DIR, exist_ok=True)

def get_evaluated_files():
    if not os.path.exists(EVALUATED_LOG):
        return set()
    with open(EVALUATED_LOG, 'r') as f:
        return set(line.strip() for line in f.readlines())

def mark_file_as_evaluated(filename):
    with open(EVALUATED_LOG, 'a') as f:
        f.write(filename + '\n')

def load_real_data(symbol):
    filepath = os.path.join(REAL_DATA_DIR, f"{symbol}.csv")
    if not os.path.exists(filepath):
        print(f"[SKIP] Nessun file real_data per {symbol}")
        return None
    try:
        df = pd.read_csv(filepath)
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df = df.dropna(subset=['timestamp', 'close'])
        df = df.sort_values('timestamp')
        return df
    except Exception as e:
        print(f"[ERRORE] Caricamento dati reali fallito per {symbol}: {e}")
        return None

def score_prediction(row, real_data, prediction_time):
    base_price = row['price']
    direction = row['prediction']
    if pd.isna(base_price) or base_price <= 0:
        print(f"[ERRORE] Prezzo base non valido per {row['symbol']} → {base_price}")
        return None, None

    start_time = prediction_time
    end_time = prediction_time + timedelta(hours=RANGE_HOURS)
    future = real_data[(real_data['timestamp'] >= start_time) & (real_data['timestamp'] <= end_time)]
    if future.empty:
        print(f"[DEBUG] Nessun dato futuro per {row['symbol']} nel range {start_time} → {end_time}")
        return None, None

    target_price = future['close'].min() if direction == "SHORT" else future['close'].max()
    delta_pct = ((target_price - base_price) / base_price) * 100
    if direction == "LONG" and delta_pct >= MIN_DELTA:
        return 1, delta_pct
    elif direction == "SHORT" and delta_pct <= -MIN_DELTA:
        return 1, delta_pct
    else:
        return 0, delta_pct

def evaluate_predictions():
    print("[VALUTAZIONE] Inizio valutazione predizioni...")
    now = datetime.utcnow()
    evaluated_files = get_evaluated_files()
    prediction_files = glob.glob(os.path.join(PREDICTIONS_DIR, 'predictions_*.csv'))

    for file_path in sorted(prediction_files):
        filename = os.path.basename(file_path)
        if filename in evaluated_files:
            continue

        ts_str = filename.replace("predictions_", "").replace(".csv", "")
        try:
            file_time = datetime.strptime(ts_str, "%Y-%m-%d %H-%M-%S")
        except ValueError:
            print(f"[ERRORE] Nome file invalido (formato timestamp): {filename}")
            continue

        # Skip file troppo vecchi (>24h)
        if now - file_time > timedelta(hours=24):
            print(f"[SKIP] {filename} troppo vecchio per essere valutato.")
            mark_file_as_evaluated(filename)
            continue

        # Controlla se è maturo abbastanza
        if now < file_time + timedelta(hours=RANGE_HOURS):
            print(f"[WAIT] {filename} non ancora maturo per valutazione.")
            continue

        print(f"[OK] Valutazione di: {filename}")
        df = pd.read_csv(file_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df['timestamp'] = df['timestamp'].dt.floor('H')
        df = df.dropna(subset=['timestamp', 'symbol', 'prediction', 'price'])

        results = []
        missing_symbols = []

        for _, row in df.iterrows():
            symbol = row['symbol']
            prediction_time = row['timestamp']
            real_data = load_real_data(symbol)
            if real_data is None:
                missing_symbols.append(symbol)
                continue

            real_max_time = real_data['timestamp'].max()
            if real_max_time < prediction_time + timedelta(hours=RANGE_HOURS):
                print(f"[DEBUG] {symbol} → pred_time: {prediction_time}, last_real: {real_max_time} ❌ dati reali insufficienti")
                continue

            print(f"[DEBUG] {symbol} → pred_time: {prediction_time}, last_real: {real_max_time}")

            score, delta = score_prediction(row, real_data, prediction_time)
            if score is None:
                continue

            r = row.to_dict()
            r['score'] = score
            r['delta_pct'] = delta
            if 'timeframe' in row:
                r['timeframe'] = row['timeframe']
            results.append(r)

        if not results:
            print(f"[INFO] Nessuna valutazione valida in {filename}")
            continue

        df_result = pd.DataFrame(results)
        timestamp_str = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        out_path = os.path.join(EVALUATIONS_DIR, f"evaluation_{timestamp_str}.csv")
        df_result.to_csv(out_path, index=False)
        print(f"[✅] Valutazione salvata in: {out_path}")

        total = len(df_result)
        correct = df_result['score'].sum()
        print(f"[📈 RISULTATO] {correct}/{total} predizioni corrette ({(correct/total)*100:.2f}%)")
# [TELEGRAM REMOVED]         send_telegram_message(f"✅ Valutazione completata: {correct}/{total} corrette ({(correct/total)*100:.1f}%)")

        if missing_symbols:
            with open(MISSING_LOG, 'a') as f:
                for sym in set(missing_symbols):
                    f.write(sym + '\n')

        mark_file_as_evaluated(filename)

if __name__ == "__main__":
    evaluate_predictions()

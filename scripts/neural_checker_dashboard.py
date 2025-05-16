import os
import pandas as pd
import glob
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from collections import defaultdict

# === CONFIG ===
DATASET_DIR = 'data/dataset'
PREDICTIONS_HIST_DIR = 'data/predictions/historical'
REAL_DATA_DIR = 'data/real_data'
EVAL_DIR = 'data/evaluations'
CHECK_OUTPUT = 'data/check/full_checker_report.txt'

os.makedirs(os.path.dirname(CHECK_OUTPUT), exist_ok=True)
log_lines = []

def log(msg):
    print(msg)
    log_lines.append(msg)

# === 1. TIMESTAMP CONSISTENCY ===
def check_timestamp_consistency():
    log("\n🕒 CHECK 1: Timestamp Consistency tra predizioni e real_data")
    pred_files = sorted(glob.glob(os.path.join(PREDICTIONS_HIST_DIR, 'predictions_*.csv')))
    for pred_file in pred_files:
        try:
            df = pd.read_csv(pred_file)
            if df.empty or 'timestamp' not in df.columns:
                log(f"⚠️  {pred_file} vuoto o senza timestamp")
                continue
            pred_ts = pd.to_datetime(df['timestamp'].iloc[0])
            missing = []
            for symbol in df['symbol'].unique():
                path = os.path.join(REAL_DATA_DIR, f"{symbol}.csv")
                if not os.path.exists(path):
                    missing.append(symbol)
                    continue
                r_df = pd.read_csv(path)
                if 'timestamp' not in r_df.columns:
                    missing.append(symbol)
                    continue
                r_df['timestamp'] = pd.to_datetime(r_df['timestamp'], errors='coerce')
                if r_df['timestamp'].max() < pred_ts + timedelta(hours=3):
                    missing.append(symbol)
            if missing:
                log(f"⏳ {os.path.basename(pred_file)} → dati non maturi per: {missing}")
        except Exception as e:
            log(f"❌ Errore lettura {pred_file}: {e}")

# === 2. DATASET HISTORY ===
def audit_dataset_history():
    log("\n📊 CHECK 2: Andamento storico training_memory_extended.csv")
    path = os.path.join(DATASET_DIR, 'training_memory_extended.csv')
    if not os.path.exists(path):
        log("❌ File non trovato: training_memory_extended.csv")
        return
    df = pd.read_csv(path)
    if 'timestamp' not in df.columns:
        log("❌ Nessuna colonna timestamp nel dataset")
        return
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df['day'] = df['timestamp'].dt.date
    stats = df.groupby('day')['symbol'].count()
    log("📈 Nuovi esempi per giorno:")
    for day, count in stats.items():
        log(f"  - {day}: {count} esempi")

# === 3. VALIDAZIONE PREDIZIONI ===
def validate_predictions():
    log("\n📌 CHECK 3: Controllo qualità predizioni_latest.csv")
    path = 'data/predictions/latest_global/predictions_latest.csv'
    if not os.path.exists(path):
        log("❌ File non trovato: predictions_latest.csv")
        return
    df = pd.read_csv(path)
    if df.empty:
        log("⚠️  predictions_latest.csv è vuoto")
        return
    pred_counts = df['prediction'].value_counts().to_dict()
    log(f"✅ Predizioni totali: {len(df)}")
    for label, count in pred_counts.items():
        log(f"  - {label}: {count}")
    if 'confidence' in df.columns:
        high_conf = df[df['confidence'] >= 0.9]
        log(f"🔝 Predizioni con alta confidenza (>=0.9): {len(high_conf)}")

# === 4. FLOW MAP ===
def generate_flow_map():
    log("\n🧠 CHECK 4: Flusso logico dati (statico)")
    flow = [
        "scanner.py → rsi_signals_filtered_latest.csv",
        "predictor.py → predictions_*.csv / top_predictions / latest_global",
        "real_data_collector.py → real_data/{symbol}.csv",
        "evaluator.py → evaluation_*.csv",
        "retrainer.py → training_memory_extended.csv",
        "trainer.py → transformer_model.pt, scaler.pkl, label_encoder.pkl",
        "predictor.py → predizioni nuove"
    ]
    for line in flow:
        log(f"→ {line}")

# === RUN ===
def main():
    log("==============================")
    log(" NEURALTRADER SYSTEM CHECKER ")
    log("==============================")
    check_timestamp_consistency()
    audit_dataset_history()
    validate_predictions()
    generate_flow_map()

    with open(CHECK_OUTPUT, 'w', encoding='utf-8') as f:
        for line in log_lines:
            f.write(line + '\n')
    print(f"\n[✅] Report completo salvato in: {CHECK_OUTPUT}")

if __name__ == '__main__':
    main()

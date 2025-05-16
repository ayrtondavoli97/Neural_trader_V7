import os
import pandas as pd
from datetime import datetime

# === CONFIG ===
CSV_PATHS = [
    'data/predictions/historical',
    'data/predictions/latest',
    'data/predictions/latest_global',
    'data/predictions/top',
    'data/real_data',
    'data/evaluations',
    'data/dataset'
]

ALLOWED_EXTENSIONS = ['.csv']
OUTPUT_LOG = r'C:\Users\neuralboss\Desktop\NeuralTraderV7\data\check\csv_structure_log.txt'


def check_csv(file_path, log_lines):
    log_lines.append(f"\n📄 File: {file_path}")
    try:
        df = pd.read_csv(file_path)
        log_lines.append(f"  ✅ Righe: {len(df)}, Colonne: {len(df.columns)}")
        for col in df.columns:
            sample = df[col].dropna().iloc[0] if not df[col].dropna().empty else "<vuoto>"
            dtype = df[col].dtype
            log_lines.append(f"    - {col} ({dtype}) es: {sample}")

        # Check timestamp format se presente
        if 'timestamp' in df.columns:
            try:
                ts = pd.to_datetime(df['timestamp'], errors='raise')
                log_lines.append("    ⏱️ Timestamp: formato OK")
            except Exception as e:
                log_lines.append(f"    ❌ Timestamp malformato: {e}")

    except Exception as e:
        log_lines.append(f"  ❌ Errore lettura: {e}")


def scan_directories():
    log_lines = ["🔍 Scansione CSV in corso..."]
    for base_dir in CSV_PATHS:
        if not os.path.exists(base_dir):
            continue
        for root, _, files in os.walk(base_dir):
            for file in files:
                if file.endswith(tuple(ALLOWED_EXTENSIONS)):
                    check_csv(os.path.join(root, file), log_lines)

    # Scrivi l'output su file
    os.makedirs(os.path.dirname(OUTPUT_LOG), exist_ok=True)
    with open(OUTPUT_LOG, 'w', encoding='utf-8') as f:
        for line in log_lines:
            f.write(line + '\n')
    print(f"[✅] Log salvato in: {OUTPUT_LOG}")

if __name__ == "__main__":
    scan_directories()
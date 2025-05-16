import os
import pandas as pd

EVAL_DIR = "data/evaluations"
PRED_DIR = "data/predictions"
TRASH_DIR = "trash"

os.makedirs(TRASH_DIR, exist_ok=True)

def is_valid_eval(path):
    try:
        df = pd.read_csv(path)
        return df['real_price'].notna().sum() > 0 and df['score_3h'].notna().sum() > 0
    except Exception as e:
        print(f"[⚠️] Errore nel file {path}: {e}")
        return False

def cleanup_directory(path, name):
    print(f"\n🔍 Controllo in: {path}")
    for file in os.listdir(path):
        if not file.endswith(".csv"):
            continue
        full_path = os.path.join(path, file)
        if not is_valid_eval(full_path):
            print(f"🗑️  Sposto {file} in trash/")
            os.rename(full_path, os.path.join(TRASH_DIR, file))

cleanup_directory(EVAL_DIR, "evaluations")
cleanup_directory(PRED_DIR, "predictions")

print("\n✅ Pulizia completata.")

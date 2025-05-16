import time
import traceback
import os
from datetime import datetime
# [TELEGRAM REMOVED] from telegram_notifier import send_telegram_message

# === IMPORTA I MODULI OPERATIVI ===
from scanner import main as run_scanner
from predictor_v7 import main as run_predictor
from real_data_collector import main as run_real_data_collector
from evaluator_v7 import evaluate_predictions as run_evaluator
from retrainer_v7 import main as run_retrainer
from trainer import train_model

# === CONFIG ===
LOG_FILE = "logs/cycle_log.txt"
HEARTBEAT_FILE = "logs/heartbeat.txt"
PAUSE_BETWEEN_CYCLES = 30  # secondi
PAUSE_BETWEEN_PREDICT_AND_REAL = 3 * 60 * 60  # 3 ore
PAUSE_BEFORE_EVALUATOR = 1 * 60 * 60  # 1 ora

def log(msg):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8", errors="ignore") as f:
        f.write(line + "\n")

def safe_run(step_name, func):
    try:
        log(f"Avvio step: {step_name}")
        func()
        log(f"Completato: {step_name}")
    except Exception as e:
        error_msg = f"ERRORE nel modulo {step_name}: {str(e)}\n{traceback.format_exc()}"
        log(error_msg)
# [TELEGRAM REMOVED]         send_telegram_message(error_msg)
        exit(1)

def estrai_statistiche():
    import glob
    import pandas as pd
    # Cerca prima i multitime, poi fallback ai normali
    latest_eval = sorted(glob.glob("data/evaluations/evaluation_multitime_*.csv"))
    if not latest_eval:
        latest_eval = sorted(glob.glob("data/evaluations/evaluation_*.csv"))
    if not latest_eval:
        return "Nessun file di valutazione."

    df = pd.read_csv(latest_eval[-1])
    stats = {"LONG": [0, 0], "SHORT": [0, 0], "NEUTRO": [0, 0]}

    for _, row in df.iterrows():
        pred = row.get("signal") or row.get("prediction")
        if not pred or pred not in stats:
            continue
        for tf in ["score_1h", "score_2h", "score_4h", "score_6h", "score_3h"]:
            score = row.get(tf)
            if score in [0, 1]:
                stats[pred][1] += 1
                stats[pred][0] += score

    msg = "\nPerformance predizioni:\n"
    for sig, (correct, total) in stats.items():
        msg += f"{sig}: {correct}/{total}\n"
    return msg

def log_retrainer_stats():
    import pandas as pd
    new_path = "data/dataset/training_memory_new.csv"
    ext_path = "data/dataset/training_memory_extended.csv"
    if os.path.exists(new_path):
        df = pd.read_csv(new_path)
        new_count = len(df)
        log(f"Retrainer ha trovato {new_count} nuovi esempi validi.")
# [TELEGRAM REMOVED]         send_telegram_message(f"Retrainer attivo: {new_count} nuovi esempi trovati.")
    else:
        log("Retrainer non ha generato nuovi esempi.")
# [TELEGRAM REMOVED]         send_telegram_message("Retrainer non ha generato nuovi esempi.")

    if os.path.exists(ext_path):
        total = len(pd.read_csv(ext_path))
        log(f"Dataset esteso attuale contiene {total} esempi totali.")

def main_loop():
    log("Avvio ciclo continuo NeuralTrader V7")
# [TELEGRAM REMOVED]     send_telegram_message("✅ Ciclo NeuralTrader V7 iniziato")

    while True:
        cycle_start = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        log("===========================")
        log(f"Inizio ciclo: {cycle_start}")

        safe_run("Scanner", run_scanner)
        safe_run("Predictor", run_predictor)

        log("Attesa di 3h per real data (countdown con heartbeat)...")
        countdown = PAUSE_BETWEEN_PREDICT_AND_REAL
        heartbeat_interval = 60
        heartbeat_timer = heartbeat_interval

        while countdown > 0:
            hrs, rem = divmod(countdown, 3600)
            mins, secs = divmod(rem, 60)
            print(f"\r🕒 Attesa per real data: {int(hrs):02d}:{int(mins):02d}:{int(secs):02d}", end='', flush=True)
            time.sleep(1)
            countdown -= 1
            heartbeat_timer -= 1

            if heartbeat_timer <= 0:
                with open(HEARTBEAT_FILE, "w") as f:
                    f.write(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
                heartbeat_timer = heartbeat_interval

        print("\n[INFO] Tempo d'attesa completato. Passo alla fase successiva.")

        safe_run("RealDataCollector", run_real_data_collector)

        log("⏳ Attesa extra per sicurezza prima di valutare...")
        time.sleep(PAUSE_BEFORE_EVALUATOR)

        safe_run("Evaluator", run_evaluator)
        safe_run("Retrainer", run_retrainer)
        log_retrainer_stats()

        safe_run("Trainer", lambda: train_model("data/dataset/training_memory_extended.csv"))

        stats_msg = estrai_statistiche()
# [TELEGRAM REMOVED]         send_telegram_message(f"✅ Ciclo completato con successo!\n{stats_msg}")

        log("Ciclo completato con successo.")
        log("Pausa di 30 secondi prima del prossimo ciclo...")
        time.sleep(PAUSE_BETWEEN_CYCLES)

if __name__ == "__main__":
    main_loop()

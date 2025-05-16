import os
import time
from datetime import datetime, timedelta
#from telegram_notifier import send_telegram_message

# === CONFIG ===
LOG_FILE = "logs/cycle_log.txt"
HEARTBEAT_FILE = "logs/heartbeat.txt"

TIMEOUT_HOURS = 4  # Tempo massimo dall'ultimo ciclo completo
HEARTBEAT_TIMEOUT_MINUTES = 6  # Nessun battito da più di X minuti = warning
CHECK_INTERVAL = 1800  # Ogni 30 minuti
DEBUG = True

last_alert_time = None  # Per evitare spam

def debug_print(msg):
    if DEBUG:
        print(f"[Watchdog] {msg}")

def parse_last_log_time(log_file):
    if not os.path.exists(log_file):
        return None
    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    for line in reversed(lines):
        if "Inizio ciclo:" in line:
            try:
                time_str = line.split("Inizio ciclo:")[1].strip()
                return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            except Exception:
                continue
    return None

def monitor_cycle():
    global last_alert_time
    debug_print("Monitoraggio avviato...")
    while True:
        now = datetime.utcnow()
        last_cycle_time = parse_last_log_time(LOG_FILE)

        # === Controllo HEARTBEAT ===
        if os.path.exists(HEARTBEAT_FILE):
            with open(HEARTBEAT_FILE, "r") as f:
                hb_raw = f.read().strip()
            try:
                last_heartbeat = datetime.strptime(hb_raw, "%Y-%m-%d %H:%M:%S")
                delta_hb = now - last_heartbeat
                if delta_hb > timedelta(minutes=HEARTBEAT_TIMEOUT_MINUTES):
                    if not last_alert_time or (now - last_alert_time > timedelta(minutes=30)):
                        #send_telegram_message(
                        #    f"[Watchdog] Nessun heartbeat da {delta_hb}. Il countdown potrebbe essere interrotto!"
                       # )
                        last_alert_time = now
                else:
                    debug_print(f"Heartbeat OK ({delta_hb} fa)")
            except Exception as e:
                debug_print(f"Errore parsing heartbeat: {e}")
        else:
            debug_print("Nessun file heartbeat ancora presente.")

        # === Controllo CICLO COMPLETO ===
        if last_cycle_time:
            delta = now - last_cycle_time
            if delta > timedelta(hours=TIMEOUT_HOURS):
                if not last_alert_time or (now - last_alert_time > timedelta(minutes=30)):
                    #send_telegram_message(
                        #f"[Watchdog] Nessun ciclo completo da {delta}. Il bot potrebbe essere bloccato!"
                    #)
                    last_alert_time = now
            else:
                debug_print(f"Ciclo OK ({delta} fa)")
        else:
            if not last_alert_time or (now - last_alert_time > timedelta(minutes=30)):
                #send_telegram_message("[Watchdog] Nessun ciclo mai registrato. Avvia il bot!")
                last_alert_time = now

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor_cycle()

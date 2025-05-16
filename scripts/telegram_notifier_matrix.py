# === TELEGRAM NOTIFICATION MATRIX ===
# Questo file elenca in modo centralizzato quali script inviano notifiche Telegram,
# con quali funzioni e a quali eventi/trigger.

telegram_matrix = {
    "predictor.py": {
        "function": "send_top_predictions(filepath)",
        "trigger": "Predizioni con confidenza >= threshold",
        "note": "Invia il file CSV top_predictions al bot"
    },
    "evaluator.py": {
        "function": "send_telegram_message(message)",
        "trigger": "Valutazione completata (opzionale)",
        "note": "Può essere usato per inviare conferma ciclo valutazione"
    },
    "retrainer.py": {
        "function": "send_telegram_message(message)",
        "trigger": "Nuovi esempi trovati e dataset aggiornato",
        "note": "Utile per tenere traccia dell'apprendimento"
    },
    "trainer.py": {
        "function": "send_telegram_message(message)",
        "trigger": "Modello allenato e salvato",
        "note": "Può inviare accuratezza finale e path modello"
    },
    "system_watchdog.ps1": {
        "function": "send_telegram_message(status_report)",
        "trigger": "Blocco ciclo, crash processo o sistema inattivo",
        "note": "Script esterno che monitora via PowerShell"
    },
    "daily_cycle_v7.py": {
        "function": "send_telegram_message(summary_report)",
        "trigger": "Fine ciclo giornaliero o ogni 2h",
        "note": "Includi predizioni, valutazione, training, log stato"
    },
    "paper_trader.py": {
        "function": "send_telegram_message(trade_report)",
        "trigger": "Chiusura trade virtuale o aggiornamento budget",
        "note": "(Da implementare) Invia PnL e report paper trading"
    }
}

if __name__ == "__main__":
    print("\n📡 TELEGRAM NOTIFICATION OVERVIEW:\n")
    for script, details in telegram_matrix.items():
        print(f"📄 {script}")
        print(f"  🔔 Funzione: {details['function']}")
        print(f"  📍 Trigger: {details['trigger']}")
        print(f"  📝 Note: {details['note']}\n")

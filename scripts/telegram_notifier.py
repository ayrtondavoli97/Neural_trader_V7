import requests
import pandas as pd

# === CONFIG ===
BOT_TOKEN = "7961694843:AAFaqnAs3u5_017MPfUUdSy6Hkv03o1l9js"
CHAT_ID = "495456933"

TELEGRAM_ENABLED = True  # Toggle globale

# === FUNZIONE BASE ===
def send_telegram_message(message):
    if not TELEGRAM_ENABLED:
        print("[DEBUG] Telegram disattivato")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"[ERRORE] Telegram: {e}")

# === INVIO TOP 10 PREDIZIONI ===
def send_top_predictions(filepath):
    if filepath is None:
        return
    try:
        df = pd.read_csv(filepath)
        df = df.sort_values(by="confidence", ascending=False).head(10)
        message = "*Top 10 Predizioni AI*\n"
        for _, row in df.iterrows():
            symbol = row['symbol']
            prediction = row['prediction']
            confidence = round(float(row['confidence']) * 100, 2)
            message += f"\n• {symbol}: {prediction} ({confidence}%)"
        send_telegram_message(message)
    except Exception as e:
        send_telegram_message(f"Errore invio top predictions: {e}")

# === REPORT CICLO COMPLETO ===
def send_cycle_report(success=True, message=None):
    if success:
        msg = "Ciclo completato con successo!"
    else:
        msg = "Errore nel ciclo di trading!"
    if message:
        msg += f"\n{message}"
    send_telegram_message(msg)

# === PNL PAPER TRADING ===
def send_paper_trading_report(pnl, balance):
    msg = f"Paper Trading Update\n\n• PnL: `{pnl:.2f}$`\n• Balance: `{balance:.2f}$`"
    send_telegram_message(msg)

# === ALERT WATCHDOG ===
def send_watchdog_alert(error_msg):
    msg = f"Watchdog Alert\n\n{error_msg}"
    send_telegram_message(msg)

# === REPORT TRAINING ===
def send_training_report(accuracy, loss):
    msg = f"Training completato\n\n• Accuracy: `{accuracy:.2f}%`\n• Loss: `{loss:.4f}`"
    send_telegram_message(msg)

# === REPORT RETRAIN ===
def send_retrain_report(new_samples):
    msg = f"Retrainer\n\n• Nuovi esempi aggiunti: `{new_samples}`"
    send_telegram_message(msg)

# === REPORT EVALUATION ===
def send_evaluation_report(timestamp, long_correct, long_total, short_correct, short_total):
    msg = (
        f"Valutazione completata - Ciclo delle {timestamp.strftime('%H:%M')} UTC\n"
        f"• LONG corretti: {int(long_correct)}/{long_total}\n"
        f"• SHORT corretti: {int(short_correct)}/{short_total}"
    )
    send_telegram_message(msg)

# === DEBUG TEST ===
if __name__ == "__main__":
    send_telegram_message("Sistema di notifica Telegram attivo.")

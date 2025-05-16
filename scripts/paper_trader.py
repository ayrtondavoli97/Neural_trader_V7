import os
import pandas as pd
from datetime import datetime, timedelta
import glob

from real_data_collector import get_latest_close_price  # Assunto che sia nella stessa dir

# Percorsi dei file
WALLET_FILE = 'data/wallet/virtual_wallet.csv'
OPEN_POSITIONS_FILE = 'data/wallet/open_positions.csv'
CLOSED_POSITIONS_FILE = 'data/wallet/closed_positions.csv'

PREDICTIONS_FOLDER = 'data/predictions/top/'
INITIAL_CAPITAL = 1000
ALLOCATION_PER_TRADE = 100
POSITION_DURATION_HOURS = 3

# Funzione per ottenere il file di predizione più recente
def get_latest_prediction_file():
    files = glob.glob(os.path.join(PREDICTIONS_FOLDER, 'top_predictions_*.csv'))
    if not files:
        print("[DEBUG] Nessun file di predizioni trovato.")
        return None
    latest_file = max(files, key=os.path.getctime)
    print(f"[DEBUG] File predizioni caricato: {latest_file}")
    return latest_file

# Funzione per caricare il wallet e gestire il caso in cui il file sia vuoto
def load_wallet():
    if not os.path.exists(WALLET_FILE) or os.path.getsize(WALLET_FILE) == 0:
        wallet = pd.DataFrame([{'timestamp': datetime.now(), 'capital': INITIAL_CAPITAL}])
        wallet.to_csv(WALLET_FILE, index=False)
        print("[DEBUG] Creazione nuovo wallet con capitale iniziale.")
        return INITIAL_CAPITAL
    wallet = pd.read_csv(WALLET_FILE)
    print(f"[DEBUG] Capitale attuale: {wallet.iloc[-1]['capital']}")
    return float(wallet.iloc[-1]['capital'])

# Funzione per aggiornare il wallet
def update_wallet(new_capital):
    wallet = pd.read_csv(WALLET_FILE)
    wallet = pd.concat([wallet, pd.DataFrame([{
        'timestamp': datetime.now(),
        'capital': new_capital
    }])], ignore_index=True)
    wallet.to_csv(WALLET_FILE, index=False)
    print(f"[DEBUG] Wallet aggiornato: nuovo capitale {new_capital}$")

# Funzione per aprire le posizioni in base alla predizione top
def open_positions(current_capital):
    prediction_file = get_latest_prediction_file()
    if not prediction_file or not os.path.exists(prediction_file):
        print("[DEBUG] Nessun file di predizioni valido trovato.")
        return

    predictions = pd.read_csv(prediction_file)
    predictions = predictions.sort_values(by='confidence', ascending=False).head(10)
    
    # Prendi la top predizione con la confidenza più alta
    top_prediction = predictions.iloc[0]
    symbol = top_prediction['symbol']
    signal = top_prediction['signal'].lower()  # long o short
    price_open = top_prediction['price']  # prezzo di apertura
    print(f"[DEBUG] Apertura posizione per {symbol} ({signal}) con {ALLOCATION_PER_TRADE}$ di capitale.")
    
    # Verifica se il capitale è sufficiente
    if current_capital < ALLOCATION_PER_TRADE:
        print(f"[DEBUG] Capitale insufficiente per aprire posizione per {symbol}.")
        return
    
    # Crea la posizione da aprire
    position = {
        'symbol': symbol,
        'side': signal,
        'confidence': top_prediction['confidence'],
        'entry_time': datetime.now(),
        'entry_price': price_open,
        'budget': ALLOCATION_PER_TRADE,
        'status': 'open'
    }
    
    # Aggiorna il capitale
    current_capital -= ALLOCATION_PER_TRADE
    print(f"[DEBUG] Capitale restante: {current_capital}$")

    # Verifica se il file open_positions.csv esiste e crea una nuova posizione
    if not os.path.exists(OPEN_POSITIONS_FILE) or os.path.getsize(OPEN_POSITIONS_FILE) == 0:
        open_df = pd.DataFrame([position])
        print("[DEBUG] Creazione nuovo file di posizioni aperte.")
    else:
        open_df = pd.read_csv(OPEN_POSITIONS_FILE)
        open_df = pd.concat([open_df, pd.DataFrame([position])], ignore_index=True)

    open_df.to_csv(OPEN_POSITIONS_FILE, index=False)
    update_wallet(current_capital)

# Funzione per chiudere le posizioni dopo 3 ore e calcolare il PnL
def close_positions():
    if not os.path.exists(OPEN_POSITIONS_FILE) or os.path.getsize(OPEN_POSITIONS_FILE) == 0:
        print("[DEBUG] Nessuna posizione aperta da chiudere.")
        return

    open_df = pd.read_csv(OPEN_POSITIONS_FILE)
    still_open = []
    closed = []

    for _, row in open_df.iterrows():
        entry_time = pd.to_datetime(row['entry_time'])
        if datetime.now() - entry_time >= timedelta(hours=POSITION_DURATION_HOURS):
            symbol = row['symbol']
            try:
                price_now = get_latest_close_price(symbol)
            except Exception as e:
                print(f"[ERRORE] Errore nel recuperare il prezzo per {symbol}: {e}")
                still_open.append(row)
                continue

            entry_price = row['entry_price']
            side = row['side']
            budget = row['budget']

            if side == 'long':
                pnl = (price_now - entry_price) / entry_price
            elif side == 'short':
                pnl = (entry_price - price_now) / entry_price
            else:
                pnl = 0

            capital_gain = budget + (budget * pnl)

            print(f"[DEBUG] Posizione chiusa per {symbol}: PnL: {pnl * 100:.2f}% | Capitale restituito: {capital_gain}$")

            closed.append({
                'symbol': symbol,
                'side': side,
                'confidence': row['confidence'],
                'entry_time': row['entry_time'],
                'entry_price': entry_price,
                'exit_time': datetime.now(),
                'exit_price': price_now,
                'pnl_percent': pnl * 100,
                'capital_returned': capital_gain
            })

            capital_now = load_wallet()
            update_wallet(capital_now + capital_gain)
        else:
            still_open.append(row)

    pd.DataFrame(still_open).to_csv(OPEN_POSITIONS_FILE, index=False)

    if closed:
        if os.path.exists(CLOSED_POSITIONS_FILE):
            closed_df = pd.read_csv(CLOSED_POSITIONS_FILE)
            closed = pd.concat([closed_df, pd.DataFrame(closed)], ignore_index=True)
        else:
            closed = pd.DataFrame(closed)

        closed.to_csv(CLOSED_POSITIONS_FILE, index=False)
        print(f"[DEBUG] {len(closed)} posizioni chiuse e salvate.")
    else:
        print("[DEBUG] Nessuna posizione chiusa.")

# Funzione principale per eseguire il ciclo completo
def run():
    print("[DEBUG] Inizio ciclo di trading paper.")
    capital = load_wallet()
    close_positions()
    open_positions(capital)
    print("[DEBUG] Fine ciclo di trading paper.")

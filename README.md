# NeuralTrader V7 - Manuale Tecnico

**NeuralTrader V7** è un sistema avanzato di trading automatico basato su intelligenza artificiale, progettato per operare su coppie Futures di KuCoin. Il sistema è stato progettato per essere modulare, auto-adattivo e in costante apprendimento, perfetto anche per utenti non esperti di trading.

---

## 📚 Introduzione

NeuralTrader V7 è in grado di:

* Analizzare oltre 100 asset crypto ogni 2 ore.
* Predire l'andamento futuro (LONG, SHORT o NEUTRO).
* Imparare dai propri errori grazie al retraining intelligente.
* Valutare le performance in tempo reale.

Tutto questo avviene **in modo automatico**, con notifiche via Telegram e salvataggi continui dei dati.

---

## ⚙️ Componenti del Sistema

| Modulo                   | Funzione                                                      |
| ------------------------ | ------------------------------------------------------------- |
| `scanner.py`             | Estrae dati OHLC e indicatori per ogni asset.                 |
| `predictor_v7.py`        | Applica il modello Transformer per generare le predizioni.    |
| `real_data_collector.py` | Raccoglie i dati reali dopo la predizione per la valutazione. |
| `evaluator_v7.py`        | Confronta le predizioni con i dati reali e assegna punteggi.  |
| `retrainer_v7.py`        | Genera nuovi esempi di addestramento basati sui risultati.    |
| `trainer.py`             | Addestra da zero o riaddestra il modello Transformer.         |
| `daily_cycle_v7.py`      | Coordina tutte le fasi ogni 2 ore.                            |
| `telegram_notifier.py`   | Invia notifiche informative e di errore via Telegram.         |

---

## 🧠 Come funziona

1. **Scanning**: il bot raccoglie dati storici su ogni coppia crypto.
2. **Prediction**: il modello predice la direzione più probabile del prezzo.
3. **Real Data**: dopo 3 ore, vengono scaricati i prezzi reali per il confronto.
4. **Evaluation**: il sistema valuta se la predizione era corretta (KO/OK).
5. **Retraining**: i risultati vengono usati per migliorare il modello.

Tutto viene **loggato** in CSV e documentato.

---

## 🛠️ Setup & Requisiti

1. Installa Python 3.8+
2. Crea un ambiente virtuale e attivalo:

```bash
python -m venv .venv
source .venv/bin/activate  # oppure .venv\Scripts\activate su Windows
```

3. Installa i pacchetti:

```bash
pip install -r requirements.txt
```

4. Configura le API KuCoin (per `scanner.py`).
5. Inserisci le coppie da tracciare in `configs/pairs_to_track.txt`

---

## 🧪 Addestramento del modello

Se vuoi addestrare da zero:

```bash
python scripts/trainer.py data/dataset/training_memory_manual_1500.csv
```

Oppure lascia che il sistema si aggiorni automaticamente grazie al retrainer.

---

## 📬 Notifiche Telegram

* Ricevi messaggi a ogni ciclo: predizioni, performance, errori.
* Personalizza `telegram_notifier.py` con il tuo `BOT_TOKEN` e `CHAT_ID`.

Esempio:

```
📈 Top 10 Predizioni AI
• BTC-USDT: LONG (99.81%) ✅
• ETH-USDT: SHORT (98.76%) ❌

Totale corrette: 47/73 (64.38%)
```

---

## ✅ Modalità supportate

* **Paper Trading** (default): simula gli ordini con budget virtuale.
* **Modalità Live**: in sviluppo, esecuzione reale via API.

---

## 💡 Suggerimenti per l'uso commerciale

Il sistema è pronto per essere venduto anche a:

* Team di investimento che vogliono automatizzare l’analisi.
* Utenti inesperti grazie alla modalità automatica.
* Progetti crypto che vogliono integrare un modulo predittivo.

Puoi offrire:

* Versione cloud con scheduler.
* Interfaccia semplificata.
* Formazione inclusa.

---

## 🧾 Licenza e Brevettabilità

NeuralTrader V7 è un progetto **originale**, con logica di **reinforcement multi-temporale**, **dataset dinamico** e **autonomia decisionale**.
È **brevettabile** e pronto per essere distribuito in ambito professionale.

---

Made with ❤️ by Ayrton (aka NeuralBoss) & ChatGPT-4. Transformer nel cervello, candela nel cuore.

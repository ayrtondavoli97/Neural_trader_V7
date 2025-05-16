import os
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import joblib
from datetime import datetime

class TransformerClassifier(nn.Module):
    def __init__(self, input_dim, num_classes):
        super().__init__()
        self.embedding = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.1)
        )
        encoder_layer = nn.TransformerEncoderLayer(d_model=64, nhead=4, batch_first=True)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=2)
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, num_classes)
        )

    def forward(self, x):
        x = self.embedding(x)
        x = self.transformer(x)
        return self.classifier(x)

def main():
    MODEL_PATH = 'models/transformer_model.pt'
    SCALER_PATH = 'models/scaler.pkl'
    LABELENCODER_PATH = 'models/label_encoder.pkl'
    CSV_PATH = 'data/dataset/rsi_signals_filtered_latest.csv'

    PREDICTIONS_DIR = 'data/predictions/latest'
    HISTORICAL_DIR = 'data/predictions/historical'
    LATEST_DIR = 'data/predictions/latest_global'
    TOP_DIR = 'data/predictions/top'

    CONFIDENCE_THRESHOLD = 0.9
    TOP_N = 10

    df = pd.read_csv(CSV_PATH)

    features = [
        'price', 'rsi', 'macd', 'macd_signal', 'ema_trend',
        'bollinger_pos', 'momentum', 'volatility', 'volume_relative_%',
        'sentiment_score'
    ]

    if df[features].isnull().any().any():
        raise ValueError("❌ Dataset contiene NaN nelle feature. Fixa prima!")

    if not os.path.exists(SCALER_PATH) or not os.path.exists(LABELENCODER_PATH):
        raise FileNotFoundError("⚠️ File scaler o label encoder mancante. Allenalo prima con il trainer!")

    scaler = joblib.load(SCALER_PATH)
    label_encoder = joblib.load(LABELENCODER_PATH)

    X = scaler.transform(df[features].values)
    X = X.reshape(X.shape[0], 1, X.shape[1])

    model = TransformerClassifier(input_dim=X.shape[2], num_classes=len(label_encoder.classes_))
    model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))
    model.eval()

    with torch.no_grad():
        inputs = torch.tensor(X, dtype=torch.float32)
        outputs = model(inputs)
        probs = torch.softmax(outputs, dim=1).numpy()
        preds = np.argmax(probs, axis=1)
        confidences = np.max(probs, axis=1)

    pred_labels = label_encoder.inverse_transform(preds)

    df['prediction'] = pred_labels
    df['confidence'] = confidences
    df['timestamp'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    df['timeframe'] = '3h'

    os.makedirs(PREDICTIONS_DIR, exist_ok=True)
    os.makedirs(HISTORICAL_DIR, exist_ok=True)
    os.makedirs(LATEST_DIR, exist_ok=True)

    for _, row in df.iterrows():
        symbol = row['symbol']
        out_path = os.path.join(PREDICTIONS_DIR, f"{symbol}.csv")
        row.to_frame().T.to_csv(out_path, index=False)

    timestamp = df['timestamp'].iloc[0]
    historical_path = os.path.join(HISTORICAL_DIR, f"predictions_{timestamp.replace(':', '-')}.csv")
    latest_path = os.path.join(LATEST_DIR, "predictions_latest.csv")

    if not os.path.exists(historical_path):
        df.to_csv(historical_path, index=False)
        print(f"🗃️ Storico in {historical_path}")
    else:
        print(f"⚠️ File storico già esistente: {historical_path}")

    df.to_csv(latest_path, index=False)
    print(f"✅ Predizioni salvate in {PREDICTIONS_DIR}")
    print(f"🆕 Ultimo snapshot in {latest_path}")

    top_preds = df[df['confidence'] >= CONFIDENCE_THRESHOLD]
    top_preds = top_preds.sort_values(by='confidence', ascending=False).head(TOP_N)

    if not top_preds.empty:
        os.makedirs(TOP_DIR, exist_ok=True)
        out_top = os.path.join(TOP_DIR, f"top_predictions_{timestamp.replace(':', '-')}.csv")
        top_preds.to_csv(out_top, index=False)
        print(f"🏆 Top predizioni salvate in {out_top}")

# [TELEGRAM REMOVED]         from telegram_notifier import send_top_predictions
# [TELEGRAM REMOVED]         send_top_predictions(filepath=out_top)
    else:
        print("⚠️ Nessuna predizione ad alta confidenza.")

    print("[🔍 Predizioni totali]")
    print(df['prediction'].value_counts())

if __name__ == "__main__":
    main()
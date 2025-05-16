import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import os

# === CONFIG ===
CSV_PATH = 'data/dataset/training_memory_manual_1500.csv'
MODEL_PATH = 'models/transformer_model.pt'
BATCH_SIZE = 64
EPOCHS = 25
LR = 0.001

# === LOAD DATA ===
df = pd.read_csv(CSV_PATH)

# === PREPROCESS ===
features = [
    'close', 'rsi', 'macd', 'macd_signal', 'ema_trend',
    'bollinger_pos', 'momentum', 'volatility', 'volume_relative_%',
    'sentiment_score'
]

X = df[features].values
y = df['signal'].values

# Encode y
y_encoder = LabelEncoder()
y = y_encoder.fit_transform(y)

# Normalize features
scaler = StandardScaler()
X = scaler.fit_transform(X)

# Reshape for transformer (batch, seq, feature)
X = X.reshape(X.shape[0], 1, X.shape[1])

# === SPLIT ===
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.1, random_state=42)

# === DATASET ===
class TimeSeriesDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.long)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

train_ds = TimeSeriesDataset(X_train, y_train)
val_ds = TimeSeriesDataset(X_val, y_val)
train_dl = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
val_dl = DataLoader(val_ds, batch_size=BATCH_SIZE)

# === MODEL ===
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

model = TransformerClassifier(input_dim=len(features), num_classes=3)

# === TRAIN ===
best_val_loss = float('inf')
best_model_state = None
history = []
patience = 10
no_improve_epochs = 0
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=LR)
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=5, factor=0.5, verbose=True)

for epoch in range(EPOCHS):
    model.train()
    total_loss = 0
    for xb, yb in train_dl:
        xb, yb = xb.to(device), yb.to(device)
        optimizer.zero_grad()
        preds = model(xb)
        loss = criterion(preds, yb)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()

    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for xb, yb in val_dl:
            xb, yb = xb.to(device), yb.to(device)
            preds = model(xb)
            predicted = torch.argmax(preds, dim=1)
            correct += (predicted == yb).sum().item()
            total += yb.size(0)

    acc = correct / total * 100
    print(f"Epoch {epoch+1}/{EPOCHS} - Loss: {total_loss:.4f} - Val Accuracy: {acc:.2f}%")
    history.append({'epoch': epoch+1, 'loss': total_loss, 'val_acc': acc})
    

    if total_loss < best_val_loss:
        best_val_loss = total_loss
        best_model_state = model.state_dict()
        no_improve_epochs = 0
    else:
        no_improve_epochs += 1
        if no_improve_epochs >= patience:
            print("🛑 Early stopping triggered")
            break


# === SAVE ===
# Save best model only
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
torch.save(best_model_state, MODEL_PATH)
print(f"✅ Miglior modello salvato in {MODEL_PATH}")

# Save training history
pd.DataFrame(history).to_csv('models/training_log.csv', index=False)
print("📈 Log training salvato in models/training_log.csv")

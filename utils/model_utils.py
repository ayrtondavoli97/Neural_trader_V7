# Utility per modelli e salvataggi
import pandas as pd
df = pd.read_csv('data/dataset/training_memory_2025-05-11.csv')
print(df['signal'].value_counts(normalize=True))

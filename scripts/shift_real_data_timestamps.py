import pandas as pd

df_base = pd.read_csv("data/dataset/training_memory_long_short.csv")
df_ext = pd.read_csv("data/dataset/training_memory_extended.csv")

df_all = pd.concat([df_base, df_ext], ignore_index=True)
df_all.to_csv("data/dataset/training_memory_extended.csv", index=False)

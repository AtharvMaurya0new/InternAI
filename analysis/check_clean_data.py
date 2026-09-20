import pandas as pd

df = pd.read_csv(
    "data/recommendation_clean.csv",
    nrows=10000
)

print("Shape of sample:", df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nMissing values:")
print(df.isnull().sum())

print("\nRelevance score range:")
print("Minimum:", df["relevance_score"].min())
print("Maximum:", df["relevance_score"].max())

print("\nSample:")
print(df.head(5).to_string(index=False))
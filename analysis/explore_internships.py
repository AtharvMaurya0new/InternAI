import pandas as pd

df = pd.read_csv("data/internships_clean.csv")

print("Shape:", df.shape)

print("\n--- Internship Titles ---")
print(df["internship_title"].value_counts().head(20))

print("\n--- Locations ---")
print(df["location"].value_counts().head(30))

print("\n--- Durations ---")
print(df["duration"].value_counts())

print("\n--- Stipend Examples ---")
print(df["stipend"].value_counts().head(30))

print("\n--- Companies ---")
print(df["company_name"].nunique(), "unique companies")

print("\n--- Sample Data ---")
print(df.head(10).to_string(index=False))
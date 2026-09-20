import pandas as pd

df = pd.read_csv(
    "data/huge_job_recommendation_dataset.csv",
    nrows=10000
)

print("Shape:", df.shape)

print("\n--- Job Titles ---")
print(df["title"].value_counts().head(30))

print("\n--- Education ---")
print(df["education"].value_counts())

print("\n--- Experience ---")
print(df["experience"].value_counts())

print("\n--- Locations ---")
print(df["location"].value_counts().head(30))

print("\n--- User Locations ---")
print(df["user_location"].value_counts().head(30))

print("\n--- Relevance Score ---")
print(df["relevance_score"].describe())

print("\n--- Sample Skills Required ---")
print(df["skills_required"].head(10).to_string(index=False))

print("\n--- Sample User Skills ---")
print(df["user_skills"].head(10).to_string(index=False))

print("\n--- Sample Data ---")
print(df.head(5).to_string(index=False))
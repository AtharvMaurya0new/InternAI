import pandas as pd

df = pd.read_csv(
    "data/recommendation_clean.csv",
    usecols=[
        "title",
        "skills_required",
        "user_skills",
        "education",
        "experience",
        "relevance_score"
    ]
)

print("Rows:", len(df))

print("\n--- Relevance Distribution ---")
print(
    df["relevance_score"]
    .value_counts()
    .sort_index()
)

print("\n--- Average Relevance by Job Title ---")
print(
    df.groupby("title")["relevance_score"]
    .mean()
    .sort_values(ascending=False)
    .head(20)
)

print("\n--- High Relevance Examples ---")
high = df[df["relevance_score"] >= 0.75]

print(
    high[
        [
            "title",
            "skills_required",
            "user_skills",
            "education",
            "experience",
            "relevance_score"
        ]
    ].head(10).to_string(index=False)
)

print("\n--- Low Relevance Examples ---")
low = df[df["relevance_score"] <= 0.25]

print(
    low[
        [
            "title",
            "skills_required",
            "user_skills",
            "education",
            "experience",
            "relevance_score"
        ]
    ].head(10).to_string(index=False)
)
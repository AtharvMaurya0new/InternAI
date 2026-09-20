import pandas as pd

INPUT_FILE = "data/huge_job_recommendation_dataset.csv"
OUTPUT_FILE = "data/recommendation_clean.csv"

print("Loading recommendation dataset...")

df = pd.read_csv(INPUT_FILE)

print("Original shape:", df.shape)

# Remove completely duplicated rows
df = df.drop_duplicates()

# Clean column names
df.columns = df.columns.str.strip().str.lower()

# Clean text columns
text_columns = [
    "title",
    "description",
    "location",
    "skills_required",
    "education",
    "experience",
    "user_skills",
    "user_location"
]

for col in text_columns:
    df[col] = df[col].astype(str).str.strip()

# Remove rows missing important recommendation information
df = df.dropna(
    subset=[
        "title",
        "description",
        "skills_required",
        "user_skills",
        "relevance_score"
    ]
)

# Make sure relevance score is numeric
df["relevance_score"] = pd.to_numeric(
    df["relevance_score"],
    errors="coerce"
)

# Remove rows where relevance score could not be converted
df = df.dropna(subset=["relevance_score"])

# Keep relevance score between 0 and 1
df = df[
    (df["relevance_score"] >= 0) &
    (df["relevance_score"] <= 1)
]

print("Cleaned shape:", df.shape)

# Save as a NEW file
df.to_csv(OUTPUT_FILE, index=False)

print("Saved:", OUTPUT_FILE)
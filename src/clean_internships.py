import pandas as pd

# Load dataset
df = pd.read_csv("data/internship.csv")

print("Original shape:", df.shape)

# Remove duplicate rows
df = df.drop_duplicates()

# Clean column names
df.columns = df.columns.str.strip().str.lower()

# Remove extra spaces from text columns
text_columns = [
    "internship_title",
    "company_name",
    "location",
    "start_date",
    "duration",
    "stipend"
]

for col in text_columns:
    df[col] = df[col].astype(str).str.strip()

# Remove rows where important information is missing
df = df.dropna(
    subset=[
        "internship_title",
        "company_name",
        "location"
    ]
)

print("After cleaning:", df.shape)

# Save cleaned dataset
df.to_csv("data/internships_clean.csv", index=False)

print("Saved: data/internships_clean.csv")
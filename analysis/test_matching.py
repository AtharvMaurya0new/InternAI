import pandas as pd
import sys

# Allow Python to find files inside src/
sys.path.append("src")

from matching import calculate_match


# Load a small sample
df = pd.read_csv(
    "data/recommendation_clean.csv",
    nrows=100
)


# Test using the first 5 rows
for index, row in df.head(5).iterrows():

    result = calculate_match(
        row["skills_required"],
        row["user_skills"]
    )

    print("\n" + "=" * 60)

    print("Job:", row["title"])

    print("Required skills:")
    print(row["skills_required"])

    print("\nUser skills:")
    print(row["user_skills"])

    print("\nMatch score:", result["score"])

    print("Matched skills:")
    print(result["matched_skills"])

    print("Missing skills:")
    print(result["missing_skills"])

    print("Dataset relevance:", row["relevance_score"])
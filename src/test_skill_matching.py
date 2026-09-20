import pandas as pd


def get_skills(text):
    if pd.isna(text):
        return set()

    return {
        skill.strip().lower()
        for skill in str(text).split(";")
        if skill.strip()
    }


def skill_match(required, user):
    required_skills = get_skills(required)
    user_skills = get_skills(user)

    if not required_skills:
        return 0.0

    matched = required_skills.intersection(user_skills)

    return len(matched) / len(required_skills)


# Read only a sample for this test
df = pd.read_csv(
    "data/recommendation_clean.csv",
    nrows=10000
)

df["skill_match"] = df.apply(
    lambda row: skill_match(
        row["skills_required"],
        row["user_skills"]
    ),
    axis=1
)

print("Skill matching test completed.")

print("\n--- Examples ---")

print(
    df[
        [
            "title",
            "skills_required",
            "user_skills",
            "skill_match",
            "relevance_score"
        ]
    ].head(20).to_string(index=False)
)

print("\n--- Average Skill Match ---")
print(df["skill_match"].mean())

print("\n--- Average Relevance ---")
print(df["relevance_score"].mean())

print("\n--- Skill Match vs Relevance ---")

print(
    df[
        ["skill_match", "relevance_score"]
    ].corr()
)
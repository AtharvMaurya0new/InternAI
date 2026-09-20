import pandas as pd
import re


# ============================================================
# PATHS
# ============================================================

INPUT_PATH = "data/internships_clean.csv"
OUTPUT_PATH = "data/job_skill_mapping.csv"


# ============================================================
# LOAD ACTUAL INTERNSHIPS
# ============================================================

print("Loading internships...")

df = pd.read_csv(INPUT_PATH)

print("Internships loaded:", len(df))


# ============================================================
# CLEAN TITLE
# ============================================================

df["internship_title"] = (
    df["internship_title"]
    .fillna("")
    .astype(str)
    .str.strip()
)


# ============================================================
# SKILL KEYWORDS
# ============================================================

SKILL_RULES = {

    # Programming
    "python": [
        "python",
        "data science",
        "data analyst",
        "machine learning",
        "artificial intelligence",
        "ai",
        "automation"
    ],

    "java": [
        "java",
        "android",
        "backend"
    ],

    "javascript": [
        "javascript",
        "web development",
        "frontend",
        "full stack",
        "react",
        "node"
    ],

    "c++": [
        "c++",
        "embedded",
        "game development"
    ],

    "sql": [
        "data analyst",
        "data analysis",
        "database",
        "sql",
        "business analyst"
    ],

    # Data / AI
    "machine learning": [
        "machine learning",
        "ml",
        "artificial intelligence",
        "ai",
        "data science"
    ],

    "deep learning": [
        "deep learning",
        "neural network",
        "artificial intelligence",
        "ai"
    ],

    "nlp": [
        "nlp",
        "natural language",
        "language model",
        "artificial intelligence",
        "ai"
    ],

    "tensorflow": [
        "machine learning",
        "deep learning",
        "artificial intelligence",
        "ai"
    ],

    "pandas": [
        "data analyst",
        "data analysis",
        "data science",
        "python"
    ],

    "excel": [
        "data analyst",
        "business analyst",
        "finance",
        "accounting",
        "marketing"
    ],

    # Web
    "html": [
        "web",
        "frontend",
        "full stack",
        "website"
    ],

    "css": [
        "web",
        "frontend",
        "full stack",
        "website"
    ],

    "react": [
        "react",
        "frontend",
        "full stack",
        "web development"
    ],

    "node.js": [
        "node",
        "backend",
        "full stack"
    ],

    # Cloud / DevOps
    "git": [
        "software",
        "developer",
        "development",
        "web",
        "programming",
        "devops"
    ],

    "docker": [
        "devops",
        "cloud",
        "backend"
    ],

    "aws": [
        "cloud",
        "devops",
        "aws"
    ],

    "azure": [
        "cloud",
        "azure",
        "devops"
    ],

    # Design
    "figma": [
        "ui/ux",
        "ui ux",
        "ux",
        "user experience",
        "graphic design",
        "design"
    ],

    "ui/ux design": [
        "ui/ux",
        "ui ux",
        "ux",
        "user experience",
        "design"
    ],

    "graphic design": [
        "graphic design",
        "design",
        "creative"
    ],

    # Marketing
    "seo": [
        "seo",
        "search engine optimization"
    ],

    "digital marketing": [
        "digital marketing",
        "marketing",
        "social media"
    ],

    "social media marketing": [
        "social media",
        "digital marketing",
        "marketing"
    ],

    # Finance
    "accounting": [
        "accounting",
        "finance",
        "financial"
    ],

    "financial analysis": [
        "finance",
        "financial",
        "investment",
        "accounting"
    ]
}


# ============================================================
# FUNCTION TO FIND SKILLS
# ============================================================

def find_skills(title):

    title = title.lower()

    found_skills = []

    for skill, keywords in SKILL_RULES.items():

        for keyword in keywords:

            if keyword in title:
                found_skills.append(skill)
                break

    return sorted(set(found_skills))


# ============================================================
# CREATE SKILL MAPPING
# ============================================================

df["skills_required"] = df["internship_title"].apply(find_skills)


# ============================================================
# REMOVE DUPLICATE INTERNSHIP TITLES
# ============================================================

mapping = (
    df[
        [
            "internship_title",
            "skills_required"
        ]
    ]
    .drop_duplicates(subset=["internship_title"])
    .copy()
)


# ============================================================
# CONVERT LIST TO STRING
# ============================================================

mapping["skills_required"] = mapping["skills_required"].apply(
    lambda skills: ";".join(skills)
)


# ============================================================
# SAVE
# ============================================================

mapping.to_csv(
    OUTPUT_PATH,
    index=False
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print()
print("=" * 60)
print("SKILL MAPPING CREATED")
print("=" * 60)

print("Unique internship titles:", len(mapping))

print()
print("Sample mappings:")

print(
    mapping.head(20).to_string(index=False)
)

print()
print("Saved to:")
print(OUTPUT_PATH)

print("=" * 60)
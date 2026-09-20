import os
import re
import joblib
import numpy as np
import pandas as pd

from sentence_transformers import SentenceTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATA_DIR = os.path.join(BASE_DIR, "data")

DATA_FILE = os.path.join(
    DATA_DIR,
    "recommendation_clean.csv"
)

MODEL_FILE = os.path.join(
    DATA_DIR,
    "recommendation_model.pkl"
)


# ============================================================
# SETTINGS
# ============================================================

TRAINING_ROWS = 100000
BATCH_SIZE = 64
RANDOM_STATE = 42


# ============================================================
# START
# ============================================================

print("=" * 65)
print("INTERNSHIP RECOMMENDATION MODEL TRAINING")
print("=" * 65)


# ============================================================
# LOAD DATA
# ============================================================

print("\nLoading dataset...")

df = pd.read_csv(DATA_FILE)

print(f"Original rows: {len(df)}")


# ============================================================
# SAMPLE 100,000 REPRESENTATIVE ROWS
# ============================================================

if len(df) > TRAINING_ROWS:

    print(
        f"Selecting {TRAINING_ROWS:,} representative training rows..."
    )

    # Keep the distribution of relevance_score
    # instead of taking completely random rows.

    groups = []

    unique_scores = sorted(
        df["relevance_score"].dropna().unique()
    )

    rows_per_group = TRAINING_ROWS // len(unique_scores)

    remaining = TRAINING_ROWS

    for i, score in enumerate(unique_scores):

        group = df[
            df["relevance_score"] == score
        ]

        if i == len(unique_scores) - 1:

            sample_size = min(
                len(group),
                remaining
            )

        else:

            sample_size = min(
                len(group),
                rows_per_group
            )

        if sample_size > 0:

            groups.append(
                group.sample(
                    n=sample_size,
                    random_state=RANDOM_STATE
                )
            )

            remaining -= sample_size

    df = pd.concat(
        groups,
        ignore_index=True
    )

    # If rounding/group sizes left us below 100k,
    # fill the remaining rows randomly.

    if len(df) < TRAINING_ROWS:

        used_indices = set(df.index)

        remaining_df = df.sample(
            n=0
        )

        # Take additional rows from original dataset
        # using a fresh random sample.
        original_df = pd.read_csv(DATA_FILE)

        extra_needed = TRAINING_ROWS - len(df)

        extra = original_df.sample(
            n=extra_needed,
            random_state=RANDOM_STATE + 1
        )

        df = pd.concat(
            [df, extra],
            ignore_index=True
        )

    df = df.sample(
        frac=1,
        random_state=RANDOM_STATE
    ).reset_index(drop=True)


print(f"Training rows: {len(df)}")


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):

    if pd.isna(text):
        return ""

    text = str(text).lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# CREATE JOB TEXT
# ============================================================

print("\nCreating job texts...")

job_texts = (

    df["title"].fillna("").astype(str)
    + ". "
    + df["description"].fillna("").astype(str)
    + ". Location: "
    + df["location"].fillna("").astype(str)
    + ". Skills: "
    + df["skills_required"].fillna("").astype(str)

).map(clean_text)


# ============================================================
# CREATE STUDENT TEXT
# ============================================================

print("Creating student texts...")

student_texts = (

    "Skills: "
    + df["user_skills"].fillna("").astype(str)
    + ". Location: "
    + df["user_location"].fillna("").astype(str)

).map(clean_text)


# ============================================================
# LOAD SENTENCE TRANSFORMER
# ============================================================

print("\nLoading SentenceTransformer...")

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print("SentenceTransformer loaded.")


# ============================================================
# SEMANTIC SIMILARITY
# ============================================================

print("\nCreating semantic embeddings...")

semantic_scores = np.zeros(
    len(df),
    dtype=np.float32
)

total_batches = (
    len(df) + BATCH_SIZE - 1
) // BATCH_SIZE


for batch_number, start in enumerate(
    range(0, len(df), BATCH_SIZE),
    start=1
):

    end = min(
        start + BATCH_SIZE,
        len(df)
    )

    batch_jobs = job_texts.iloc[
        start:end
    ].tolist()

    batch_students = student_texts.iloc[
        start:end
    ].tolist()

    job_embeddings = embedding_model.encode(
        batch_jobs,
        batch_size=BATCH_SIZE,
        show_progress_bar=False,
        normalize_embeddings=True,
        convert_to_numpy=True
    )

    student_embeddings = embedding_model.encode(
        batch_students,
        batch_size=BATCH_SIZE,
        show_progress_bar=False,
        normalize_embeddings=True,
        convert_to_numpy=True
    )

    # Because embeddings are normalized,
    # dot product = cosine similarity.

    similarities = np.sum(
        job_embeddings * student_embeddings,
        axis=1
    )

    # Convert [-1, 1] to [0, 1]
    similarities = (
        similarities + 1
    ) / 2

    semantic_scores[
        start:end
    ] = similarities.astype(
        np.float32
    )

    if (
        batch_number % 100 == 0
        or batch_number == total_batches
    ):

        print(
            f"Processed "
            f"{end:,}/{len(df):,} rows "
            f"({end / len(df) * 100:.1f}%)"
        )


print("Semantic scores created.")


# ============================================================
# SKILL MATCH
# ============================================================

def get_skills(text):

    if pd.isna(text):
        return set()

    parts = re.split(
        r"[,;]",
        str(text).lower()
    )

    return {
        clean_text(skill)
        for skill in parts
        if clean_text(skill)
    }


print("\nCalculating skill matching...")

skill_matches = []

for user_skills, required_skills in zip(
    df["user_skills"],
    df["skills_required"]
):

    user_set = get_skills(
        user_skills
    )

    required_set = get_skills(
        required_skills
    )

    if not required_set:

        skill_matches.append(0.5)

    else:

        matched = (
            user_set & required_set
        )

        score = (
            len(matched)
            / len(required_set)
        )

        skill_matches.append(score)


skill_match = np.array(
    skill_matches,
    dtype=np.float32
)


# ============================================================
# DOMAIN MATCH
# ============================================================

print("Calculating domain matching...")


def domain_from_title(title):

    title = clean_text(title)

    # Simple domain keywords
    domains = {

        "data science": [
            "data",
            "analytics",
            "data science"
        ],

        "machine learning": [
            "machine learning",
            "ml"
        ],

        "web development": [
            "web",
            "frontend",
            "backend",
            "full stack"
        ],

        "software development": [
            "software",
            "developer",
            "development"
        ],

        "android": [
            "android"
        ],

        "ios": [
            "ios"
        ],

        "marketing": [
            "marketing",
            "digital marketing"
        ],

        "finance": [
            "finance",
            "accounting"
        ],

        "hr": [
            "hr",
            "human resources",
            "recruitment"
        ],

        "design": [
            "design",
            "graphic",
            "ui/ux"
        ]
    }

    for domain, keywords in domains.items():

        for keyword in keywords:

            if keyword in title:

                return domain

    return "other"


domain_match = []

for title, user_skills in zip(
    df["title"],
    df["user_skills"]
):

    job_domain = domain_from_title(
        title
    )

    user_text = clean_text(
        user_skills
    )

    if job_domain == "other":

        domain_match.append(0.5)

    elif any(
        keyword in user_text
        for keyword in job_domain.split()
    ):

        domain_match.append(1.0)

    else:

        domain_match.append(0.0)


domain_match = np.array(
    domain_match,
    dtype=np.float32
)


# ============================================================
# LOCATION MATCH
# ============================================================

print("Calculating location matching...")

location_match = []

for job_location, user_location in zip(
    df["location"],
    df["user_location"]
):

    job_location = clean_text(
        job_location
    )

    user_location = clean_text(
        user_location
    )

    if not user_location:

        location_match.append(0.5)

    elif not job_location:

        location_match.append(0.5)

    elif (
        user_location in job_location
        or job_location in user_location
    ):

        location_match.append(1.0)

    elif "remote" in job_location or "wfh" in job_location:

        location_match.append(1.0)

    else:

        location_match.append(0.0)


location_match = np.array(
    location_match,
    dtype=np.float32
)


# ============================================================
# DURATION AND STIPEND
# ============================================================
#
# The training dataset does not contain internship
# duration or stipend columns.
#
# Therefore these two features are neutral during training.
#
# The live recommendation engine calculates them separately.
# ============================================================

duration_match = np.full(
    len(df),
    0.5,
    dtype=np.float32
)

stipend_match = np.full(
    len(df),
    0.5,
    dtype=np.float32
)


# ============================================================
# CREATE FEATURE MATRIX
# ============================================================

print("\nCreating feature matrix...")

X = np.column_stack([

    semantic_scores,

    skill_match,

    domain_match,

    location_match,

    duration_match,

    stipend_match
])


y = df[
    "relevance_score"
].astype(
    np.float32
).values


print(
    f"Feature matrix shape: {X.shape}"
)


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,

    test_size=0.20,

    random_state=RANDOM_STATE
)


print(
    f"Training samples: {len(X_train):,}"
)

print(
    f"Testing samples: {len(X_test):,}"
)


# ============================================================
# TRAIN MODEL
# ============================================================

print("\nTraining HistGradientBoostingRegressor...")

model = HistGradientBoostingRegressor(

    max_iter=300,

    learning_rate=0.05,

    max_leaf_nodes=31,

    l2_regularization=0.1,

    random_state=RANDOM_STATE
)


model.fit(
    X_train,
    y_train
)


print("Model training completed.")


# ============================================================
# EVALUATION
# ============================================================

print("\nEvaluating model...")

predictions = model.predict(
    X_test
)

predictions = np.clip(
    predictions,
    0,
    1
)


mae = mean_absolute_error(
    y_test,
    predictions
)

rmse = np.sqrt(
    mean_squared_error(
        y_test,
        predictions
    )
)

r2 = r2_score(
    y_test,
    predictions
)


print("\n" + "=" * 65)
print("MODEL PERFORMANCE")
print("=" * 65)

print(
    f"MAE  : {mae:.4f}"
)

print(
    f"RMSE : {rmse:.4f}"
)

print(
    f"R²   : {r2:.4f}"
)


# ============================================================
# SAVE MODEL
# ============================================================

joblib.dump(
    model,
    MODEL_FILE
)


print("\n" + "=" * 65)

print(
    f"Model saved to:\n{MODEL_FILE}"
)

print("=" * 65)

print("\nTraining finished successfully.")
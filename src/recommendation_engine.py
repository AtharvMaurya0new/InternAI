import os
import re
import joblib
import numpy as np
import pandas as pd

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

INTERNSHIP_FILE = os.path.join(
    BASE_DIR,
    "data",
    "internships_clean.csv"
)

SKILL_MAPPING_FILE = os.path.join(
    BASE_DIR,
    "data",
    "job_skill_mapping.csv"
)

MODEL_FILE = os.path.join(
    BASE_DIR,
    "data",
    "recommendation_model.pkl"
)

EMBEDDING_FILE = os.path.join(
    BASE_DIR,
    "data",
    "internship_embeddings_v2.npy"
)

MODEL_NAME = "all-MiniLM-L6-v2"


# ============================================================
# BASIC TEXT CLEANING
# ============================================================

def clean_text(text):

    if text is None:
        return ""

    if pd.isna(text):
        return ""

    return re.sub(
        r"\s+",
        " ",
        str(text).lower().strip()
    )


# ============================================================
# SKILLS
# ============================================================

def get_skills(text):

    text = clean_text(text)

    if not text:
        return set()

    parts = re.split(
        r"[;,|]",
        text
    )

    skills = set()

    for part in parts:

        part = part.strip()

        if part:
            skills.add(part)

    return skills


def calculate_skill_match(
    required_skills,
    student_skills
):

    required = get_skills(
        required_skills
    )

    student = get_skills(
        student_skills
    )

    if not required:

        return 0.5, [], []

    matched = required.intersection(
        student
    )

    missing = required.difference(
        student
    )

    score = (
        len(matched)
        /
        len(required)
    )

    return (
        score,
        sorted(matched),
        sorted(missing)
    )


# ============================================================
# DOMAIN KEYWORDS
# ============================================================

DOMAIN_KEYWORDS = {

    "data science": [
        "data science",
        "data scientist",
        "data analyst",
        "analytics",
        "business intelligence",
        "machine learning",
        "python",
        "pandas",
        "numpy",
        "sql"
    ],

    "software development": [
        "software developer",
        "software development",
        "software engineer",
        "web developer",
        "web development",
        "backend",
        "frontend",
        "full stack",
        "java",
        "javascript",
        "react",
        "node",
        "spring"
    ],

    "artificial intelligence": [
        "artificial intelligence",
        "ai engineer",
        "machine learning",
        "deep learning",
        "nlp",
        "natural language processing",
        "computer vision"
    ],

    "cybersecurity": [
        "cybersecurity",
        "cyber security",
        "ethical hacking",
        "penetration testing",
        "network security",
        "information security"
    ],

    "ui ux design": [
        "ui/ux",
        "ui ux",
        "user interface",
        "user experience",
        "graphic design",
        "figma",
        "photoshop"
    ],

    "marketing": [
        "digital marketing",
        "marketing",
        "seo",
        "social media",
        "content marketing"
    ],

    "human resources": [
        "human resources",
        "hr",
        "recruitment",
        "talent acquisition"
    ],

    "sales": [
        "sales",
        "business development"
    ],

    "finance": [
        "finance",
        "financial analysis",
        "accounting",
        "investment",
        "banking"
    ]
}


def detect_domains(text):

    text = clean_text(text)

    detected = set()

    for domain, keywords in DOMAIN_KEYWORDS.items():

        for keyword in keywords:

            if keyword in text:

                detected.add(domain)

                break

    return detected


def calculate_domain_match(
    student_text,
    internship_text
):

    student_domains = detect_domains(
        student_text
    )

    internship_domains = detect_domains(
        internship_text
    )

    if not internship_domains:
        return 0.5

    if not student_domains:
        return 0.5

    matched = student_domains.intersection(
        internship_domains
    )

    return (
        len(matched)
        /
        len(internship_domains)
    )


# ============================================================
# LOCATION
# ============================================================

def calculate_location_match(
    preferred_location,
    internship_location
):

    preferred = clean_text(
        preferred_location
    )

    actual = clean_text(
        internship_location
    )

    if not preferred:
        return 0.5

    if not actual:
        return 0.0

    if "work from home" in actual:
        return 1.0

    if preferred == actual:
        return 1.0

    if preferred in actual:
        return 1.0

    if actual in preferred:
        return 1.0

    return 0.0


# ============================================================
# DURATION
# ============================================================

def extract_months(duration):

    if duration is None:
        return None

    if pd.isna(duration):
        return None

    text = clean_text(duration)

    month_match = re.search(
        r"(\d+(?:\.\d+)?)\s*month",
        text
    )

    if month_match:

        return float(
            month_match.group(1)
        )

    week_match = re.search(
        r"(\d+(?:\.\d+)?)\s*week",
        text
    )

    if week_match:

        return (
            float(
                week_match.group(1)
            )
            /
            4
        )

    return None


def calculate_duration_match(
    preferred_duration,
    internship_duration
):

    if not preferred_duration:
        return 0.5

    preferred = extract_months(
        preferred_duration
    )

    actual = extract_months(
        internship_duration
    )

    if preferred is None or actual is None:
        return 0.5

    difference = abs(
        preferred - actual
    )

    if difference == 0:
        return 1.0

    if difference <= 1:
        return 0.8

    if difference <= 2:
        return 0.5

    return 0.0


# ============================================================
# STIPEND
# ============================================================

def extract_stipend(stipend):

    if stipend is None:
        return 0.0

    if pd.isna(stipend):
        return 0.0

    text = clean_text(stipend)

    if (
        "unpaid" in text
        or
        "no stipend" in text
    ):
        return 0.0

    numbers = re.findall(
        r"\d[\d,]*",
        text
    )

    values = []

    for number in numbers:

        number = number.replace(
            ",",
            ""
        )

        try:

            values.append(
                float(number)
            )

        except ValueError:

            pass

    if not values:
        return 0.0

    return sum(values) / len(values)


def calculate_stipend_match(
    preferred_stipend,
    internship_stipend
):

    if preferred_stipend is None:
        return 0.5

    try:

        preferred = float(
            preferred_stipend
        )

    except (
        ValueError,
        TypeError
    ):

        return 0.5

    if preferred <= 0:
        return 0.5

    actual = extract_stipend(
        internship_stipend
    )

    if actual >= preferred:
        return 1.0

    return max(
        0.0,
        min(
            actual / preferred,
            1.0
        )
    )


# ============================================================
# STUDENT TEXT
# ============================================================

def create_student_text(student):

    return " ".join([

        clean_text(
            student.get(
                "branch",
                ""
            )
        ),

        clean_text(
            student.get(
                "education",
                ""
            )
        ),

        clean_text(
            student.get(
                "skills",
                ""
            )
        ),

        clean_text(
            student.get(
                "projects",
                ""
            )
        ),

        clean_text(
            student.get(
                "certifications",
                ""
            )
        ),

        clean_text(
            student.get(
                "preferred_domain",
                ""
            )
        ),

        clean_text(
            student.get(
                "preferred_location",
                ""
            )
        )

    ])


# ============================================================
# INTERNSHIP TEXT
# ============================================================

def create_internship_text(row):

    return " ".join([

        clean_text(
            row.get(
                "internship_title",
                ""
            )
        ),

        clean_text(
            row.get(
                "company_name",
                ""
            )
        ),

        clean_text(
            row.get(
                "location",
                ""
            )
        ),

        clean_text(
            row.get(
                "duration",
                ""
            )
        ),

        clean_text(
            row.get(
                "stipend",
                ""
            )
        )

    ])


# ============================================================
# RECOMMENDATION ENGINE
# ============================================================

class RecommendationEngine:

    def __init__(self):

        print()
        print("=" * 60)
        print("INITIALIZING INTERN AI ENGINE")
        print("=" * 60)


        # ----------------------------------------------------
        # LOAD INTERNSHIPS
        # ----------------------------------------------------

        print(
            "Loading internships..."
        )

        self.internships = pd.read_csv(
            INTERNSHIP_FILE
        )

        print(
            f"Internships loaded: "
            f"{len(self.internships)}"
        )


        # ----------------------------------------------------
        # LOAD SKILL MAPPING
        # ----------------------------------------------------

        print(
            "Loading skill mappings..."
        )

        self.skill_mapping = {}

        if os.path.exists(
            SKILL_MAPPING_FILE
        ):

            mapping_df = pd.read_csv(
                SKILL_MAPPING_FILE
            )

            for _, row in mapping_df.iterrows():

                title = clean_text(
                    row.get(
                        "internship_title",
                        ""
                    )
                )

                skills = row.get(
                    "skills_required",
                    ""
                )

                if title:

                    self.skill_mapping[
                        title
                    ] = str(skills)

            print(
                "Skill mappings loaded: "
                f"{len(self.skill_mapping)}"
            )

        else:

            print(
                "WARNING: skill mapping file not found."
            )


        # ----------------------------------------------------
        # LOAD SENTENCE TRANSFORMER
        # ----------------------------------------------------

        print(
            "Loading SentenceTransformer..."
        )

        self.encoder = SentenceTransformer(
            MODEL_NAME
        )

        print(
            "SentenceTransformer loaded."
        )


        # ----------------------------------------------------
        # CREATE INTERNSHIP TEXT
        # ----------------------------------------------------

        self.internship_texts = []

        for _, row in self.internships.iterrows():

            self.internship_texts.append(
                create_internship_text(row)
            )


        # ----------------------------------------------------
        # LOAD EMBEDDINGS
        # ----------------------------------------------------

        print(
            "Loading saved embeddings..."
        )

        if os.path.exists(
            EMBEDDING_FILE
        ):

            embeddings = np.load(
                EMBEDDING_FILE
            )

            if len(embeddings) == len(
                self.internships
            ):

                self.internship_embeddings = (
                    embeddings
                )

                norms = np.linalg.norm(
                    self.internship_embeddings,
                    axis=1,
                    keepdims=True
                )

                norms[
                    norms == 0
                ] = 1

                self.internship_embeddings = (
                    self.internship_embeddings
                    /
                    norms
                )

                print(
                    "Saved embeddings loaded: "
                    f"{self.internship_embeddings.shape}"
                )

            else:

                print(
                    "Embedding count mismatch."
                )

                print(
                    "Creating embeddings again..."
                )

                self.internship_embeddings = (
                    self.encoder.encode(
                        self.internship_texts,
                        show_progress_bar=True,
                        normalize_embeddings=True,
                        batch_size=64
                    )
                )

        else:

            print(
                "Embeddings file not found."
            )

            print(
                "Creating embeddings..."
            )

            self.internship_embeddings = (
                self.encoder.encode(
                    self.internship_texts,
                    show_progress_bar=True,
                    normalize_embeddings=True,
                    batch_size=64
                )
            )


        # ----------------------------------------------------
        # LOAD ML MODEL
        #
        # IMPORTANT:
        # Your recommendation_model.pkl is loaded
        # using joblib, NOT pickle.
        # ----------------------------------------------------

        print(
            "Loading ML relevance model..."
        )

        if os.path.exists(
            MODEL_FILE
        ):

            self.ml_model = joblib.load(
                MODEL_FILE
            )

            print(
                "ML relevance model loaded."
            )

        else:

            self.ml_model = None

            print(
                "WARNING: ML model not found."
            )


        print()
        print(
            "=" * 60
        )
        print(
            "INTERN AI ENGINE READY"
        )
        print(
            "=" * 60
        )
        print()


    # ========================================================
    # GET REQUIRED SKILLS
    # ========================================================

    def get_required_skills(
        self,
        internship_title
    ):

        title = clean_text(
            internship_title
        )

        if title in self.skill_mapping:

            return self.skill_mapping[
                title
            ]

        for mapped_title, skills in (
            self.skill_mapping.items()
        ):

            if (
                mapped_title in title
                or
                title in mapped_title
            ):

                return skills

        return ""


    # ========================================================
    # SEARCH FILTER
    # ========================================================

    def search_match(
        self,
        row,
        query,
        required_skills
    ):

        query = clean_text(query)

        if not query:
            return True

        searchable_text = " ".join([

            clean_text(
                row.get(
                    "internship_title",
                    ""
                )
            ),

            clean_text(
                row.get(
                    "company_name",
                    ""
                )
            ),

            clean_text(
                row.get(
                    "location",
                    ""
                )
            ),

            clean_text(
                row.get(
                    "duration",
                    ""
                )
            ),

            clean_text(
                row.get(
                    "stipend",
                    ""
                )
            ),

            clean_text(
                required_skills
            )

        ])

        if query in searchable_text:
            return True

        words = [
            word
            for word in re.split(
                r"\s+",
                query
            )
            if word
        ]

        if not words:
            return False

        return all(
            word in searchable_text
            for word in words
        )


    # ========================================================
    # LOCATION FILTER
    # ========================================================

    def location_filter_match(
        self,
        internship_location,
        selected_location,
        include_remote=True
    ):

        selected = clean_text(
            selected_location
        )

        actual = clean_text(
            internship_location
        )

        if (
            not selected
            or
            selected in [
                "all",
                "all locations",
                "any"
            ]
        ):

            return True

        if (
            include_remote
            and
            "work from home" in actual
        ):

            return True

        if selected == actual:
            return True

        if selected in actual:
            return True

        if actual in selected:
            return True

        return False


    # ========================================================
    # DOMAIN FILTER
    # ========================================================

    def domain_filter_match(
        self,
        row,
        selected_domain,
        required_skills
    ):

        selected = clean_text(
            selected_domain
        )

        if (
            not selected
            or
            selected in [
                "all",
                "all domains",
                "any"
            ]
        ):

            return True

        internship_text = " ".join([

            clean_text(
                row.get(
                    "internship_title",
                    ""
                )
            ),

            clean_text(
                row.get(
                    "company_name",
                    ""
                )
            ),

            clean_text(
                required_skills
            )

        ])

        selected_domains = detect_domains(
            selected
        )

        internship_domains = detect_domains(
            internship_text
        )

        if not selected_domains:

            return (
                selected
                in
                internship_text
            )

        return bool(
            selected_domains.intersection(
                internship_domains
            )
        )


    # ========================================================
    # MAIN RECOMMENDATION FUNCTION
    # ========================================================

    def recommend(
        self,
        student,
        top_n=10,
        search_query="",
        selected_domain="",
        selected_location="",
        include_remote=True,
        min_stipend=None,
        preferred_duration=None
    ):

        print()
        print("=" * 60)
        print("NEW RECOMMENDATION REQUEST")
        print("=" * 60)

        print(
            "Student skills:",
            student.get(
                "skills",
                ""
            )
        )

        print(
            "Student domain:",
            student.get(
                "preferred_domain",
                ""
            )
        )

        print(
            "Selected location:",
            selected_location
            or
            student.get(
                "preferred_location",
                ""
            )
        )

        print(
            "Search:",
            search_query
            or
            "None"
        )


        # ----------------------------------------------------
        # PREFERENCES
        # ----------------------------------------------------

        location = (
            selected_location
            or
            student.get(
                "preferred_location",
                ""
            )
        )

        domain = (
            selected_domain
            or
            student.get(
                "preferred_domain",
                ""
            )
        )

        duration = (
            preferred_duration
            or
            student.get(
                "preferred_duration",
                ""
            )
        )

        if min_stipend is None:

            min_stipend = student.get(
                "preferred_stipend"
            )

        if min_stipend is None:

            min_stipend = student.get(
                "expected_stipend"
            )


        # ----------------------------------------------------
        # STUDENT EMBEDDING
        # ----------------------------------------------------

        student_text = create_student_text(
            student
        )

        student_embedding = (
            self.encoder.encode(
                [student_text],
                normalize_embeddings=True
            )
        )


        # ----------------------------------------------------
        # FILTER ALL 6449 INTERNSHIPS
        # ----------------------------------------------------

        candidate_indices = []

        for index, row in (
            self.internships.iterrows()
        ):

            title = row.get(
                "internship_title",
                ""
            )

            required_skills = (
                self.get_required_skills(
                    title
                )
            )


            # SEARCH

            if not self.search_match(
                row,
                search_query,
                required_skills
            ):

                continue


            # LOCATION

            if not self.location_filter_match(
                row.get(
                    "location",
                    ""
                ),
                location,
                include_remote
            ):

                continue


            # DOMAIN

            if not self.domain_filter_match(
                row,
                domain,
                required_skills
            ):

                continue


            # DURATION

            if duration:

                duration_score = (
                    calculate_duration_match(
                        duration,
                        row.get(
                            "duration",
                            ""
                        )
                    )
                )

                if duration_score == 0:

                    continue


            # MINIMUM STIPEND

            if min_stipend is not None:

                try:

                    minimum = float(
                        min_stipend
                    )

                except (
                    ValueError,
                    TypeError
                ):

                    minimum = 0

                if minimum > 0:

                    actual_stipend = (
                        extract_stipend(
                            row.get(
                                "stipend",
                                ""
                            )
                        )
                    )

                    if actual_stipend < minimum:

                        continue


            candidate_indices.append(
                index
            )


        print(
            "Candidates after filters:",
            len(candidate_indices)
        )


        # ----------------------------------------------------
        # NO RESULTS
        # ----------------------------------------------------

        if not candidate_indices:

            print(
                "No internships matched."
            )

            return []


        # ----------------------------------------------------
        # SEMANTIC SIMILARITY
        # ----------------------------------------------------

        candidate_embeddings = (
            self.internship_embeddings[
                candidate_indices
            ]
        )

        semantic_scores = (
            cosine_similarity(
                student_embedding,
                candidate_embeddings
            )[0]
        )


        # ----------------------------------------------------
        # SCORE CANDIDATES
        # ----------------------------------------------------

        results = []

        for position, index in enumerate(
            candidate_indices
        ):

            row = self.internships.iloc[
                index
            ]

            title = row.get(
                "internship_title",
                ""
            )


            # SEMANTIC

            semantic_score = float(
                semantic_scores[position]
            )


            # REQUIRED SKILLS

            required_skills = (
                self.get_required_skills(
                    title
                )
            )


            # SKILL MATCH

            (
                skill_score,
                matched_skills,
                missing_skills
            ) = calculate_skill_match(
                required_skills,
                student.get(
                    "skills",
                    ""
                )
            )


            # DOMAIN

            internship_text = " ".join([

                clean_text(title),

                clean_text(
                    row.get(
                        "company_name",
                        ""
                    )
                ),

                clean_text(
                    required_skills
                )

            ])

            domain_score = (
                calculate_domain_match(
                    student_text,
                    internship_text
                )
            )


            # LOCATION

            location_score = (
                calculate_location_match(
                    location,
                    row.get(
                        "location",
                        ""
                    )
                )
            )


            # DURATION

            duration_score = (
                calculate_duration_match(
                    duration,
                    row.get(
                        "duration",
                        ""
                    )
                )
            )


            # STIPEND

            stipend_score = (
                calculate_stipend_match(
                    min_stipend,
                    row.get(
                        "stipend",
                        ""
                    )
                )
            )


            # ------------------------------------------------
            # ML MODEL
            # ------------------------------------------------

            ml_relevance = 0.5

            if self.ml_model is not None:

                features = np.array([[

                    semantic_score,

                    skill_score,

                    domain_score,

                    location_score,

                    duration_score,

                    stipend_score

                ]])

                try:

                    ml_relevance = float(
                        self.ml_model.predict(
                            features
                        )[0]
                    )

                    ml_relevance = max(
                        0.0,
                        min(
                            1.0,
                            ml_relevance
                        )
                    )

                except Exception as error:

                    print(
                        "ML prediction error:",
                        error
                    )

                    ml_relevance = 0.5


            # ------------------------------------------------
            # FINAL SCORE
            # ------------------------------------------------

            final_score = (

                semantic_score * 0.30

                +

                skill_score * 0.25

                +

                domain_score * 0.15

                +

                location_score * 0.10

                +

                duration_score * 0.05

                +

                stipend_score * 0.05

                +

                ml_relevance * 0.10

            )

            final_score = max(
                0.0,
                min(
                    1.0,
                    final_score
                )
            )


            # ------------------------------------------------
            # RESULT
            # ------------------------------------------------

            results.append({

                "internship_title":
                    str(title),

                "company_name":
                    str(
                        row.get(
                            "company_name",
                            ""
                        )
                    ),

                "location":
                    str(
                        row.get(
                            "location",
                            ""
                        )
                    ),

                "duration":
                    str(
                        row.get(
                            "duration",
                            ""
                        )
                    ),

                "stipend":
                    str(
                        row.get(
                            "stipend",
                            ""
                        )
                    ),

                "skills_required":
                    str(
                        required_skills
                    ),

                "matched_skills":
                    matched_skills,

                "missing_skills":
                    missing_skills,

                "match_score":
                    round(
                        final_score,
                        4
                    ),

                "match_percentage":
                    round(
                        final_score * 100,
                        2
                    ),

                "semantic_score":
                    round(
                        semantic_score,
                        4
                    ),

                "skill_score":
                    round(
                        skill_score,
                        4
                    ),

                "domain_score":
                    round(
                        domain_score,
                        4
                    ),

                "location_score":
                    round(
                        location_score,
                        4
                    ),

                "duration_score":
                    round(
                        duration_score,
                        4
                    ),

                "stipend_score":
                    round(
                        stipend_score,
                        4
                    ),

                "ml_relevance":
                    round(
                        ml_relevance,
                        4
                    )

            })


        # ----------------------------------------------------
        # SORT
        # ----------------------------------------------------

        results.sort(
            key=lambda item:
                item["match_score"],
            reverse=True
        )


        final_results = results[
            :top_n
        ]


        print()
        print(
            "Final recommendations:",
            len(final_results)
        )

        for number, item in enumerate(
            final_results,
            start=1
        ):

            print(
                f"{number}. "
                f"{item['internship_title']} | "
                f"{item['location']} | "
                f"{item['match_percentage']}%"
            )

        print(
            "=" * 60
        )


        return final_results


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    engine = RecommendationEngine()


    student = {

        "skills":
            "python, machine learning, pandas, numpy, scikit-learn",

        "projects":
            "machine learning project, data analysis project",

        "certifications":
            "machine learning certification",

        "branch":
            "CSE AI ML",

        "education":
            "BTech",

        "experience":
            "0",

        "preferred_domain":
            "Data Science",

        "preferred_location":
            "Hyderabad",

        "preferred_duration":
            "3 months",

        "preferred_stipend":
            15000

    }


    recommendations = engine.recommend(
        student,
        top_n=10
    )


    print()
    print("=" * 60)
    print("TEST RECOMMENDATIONS")
    print("=" * 60)


    for i, item in enumerate(
        recommendations,
        start=1
    ):

        print()
        print(
            f"{i}. {item['internship_title']}"
        )

        print(
            "Company:",
            item["company_name"]
        )

        print(
            "Location:",
            item["location"]
        )

        print(
            "Duration:",
            item["duration"]
        )

        print(
            "Stipend:",
            item["stipend"]
        )

        print(
            "Required skills:",
            item["skills_required"]
        )

        print(
            "Matched skills:",
            item["matched_skills"]
        )

        print(
            "Missing skills:",
            item["missing_skills"]
        )

        print(
            "Match:",
            item["match_percentage"],
            "%"
        )

        print(
            "ML relevance:",
            item["ml_relevance"]
        )
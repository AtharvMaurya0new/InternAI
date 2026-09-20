import pandas as pd


def get_skills(text):
    """
    Convert a semicolon-separated skill string
    into a set of lowercase skills.
    """

    if pd.isna(text):
        return set()

    return {
        skill.strip().lower()
        for skill in str(text).split(";")
        if skill.strip()
    }


def calculate_skill_match(required_skills, user_skills):
    """
    Calculate how many required skills
    are present in the user's skills.
    """

    required = get_skills(required_skills)
    user = get_skills(user_skills)

    if not required:
        return 0.0

    matched = required.intersection(user)

    return len(matched) / len(required)


def calculate_match(required_skills, user_skills):
    """
    Return detailed skill matching information.
    """

    required = get_skills(required_skills)
    user = get_skills(user_skills)

    if not required:
        return {
            "score": 0.0,
            "matched_skills": [],
            "missing_skills": []
        }

    matched = required.intersection(user)
    missing = required - user

    score = len(matched) / len(required)

    return {
        "score": score,
        "matched_skills": sorted(matched),
        "missing_skills": sorted(missing)
    }
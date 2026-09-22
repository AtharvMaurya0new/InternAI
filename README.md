# InternAI 🤖

### AI-Powered Internship Recommendation System

InternAI is an AI-powered internship recommendation platform designed to help students discover relevant internship opportunities based on their skills, preferred domain, location, duration, stipend, and other preferences.

The system combines semantic similarity, skill matching, domain matching, location matching, duration preferences, and stipend preferences to generate personalized internship recommendations.

## 🚀 Live Demo

[Visit InternAI](YOUR_LIVE_DEMO_LINK)

## 📌 Features

- 🤖 AI-powered internship recommendations
- 🧠 Semantic similarity using Sentence Transformers
- 💡 Skill-based matching
- 🎯 Domain-based filtering
- 📍 Location-based filtering
- 🏠 Remote internship support
- 💰 Minimum stipend filtering
- ⏱️ Internship duration filtering
- 🔎 Search by role, skill, or company
- ❤️ Save internships
- 👤 Student profile management
- ⚡ Real-time recommendation generation
- 🌐 Fully deployed web application

## 🧠 How InternAI Works

The recommendation system combines multiple matching signals:

1. Semantic similarity
2. Skill matching
3. Domain matching
4. Location matching
5. Duration matching
6. Stipend matching

These features are passed to a trained machine-learning model which generates a relevance score for internship recommendations.

## 🤖 Machine Learning

### Semantic Model

InternAI uses:

- Sentence Transformers
- `all-MiniLM-L6-v2`
- 384-dimensional embeddings
- Cosine/semantic similarity

The internship dataset is converted into embeddings so that student profiles and internship descriptions can be compared based on meaning rather than only exact keywords.

### Recommendation Model

The final recommendation model is a:

**HistGradientBoostingRegressor**

It uses six main features:

```text
semantic_score
skill_match
domain_match
location_match
duration_match
stipend_match

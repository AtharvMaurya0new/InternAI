from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np

from src.recommendation_engine import RecommendationEngine



# ============================================================
# CREATE FLASK APP
# ============================================================

app = Flask(__name__)

CORS(app)


# ============================================================
# LOAD ML ENGINE ONCE
# ============================================================

print()
print("=" * 60)
print("LOADING INTERN AI RECOMMENDATION ENGINE")
print("=" * 60)

engine = RecommendationEngine()

print()
print("=" * 60)
print("BACKEND + ML ENGINE READY")
print("=" * 60)
print()


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route(
    "/api/health",
    methods=["GET"]
)
def health():

    return jsonify({

        "success": True,

        "message":
            "InternAI backend is running",

        "ml_engine":
            True

    })


# ============================================================
# RECOMMENDATION API
# ============================================================

@app.route(
    "/api/recommend",
    methods=["POST"]
)
def recommend():

    try:

        # ----------------------------------------------------
        # RECEIVE DATA FROM WEBSITE
        # ----------------------------------------------------

        data = request.get_json(
            silent=True
        )


        if not data:

            return jsonify({

                "success": False,

                "error":
                    "No profile data received"

            }), 400


        print()
        print("=" * 60)
        print("NEW WEBSITE RECOMMENDATION REQUEST")
        print("=" * 60)

        print(
            "Received profile:"
        )

        print(data)


        # ----------------------------------------------------
        # PROFILE
        # ----------------------------------------------------

        student = {

            "name":
                data.get(
                    "name",
                    ""
                ),

            "email":
                data.get(
                    "email",
                    ""
                ),

            "education":
                data.get(
                    "education",
                    ""
                ),

            "branch":
                data.get(
                    "branch",
                    ""
                ),

            "experience":
                data.get(
                    "experience",
                    "0"
                ),

            "skills":
                data.get(
                    "skills",
                    ""
                ),

            "projects":
                data.get(
                    "projects",
                    ""
                ),

            "certifications":
                data.get(
                    "certifications",
                    ""
                ),

            "preferred_domain":
                data.get(
                    "preferred_domain",
                    ""
                ),

            "preferred_location":
                data.get(
                    "preferred_location",
                    ""
                ),

            "preferred_duration":
                data.get(
                    "preferred_duration",
                    ""
                ),

            "preferred_stipend":
                data.get(
                    "preferred_stipend",
                    0
                )

        }


        # ----------------------------------------------------
        # WEBSITE FILTERS
        # ----------------------------------------------------

        search_query = data.get(
            "search_query",
            ""
        )

        selected_domain = data.get(
            "selected_domain",
            ""
        )

        selected_location = data.get(
            "selected_location",
            ""
        )

        include_remote = data.get(
            "include_remote",
            True
        )

        min_stipend = data.get(
            "min_stipend",
            None
        )

        preferred_duration = data.get(
            "preferred_duration",
            ""
        )

        top_n = data.get(
            "top_n",
            10
        )


        # ----------------------------------------------------
        # CONVERT VALUES SAFELY
        # ----------------------------------------------------

        try:

            top_n = int(
                top_n
            )

        except (
            ValueError,
            TypeError
        ):

            top_n = 10


        try:

            if min_stipend is not None:

                min_stipend = float(
                    min_stipend
                )

        except (
            ValueError,
            TypeError
        ):

            min_stipend = None


        # ----------------------------------------------------
        # PRINT ACTIVE FILTERS
        # ----------------------------------------------------

        print()
        print(
            "ACTIVE WEBSITE FILTERS"
        )

        print(
            "Search:",
            search_query
        )

        print(
            "Domain:",
            selected_domain
        )

        print(
            "Location:",
            selected_location
        )

        print(
            "Remote:",
            include_remote
        )

        print(
            "Minimum stipend:",
            min_stipend
        )

        print(
            "Duration:",
            preferred_duration
        )


        # ----------------------------------------------------
        # CALL REAL ML ENGINE
        # ----------------------------------------------------

        recommendations = engine.recommend(

            student=student,

            top_n=top_n,

            search_query=search_query,

            selected_domain=selected_domain,

            selected_location=selected_location,

            include_remote=include_remote,

            min_stipend=min_stipend,

            preferred_duration=preferred_duration

        )


        # ----------------------------------------------------
        # MAKE JSON SAFE
        # ----------------------------------------------------

        clean_recommendations = []


        for item in recommendations:

            clean_item = {}


            for key, value in item.items():

                # numpy scalar

                if hasattr(
                    value,
                    "item"
                ):

                    value = value.item()


                # numpy array

                elif isinstance(
                    value,
                    np.ndarray
                ):

                    value = value.tolist()


                # set

                elif isinstance(
                    value,
                    set
                ):

                    value = list(
                        value
                    )


                clean_item[key] = value


            clean_recommendations.append(
                clean_item
            )


        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        print()
        print(
            "Recommendations generated:",
            len(
                clean_recommendations
            )
        )


        print("=" * 60)


        return jsonify({

            "success": True,

            "count":
                len(
                    clean_recommendations
                ),

            "recommendations":
                clean_recommendations

        })


    except Exception as error:

        print()
        print("=" * 60)
        print("BACKEND ERROR")
        print("=" * 60)

        print(
            repr(error)
        )

        return jsonify({

            "success": False,

            "error":
                str(error)

        }), 500


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("             INTERN AI BACKEND")
    print("=" * 60)

    print()
    print(
        "Backend:"
    )

    print(
        "http://127.0.0.1:5000"
    )

    print()
    print(
        "Health check:"
    )

    print(
        "http://127.0.0.1:5000/api/health"
    )

    print()
    print(
        "Recommendation API:"
    )

    print(
        "http://127.0.0.1:5000/api/recommend"
    )

    print()
    print(
        "Waiting for website requests..."
    )

    print()


    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True

    )
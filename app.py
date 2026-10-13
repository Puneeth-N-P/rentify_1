from pathlib import Path
import random

import joblib
import pandas as pd
from flask import Flask, render_template, request


# --------------------------------------------------
# 1. PROJECT CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / "dataset"
MODEL_PATH = BASE_DIR / "model" / "rent_model.pkl"
HOUSES_PATH = DATASET_DIR / "houses_7500.csv"

app = Flask(__name__)


# --------------------------------------------------
# 2. LOAD HOUSE DATASET
# --------------------------------------------------

def load_houses():
    """Load the property dataset safely."""

    if not HOUSES_PATH.exists():
        print(f"House dataset not found: {HOUSES_PATH}")
        return pd.DataFrame()

    try:
        df = pd.read_csv(HOUSES_PATH)
        df.columns = df.columns.str.strip()

        # Normalize text columns for reliable matching
        for col in ["state", "district", "location"]:
            if col in df.columns:
                df[col] = (
                    df[col]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                )

        # Normalize numeric columns
        for col in ["bhk", "rent", "bathrooms"]:
            if col in df.columns:
                df[col] = pd.to_numeric(
                    df[col], errors="coerce"
                )

        return df

    except Exception as exc:
        print(f"Error reading house dataset: {exc}")
        return pd.DataFrame()


# --------------------------------------------------
# 3. RECOMMENDATION ENGINE
# --------------------------------------------------

def recommend_houses(state, district, location, bhk, prediction):
    """
    Prioritize:
    1. Exact state, district, location and BHK.
    2. Same state and district with the requested BHK.
    3. Same state with the requested BHK.
    4. Other properties with the requested BHK.
    5. Closest available BHK if no properties match.
    """

    df = load_houses()

    if df.empty:
        return []

    required = {
        "state", "district", "location", "bhk", "rent"
    }

    if not required.issubset(df.columns):
        print("Missing required columns in houses_7500.csv")
        return []

    df = df.dropna(subset=["bhk", "rent"]).copy()

    if df.empty:
        return []

    # Case-insensitive matching
    for col in ["state", "district", "location"]:
        df[col + "_key"] = (
            df[col].fillna("").astype(str).str.strip().str.casefold()
        )

    state_key = state.strip().casefold()
    district_key = district.strip().casefold()
    location_key = location.strip().casefold()

    # Calculate match scores
    df["match_score"] = 0

    df.loc[
        df["state_key"] == state_key, "match_score"
    ] += 30

    df.loc[
        df["district_key"] == district_key, "match_score"
    ] += 40

    df.loc[
        df["location_key"] == location_key, "match_score"
    ] += 100

    # Strongly prefer the requested BHK
    df["bhk_difference"] = (df["bhk"] - bhk).abs()

    # Prefer houses close to the model's predicted rent
    df["rent_difference"] = (df["rent"] - prediction).abs()

    # Filter progressively to avoid an empty result when possible
    candidates = df[df["bhk"] == bhk].copy()

    if not candidates.empty:
        exact_location = candidates[
            (candidates["state_key"] == state_key)
            & (candidates["district_key"] == district_key)
            & (candidates["location_key"] == location_key)
        ]

        same_district = candidates[
            (candidates["state_key"] == state_key)
            & (candidates["district_key"] == district_key)
        ]

        same_state = candidates[
            candidates["state_key"] == state_key
        ]

        if not exact_location.empty:
            candidates = exact_location.copy()
        elif not same_district.empty:
            candidates = same_district.copy()
        elif not same_state.empty:
            candidates = same_state.copy()

    else:
        closest_bhk = df["bhk_difference"].min()

        candidates = df[
            df["bhk_difference"] == closest_bhk
        ].copy()

        same_state = candidates[
            candidates["state_key"] == state_key
        ]

        if not same_state.empty:
            candidates = same_state.copy()

    # Rank by location match, then predicted rent proximity
    candidates = candidates.sort_values(
        by=["match_score", "rent_difference"],
        ascending=[False, True]
    )

    # Return up to six recommendations
    candidates = candidates.head(6).copy()

    # Remove helper columns before passing records to HTML
    candidates.drop(
        columns=[
            "state_key",
            "district_key",
            "location_key",
            "match_score",
            "bhk_difference",
            "rent_difference"
        ],
        inplace=True,
        errors="ignore"
    )

    # Convert pandas values to ordinary Python values for templates
    candidates = candidates.astype(object).where(
        pd.notna(candidates), None
    )

    records = candidates.to_dict(orient="records")

    # Assign UNIQUE random house images (house1.jpg through house9.jpg) without duplicates
    if records:
        unique_images = random.sample(range(1, 10), min(len(records), 9))
        for i, house in enumerate(records):
            house["house_image"] = f"house{unique_images[i]}.jpg"

    return records


# --------------------------------------------------
# 4. HOME PAGE
# --------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# --------------------------------------------------
# 5. PREDICTION PAGE
# --------------------------------------------------

@app.route("/predict", methods=["POST"])
def predict():

    if not MODEL_PATH.exists():
        return (
            "The trained model was not found. "
            "Open the terminal and run: python train_model.py",
            500
        )

    state = request.form.get("state", "").strip()
    district = request.form.get("district", "").strip()
    location = request.form.get("location", "").strip()
    bhk_input = request.form.get("bhk", "").strip()

    if not all([state, district, location, bhk_input]):
        return "Please fill in all the search fields.", 400

    try:
        bhk = 5 if bhk_input == "5+" else int(bhk_input)

        if bhk < 1:
            raise ValueError

    except ValueError:
        return "Please select a valid BHK value.", 400

    try:
        model = joblib.load(MODEL_PATH)

        user_input = pd.DataFrame([{
            "state": state,
            "district": district,
            "location": location,
            "bhk": bhk
        }])

        prediction = float(model.predict(user_input)[0])

        houses = recommend_houses(
            state=state,
            district=district,
            location=location,
            bhk=bhk,
            prediction=prediction
        )

        print(f"Search: {state}, {district}, {location}, {bhk} BHK")
        print(f"Predicted rent: Rs. {prediction:,.0f}")
        print(f"Recommendations found: {len(houses)}")

        return render_template(
            "result.html",
            prediction=round(prediction),
            state=state,
            district=district,
            location=location,
            bhk=bhk,
            houses=houses
        )

    except Exception as exc:
        app.logger.exception("Prediction failed")
        return (
            f"An error occurred while predicting rent: {exc}",
            500
        )


# --------------------------------------------------
# 6. RUN FLASK APPLICATION
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
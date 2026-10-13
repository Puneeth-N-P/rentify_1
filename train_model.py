
from pathlib import Path

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "dataset" / "rent_data_7500.csv"
MODEL_DIR = BASE_DIR / "model"
MODEL_PATH = MODEL_DIR / "rent_model.pkl"


def train_model():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    required = [
        "state", "district", "location", "bhk", "rent"
    ]

    missing = set(required) - set(df.columns)
    if missing:
        raise ValueError(
            f"Missing dataset columns: {sorted(missing)}"
        )

    df = df[required].dropna().copy()
    df["bhk"] = pd.to_numeric(df["bhk"], errors="coerce")
    df["rent"] = pd.to_numeric(df["rent"], errors="coerce")
    df = df.dropna()

    X = df[["state", "district", "location", "bhk"]]
    y = df["rent"]

    categorical = ["state", "district", "location"]
    numeric = ["bhk"]

    preprocess = ColumnTransformer(
        transformers=[
            (
                "categories",
                OneHotEncoder(handle_unknown="ignore"),
                categorical
            ),
            ("numbers", "passthrough", numeric)
        ]
    )

    pipeline = Pipeline([
        ("preprocess", preprocess),
        (
            "model",
            RandomForestRegressor(
                n_estimators=200,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
        )
    ])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    pipeline.fit(X_train, y_train)
    predictions = pipeline.predict(X_test)

    print("Model training completed!")
    print(f"Records used: {len(df)}")
    print(
        f"Mean Absolute Error: "
        f"{mean_absolute_error(y_test, predictions):.2f}"
    )
    print(f"R² Score: {r2_score(y_test, predictions):.3f}")

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)

    print(f"Model saved to: {MODEL_PATH}")


if __name__ == "__main__":
    train_model()

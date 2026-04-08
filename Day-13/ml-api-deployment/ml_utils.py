import os
import json
import time
import numpy as np
import pandas as pd
import joblib
from datetime import datetime
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
REGISTRY_FILE = os.path.join(MODELS_DIR, "registry.json")

NUM_COLS = ["area", "bedrooms", "bathrooms", "stories", "parking"]
CAT_COLS = [
    "mainroad", "guestroom", "basement",
    "hotwaterheating", "airconditioning", "prefarea",
    "furnishingstatus"
]
FEATURE_COLS = NUM_COLS + CAT_COLS

VALID_YES_NO = {"yes", "no"}
VALID_FURNISHING = {"furnished", "semi-furnished", "unfurnished"}


def _load_registry():
    if not os.path.exists(REGISTRY_FILE):
        return {"versions": []}
    with open(REGISTRY_FILE) as f:
        return json.load(f)


def _save_registry(registry):
    os.makedirs(MODELS_DIR, exist_ok=True)
    with open(REGISTRY_FILE, "w") as f:
        json.dump(registry, f, indent=2)


def get_latest_version(registry=None):
    if registry is None:
        registry = _load_registry()
    versions = registry.get("versions", [])
    return versions[-1] if versions else None


def train(data_path):
    df = pd.read_csv(data_path)

    X = df[FEATURE_COLS]
    y = df["price"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    preprocessor = ColumnTransformer(transformers=[
        ("num", StandardScaler(), NUM_COLS),
        ("cat", OneHotEncoder(drop="first", handle_unknown="ignore"), CAT_COLS)
    ])

    pipeline = Pipeline(steps=[
        ("preprocessing", preprocessor),
        ("model", LinearRegression())
    ])

    pipeline.fit(X_train, np.log(y_train))

    y_pred = np.exp(pipeline.predict(X_test))
    mse = float(mean_squared_error(y_test, y_pred))
    rmse = float(np.sqrt(mse))
    r2 = float(r2_score(y_test, y_pred))

    registry = _load_registry()
    version_num = len(registry["versions"]) + 1
    version = f"v{version_num}"
    model_file = os.path.join(MODELS_DIR, f"model_{version}.joblib")

    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(pipeline, model_file)

    entry = {
        "version": version,
        "file": model_file,
        "metrics": {"mse": mse, "rmse": rmse, "r2": r2},
        "trained_at": datetime.utcnow().isoformat() + "Z",
        "data_path": data_path,
        "train_size": len(X_train),
        "test_size": len(X_test)
    }
    registry["versions"].append(entry)
    _save_registry(registry)

    return entry


def predict(features, version=None):
    registry = _load_registry()
    versions = registry.get("versions", [])

    if not versions:
        raise ValueError("No trained model found. Call POST /train first.")

    if version:
        matches = [v for v in versions if v["version"] == version]
        if not matches:
            raise ValueError(f"Model version '{version}' not found.")
        model_entry = matches[0]
    else:
        model_entry = versions[-1]

    start = time.time()
    pipeline = joblib.load(model_entry["file"])
    df = pd.DataFrame([features])
    predicted_price = float(np.exp(pipeline.predict(df)[0]))
    elapsed_ms = round((time.time() - start) * 1000, 2)

    return {
        "predicted_price": round(predicted_price, 2),
        "model_version": model_entry["version"],
        "response_time_ms": elapsed_ms
    }


def validate_input(data):
    errors = []

    for col in FEATURE_COLS:
        if col not in data:
            errors.append(f"Missing required field: '{col}'")

    if errors:
        return errors

    for col in NUM_COLS:
        val = data[col]
        if not isinstance(val, (int, float)) or val < 0:
            errors.append(f"'{col}' must be a non-negative number, got: {val!r}")

    yes_no_cols = ["mainroad", "guestroom", "basement", "hotwaterheating", "airconditioning", "prefarea"]
    for col in yes_no_cols:
        if data[col] not in VALID_YES_NO:
            errors.append(f"'{col}' must be 'yes' or 'no', got: {data[col]!r}")

    if data["furnishingstatus"] not in VALID_FURNISHING:
        errors.append(
            f"'furnishingstatus' must be one of {sorted(VALID_FURNISHING)}, "
            f"got: {data['furnishingstatus']!r}"
        )

    return errors

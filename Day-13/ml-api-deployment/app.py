import logging
import os
import time
from flask import Flask, request, jsonify
from ml_utils import train, predict, validate_input, _load_registry, get_latest_version

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ── App ───────────────────────────────────────────────────────────────────────
app = Flask(__name__)

# Default dataset: reuse the CSV from Day-7
DEFAULT_DATA_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "Day-7", "Housing.csv")
)


# ── Request / response logging ────────────────────────────────────────────────
@app.before_request
def _start_timer():
    request.start_time = time.time()
    logger.info("→ %s %s | body: %s", request.method, request.path,
                request.get_json(silent=True))


@app.after_request
def _log_response(response):
    elapsed = round((time.time() - request.start_time) * 1000, 2)
    logger.info("← %s | %.2f ms", response.status_code, elapsed)
    return response


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.route("/train", methods=["POST"])
def train_model():
    """
    Train a new model version and save it to disk.

    Body (optional):
        { "data_path": "/path/to/Housing.csv" }

    Returns 201 with version info and metrics on success.
    """
    body = request.get_json(silent=True) or {}
    data_path = os.path.normpath(body.get("data_path", DEFAULT_DATA_PATH))

    if not os.path.exists(data_path):
        return jsonify({"error": f"Data file not found: {data_path}"}), 400

    try:
        result = train(data_path)
        logger.info("Model trained: %s | R²=%.4f RMSE=%.0f",
                    result["version"], result["metrics"]["r2"], result["metrics"]["rmse"])
        return jsonify({
            "message": "Model trained successfully",
            "version": result["version"],
            "metrics": result["metrics"],
            "trained_at": result["trained_at"],
            "train_size": result["train_size"],
            "test_size": result["test_size"]
        }), 201
    except Exception as e:
        logger.error("Training failed: %s", e)
        return jsonify({"error": str(e)}), 500


@app.route("/predict", methods=["POST"])
def make_prediction():
    """
    Predict house price from input features.

    Body:
        {
            "area": 7420, "bedrooms": 4, "bathrooms": 2,
            "stories": 3, "parking": 2,
            "mainroad": "yes", "guestroom": "no", "basement": "no",
            "hotwaterheating": "no", "airconditioning": "yes",
            "prefarea": "yes", "furnishingstatus": "furnished",
            "version": "v1"   ← optional, defaults to latest
        }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON request body is required"}), 400

    version = data.pop("version", None)

    errors = validate_input(data)
    if errors:
        return jsonify({"error": "Validation failed", "details": errors}), 422

    try:
        result = predict(data, version=version)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error("Prediction failed: %s", e)
        return jsonify({"error": str(e)}), 500


@app.route("/model-info", methods=["GET"])
def model_info():
    """
    Return info about trained models.

    Query params:
        ?version=v1   ← return a specific version (omit for all)
    """
    version = request.args.get("version")
    registry = _load_registry()
    versions = registry.get("versions", [])

    if not versions:
        return jsonify({"error": "No models trained yet. Call POST /train first."}), 404

    # Strip internal file paths before responding
    def _safe(entry):
        return {k: v for k, v in entry.items() if k != "file"}

    if version:
        matches = [v for v in versions if v["version"] == version]
        if not matches:
            return jsonify({"error": f"Version '{version}' not found"}), 404
        return jsonify(_safe(matches[0]))

    latest = get_latest_version(registry)
    return jsonify({
        "latest_version": latest["version"],
        "total_versions": len(versions),
        "versions": [_safe(v) for v in versions]
    })


if __name__ == "__main__":
    app.run(debug=True)

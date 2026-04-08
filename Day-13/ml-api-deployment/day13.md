# Day 13 – ML API Deployment

Flask REST API that exposes the Day-7 house price prediction model with model versioning, input validation, and request logging.

## Setup

```bash
pip install flask scikit-learn pandas numpy joblib
python app.py
```

The server starts at `http://127.0.0.1:5000`.

## Endpoints

### `POST /train`
Train a new model version. Each call saves a new `.joblib` file and increments the version (`v1`, `v2`, …).

```json
// Body (optional)
{ "data_path": "/custom/path/Housing.csv" }
```

Defaults to `Day-7/Housing.csv` when no body is sent.

**Response 201**
```json
{
  "message": "Model trained successfully",
  "version": "v1",
  "metrics": { "mse": 1728299885729.06, "rmse": 1314648.2, "r2": 0.658 },
  "trained_at": "2026-04-08T10:00:00Z",
  "train_size": 436,
  "test_size": 109
}
```

---

### `POST /predict`
Predict house price. Optionally pin a model version with `"version": "v1"` (defaults to latest).

```json
{
  "area": 7420,
  "bedrooms": 4,
  "bathrooms": 2,
  "stories": 3,
  "parking": 2,
  "mainroad": "yes",
  "guestroom": "no",
  "basement": "no",
  "hotwaterheating": "no",
  "airconditioning": "yes",
  "prefarea": "yes",
  "furnishingstatus": "furnished"
}
```

| Field | Type | Valid values |
|---|---|---|
| `area`, `bedrooms`, `bathrooms`, `stories`, `parking` | number ≥ 0 | any |
| `mainroad`, `guestroom`, `basement`, `hotwaterheating`, `airconditioning`, `prefarea` | string | `"yes"` / `"no"` |
| `furnishingstatus` | string | `"furnished"` / `"semi-furnished"` / `"unfurnished"` |

**Response 200**
```json
{
  "predicted_price": 12540320.5,
  "model_version": "v1",
  "response_time_ms": 4.21
}
```

**Response 422** (invalid input)
```json
{
  "error": "Validation failed",
  "details": ["'mainroad' must be 'yes' or 'no', got: 'maybe'"]
}
```

---

### `GET /model-info`
List all trained versions, or query a specific one.

```
GET /model-info              → all versions
GET /model-info?version=v1   → specific version
```

## Model Versioning

Each `POST /train` call:
1. Trains a fresh scikit-learn pipeline (StandardScaler + OneHotEncoder + LinearRegression)
2. Fits on log-transformed prices (same as Day-7 notebook)
3. Saves the pipeline as `models/model_vN.joblib`
4. Appends an entry to `models/registry.json`

`/predict` loads `models/registry.json` at request time and picks the latest version unless `version` is specified.

## Logging

All requests and responses are logged to `api.log` and stdout:
```
2026-04-08 10:00:01 [INFO] → POST /train | body: {}
2026-04-08 10:00:03 [INFO] Model trained: v1 | R²=0.6581 RMSE=1314648
2026-04-08 10:00:03 [INFO] ← 201 | 1843.22 ms
```

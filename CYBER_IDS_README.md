# Cyber IDS Module Documentation

## Overview

The **Cyber IDS** module is a production-ready binary intrusion detection system built on the CSE-CIC-IDS2018 dataset. It uses classical tabular machine learning (Logistic Regression, Random Forest, XGBoost) with probability calibration, exposed through Django Ninja REST APIs.

### Key Features

- **Temporal Split by Day**: Prevents data leakage by holding out entire days for validation/test
- **Class Imbalance Handling**: Balanced class weights, scale_pos_weight, optional SMOTE
- **Probability Calibration**: Platt scaling or isotonic regression for reliable confidence scores
- **Reproducible Experiments**: Fixed seeds, artifact manifests, preprocessing parameters
- **CPU-Friendly**: No deep learning; optimized for standard compute

### Metrics Focus

- **Primary**: PR-AUC (macro), Recall@1% FPR, F1 (macro)
- **Secondary**: ROC-AUC, Brier score, per-attack-family metrics, latency (p50/p95)

---

## Architecture

```
CSE-CIC-IDS2018 CSV/Parquet (by day)
    ↓
data_pipeline/pipeline.py
    ├── load_raw_data()
    ├── build_train_test_split_by_day()
    └── preprocess_features()
    ↓
models/train.py
    ├── train_baseline_models() → Majority, LogReg
    ├── train_ensemble_models() → RF, XGBoost
    ├── select_champion() → by PR-AUC
    └── calibrate_model() → isotonic/sigmoid
    ↓
artifacts/ids/
    ├── models/model_{version}.joblib
    ├── metrics/metrics_{version}.json
    ├── pipeline/features_{version}.json
    └── runs/manifest_{version}.json
    ↓
service/predictor.py (PredictorService)
    ↓
app/api/cyber_ids/router.py (Django Ninja)
    ├── POST /ml/train
    ├── POST /ml/predict
    ├── GET /ml/metrics
    └── GET /ml/health
```

---

## Directory Structure

```
cyber_ids/
├── __init__.py
├── config.py                    # Configuration: paths, hyperparams, seeds
├── data_pipeline/
│   ├── __init__.py
│   └── pipeline.py              # Data loading, splitting, preprocessing
├── models/
│   ├── __init__.py
│   └── train.py                 # Training orchestrator
├── metrics/
│   ├── __init__.py
│   └── evaluation.py            # Metrics computation (PR-AUC, Recall@FPR)
└── service/
    ├── __init__.py
    └── predictor.py             # Model serving and inference

app/api/cyber_ids/
├── __init__.py
├── schemas.py                   # Pydantic request/response models
└── router.py                    # Django Ninja endpoints

tests/cyber_ids/
├── __init__.py
├── test_data_pipeline.py
├── test_metrics.py
└── test_api.py

artifacts/ids/                   # Gitignored
├── models/
├── metrics/
├── pipeline/
└── runs/

data/cse-cic-ids2018/            # Mount or download dataset here
├── raw/
│   ├── Wednesday-14-02-2018/
│   ├── Thursday-15-02-2018/
│   └── ...
└── parquet/                     # Converted for fast loading
    ├── Wednesday-14-02-2018.parquet
    └── ...
```

---

## Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Key ML dependencies:
- `numpy>=1.24.0`
- `pandas>=2.0.0`
- `scikit-learn>=1.3.0`
- `xgboost>=2.0.0`
- `joblib>=1.3.0`
- `pyarrow>=14.0.0` (for Parquet)

### 2. Prepare Dataset

Download CSE-CIC-IDS2018 from [UNB](https://www.unb.ca/cic/datasets/ids-2018.html) and organize:

```bash
data/cse-cic-ids2018/raw/
├── Wednesday-14-02-2018/
│   └── Wednesday-14-02-2018.csv
├── Thursday-15-02-2018/
│   └── Thursday-15-02-2018.csv
└── ...
```

**Optional**: Convert to Parquet for faster loading:

```python
from cyber_ids.data_pipeline.pipeline import convert_csv_to_parquet
from pathlib import Path

convert_csv_to_parquet(
    csv_dir=Path("data/cse-cic-ids2018/raw"),
    parquet_dir=Path("data/cse-cic-ids2018/parquet"),
)
```

### 3. Configure Paths

Edit `cyber_ids/config.py` or set environment variables:

```python
# In config.py
DATA_DIR = BASE_DIR / "data" / "cse-cic-ids2018"
ARTIFACT_DIR = BASE_DIR / "artifacts" / "ids"

# Adjust train/val/test days based on your subset
DEFAULT_TRAIN_DAYS = ["Wednesday-14-02-2018", "Thursday-15-02-2018"]
DEFAULT_VAL_DAYS = ["Wednesday-21-02-2018"]
DEFAULT_TEST_DAYS = ["Thursday-22-02-2018"]
```

---

## Usage

### Training via CLI

Run training directly:

```bash
python -m cyber_ids.models.train
```

This will:
1. Load data by day (train/val split)
2. Train baselines and ensembles
3. Select champion by PR-AUC
4. Calibrate probabilities
5. Save artifacts to `artifacts/ids/models/latest.joblib`

**Output**:
```
Training Summary
================================================================================
Champion: xgboost
PR-AUC: 0.9234
Recall@1%FPR: 0.8567
F1 (macro): 0.8821
Model path: artifacts/ids/models/model_20231120T123456Z.joblib
```

### Training via API

Start Django server:

```bash
python manage.py runserver
```

**Trigger training**:

```bash
curl -X POST http://localhost:8000/app/v1/cyber/ml/train \
  -H "Content-Type: application/json" \
  -d '{
    "train_days": ["Wednesday-14-02-2018", "Thursday-15-02-2018"],
    "val_days": ["Wednesday-21-02-2018"],
    "calibration_method": "isotonic",
    "random_seed": 42
  }'
```

**Response**:
```json
{
  "success": true,
  "champion": "xgboost",
  "model_version": "20231120T123456Z",
  "metrics": {
    "pr_auc_macro": 0.9234,
    "recall_at_fpr_1pct": 0.8567,
    "f1_macro": 0.8821,
    "roc_auc": 0.9512,
    "brier_score": 0.0823
  },
  "artifact_paths": {
    "model": "artifacts/ids/models/model_20231120T123456Z.joblib",
    "metrics": "artifacts/ids/metrics/metrics_20231120T123456Z.json"
  },
  "elapsed_seconds": 142.3
}
```

### Prediction via API

**Predict on network flows**:

```bash
curl -X POST http://localhost:8000/app/v1/cyber/ml/predict \
  -H "Content-Type: application/json" \
  -d '{
    "flows": [
      {
        "Fwd Packet Length Mean": 123.45,
        "Bwd Packet Length Mean": 67.89,
        "Flow Duration": 5000.0,
        "Total Fwd Packets": 10,
        "Total Bwd Packets": 5
      }
    ],
    "threshold": 0.5
  }'
```

**Response**:
```json
{
  "predictions": [
    {
      "label": 1,
      "prob": 0.8734,
      "model_version": "20231120T123456Z"
    }
  ],
  "count": 1,
  "latency_ms": 2.34
}
```

**Batch prediction** (up to 100 flows):

```bash
curl -X POST http://localhost:8000/app/v1/cyber/ml/predict \
  -H "Content-Type: application/json" \
  -d '{
    "flows": [
      {"Fwd Packet Length Mean": 123.45, ...},
      {"Fwd Packet Length Mean": 234.56, ...},
      {"Fwd Packet Length Mean": 345.67, ...}
    ]
  }'
```

### Retrieve Metrics

```bash
curl http://localhost:8000/app/v1/cyber/ml/metrics
```

**Response**:
```json
{
  "latest_version": "20231120T123456Z",
  "metrics": {
    "pr_auc_macro": 0.9234,
    "recall_at_fpr_1pct": 0.8567,
    "f1_macro": 0.8821,
    "roc_auc": 0.9512,
    "brier_score": 0.0823
  },
  "latency_stats": {
    "p50_ms": 2.1,
    "p95_ms": 3.8,
    "mean_ms": 2.3,
    "count": 150
  }
}
```

### Health Check

```bash
curl http://localhost:8000/app/v1/cyber/ml/health
```

**Response**:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_version": "20231120T123456Z",
  "n_features": 76
}
```

---

## Docker Deployment

### Update docker-compose.yml

Add volume mounts for dataset and artifacts:

```yaml
services:
  django:
    volumes:
      - .:/code
      - ./data:/code/data              # Dataset
      - ./artifacts:/code/artifacts    # Model artifacts
    # ... rest of config
```

### Training in Docker

**Option 1**: Run training inside existing Django container:

```bash
docker exec -it django python -m cyber_ids.models.train
```

**Option 2**: Add dedicated training service (optional):

```yaml
  ids-trainer:
    container_name: ids-trainer
    build:
      context: .
      dockerfile: Dockerfile
    command: python -m cyber_ids.models.train
    volumes:
      - .:/code
      - ./data:/code/data
      - ./artifacts:/code/artifacts
    env_file:
      - ./.env
    networks:
      - cyber_network
    depends_on:
      - cyber_db
```

Run manually:

```bash
docker-compose run --rm ids-trainer
```

### Serving in Docker

Artifacts are persisted in `./artifacts/ids/`, so Django container can load them:

```bash
docker-compose up -d django
curl http://localhost:8000/app/v1/cyber/ml/health
```

---

## Testing

Run all tests:

```bash
pytest tests/cyber_ids/ -v
```

Run specific test modules:

```bash
# Data pipeline tests
pytest tests/cyber_ids/test_data_pipeline.py -v

# Metrics tests
pytest tests/cyber_ids/test_metrics.py -v

# API tests
pytest tests/cyber_ids/test_api.py -v
```

With coverage:

```bash
pytest tests/cyber_ids/ --cov=cyber_ids --cov-report=html
```

---

## Configuration Reference

### Key Settings (`cyber_ids/config.py`)

| Setting | Default | Description |
|---------|---------|-------------|
| `RANDOM_SEED` | 42 | Reproducibility seed |
| `DEFAULT_TRAIN_DAYS` | `["Wednesday-14-02-2018", ...]` | Training days |
| `DEFAULT_VAL_DAYS` | `["Wednesday-21-02-2018"]` | Validation days |
| `CALIBRATION_METHOD` | `"isotonic"` | `"sigmoid"` or `"isotonic"` |
| `DEFAULT_DECISION_THRESHOLD` | 0.5 | Binary classification threshold |
| `MISSING_THRESHOLD` | 0.3 | Drop features with >30% missing |
| `FPR_TARGETS` | `[0.01, 0.001]` | FPR levels for recall |

### Model Hyperparameters

Configured in `MODEL_CONFIGS` dict:

**Random Forest**:
- `n_estimators`: 300
- `max_depth`: 18
- `class_weight`: `"balanced_subsample"`

**XGBoost**:
- `n_estimators`: 400
- `max_depth`: 8
- `learning_rate`: 0.08
- `scale_pos_weight`: Computed dynamically from class distribution

---

## Troubleshooting

### 1. FileNotFoundError: Data not found

**Cause**: Dataset not in expected location.

**Fix**: Ensure `data/cse-cic-ids2018/parquet/` contains `.parquet` files, or update `DATA_DIR` in `config.py`.

### 2. Model not loaded

**Cause**: No trained model at `artifacts/ids/models/latest.joblib`.

**Fix**: Train a model first:

```bash
python -m cyber_ids.models.train
```

### 3. Feature mismatch in prediction

**Cause**: Input features don't match training features.

**Fix**: Ensure prediction request includes all features in `features_{version}.json`. Missing features are filled with imputed values, but column names must match.

### 4. Low PR-AUC

**Cause**: Poor class balance, insufficient data, or weak features.

**Fix**: 
- Increase training days
- Tune `scale_pos_weight` in XGBoost
- Try SMOTE (add to `train.py`)
- Check feature distributions

### 5. High Brier score (poor calibration)

**Cause**: Probabilities not well-calibrated.

**Fix**: Ensure calibration is enabled; try switching between `"sigmoid"` and `"isotonic"` methods.

---

## API Reference

### POST /ml/train

**Request**:
```json
{
  "train_days": ["string"],
  "val_days": ["string"],
  "test_days": ["string"],  // optional
  "calibration_method": "isotonic",  // or "sigmoid"
  "random_seed": 42
}
```

**Response**: `TrainResponse` schema

### POST /ml/predict

**Request**:
```json
{
  "flows": [{"feature_name": float, ...}],
  "threshold": 0.5  // optional
}
```

**Response**: `PredictResponse` schema

### GET /ml/metrics

**Response**: `MetricsResponse` schema

### GET /ml/health

**Response**: `HealthResponse` schema

---

## Leakage Guards

The module implements strict guards against data leakage:

1. **Day-Level Split**: Entire days held out; no row-level shuffling across days
2. **Feature List Derived from Train Only**: Validation/test never influence feature selection
3. **Preprocessing Fit on Train**: Imputation medians, clipping quantiles computed only on training set
4. **No Future Information**: Timestamps, flow IDs, IPs dropped before modeling

---

## Performance Tips

### Faster Training

- Use Parquet instead of CSV (10-100x faster loading)
- Reduce `n_estimators` for prototyping
- Use subset of days (e.g., 2-3 days instead of 7)

### Faster Inference

- Batch predictions (up to 100 flows per request)
- Model loaded once and cached in `PredictorService`
- Use `tree_method="hist"` in XGBoost for speed

### Memory Optimization

- Process days sequentially if full dataset doesn't fit in RAM
- Use `low_memory=False` in `pd.read_csv()` or switch to Parquet

---

## Extending the Module

### Add New Model

Edit `cyber_ids/models/train.py`:

```python
def train_ensemble_models(...):
    # ...existing code...
    
    # Add LightGBM
    import lightgbm as lgb
    lgb_model = lgb.LGBMClassifier(...)
    lgb_model.fit(X_train, y_train)
    models["lightgbm"] = lgb_model
    
    return models
```

### Add Per-Family Metrics

Implement in `cyber_ids/metrics/evaluation.py`:

```python
def compute_per_family_metrics(...):
    # Already stubbed; load attack labels and compute family-wise precision/recall
    ...
```

Wire into `router.py`:

```python
@router.get("/metrics", response=schemas.MetricsResponse)
def metrics_endpoint(...):
    # Load per-family metrics from manifest
    per_family = load_per_family_from_manifest(...)
    return schemas.MetricsResponse(..., per_family=per_family)
```

### Add Threshold Tuning Endpoint

```python
@router.post("/ml/tune_threshold")
def tune_threshold_endpoint(request, target_metric: str):
    # Load validation data
    # Compute optimal threshold for target_metric (e.g., "f1", "recall@1%fpr")
    # Update artifact and return new threshold
    ...
```

---

## Citation

If using CSE-CIC-IDS2018, cite:

```
Sharafaldin, I., Lashkari, A.H., Ghorbani, A.A. (2018).
Toward Generating a New Intrusion Detection Dataset and Intrusion Traffic Characterization.
In: 4th International Conference on Information Systems Security and Privacy (ICISSP).
```

---

## License

This module is part of the Cyber project. See main repository LICENSE.

---

## Support

For issues or questions:
- GitHub Issues: https://github.com/antgonto/Cyber/issues
- Contact: antonio.gonto@nyu.edu (replace with actual contact)


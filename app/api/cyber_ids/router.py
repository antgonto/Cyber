"""
Django Ninja router for Cyber IDS API endpoints.

Exposes:
- POST /ml/train: Trigger model training
- POST /ml/predict: Predict on network flows
- GET /ml/metrics: Retrieve latest metrics
- GET /ml/health: Health check
"""

import json
import logging
from pathlib import Path
from typing import Optional

from ninja import Router
from django.http import HttpRequest

from app.api.cyber_ids import schemas
from cyber_ids.models.train import train_all
from cyber_ids.service.predictor import get_predictor
from cyber_ids.config import ARTIFACT_DIR

logger = logging.getLogger(__name__)

router = Router(tags=["cyber-ids"])


@router.post("/train", response=schemas.TrainResponse)
def train_endpoint(request: HttpRequest, payload: schemas.TrainRequest):
    """
    Train Cyber IDS models on CSE-CIC-IDS2018 dataset.

    Workflow:
    1. Load data by day (train/val/test split)
    2. Train baselines (majority, logistic regression)
    3. Train ensembles (Random Forest, XGBoost)
    4. Select champion by PR-AUC
    5. Calibrate probabilities
    6. Save artifacts and metrics

    Returns:
        Training summary with champion model, metrics, and artifact paths
    """
    logger.info("Received training request")

    try:
        # Build config from request
        config = {}
        if payload.train_days:
            config["train_days"] = payload.train_days
        if payload.val_days:
            config["val_days"] = payload.val_days
        if payload.test_days:
            config["test_days"] = payload.test_days
        if payload.calibration_method:
            config["calibration_method"] = payload.calibration_method
        if payload.random_seed:
            config["random_seed"] = payload.random_seed

        # Run training
        result = train_all(config)

        # Extract version from artifact path
        model_path = Path(result["artifact_paths"]["model"])
        version = model_path.stem.split("_")[-1]

        # Force predictor reload after training
        predictor = get_predictor()
        predictor.reload()

        return schemas.TrainResponse(
            success=True,
            champion=result["champion"],
            model_version=version,
            metrics=schemas.MetricsEntry(**result["metrics"]),
            artifact_paths=result["artifact_paths"],
            elapsed_seconds=result["elapsed_seconds"],
            message=f"Training complete. Champion: {result['champion']}",
        )

    except FileNotFoundError as e:
        logger.error(f"Training failed - data not found: {e}")
        return schemas.TrainResponse(
            success=False,
            champion="none",
            model_version="none",
            metrics=schemas.MetricsEntry(
                pr_auc_macro=0.0,
                recall_at_fpr_1pct=0.0,
                f1_macro=0.0,
                precision_macro=0.0,
                recall_macro=0.0,
                roc_auc=0.0,
                brier_score=1.0,
            ),
            artifact_paths={},
            elapsed_seconds=0.0,
            message=f"Training failed: {str(e)}",
        )

    except Exception as e:
        logger.exception("Training failed with unexpected error")
        return schemas.TrainResponse(
            success=False,
            champion="none",
            model_version="none",
            metrics=schemas.MetricsEntry(
                pr_auc_macro=0.0,
                recall_at_fpr_1pct=0.0,
                f1_macro=0.0,
                precision_macro=0.0,
                recall_macro=0.0,
                roc_auc=0.0,
                brier_score=1.0,
            ),
            artifact_paths={},
            elapsed_seconds=0.0,
            message=f"Training failed: {str(e)}",
        )


@router.post("/predict", response=schemas.PredictResponse)
def predict_endpoint(request: HttpRequest, payload: schemas.PredictRequest):
    """
    Predict attack/benign labels for network flows.

    Input:
        List of flow feature dictionaries with CICFlowMeter features

    Output:
        List of predictions with label, probability, and model version

    Example:
        POST /ml/predict
        {
            "flows": [
                {"Fwd Packet Length Mean": 123.45, "Flow Duration": 1000.0, ...},
                {"Fwd Packet Length Mean": 200.0, "Flow Duration": 5000.0, ...}
            ],
            "threshold": 0.5
        }
    """
    logger.info(f"Received prediction request for {len(payload.flows)} flow(s)")

    try:
        # Get predictor (lazy loads model)
        predictor = get_predictor()
        predictor.ensure_loaded()

        # Predict
        import time
        start = time.perf_counter()
        results = predictor.predict(payload.flows, threshold=payload.threshold)
        latency_ms = (time.perf_counter() - start) * 1000

        return schemas.PredictResponse(
            predictions=[schemas.PredictionItem(**r) for r in results],
            count=len(results),
            latency_ms=latency_ms,
        )

    except FileNotFoundError as e:
        logger.error(f"Prediction failed - model not found: {e}")
        raise

    except Exception as e:
        logger.exception("Prediction failed")
        raise


@router.get("/metrics", response=schemas.MetricsResponse)
def metrics_endpoint(request: HttpRequest):
    """
    Retrieve latest model metrics.

    Returns:
        Latest validation metrics, per-family stats, and latency statistics
    """
    logger.info("Received metrics request")

    try:
        artifact_dir = Path(ARTIFACT_DIR)

        # Find latest metrics file
        metrics_dir = artifact_dir / "metrics"
        metrics_files = sorted(metrics_dir.glob("metrics_*.json"), reverse=True)

        if not metrics_files:
            raise FileNotFoundError("No metrics found. Train a model first.")

        latest_metrics_file = metrics_files[0]
        version = latest_metrics_file.stem.split("_")[-1]

        # Load metrics
        with open(latest_metrics_file, "r") as f:
            metrics_data = json.load(f)

        # Get latency stats from predictor
        predictor = get_predictor()
        latency_stats = predictor.get_latency_stats() if predictor.model else None

        return schemas.MetricsResponse(
            latest_version=version,
            metrics=schemas.MetricsEntry(**metrics_data),
            per_family=None,  # TODO: implement per-family metrics loading
            latency_stats=latency_stats,
        )

    except FileNotFoundError as e:
        logger.error(f"Metrics retrieval failed: {e}")
        raise

    except Exception as e:
        logger.exception("Metrics retrieval failed")
        raise


@router.get("/health", response=schemas.HealthResponse)
def health_endpoint(request: HttpRequest):
    """
    Health check endpoint.

    Returns:
        Service status and model loading state
    """
    try:
        predictor = get_predictor()

        if predictor.model is None:
            return schemas.HealthResponse(
                status="healthy",
                model_loaded=False,
                model_version=None,
                n_features=None,
            )

        return schemas.HealthResponse(
            status="healthy",
            model_loaded=True,
            model_version=predictor.version,
            n_features=len(predictor.feature_order),
        )

    except Exception as e:
        logger.exception("Health check failed")
        return schemas.HealthResponse(
            status="unhealthy",
            model_loaded=False,
            model_version=None,
            n_features=None,
        )


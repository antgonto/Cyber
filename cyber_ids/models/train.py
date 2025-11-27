"""
Model training orchestrator for Cyber IDS.

Trains baseline and ensemble models on CSE-CIC-IDS2018 with:
- Class imbalance handling (balanced weights, scale_pos_weight)
- Probability calibration (isotonic/Platt scaling)
- Model selection by PR-AUC
- Artifact persistence (models, metrics, manifests)
"""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV

try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    logging.warning("XGBoost not available; install with: pip install xgboost")

from cyber_ids.config import (
    ARTIFACT_DIR,
    RANDOM_SEED,
    MODEL_CONFIGS,
    CALIBRATION_METHOD,
    CALIBRATION_CV,
    SELECTION_METRICS,
    FPR_TARGETS,
    DEFAULT_TRAIN_DAYS,
    DEFAULT_VAL_DAYS,
    DEFAULT_TEST_DAYS,
)
from cyber_ids.data_pipeline.pipeline import (
    build_train_test_split_by_day,
    derive_feature_list,
    build_feature_matrix_and_labels,
    preprocess_features,
)
from cyber_ids.metrics.evaluation import (
    compute_metrics_bundle,
    compare_models,
    find_optimal_threshold_for_f1,
)

logger = logging.getLogger(__name__)


def set_random_seed(seed: int = RANDOM_SEED) -> None:
    """Set random seeds for reproducibility."""
    np.random.seed(seed)
    try:
        import random
        random.seed(seed)
    except ImportError:
        pass


def train_baseline_models(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    random_state: int = RANDOM_SEED,
) -> Dict[str, Any]:
    """
    Train baseline models: majority class predictor and logistic regression.

    Args:
        X_train: Training features
        y_train: Training labels
        random_state: Random seed

    Returns:
        Dictionary of model_name → fitted model
    """
    models = {}

    # 1. Majority class baseline
    logger.info("Training majority class baseline...")
    majority = DummyClassifier(strategy="most_frequent", random_state=random_state)
    majority.fit(X_train, y_train)
    models["majority"] = majority

    # 2. Logistic Regression with balanced weights
    logger.info("Training logistic regression...")
    log_reg_config = MODEL_CONFIGS.get("logistic_regression", {})
    log_reg = LogisticRegression(**log_reg_config)
    log_reg.fit(X_train, y_train)
    models["logistic_regression"] = log_reg

    return models


def train_ensemble_models(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    random_state: int = RANDOM_SEED,
) -> Dict[str, Any]:
    """
    Train tree ensemble models: Random Forest and XGBoost.

    Args:
        X_train: Training features
        y_train: Training labels
        random_state: Random seed

    Returns:
        Dictionary of model_name → fitted model
    """
    models = {}

    # 1. Random Forest with balanced subsample weights
    logger.info("Training Random Forest...")
    rf_config = MODEL_CONFIGS.get("random_forest", {})
    rf = RandomForestClassifier(**rf_config)
    rf.fit(X_train, y_train)
    models["random_forest"] = rf

    # 2. XGBoost with scale_pos_weight for imbalance
    if XGBOOST_AVAILABLE:
        logger.info("Training XGBoost...")
        xgb_config = MODEL_CONFIGS.get("xgboost", {}).copy()

        # Compute scale_pos_weight dynamically
        n_neg = (y_train == 0).sum()
        n_pos = (y_train == 1).sum()
        scale_pos_weight = n_neg / max(n_pos, 1)
        xgb_config["scale_pos_weight"] = scale_pos_weight

        logger.info(f"XGBoost scale_pos_weight: {scale_pos_weight:.2f}")

        xgb = XGBClassifier(**xgb_config)
        xgb.fit(X_train, y_train)
        models["xgboost"] = xgb
    else:
        logger.warning("Skipping XGBoost (not installed)")

    return models


def evaluate_models(
    models: Dict[str, Any],
    X_val: pd.DataFrame,
    y_val: pd.Series,
    fpr_targets: List[float] = FPR_TARGETS,
) -> Dict[str, Dict[str, float]]:
    """
    Evaluate all models on validation set.

    Args:
        models: Dictionary of fitted models
        X_val: Validation features
        y_val: Validation labels
        fpr_targets: FPR thresholds for recall computation

    Returns:
        Dictionary of model_name → metrics_dict
    """
    metrics_per_model = {}

    for name, model in models.items():
        logger.info(f"Evaluating {name}...")

        # Predict probabilities
        if hasattr(model, "predict_proba"):
            y_proba = model.predict_proba(X_val)[:, 1]
        else:
            # Fallback for models without predict_proba
            y_proba = model.predict(X_val).astype(float)

        # Compute metrics
        metrics = compute_metrics_bundle(y_val, y_proba, fpr_targets=fpr_targets)
        metrics_per_model[name] = metrics

        logger.info(
            f"{name}: PR-AUC={metrics['pr_auc_macro']:.4f}, "
            f"Recall@1%FPR={metrics.get('recall_at_fpr_1pct', 0):.4f}, "
            f"F1={metrics['f1_macro']:.4f}"
        )

    return metrics_per_model


def select_champion(
    metrics_per_model: Dict[str, Dict[str, float]],
    selection_metrics: List[str] = SELECTION_METRICS,
) -> str:
    """
    Select best model by hierarchical metric criteria.

    Selection protocol:
    1. Maximize PR-AUC (macro)
    2. Break ties with Recall@1%FPR
    3. Final tie-breaker: F1 (macro)

    Args:
        metrics_per_model: model_name → metrics
        selection_metrics: Priority-ordered list of metric names

    Returns:
        Name of champion model
    """
    # Sort by metrics in priority order
    items = list(metrics_per_model.items())

    def sort_key(item):
        name, metrics = item
        return tuple(metrics.get(m, 0) for m in selection_metrics)

    best = sorted(items, key=sort_key, reverse=True)[0]
    champion_name = best[0]

    logger.info(f"Champion model: {champion_name}")
    return champion_name


def calibrate_model(
    model: Any,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    method: str = CALIBRATION_METHOD,
) -> Any:
    """
    Apply probability calibration to model.

    Calibration improves probability estimates, which is critical for:
    - Reliable thresholding
    - Better Brier scores
    - Trustworthy confidence scores

    Args:
        model: Fitted model
        X_val: Validation features (held-out for calibration)
        y_val: Validation labels
        method: 'sigmoid' (Platt scaling) or 'isotonic'

    Returns:
        Calibrated model
    """
    logger.info(f"Calibrating model with method={method}...")

    calibrated = CalibratedClassifierCV(
        model,
        method=method,
        cv=CALIBRATION_CV,  # 'prefit' since we have separate val set
    )

    calibrated.fit(X_val, y_val)

    logger.info("Calibration complete")
    return calibrated


def persist_artifacts(
    model: Any,
    metrics: Dict[str, float],
    feature_cols: List[str],
    preprocess_params: Dict,
    config: Dict,
    champion_name: str,
) -> Dict[str, str]:
    """
    Save model, metrics, feature list, and run manifest to disk.

    Args:
        model: Trained (and calibrated) model
        metrics: Evaluation metrics dictionary
        feature_cols: List of feature column names
        preprocess_params: Preprocessing parameters (imputation values, etc.)
        config: Training configuration
        champion_name: Name of champion model

    Returns:
        Dictionary of artifact_type → file_path
    """
    # Generate version timestamp
    version = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

    artifact_dir = Path(ARTIFACT_DIR)
    artifact_dir.mkdir(parents=True, exist_ok=True)

    paths = {}

    # 1. Save model
    model_path = artifact_dir / "models" / f"model_{version}.joblib"
    model_path.parent.mkdir(exist_ok=True)
    joblib.dump(model, model_path)
    paths["model"] = str(model_path)
    logger.info(f"Saved model: {model_path}")

    # 2. Save metrics
    metrics_path = artifact_dir / "metrics" / f"metrics_{version}.json"
    metrics_path.parent.mkdir(exist_ok=True)
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    paths["metrics"] = str(metrics_path)
    logger.info(f"Saved metrics: {metrics_path}")

    # 3. Save feature list
    features_path = artifact_dir / "pipeline" / f"features_{version}.json"
    features_path.parent.mkdir(exist_ok=True)
    with open(features_path, "w") as f:
        json.dump(feature_cols, f, indent=2)
    paths["features"] = str(features_path)

    # 4. Save preprocessing parameters
    preprocess_path = artifact_dir / "pipeline" / f"preprocess_{version}.json"
    with open(preprocess_path, "w") as f:
        json.dump(preprocess_params, f, indent=2)
    paths["preprocess"] = str(preprocess_path)

    # 5. Save run manifest
    manifest = {
        "version": version,
        "timestamp": datetime.utcnow().isoformat(),
        "champion_model": champion_name,
        "train_days": config.get("train_days"),
        "val_days": config.get("val_days"),
        "test_days": config.get("test_days"),
        "random_seed": config.get("random_seed", RANDOM_SEED),
        "n_features": len(feature_cols),
        "calibration_method": config.get("calibration_method", CALIBRATION_METHOD),
        "metrics_summary": {
            "pr_auc_macro": metrics.get("pr_auc_macro"),
            "recall_at_fpr_1pct": metrics.get("recall_at_fpr_1pct"),
            "f1_macro": metrics.get("f1_macro"),
        },
    }

    manifest_path = artifact_dir / "runs" / f"manifest_{version}.json"
    manifest_path.parent.mkdir(exist_ok=True)
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    paths["manifest"] = str(manifest_path)
    logger.info(f"Saved manifest: {manifest_path}")

    # 6. Update "latest" symlink (or copy)
    latest_model_path = artifact_dir / "models" / "latest.joblib"
    try:
        latest_model_path.unlink(missing_ok=True)
    except Exception:
        pass
    joblib.dump(model, latest_model_path)
    paths["latest"] = str(latest_model_path)

    return paths


def train_all(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Main training orchestrator.

    Workflow:
    1. Load data (train/val/test split by day)
    2. Derive feature list (from train only)
    3. Preprocess features (fit on train, apply to val/test)
    4. Train baselines and ensembles
    5. Evaluate on validation set
    6. Select champion model
    7. Calibrate champion on validation set
    8. Persist artifacts
    9. Return summary

    Args:
        config: Optional config overrides (days, hyperparams, etc.)

    Returns:
        Dictionary with champion_name, metrics, artifact_paths
    """
    config = config or {}
    set_random_seed(config.get("random_seed", RANDOM_SEED))

    logger.info("=" * 80)
    logger.info("Starting Cyber IDS training pipeline")
    logger.info("=" * 80)

    start_time = time.time()

    # 1. Load data
    train_days = config.get("train_days", DEFAULT_TRAIN_DAYS)
    val_days = config.get("val_days", DEFAULT_VAL_DAYS)
    test_days = config.get("test_days", DEFAULT_TEST_DAYS)

    logger.info(f"Loading data: train={train_days}, val={val_days}, test={test_days}")

    train_df, val_df, test_df = build_train_test_split_by_day(
        train_days=train_days,
        val_days=val_days,
        test_days=test_days,
        use_parquet=True,
    )

    # 2. Derive feature list (from train only to prevent leakage)
    feature_cols = derive_feature_list(train_df)
    logger.info(f"Selected {len(feature_cols)} features")

    # 3. Build feature matrices
    X_train, y_train = build_feature_matrix_and_labels(train_df, feature_cols)
    X_val, y_val = build_feature_matrix_and_labels(val_df, feature_cols)

    if test_df is not None:
        X_test, y_test = build_feature_matrix_and_labels(test_df, feature_cols)
    else:
        X_test, y_test = None, None

    # 4. Preprocess
    X_train, X_val, X_test, preprocess_params = preprocess_features(
        X_train, X_val, X_test
    )

    # 5. Train models
    logger.info("Training baseline models...")
    baseline_models = train_baseline_models(X_train, y_train)

    logger.info("Training ensemble models...")
    ensemble_models = train_ensemble_models(X_train, y_train)

    all_models = {**baseline_models, **ensemble_models}

    # 6. Evaluate on validation set
    logger.info("Evaluating models on validation set...")
    metrics_per_model = evaluate_models(all_models, X_val, y_val)

    # Print comparison table
    comparison_df = compare_models(metrics_per_model)
    logger.info(f"\nModel comparison:\n{comparison_df.to_string()}")

    # 7. Select champion
    champion_name = select_champion(metrics_per_model)
    champion_model = all_models[champion_name]
    champion_metrics = metrics_per_model[champion_name]

    # 8. Calibrate champion
    calibrated_model = calibrate_model(
        champion_model,
        X_val,
        y_val,
        method=config.get("calibration_method", CALIBRATION_METHOD),
    )

    # Re-evaluate calibrated model
    logger.info("Evaluating calibrated champion...")
    y_val_proba_calibrated = calibrated_model.predict_proba(X_val)[:, 1]
    calibrated_metrics = compute_metrics_bundle(y_val, y_val_proba_calibrated)

    logger.info(
        f"After calibration: Brier={calibrated_metrics['brier_score']:.4f} "
        f"(before: {champion_metrics['brier_score']:.4f})"
    )

    # 9. Persist artifacts
    artifact_paths = persist_artifacts(
        model=calibrated_model,
        metrics=calibrated_metrics,
        feature_cols=feature_cols,
        preprocess_params=preprocess_params,
        config=config,
        champion_name=champion_name,
    )

    elapsed = time.time() - start_time
    logger.info(f"Training complete in {elapsed:.1f}s")

    return {
        "champion": champion_name,
        "metrics": calibrated_metrics,
        "artifact_paths": artifact_paths,
        "all_metrics": metrics_per_model,
        "elapsed_seconds": elapsed,
    }


if __name__ == "__main__":
    # CLI entry point for manual training
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    result = train_all()
    print("\n" + "=" * 80)
    print("Training Summary")
    print("=" * 80)
    print(f"Champion: {result['champion']}")
    print(f"PR-AUC: {result['metrics']['pr_auc_macro']:.4f}")
    print(f"Recall@1%FPR: {result['metrics'].get('recall_at_fpr_1pct', 0):.4f}")
    print(f"F1 (macro): {result['metrics']['f1_macro']:.4f}")
    print(f"Model path: {result['artifact_paths']['model']}")


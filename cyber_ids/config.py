"""
Configuration for Cyber IDS module.

Centralizes all paths, hyperparameters, feature lists, and reproducibility settings.
"""

from pathlib import Path
from typing import List, Dict, Any

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
CYBER_IDS_DIR = BASE_DIR / "cyber_ids"
DATA_DIR = BASE_DIR / "data" / "cse-cic-ids2018"
ARTIFACT_DIR = BASE_DIR / "artifacts" / "ids"

# Ensure directories exist
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
(ARTIFACT_DIR / "models").mkdir(exist_ok=True)
(ARTIFACT_DIR / "metrics").mkdir(exist_ok=True)
(ARTIFACT_DIR / "pipeline").mkdir(exist_ok=True)
(ARTIFACT_DIR / "runs").mkdir(exist_ok=True)

# Reproducibility
RANDOM_SEED = 42

# Dataset configuration
# These are the typical CSE-CIC-IDS2018 days; adjust based on your subset
DEFAULT_TRAIN_DAYS = ["Wednesday-14-02-2018", "Thursday-15-02-2018", "Friday-16-02-2018"]
DEFAULT_VAL_DAYS = ["Wednesday-21-02-2018"]
DEFAULT_TEST_DAYS = ["Thursday-22-02-2018"]

# Label configuration
LABEL_COL = "Label"
ATTACK_CATEGORY_COL = "Attack"  # For per-family metrics (if available in your dataset)

# Binary label mapping
LABEL_MAP = {
    "Benign": 0,
    "Attack": 1,
    # If your dataset has specific attack names, they should all map to 1
}

# Features to drop (leakage-prone or non-predictive)
# Typical CICFlowMeter columns that can cause leakage:
DROP_COLS = [
    "Flow ID",
    "Source IP",
    "Src IP",
    "Destination IP",
    "Dst IP",
    "Source Port",
    "Src Port",
    "Destination Port",
    "Dst Port",
    "Timestamp",
    "Protocol",  # Consider keeping if categorical encoding is used
    "Label",
    "Attack",
]

# Model hyperparameters
MODEL_CONFIGS = {
    "logistic_regression": {
        "max_iter": 200,
        "class_weight": "balanced",
        "random_state": RANDOM_SEED,
        "n_jobs": -1,
    },
    "random_forest": {
        "n_estimators": 300,
        "max_depth": 18,
        "min_samples_split": 10,
        "min_samples_leaf": 4,
        "class_weight": "balanced_subsample",
        "random_state": RANDOM_SEED,
        "n_jobs": -1,
    },
    "xgboost": {
        "n_estimators": 400,
        "max_depth": 8,
        "learning_rate": 0.08,
        "subsample": 0.9,
        "colsample_bytree": 0.8,
        "reg_lambda": 1.0,
        "random_state": RANDOM_SEED,
        "tree_method": "hist",
        "n_jobs": -1,
        # scale_pos_weight will be computed dynamically based on class distribution
    },
}

# Calibration settings
CALIBRATION_METHOD = "isotonic"  # 'sigmoid' for Platt scaling, 'isotonic' for isotonic regression
CALIBRATION_CV = "prefit"  # Use prefit since we have separate validation set

# Decision threshold (can be tuned post-training)
DEFAULT_DECISION_THRESHOLD = 0.5

# Preprocessing
IMPUTATION_STRATEGY = "median"  # For numeric features
VARIANCE_THRESHOLD = 0.01  # Drop features with variance below this
MISSING_THRESHOLD = 0.3  # Drop features with >30% missing values

# Model selection criteria
# Primary: PR-AUC (macro)
# Tie-breaker: Recall@1%FPR
# Fallback: F1 (macro)
SELECTION_METRICS = ["pr_auc_macro", "recall_at_fpr_1pct", "f1_macro"]

# FPR targets for recall computation
FPR_TARGETS = [0.01, 0.001]  # 1% and 0.1%

# Attack families for per-family metrics (adjust based on your dataset)
ATTACK_FAMILIES = {
    "DoS/DDoS": ["DoS slowloris", "DoS Slowhttptest", "DoS Hulk", "DoS GoldenEye", "DDoS"],
    "Brute Force": ["FTP-BruteForce", "SSH-Bruteforce", "Brute Force"],
    "Web Attack": ["Web Attack – Brute Force", "Web Attack – XSS", "Web Attack – Sql Injection"],
    "Botnet": ["Bot"],
    "Infiltration": ["Infiltration"],
}

# API settings
API_BATCH_SIZE_LIMIT = 100  # Max flows per predict request

# Logging
LOG_LEVEL = "INFO"


def get_config() -> Dict[str, Any]:
    """Return full configuration as dictionary."""
    return {
        "data_dir": str(DATA_DIR),
        "artifact_dir": str(ARTIFACT_DIR),
        "random_seed": RANDOM_SEED,
        "train_days": DEFAULT_TRAIN_DAYS,
        "val_days": DEFAULT_VAL_DAYS,
        "test_days": DEFAULT_TEST_DAYS,
        "label_col": LABEL_COL,
        "drop_cols": DROP_COLS,
        "model_configs": MODEL_CONFIGS,
        "calibration_method": CALIBRATION_METHOD,
        "decision_threshold": DEFAULT_DECISION_THRESHOLD,
        "selection_metrics": SELECTION_METRICS,
        "fpr_targets": FPR_TARGETS,
    }

